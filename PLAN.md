# PLAN.md

Why this repo exists, and what the twenty patents are for.

## The problem

LiteratureIQ extracts chemistry from patents. Its benchmark measures extraction:
patent in, reactions out, scored against a previous run. What it does not have is
a reference that a human has actually checked.

Without one, a benchmark score is a measure of **agreement between two automated
runs**. Two runs of the same model agree with each other for the same reasons
they are wrong, so the score goes up and nothing is learned.

## What we are building

Twenty patents annotated to a standard where a chemist can check any record
against the page it came from in under a minute. Same JSON shapes as production,
so a diff between this and an extraction is a real diff and not a shape mismatch.

Three properties make it worth the effort:

1. **Schema identical.** Field names, nesting and vocabularies taken from the
   Java records, not paraphrased.
2. **Independently derived.** The prompts here are written from scratch. If they
   were copies of the production prompts, the benchmark would score a model
   against itself.
3. **Adversarially checked.** Pass A5 audits the output against the source in a
   fresh context, assuming it is wrong until the text proves otherwise.

## Why one patent already exists

`runs/CN104292137A/` is complete. It was done first, by hand, to find out what
the procedure actually is. Nearly everything in `pipeline/contracts/` was
discovered during it, including:

- The extraction is measured for correctness by every check in the repo, and none
  of those measure completeness. An independent read of every line found **7
  substances that no record held** and that every correctness check had passed.
- A recall statistic of zero was not evidence of anything: coverage was counted
  per line, and a 730 character line carrying eight facts read as covered when
  three had been captured.
- The mass and mole pairs printed across the worked example imply molecular
  weights about 34.5 too low, consistently, which is exactly a chlorine for
  hydrogen substitution. The annotation records the numbers as printed and flags
  them rather than repairing them, because an extractor that also misses this has
  to score as a miss.

That patent is the reference. Every other run is checked against it, and it is
the only worked example of the format.

## What "done" looks like

Twenty run directories, each reaching the end of `run_pipeline.py` with
`selfcheck` reporting zero failures, each visible on the review site, each with
its inputs committed so the run can be reproduced from scratch by someone who was
not there.

## What this is not for

It is not a route-finding exercise, not a costing exercise, and not a
retrosynthesis. It records what twenty patents say. What anybody does with that
afterwards is a different piece of work with different rules.

## The honest caveat

Three of the contributions here come from a language model: the vision pass, the
extraction passes, and the independent read that is supposed to catch what the
extraction missed. A model checking a model is not the same as two independent
observers, and where both miss the same thing, nothing in this pipeline can see
it. It reports as clean.

That is a real limit on what these twenty patents can prove, and it is worth
stating in whatever this dataset ends up supporting. The mitigations are that A5
runs adversarially in a fresh context, that a grammar-based name parser reads
every compound name a second time without a model involved, and that the numbers
are checked arithmetically rather than by agreement. None of them close the gap
completely.
