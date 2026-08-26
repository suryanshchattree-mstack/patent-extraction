# The pipeline

One entry point. One patent in, the whole deliverable out.

```bash
python3 run_pipeline.py --patent-id CN104292137A
```

![The stage graph of run_pipeline.py](svg/p1-pipeline-stages.svg)

> Fourteen deterministic stages, in the only order that satisfies the real
> dependencies between them. Three of them are gates: they exit non-zero and stop
> the run rather than shipping something a human has not supplied. The top band is
> what the runner does **not** do, and refuses to start without.

---

## Why this exists

The annotation passes A0 to A5 produce the gold. Everything that makes the gold
*usable* was a series of scripts run by hand: structures, translations, diagrams,
the deliverable tree, the verification file the reviewer UI reads. The order lived
in one person's head.

Run patent number two and you got the gold and nothing else. No structures, so the
verification contract's `structure_svg_path` was null on every claim. No
translations, so every quote reaching a reviewer was in Chinese. No route diagram,
or worse, the *previous* patent's route diagram, still asserting the previous
patent's eight steps under the new patent's id. Nothing said so.

This is that order, written down, executed, and hashed.

---

## What the runner does not do

**The LLM annotation passes are not run by this script.** Pass V and pass A5 need
the rendered page images and an agent; A0 to A4 need the prompts and a context. A
subprocess cannot do any of it.

What the runner does instead is render this patent's prompts, then check whether
each pass's output is there. If it is not, it prints which pass is missing, which
prompt produces it, where the result must land, and how many times to run it, then
exits 3.

```
pass V   MISSING
         prompt : output/prompts/CN104292137A/V-page-vision.md
         writes : input/vision/p*.json
         how    : one agent per rendered page in input/pages/, in parallel
```

The prompt it names is the **rendered** one, not the template. `prompts/*.md` still
carries a patent id, because a prompt is read by an agent rather than imported by a
process, and an agent following a template faithfully would stamp the wrong id into
the new patent's gold. `render_prompts.py` fills it in, and it is stage 1 so that
the file this message names exists by the time the message is printed.

It never half-runs. Either every prerequisite is present and the run proceeds, or
none of it does.

---

## The stages

| # | stage | runs | produces | gate |
|---:|---|---|---|:--:|
| 1 | `prompts` | `render_prompts.py` | `output/prompts/<ID>/*.md`, the annotation prompts with this patent's id in them | |
| 2 | `enrich` | `build_enriched.py` | `input/<ID>-enriched.md`, `-numbered.md`, `output/structures.json` | |
| 3 | `collect` | internal copy | `output/00-sections.json`, `raw-pathways.json`, `raw-patent.json` | |
| 4 | `merge` | `merge_stages.py` | `output/raw-compounds.json`, `raw-reactions.json`, the two provenance files, the A4 rollup | |
| 5 | `finalise` | `finalise.py` | `compounds.json`, `reactions.json`, `pathways.json`, `patent.json`, the equivalence and sections indices | |
| 6 | `validate` | `schemas/validate.py` | nothing; exits non-zero on a schema violation | |
| 7 | `publish-gold` | `make_relevant_output.py` | `relevant_output/gold/`, `provenance/`, `verification/`, `FINDINGS.md`, `AUDIT.md` | |
| 8 | `structures` | `resolve_structures.py` | `output/structures-resolved.json`, `output/structures/<slug>.svg` | yes |
| 9 | `translations` | `resolve_translations.py` | `output/translations.json` | yes |
| 10 | `diagrams` | `make_svgs.py`, `make_approach.py` | `svg/m1` to `m5`, `svg/approach.svg` | |
| 11 | `rasterise` | `svg2jpg.py --all` | `svg/*.jpg` | |
| 12 | `assemble` | `make_relevant_output.py` | the deliverable again, now including structures, translations and diagrams | |
| 13 | `verify` | `verify.py` | `relevant_output/verification/checks-<ID>.json` | yes |
| 14 | `manifest` | internal | `relevant_output/manifest.json` | |

### Two things about that order that are not obvious

**`make_relevant_output.py` runs twice, and has to.** `resolve_structures.py` and
`resolve_translations.py` read the gold from `output/relevant_output/gold/` first
and fall back to `output/` only when it is absent. So on any re-run they would
resolve against the *previous* run's gold unless the deliverable is republished
first. Stage 7 publishes the gold the resolvers read; stage 12 picks up what they
produced. The script is a pure copy plus two regenerated markdown files, so running
it twice costs nothing and changes nothing on the second pass.

