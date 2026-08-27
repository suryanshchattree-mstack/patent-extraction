---
description: Annotate one patent end to end. Drives the whole loop and stops when a human is genuinely needed.
argument-hint: <PATENT_ID>   e.g. /run-pipeline CN109678767A
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
---

Annotate patent **$1** end to end.

Read `AGENT.md` in full first. It is the procedure and this command only drives it.
Read `CLAUDE.md` too; it overrides `AGENT.md` wherever they disagree.

## How to work

`run_pipeline.py` is the loop. Run it, do exactly what it asks, run it again.
Never guess the next step and never run stages by hand out of order. The order is
the thing this repo exists to encode.

```bash
python3 pipeline/run_pipeline.py --patent-id $1
```

Its exit code says what happened:

| exit | means | what you do |
|---|---|---|
| 0 | everything ran or was already current | check `selfcheck` says 0 fail, then finish |
| 1 | a stage failed | read the message, fix the cause, re-run |
| 2 | a coverage gate stopped it | a human owes curated entries. See below |
| 3 | the LLM passes have not been run | run the ones it names, then re-run |
| 4 | this run holds a different patent's work | stop and report. Do not continue |
| 5 | the bibliographic record is missing or malformed | fill it in by hand |

## Start

If `runs/$1/` does not exist, run `python3 pipeline/new_run.py $1` and follow what
it prints. Confirm `TARGETS.md` shows `$1` claimed by the person running this
session before doing any real work.

## What you may do without asking

- Run any script under `pipeline/`
- Run the LLM passes the runner names, following the **rendered** prompts under
  `runs/$1/output/prompts/$1/`, never the templates in `pipeline/prompts/`
- Write to `runs/$1/input/` and let stages write `runs/$1/output/`
- Fetch the patent from Google Patents
- Commit, with a message a person can skim and no AI attribution

## What you must stop and ask about

- **Any SMILES you would hand-author at the structures gate.** Show the name, the
  SMILES, the formula the SMILES implies and the formula the name implies, and
  ask for confirmation. There is no OPSIN and no network in that gate, so nothing
  else checks it, and a wrong structure corrupts a mass balance silently several
  steps downstream. This is the single highest-cost mistake available here.
- Any run where `verify` fails and you cannot say in one sentence what it is
  objecting to.
- Anything that would touch a run directory other than `runs/$1/`.
- Anything that looks like writing software rather than annotating a patent.

## Reading the patent yourself

Step 6 of `AGENT.md` asks you to read every line and list every substance named,
into `runs/$1/input/substances-observed.json`, **without consulting the
extraction**. Do that literally. The whole value of the step is that it is an
independent read; a list derived from the records measures nothing, and it will
score as clean while the extraction stays exactly as incomplete as it was.

You are one language model checking another language model's reading of the same
page. Say so in the run notes. Where you and the extraction agree, that agreement
is weaker evidence than it looks.

## Finishing

Done means `run_pipeline.py` reaches the end and `selfcheck` reports 0 fail.
Then update `status` in `TARGETS.md`, commit `runs/$1/` in full including
`input/`, and push. Pushing triggers CI, which validates the schemas and
redeploys the review site with this patent on it.

Report at the end: the stage the run reached, the selfcheck line, how many
structures and translations you hand-authored, and anything you were unsure of.
Be specific about the last one. It is worth more than the rest of the report.
