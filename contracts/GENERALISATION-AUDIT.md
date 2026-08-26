# What happens if you run this pipeline on a second patent

The user's question, in their words: "if i ran this for diff patent add this thing in
that so that we all the data created in the pipeline".

Audited 2026-08-27 by running a synthetic `US9999999B2` through a pack already holding
a completed CN104292137A, in a throwaway copy. The answer is worse than "it breaks".

## The headline

**It builds a chimera and publishes it to the deliverable before anything objects.**

Of the paths the runner declares across its sixteen stages, **11 carry the patent id
and 108 do not.** The scoped ones are only the enriched markdown, the biblio, the
rendered prompts and the checks file. Everything else - the whole of `output/stages/`,
the whole of `output/relevant_output/gold/`, `input/vision/`, `input/pages/`, both
curated files and all fifteen `output/*.json` - is a single unnamed slot.

**The pack holds exactly one patent at a time, structurally.** A second run does not
create a second dataset. It overwrites the first in place.

## The failure, step by step

1. The prereq check **passes**, because every A0-A5 file it looks for is unscoped, so
   patent one's files satisfy patent two's prerequisites.
2. `collect`, `merge`, `publish-gold`, `structures` and `assemble` are all judged
   **current** and skipped, on patent one's outputs.
3. `finalise` runs and prints `compounds : 143 extracted across sections -> 75 unique`
   **for US9999999B2**. Those are patent one's 75 compounds.
4. It writes `output/compounds.json`: 75 records, **every one carrying
   `patent_id: CN104292137A`**.
5. It writes `output/patent.json` with `patent_id: US9999999B2` and an aspirin title.
6. `validate` **passes**. The schema never cross-checks that a record's `patent_id`
   matches the run, or matches `patent.json`.
7. `publish-gold` copies the result into the deliverable. `AUDIT.md` is retitled
   "# A5 adversarial audit of US9999999B2" over patent one's four audits.

Seven artifacts written and the gold published before anything complains.

## What saves it, and why that is not enough

`resolve_structures.py`, at stage 8 of 16, refuses:

    structures-curated.json is for patent 'CN104292137A', this run is 'US9999999B2'
    gold compounds.json carries patent_id ['CN104292137A'], this run is 'US9999999B2'

Both messages are exactly right. But it is one script, eight stages downstream of the
damage, and **on a run where the structures stage looks current it is skipped
entirely.** It only fired here because the runner had recorded a previous failure.

**Fix: move the `patent_id` assertion up into `finalise.py` and `schemas/validate.py`,
the first two places that touch every record.** A guard that runs after the deliverable
is published is a post-mortem, not a gate.

## Three more defects found on the way

**The plan is computed once and never re-checked.** `main()` evaluates `is_current()`
for all sixteen stages BEFORE running any, then executes that fixed plan. But running
stage N rewrites stage N+1's inputs. Demonstrated on the real patent: change one field
in the biblio, and `finalise` runs while `publish-gold` stays skipped, so
`output/patent.json` holds the new value, the published gold holds the old one, and
**the manifest records `publish-gold: current`.** The deliverable is stale and the
manifest asserts it is fresh, which is the one question a manifest exists to answer.
Evaluate `is_current()` immediately before each stage, or mark downstream stages dirty
when a stage actually runs. Keep the up-front plan as a forecast, never as a decision.

**`visual` and `selfcheck` never run.** They are ordered after `verify`, which is a
gate and fails today by design. So a plain full run exits 2 at `verify` and never
reaches them. Deleting `output/relevant_output/visual/` and running the pipeline does
not recreate it. The visual assets exist only because someone runs the script by hand -
**which is exactly the gap the user asked to close, reappearing one stage downstream of
a gate that is red on purpose and may stay red for a long time.** Whether visual
evidence should be blocked by a grounding failure is a judgement call. Right now it is
blocked by default and nothing says so.

**`finalise.py:364` hardcodes `"country": "CN"` for every inventor.** A US patent's
inventors are silently labelled Chinese. Not a crash. Wrong data, in the deliverable.

**The biblio input has no contract.** 13 fields are required through bare `b["key"]`
access with no schema, failing one at a time. `grant_date` is fatal for any ungranted
application, which is most published applications.

## The honest summary

The deterministic stages after the gold are reproducible, gated properly, and the
runner swallows nothing: eight induced failures all propagated, gate stages exiting 2
and non-gate stages 1, every message reprinted.

What does not generalise is the **layout**. One patent per pack, enforced nowhere,
with the id carried on 11 paths out of 119. Until that is fixed, "run it on a different
patent" means "overwrite the last one and hope a stage eight steps in notices".