**`collect` used to be a `cp` somebody typed.** A0, A3 and A4 each write one file
into their stage folder, and `finalise.py` reads them from `output/` under a
different name. That copy was not written down anywhere. It is a stage now, and it
copies rather than moves, so `output/stages/` stays the untouched record of what
each pass actually returned.

---

## The gates

A gate is a stage that refuses to pass until a human supplies something no
deterministic step can derive. There are three.

### `structures` - a molecule that carries chemistry has no structure

A molecule carries chemistry when it is the product of some reaction, or when it
appears in a reaction-compound row with both `mass_g` and `mmol`. The first because
a route with an unknown product is not a route; the second because such a row is an
implicit claim about molecular weight, and checking that claim is the most valuable
thing to do with a patent.

On failure the stage prints the missing identifiers and a JSON stub ready to paste
into `input/structures-curated.json`:

```
  2 carry chemistry and have NO structure. FAIL
    thionyl chloride   (mass_g + mmol)
    triethylamine   (mass_g + mmol)
```

**Check every hand-authored SMILES atom by atom against the name.** There is no
OPSIN and no network here, so nothing verifies it except a human doing it, and a
wrong structure does not fail loudly - it corrupts a mass balance quietly.

### `translations` - Chinese that can reach a screen has no English

Every compound identifier, every alias, every provenance `quote_zh`, every quote on
an A5 finding, and every source line that carries Chinese. The reviewer the
deliverable exists for does not read Chinese and has twenty minutes.

On failure the stage prints the missing strings grouped by where they surface, and
a stub for `input/translations-curated.json`.

### `verify` - a number or a quote is not on the lines the record cites

The hallucination check. `verify.py` matches every claimed value against the source
lines the record itself cites and exits non-zero when a `grounding` check fails.

### What the runner does with a gate

Stops. Prints the stage's own message unmodified, says how to resume, and exits 2.

```
STOP  the structures stage gate did not pass (exit 1).
      Supply it, then: python3 run_pipeline.py --patent-id <ID> --from structures
```

It never routes around one, and it never treats a gate failure as a warning.

**One trap worth knowing about.** Every gated stage writes its artifact and *then*
fails: `resolve_structures.py` writes `structures-resolved.json` before it reports
what is missing, and `verify.py` writes a 3 MB checks file before it reports a
grounding failure. A minute later every output is present and newer than every
input, and a purely mtime-based runner would call the stage current and walk past
the failure. So the manifest records each stage's outcome, the runner reads it back
at plan time, and **a stage that failed last time always runs again.**

---

## Skipping, and the plan

Every stage declares its inputs and its outputs. A stage is skipped when every
output exists and the sha256 of every input and every output is exactly what the
manifest says it last ran with.

**Not mtimes.** Two things rule them out, and both were found by watching a run
refuse to settle. `make_relevant_output.py` copies with `shutil.copy2`, which
*preserves* the source mtime, so a copied file is never newer than what it was
copied from and the stage re-runs forever. And a gated stage writes its artifact
and then fails, so a minute later every output is present and newer than every
input and an mtime rule walks straight past the failure. Hashing the tree costs a
fraction of a second and gives an answer that survives a `touch`, a copy, a
checkout and a clock change.

The plan is printed before anything executes, always:

```
pipeline: CN104292137A
plan     3 to run, 9 current, 0 absent, 1 not selected

  ---- enrich                vision page reads -> enriched markdown ...
  RUN  finalise              deterministic ids and uuids, rollup, bibliographic merge
                             input output/raw-compounds.json changed
  RUN  structures     [gate] identifier -> drawable molecule over five tiers ...
                             last run: failed (1)
```

| flag | effect |
|---|---|
| `--plan` | print the plan and stop |
| `--list` | list the stages and stop |
| `--from <stage>` | start there, run everything after |
| `--only <stage>` | run exactly that one |
| `--force` | run everything, ignoring every up-to-date check |
| `--patent-id <ID>` | which patent; discovered from `input/*-biblio.json` if omitted |

Exit codes: `0` ok, `1` a stage failed, `2` a coverage gate stopped the run, `3`
the LLM passes have not been run.

Running twice changes nothing. Verified three ways: two `--force` runs produce a
byte-identical tree including the manifest; a `--force` run followed by a plain run
moves only the per-stage `status` fields in the manifest; and two plain runs are
byte-identical.

`verify.py` stamps its output with a build timestamp, so the runner pins
`SOURCE_DATE_EPOCH` to the newest mtime among the hand-authored inputs
(`input/*-biblio.json`, `input/*-curated.json`, `input/vision/`). That is still an
honest "as of", it moves when somebody changes an input, and it does not move
merely because the pipeline rebuilt itself.

