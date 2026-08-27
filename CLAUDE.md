# CLAUDE.md

The constitution for this repo. It overrides `AGENT.md` wherever they disagree.

## What this is

A hand-run, prompt-driven annotation of patent chemistry, produced in the same
JSON shapes LiteratureIQ writes, so the two can be compared field by field. One
patent per run directory, twenty patents in `TARGETS.md`, one worked reference
run already complete.

The point is a reference a **human has actually checked**. Without one, a
benchmark score is a measure of agreement between two automated runs.

## What this is explicitly NOT

- **Not software.** No CLI to build, no library, no service, no API. Every script
  you need is under `pipeline/` and already works. If you are designing a module,
  you have misread the task.
- **Not a benchmark scorer.** There is no machine extraction on disk to score
  against. This produces the reference; scoring comes later and elsewhere.
- **Not an editor of the gold.** Records are produced by stages from inputs. A
  wrong record is fixed by fixing its input and re-running, never by hand-editing
  `output/`.
- **Not chemistry tooling.** No route design, no retrosynthesis, no de novo
  anything. You are recording what a patent says, not deciding whether it is
  good chemistry.

## The two halves, and why the second is dangerous

```
  DETERMINISTIC                        JUDGEMENT
  pipeline/*.py, 18 stages             7 LLM passes, 2 curated files, 1 reading
  ----------------------------         ----------------------------------------
  same input -> same bytes             a person or a model, reading a page
  fails loudly, non-zero exit          fails SILENTLY and looks correct
  costs nothing to repeat              one wrong SMILES corrupts a mass balance
                                       eight steps downstream, in the deliverable
```

Every rule below exists because something in the right-hand column failed quietly
once.

## The hard rules

1. **A run directory is named after its patent and nothing else.** `runs/<ID>/`.
   There is no flag selecting it, because a flag can be forgotten and forgetting
   it used to overwrite somebody else's completed work in place. See
   `pipeline/contracts/GENERALISATION-AUDIT.md` for what that cost.
2. **`runs/CN104292137A/` is read only.** It is the reference run. Every other
   run is checked against it and it is the only worked example of the format.
3. **Never hand-edit anything under any `output/`.** It is generated, the
   manifest hashes it, and a hand-edited artifact is indistinguishable from a
   generated one to every consumer downstream.
4. **Never change a pinned number to make a check pass.** Pinned numbers are
   measurements, not targets. If code and a pinned number disagree, the code is
   wrong until proven otherwise, and proving otherwise means re-measuring and
   saying so in the same commit.
5. **Check every hand-authored SMILES atom by atom against its name.** The
   structures gate has no OPSIN and no network. Nothing else checks it.
6. **A guard must not pass on absence.** "We could not check" is not "the answer
   is no". `pipeline/contracts/GUARDS-THAT-PASS-ON-ABSENCE.md` lists eleven ways
   this has actually happened in this codebase, one of them introduced during the
   move that created this repo.
7. **A5 runs in a fresh context.** An audit that can see the reasoning it is
   auditing agrees with itself, produces output identical in shape to a real
   audit, and is worth nothing.
8. **Record disagreement, never resolve it silently.** Where two readings of a
   page differ, the artifact carries both. The whole value of this dataset is
   that it does not quietly average away the interesting cases.

## Style

- **No em dash character anywhere.** Not in prose, code, comments, JSON or commit
  messages. Use a regular hyphen or rewrite the sentence.
- Comment **why**, not what. Where the logic is non-obvious, a short ASCII
  diagram in the comment earns its space; several in `pipeline/` do.
- Match the existing voice: plain, direct, no ceremony, no banner comments.
- English only in anything that can reach a screen. The gold keeps its Chinese
  because the Chinese is authoritative; the reviewer must not be shown it
  untranslated.

## Provenance of everything a model wrote

Three separate contributions here come from a language model: the vision pass,
the extraction passes, and the independent read in step 6 of `AGENT.md`. They are
not independent in the way the word usually implies. Where the extraction missed
something **and** the independent read also missed it, nothing in this pipeline
can see that, and it reports as clean.

Say which model produced each artifact, in the run notes. It is the only handle
anyone will have on correlated blindness later.

## Git

- Small, readable commits. One idea per commit, message a person can skim.
- **Never attribute a commit to an AI.** No `Co-Authored-By: Claude` trailer, no
  "generated with" footer, no agent name in the body. Commits are authored solely
  by the person running the session.
- Commit `runs/<ID>/` in full, including `input/`. The inputs are what make a run
  reproducible and are the only record of what was actually read.
- Push when a patent is done, or when you are stopping and want the state visible.
  Pushing `runs/**` triggers CI and redeploys the review site.
