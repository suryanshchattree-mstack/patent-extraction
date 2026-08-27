# AGENT.md

You are annotating **one patent**, end to end, in this repo. This file is the
whole procedure. `PLAN.md` says why it exists; you do not need it to work.

Read `CLAUDE.md` before you write anything. It is the constitution and it
overrides this file wherever they disagree.

---

## What you are producing

A dataset that a chemist can check by eye against the patent it came from. Four
JSON artifacts in the exact shapes LiteratureIQ writes, plus the provenance,
structures, translations and diagrams that make them readable, plus a
verification file the review UI renders.

**You are not writing software.** There is no feature to build here. Every script
you need already exists under `pipeline/`. If you find yourself designing a
module, you have misread the task.

---

## The one thing to understand first

The pipeline splits into two halves that fail in completely different ways.

```
  DETERMINISTIC                              JUDGEMENT
  18 stages, run_pipeline.py                 7 LLM passes + 2 curated files
  ------------------------------             ---------------------------------
  same input -> same bytes                   you, reading the patent
  fails loudly, exits non-zero               fails SILENTLY, looks fine
  re-runnable, idempotent                    one wrong SMILES corrupts a
  costs nothing to repeat                    mass balance eight steps later
```

`run_pipeline.py` will not run the LLM passes. It cannot: they need an agent
looking at page images, not a subprocess. What it does instead is check whether
each pass's output is present and, when it is not, print which pass is missing,
which prompt produces it, where the result must land, and how many times to run
it. Then it stops, before it has half-built anything.

So the loop is: **run the pipeline, do what it asks, run it again.** It is
designed to be run repeatedly and to tell you the next thing you owe. Do not try
to work out the order yourself; that order lived in one person's head once and
that is the problem this repo exists to fix.

---

## Before you touch anything

```bash
python3 pipeline/doctor.py
```

It reports every problem at once rather than one per run. If it is not clean,
stop: everything below assumes it is, and a missing RDKit does not announce
itself until the structures gate, which is after all 27 agent invocations.

Claim your patent in `TARGETS.md`: put your name in `owner`, set `status` to
`claimed`, commit and push **that change alone**. Two people annotating the same
patent is the one waste this costs real money to undo.

Then:

```bash
python3 pipeline/new_run.py <PATENT_ID>
```

This creates `runs/<PATENT_ID>/` and prints what you owe. Your run directory is
named after your patent and nothing else, so you cannot collide with anyone
else's work in the same checkout.

---

## The procedure

### 1. Get the PDF

From Google Patents, into `runs/<ID>/input/pdf/<ID>.pdf`.

**Check whether it has a text layer before doing anything else:**

```bash
python3 -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); print([len(p.get_text()) for p in d])" runs/<ID>/input/pdf/<ID>.pdf
```

All zeros means a scan, and every readable character has to come from the vision
pass. Non-zero means the patent is born digital and reading its pixels is the
wrong tool: you still run the vision pass for the **drawn structures**, which no
text layer contains, but the prose should come from the text layer.

Most CN patents in `TARGETS.md` are scans. Most US, EP and WO ones are not.

### 2. Fill in the bibliographic record

`runs/<ID>/input/<ID>-biblio.json`, by hand. Read the `_readme` block in it.

The field most likely to be wrong is `title_en`. Machine translation of a
chemical title routinely names a real and **different** compound: the reference
patent's own title translates to "cyclic sulcotrione", which is a different
herbicide from the one the patent is actually about. Where the source's English
disagrees with the original, follow the original and say why in `title_en_note`.

The pipeline validates this file as a whole before any stage runs, so a missing
field costs you one run rather than five.

### 3. Render the pages

```bash
python3 pipeline/render_pages.py --patent-id <ID>
```

### 4. Run the pipeline, and do what it tells you

```bash
python3 pipeline/run_pipeline.py --patent-id <ID>
```

It will exit 3 and print something like:

```
pass V   MISSING
         prompt : output/prompts/<ID>/V-page-vision.md
         writes : input/vision/p*.json
         how    : one agent per rendered page in input/pages/, in parallel
```

**Follow the rendered prompt, not the template in `pipeline/prompts/`.** The
templates carry a patent id, because a prompt is read by an agent rather than
imported by a process, and an agent following a template faithfully stamps the
wrong patent's id into your gold. `render_prompts.py` fills the id in, and it is
stage 1 so the file that message names exists by the time you read the message.

The passes, and roughly what each costs on a nine-page patent:

| pass | prompt | runs | writes |
|---|---|---|---|
| V | `V-page-vision.md` | once per rendered page, in parallel | `input/vision/pNN.json` |
| A0 | `A0-section-map.md` | once | `output/stages/A0-sections/` |
| A1 | `A1-compounds.md` | once per section | `output/stages/A1-compounds/` |
| A2 | `A2-reactions.md` | once per section with procedures | `output/stages/A2-reactions/` |
| A3 | `A3-pathways.md` | once | `output/stages/A3-pathways/` |
| A4 | `A4-patent.md` | once | `output/stages/A4-patent/` |
| A5 | `A5-verify.md` | once per artifact, **fresh context each time** | `output/stages/A5-verify/` |

About 27 invocations for a nine-page patent. Re-run `run_pipeline.py` after each
group; it will tell you what is next.

**A5 must run in a fresh context.** Its job is to audit the other passes
adversarially, assuming they are wrong until the text proves otherwise. An A5 that
can see A1's reasoning is agreeing with itself, which is worth nothing and looks
identical to a real audit in the output.

### 5. Clear the two gates

A gate is a stage that refuses to pass until a human supplies something no
deterministic step can derive. Both print exactly what they need, as a JSON stub
ready to paste.

**`structures`** wants a structure for every molecule that carries chemistry: it
is the product of a reaction, or it appears in a row with both a mass and a mole
count. Paste the stub into `input/structures-curated.json` and fill in each
SMILES.

> **Check every SMILES atom by atom against the name before you commit it.**
> There is no OPSIN and no network in the gate. A wrong structure does not fail
> loudly, it silently corrupts a mass balance downstream. Comparing the formula
> the report prints against the formula the name implies catches most slips.

**`translations`** wants an English form for every Chinese string that can reach a
screen. Same shape, into `input/translations-curated.json`.

### 6. Read the patent yourself, once, for what the passes missed

Everything above measures whether what was extracted is **correct**. None of it
measures whether it is **complete**, and those fail in opposite directions: a
false positive is visible in the output, a missing fact is not there to look at.

So: read every line of `input/<ID>-enriched-numbered.md` and write down every
chemical substance named on it, into `input/substances-observed.json`. Do not
consult the extraction while you do this. The pipeline then compares your list
against what the records hold for the same line, and anything on your list that
no record holds is something the extraction lost.

The reference run's file is the format. On CN104292137A this found 7 real misses
that every correctness check had passed.

### 7. Finish

```bash
python3 pipeline/run_pipeline.py --patent-id <ID>
```

You are done when it reaches the end and `selfcheck` reports **0 fail**. Warnings
are acceptable and are described in the output. A failing `verify` gate is not
automatically a defect in your work: it is the engine saying the gold makes a
claim it cannot ground, and on the reference patent it is red on purpose. Read
what it says before you treat it as either.

Then set `status` in `TARGETS.md`, commit, push.

---

## What pushing does

Pushing `runs/**` triggers CI, which validates every artifact against its schema
and then redeploys the review site with your patent on it. A push that fails
schema validation does not deploy, and you will get the failure on the commit.

Commit the whole run directory including `input/`. The inputs are what make the
run reproducible, and they are the only record of what you actually read.

---

## Hard rules

- **Never edit another patent's run directory.** Yours is `runs/<your id>/`.
- **Never edit `runs/CN104292137A/`.** It is the reference run and the worked
  example every other run is checked against.
- **Never hand-edit anything under `output/`.** It is generated. Fix the input
  and re-run. A hand-edited artifact is indistinguishable from a generated one
  and the manifest will assert it is current.
- **Never change a pinned number to make a check pass.** If code and a pinned
  number disagree, the code is wrong until proven otherwise.
- **Never delete a finding because you disagree with it.** Record the
  disagreement.
- **No em dash character anywhere**, in prose, code, comments or JSON. Use a
  regular hyphen.
- **Do not attribute any commit to an AI.** No `Co-Authored-By`, no "generated
  with", no agent name. Commits are authored by the person running the session.

## When you are stuck

Stop and say so, in the commit or in the tracking issue. The failure modes here
are silent by construction, and an hour of someone else's time is much cheaper
than a plausible wrong answer that reaches the deliverable and is believed.

`pipeline/contracts/` holds the reasoning behind every non-obvious rule in this
pipeline, written at the time the rule was found to be necessary. If a check
seems arbitrary, its justification is almost certainly in there.