---

## The manifest

`output/relevant_output/manifest.json`. Every artifact, the stage that produced it,
its sha256 and its size, and the sha256 of every input it was built from.

```json
{
  "path": "output/relevant_output/structures/tembotrione.svg",
  "sha256": "…", "bytes": 4213,
  "stage": "structures",
  "input_sha256": ["…", "…"]
}
```

That is what lets a consumer ask *are these assets current for this gold* and get
an answer from hashes rather than from file times. It is also what lets the
reviewer UI say so.

Two deliberate properties:

- **No timestamp anywhere.** A `generated_at` field would make every second run a
  diff, and byte-level idempotence is worth more than knowing the wall clock.
- **Anything in the deliverable that no stage produced is listed with a null
  stage.** On a healthy run that is exactly two files: the hand-written
  `README.md` and the reviewer's own `verdicts-<ID>.jsonl`. Anything else
  appearing there is the failure this pipeline exists to fix, so it is reported
  rather than hidden.

The manifest is written even when a gate stops the run, with the failing stage's
status recorded. A stopped run is exactly when a consumer most needs to be told
the assets are not current.

---

## Running a new patent

Nothing below mentions `CN104292137A`, and nothing in the scripts does either. The
id comes from `--patent-id`, from `$ANNOTATION_PATENT_ID`, or from the one
`input/<id>-biblio.json` in the pack.

1. **Put the source in place.** The PDF in `input/pdf/`, the pages rendered to PNG
   at 200 dpi in `input/pages/`.

2. **Write `input/<ID>-biblio.json`.** Same shape as the existing one:
   `family_id`, `title_en`, the dates, `jurisdiction`, `language`, `assignees`,
   `inventors`, `legal_status`, `ipc_codes`, `abstract_zh`.

3. **Start the two curated tables empty.** The gates will tell you what goes in
   them; guessing first wastes the trip.

   ```bash
   echo '{"patent_id":"<ID>","entries":{},"no_structure_needed":[]}' > input/structures-curated.json
   echo '{"patent_id":"<ID>","entries":{}}'                          > input/translations-curated.json
   ```

4. **Run the passes.** `python3 run_pipeline.py --patent-id <ID>` renders the
   prompts for this patent into `output/prompts/<ID>/`, then exits 3 printing
   exactly which passes are missing and where their output goes. Work through that
   list, following the rendered prompts rather than the templates.

5. **Run the pipeline.** It will get as far as `structures` and stop, listing the
   molecules the patent names but never draws. Fill them in, atom by atom.

   ```bash
   python3 run_pipeline.py --patent-id <ID> --from structures
   ```

6. **Repeat for `translations`, then `verify`.** Each stops with its own list.

7. **Read `output/relevant_output/`.** Start at `manifest.json` to see what was
   produced, then `FINDINGS.md`.

### What is still hand-authored per patent, and says so

Three pieces of the deliverable are arguments about one patent's chemistry rather
than functions of its data. They are keyed by patent id and, for a patent nobody
has written them for, the generated content still appears and the hand-written
section says it is absent rather than repeating the previous patent's:

| what | where | fallback |
|---|---|---|
| the route diagram `m2-route.svg` | `HAND_DRAWN_ROUTES` in `make_svgs.py` | generated from `pathways.json` and `reactions.json`: transformation, conditions, yield and flags per step |
| "the three that matter" in `FINDINGS.md` | `HEADLINE_FINDINGS` in `make_relevant_output.py` | a line saying no analysis has been written for this patent |
| the findings row on `approach.svg` | `HAND_WRITTEN_FINDINGS` in `make_approach.py` | the same, on the poster |

Everything else on those diagrams is counted from the run: the page count from
`input/vision/`, the record counts from the gold, the scheme page from whichever
page carries the most drawn structures, the cumulative yield from the pathway the
annotation stands behind.

---

## Where the patent id lives now

`pipeline_context.py`. One module, four sources in order: `--patent-id`, the first
bare positional argument, `$ANNOTATION_PATENT_ID`, then discovery from the one
`input/<id>-biblio.json` in the pack. Discovery refuses to choose when there is
more than one candidate, because a pack holding two patents that silently picked
one would reintroduce exactly the failure the module exists to remove.

It also supplies the counted facts the diagrams need - page count, family id,
scheme page, source size, record counts, the route - so that a caption naming a
number is naming *this* run's number.
