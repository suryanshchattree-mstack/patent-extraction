# patent-extraction

Twenty patents, annotated by hand with an agent, into a chemistry dataset a
chemist can check by eye against the source.

**If you have been assigned a patent, you need three files: this one, then
[`AGENT.md`](AGENT.md), then [`TARGETS.md`](TARGETS.md).** Everything else is
reference.

---

## Start here

```bash
git clone https://github.com/yashmstack/patent-extraction
cd patent-extraction
python3 -m pip install -r requirements.txt
python3 pipeline/doctor.py
claude
```

`doctor.py` checks this machine can actually run the pipeline: the Python
version, that every dependency imports, that the reference run validates here.
Every failure it reports is one you would otherwise hit several hours in, after
the 27 agent invocations that produce a patent's annotation.

Then, in Claude Code:

```
/run-pipeline CN109678767A
```

Claim your patent in [`TARGETS.md`](TARGETS.md) first, and push that change
before you start. That is the only coordination this needs.

---

## What you get

One directory per patent, holding everything that went in and everything that
came out:

```
runs/CN104292137A/
  input/                      what a human and a vision model read
    pdf/                      the patent, as downloaded
    pages/                    rendered at 200 dpi, one PNG per page
    vision/                   pNN.json, one per page, written by the vision pass
    <ID>-enriched.md          the actual input to every extraction pass
    <ID>-biblio.json          the bibliographic record, hand-authored
    structures-curated.json   hand-authored structures, one per molecule
    translations-curated.json hand-authored English, one per Chinese string
    substances-observed.json  an independent read of every line
  output/
    relevant_output/          THE DELIVERABLE. Start here.
      gold/                   compounds, reactions, pathways, patent
      provenance/             which lines each record came from
      verification/           the file the review UI renders
      structures/             one SVG per molecule
      export/                 every reaction joined to its participants' SMILES
      svg/                    the route and method diagrams
      manifest.json           sha256 of every artifact and every input
    stages/                   per-pass output, unmerged, for checking one pass
```

The reference run for `CN104292137A` is complete and committed. It is the worked
example: when a format question comes up, the answer is in there.

---

## How it works, in one picture

```
   patent PDF
       |
       |  render_pages.py                       deterministic
       v
   page images
       |
       |  pass V, one agent per page            JUDGEMENT
       v
   structures + text per page
       |
       |  build_enriched.py                     deterministic
       v
   enriched markdown, line-numbered
       |
       |  passes A0 to A4                       JUDGEMENT
       v
   raw records
       |
       |  finalise.py, validate.py              deterministic
       v
   the four artifacts
       |
       |  pass A5, fresh context                JUDGEMENT
       |  structures + translations gates       JUDGEMENT
       |  your own read of every line           JUDGEMENT
       v
       |  13 more deterministic stages
       v
   the deliverable, plus a manifest that hashes all of it
```

The deterministic half is re-runnable and fails loudly. The judgement half fails
silently and looks correct. Every rule in [`CLAUDE.md`](CLAUDE.md) exists because
something in the second column failed quietly once.

---

## Pushing

Pushing `runs/**` runs CI, which validates every artifact against its schema and
then redeploys the review site with your patent on it. A run that fails
validation does not deploy and you get the failure on your commit.

---

## Repository layout

| path | what |
|---|---|
| [`AGENT.md`](AGENT.md) | the procedure. The one file to read before starting |
| [`CLAUDE.md`](CLAUDE.md) | the constitution. Overrides AGENT.md |
| [`PLAN.md`](PLAN.md) | why this exists and what it is for |
| [`TARGETS.md`](TARGETS.md) | the twenty patents, who owns each, and status |
| `.claude/commands/` | `/run-pipeline`, which drives the whole loop |
| `pipeline/` | every script. You run these, you do not edit them |
| `pipeline/prompts/` | the seven LLM pass prompts, as templates |
| `pipeline/schemas/` | JSON Schema for every artifact, plus the validator |
| `pipeline/contracts/` | why every non-obvious rule exists, written when found |
| `runs/<ID>/` | one patent's inputs and outputs |

`pipeline/contracts/` is the most useful directory in the repo and the least
obvious. If a check seems arbitrary, its justification is in there, written at
the time the check was found to be necessary.

---

## Requirements

Python 3.12, then:

```bash
python3 -m pip install -r requirements.txt
```

`pymupdf` renders the pages, `rdkit` does every structure operation, `jsonschema`
validates the artifacts, `numpy` builds the visual evidence crops.

**One stage needs the network.** `resolve_names.py` reads every compound name a
second time with a grammar-based parser, as an independent check on the model
that read it first. There is no Java runtime here, so it calls the public OPSIN
service at `opsin.ch.cam.ac.uk` over HTTPS and caches every answer in the run's
`input/opsin-cache.json`. Once that cache is committed the stage needs no
network; the first run on a new patent does.

No Java, no paid or licensed sources. Reaxys, SciFinder and CAS Registry are
excluded; public sources only.
