# TODOS

Captured during /plan-eng-review of the substance-recall plan, 27 Aug 2026. Both
items are correctness, neither blocks the recall work.

## Three guards can write into the real annotations; only one refuses to

**What:** Lift check-writes.mjs's REAL_ROOT refusal into a shared helper that
check-english.mjs, check-layout.mjs and check-overflow.mjs all import.

**Why:** check-writes refuses to run unless ANNOTATIONS_ROOT points at a throwaway
copy, and the reason is written on the file: a stray verdict would assert on disk
that a human confirmed a claim nobody confirmed, and the completeness report counts
those. The other three guards drive the same live dev server with Playwright and
have no such refusal.

**Current state:** They do not press keys or POST today, so nothing has leaked. That
is a property of what they happen to do, not a property anything enforces. The next
guard added, or the next feature added to an existing one, has nothing stopping it.

**Pros:** One shared refusal, four guards protected, and the protection survives
somebody adding a keyboard interaction to a guard that is currently read-only.
**Cons:** Every guard then needs a sandbox to run against, so the one-line
`npm run check:english` becomes a two-step. Worth it; check-writes already pays it.

**Where to start:** scripts/check-writes.mjs lines 44-100, the `realVerdictLogs()`
and `fingerprint()` pair plus the `root === REAL_ROOT` refusal. Extract to
scripts/lib/sandbox.mjs and import from all four.

**Depends on:** nothing.

## svg/ is shared across runs while input/ and output/ are per-run

**What:** Move the diagram output directory under RUN_ROOT, as input/ and output/
already are, or make make_svgs.py and svg2jpg.py take the run as an argument.

**Why:** The run split made data per-run so a second run cannot overwrite the first.
make_svgs.py resolves `OUT = Path(__file__).resolve().parent / "svg"` and
svg2jpg.py resolves `HERE / "svg"`, both against the CODE. m2-route.svg is a diagram
of one patent's route, so running the pack on a second patent silently overwrites
the first patent's route diagram in place.

**Current state:** Not yet harmful. Each run's deliverable holds its own copy under
output/relevant_output/svg/, so nothing has been lost, and both runs so far are the
same patent so the diagrams are near-identical anyway. The clobber is waiting for
the second patent, which is precisely the case the run split was built for.

**Pros:** Removes the last path in the pipeline that means two different things
depending on which half of the code you are in. That confusion has already cost two
bugs this week (the orchestrator/stages disagreement, and the visual stage reading
the code directory).
**Cons:** run_pipeline.py's `at()` helper gains a third prefix, and the existing
manual_annotations/svg/ contents need a decision: move into run_26_aug, or leave as
the pack-level explanation diagrams they partly are. m1-pass-map and
m3-artifact-joins describe the PIPELINE, not the patent, so the split is not clean.

**Where to start:** make_svgs.py:22, svg2jpg.py:60 and :66, and RUN_RELATIVE in
run_pipeline.py. Decide first which of the nine diagrams are per-patent and which
describe the pipeline itself.

**Depends on:** nothing. Do it before the second patent, not after.
