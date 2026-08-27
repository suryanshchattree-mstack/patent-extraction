#!/usr/bin/env python3
"""Assemble output/relevant_output/: the things this exercise actually produced.

Everything else in the repo is either input (the PDF, the page renders, the vision
reads, the enriched markdown) or working state (raw-*.json, the per-section stage
files, the rollup handed to A4). Those are kept because they make the run auditable
and re-runnable, but they are not the deliverable.

The deliverable is a gold reference annotation of one patent in LiteratureIQ's own
schema, plus the evidence that it is worth trusting.

Usage:  python3 make_relevant_output.py [--patent-id ID]
"""
from __future__ import annotations

import json
import shutil
import sys
from collections import Counter
from pathlib import Path

from pipeline_context import ContextError, RUN_ROOT, resolve_patent_id

HERE = Path(__file__).resolve().parent
OUT = RUN_ROOT / "output"
REL = OUT / "relevant_output"

try:
    PATENT_ID = resolve_patent_id()
except ContextError as e:
    raise SystemExit(f"FAIL  {e}")

for sub in ("gold", "provenance", "verification", "svg", "structures"):
    (REL / sub).mkdir(parents=True, exist_ok=True)

GOLD = ["compounds.json", "reactions.json", "pathways.json", "patent.json",
        "structures.json", "structures-resolved.json", "translations.json"]
PROV = ["compounds-provenance.json", "reactions-provenance.json",
        "compounds-sections.json", "compounds-equivalence.json"]

copied = []
for n in GOLD:
    if (OUT / n).exists():
        shutil.copy2(OUT / n, REL / "gold" / n)
        copied.append(f"gold/{n}")
for n in PROV:
    if (OUT / n).exists():
        shutil.copy2(OUT / n, REL / "provenance" / n)
        copied.append(f"provenance/{n}")
for f in sorted((OUT / "stages" / "A5-verify").glob("*.json")):
    shutil.copy2(f, REL / "verification" / f.name)
    copied.append(f"verification/{f.name}")
for pat in ("*.svg", "*.jpg"):
    for f in sorted((HERE / "svg").glob(pat)):
        shutil.copy2(f, REL / "svg" / f.name)

# One molecule drawing per unique structure, written by resolve_structures.py. The
# `svg` field of every structures-resolved.json entry is a path relative to here,
# so the two have to travel together. Mirrored rather than merged: a drawing the
# resolver no longer claims is removed, or a renamed molecule would leave its old
# picture behind for a reader to trust.
structures = sorted((OUT / "structures").glob("*.svg"))
for f in structures:
    shutil.copy2(f, REL / "structures" / f.name)
for f in (REL / "structures").glob("*.svg"):
    if f.name not in {s.name for s in structures}:
        f.unlink()
for f in sorted((HERE / "schemas").glob("*.schema.json")):
    shutil.copy2(f, REL / "gold" / f.name)

# ---------------------------------------------------------------- FINDINGS.md
rx = json.loads((OUT / "reactions.json").read_text())
mols = json.loads((OUT / "compounds.json").read_text())
pws = json.loads((OUT / "pathways.json").read_text())
prov = {p.get("reaction_id"): p for p in json.loads((OUT / "reactions-provenance.json").read_text())}
vision = [json.loads(p.read_text()) for p in sorted((RUN_ROOT / "input" / "vision").glob("*.json"))]

flags = Counter(f for r in rx for f in (r.get("validation_flags") or []))
disc = [(v["page"], d) for v in vision for d in (v.get("discrepancies") or [])]

lines = []
A = lines.append
A(f"# What is wrong with {PATENT_ID}\n")
A("Produced by annotating the patent by hand, against the scanned pages rather than")
A("against anyone's OCR. Every item below is a defect in the **patent**, not in the")
A("annotation. The annotation records them and changes nothing.\n")
A(f"- {len(rx)} reactions extracted, of which "
  f"{sum(1 for r in rx if r.get('validation_flags'))} carry at least one flag")
A(f"- {len(mols)} unique compounds, {len(pws)} pathways")
A(f"- {len(disc)} discrepancies raised by the page-vision pass\n")

A("## Flags raised, by kind\n")
A("| flag | count | what it means |")
A("|---|---:|---|")
MEAN = {
    "mass_balance_implausible": "stated product mass cannot be reconciled with the stated input moles and yield",
    "molar_mass_inconsistent": "a stated mass/mole pair implies a molecular weight that is not the named compound's",
    "scale_discontinuity": "a step charges more material than the previous step produced",
    "route_attribution_unclear": "cannot tell from the page whether the drawn route is the invention's or prior art",
    "no_conditions": "no reaction conditions stated at all",
    "drawing_text_conflict": "the drawn scheme and the written procedure disagree",
    "reagent_written_not_drawn": "a reagent in the procedure appears on no arrow",
    "reagent_drawn_not_written": "a reagent on an arrow appears in no procedure",
}
for k, v in flags.most_common():
    A(f"| `{k}` | {v} | {MEAN.get(k, '')} |")

# Hand-authored narrative about ONE patent's defects. It used to print
# unconditionally, so a run on a second patent would have asserted this patent's
# three findings over that patent's data, in the deliverable, as fact. Keyed by
# patent id instead: a patent nobody has written this up for gets the generated
# sections only, and says so.
HEADLINE_FINDINGS = {"CN104292137A"}
if PATENT_ID in HEADLINE_FINDINGS:
    A("\n## The three that matter\n")
    A("### 1. The molar masses are those of the des-chloro compounds\n")
    A("Across Example 1 the printed mass/mole pairs imply a molecular weight roughly")
    A("34.5 lower than the compound the text names and the page draws. That is exactly a")
    A("chlorine-for-hydrogen substitution. The reagent charges are all correct; only the")
    A("chlorinated aromatic intermediates carry the offset. Steps 5, 7 and 8 carry a")
    A("second, different shortfall of about 44.7 that propagates forward.\n")
    A("Working, per step, is in `provenance/reactions-provenance.json` under")
    A("`arithmetic_check`.\n")
    A("### 2. The drawn route is not the route the text describes\n")
    A("Page 6 carries the whole synthesis drawn as structures. Its first arrow uses")
    A("CH3SNa, which [0031] says the invention **replaced**. It contains a")
    A("sulfide-to-sulfone oxidation, which [0031] says the invention **eliminated**,")
    A("drawn with no arrow and no reagent. But it also uses Br2, which [0031] claims")
    A("**as** the invention's own improvement over NBS. It starts from")
    A("2,6-dichlorotoluene where Example 1 starts from 2-chlorotoluene.\n")
    A("So the scheme is neither cleanly the prior art nor cleanly the invention. The")
    A("annotation refuses to decide: all nine scheme records carry")
    A("`route_attribution_unclear` and both readings are in their notes.\n")
    A("### 3. The final-step catalyst is drawn as one compound and written as another\n")
    A("The last arrow's catalyst is **drawn** as a quaternary carbon bearing CN and OH")
    A("with two methyls, i.e. (CH3)2C(CN)OH, acetone cyanohydrin. The text names")
    A("cyanoacetone, a different molecule. Acetone cyanohydrin is the reagent normally")
    A("used for this enol-ester rearrangement.\n")
    A("Only a pass that looks at the drawing can catch this. It is the single clearest")
    A("argument for reading the pages rather than the OCR.\n")
else:
    A("\n## The headline findings\n")
    A(f"No hand-written analysis exists for {PATENT_ID}. The generated sections "
      "above and below are complete; this section is not, and is omitted rather "
      "than filled with another patent's findings.\n")

A("## Everything the page-vision pass raised\n")
for page, d in disc:
    A(f"- **[{page}]** {d.get('what','')}")
    if d.get("drawing_says"):
        A(f"  - drawing: {str(d['drawing_says'])[:210]}")
    if d.get("text_says"):
        A(f"  - text: {str(d['text_says'])[:210]}")
A("")

(REL / "FINDINGS.md").write_text("\n".join(lines))



# ---------------------------------------------------------------- AUDIT.md
import itertools
reports = {p.stem: json.loads(p.read_text())
           for p in sorted((OUT / "stages" / "A5-verify").glob("*.json"))}
# What a previous iteration of THIS patent's run acted on, recorded by hand. Also
# used to suppress those findings from the outstanding list below. Keyed by patent
# because a second patent's audit has its own history and inherits none of this.
FIXED_BY_PATENT = {"CN104292137A": {
    "Three of the five pathways carry the identical pathway_uuid":
        "FIXED. finalise.py now seeds pathway_uuid the way PathwaysBuilder actually "
        "does, folding in the ordered step signature. The PathwayRecord javadoc we "
        "had transcribed is stale; the code carries a comment explaining that the "
        "endpoint-only seed lost 20 distinct routes across a ten-patent set.",
    "abstract is null":
        "FIXED. A4 is given the abstract, it does not emit one, and finalise.py had "
        "no source wired. Now taken from the pass-V read of the front page.",
    "ipc_codes is null":
        "FIXED. Both IPC classes were transcribed by pass V from the (51) field; "
        "finalise.py now reads them.",
    "The title names a different herbicide":
        "FIXED. input/<patent>-biblio.json carried Google's English title, which "
        "glosses 环磺草酮 character by character into 'cyclic sulcotrione' and so "
        "names a real and different triketone. finalise.py copies title_en "
        "verbatim, so it reached gold/patent.json, the completeness report and the "
        "self-contained export, where it was the first line under the patent "
        "number. The biblio now carries 'Synthesis process for the triketone "
        "herbicide tembotrione', which is what the Chinese title and the gold's own "
        "translation index both say, and title_en_note records why it is not the "
        "machine title so nobody restores it.",
    "mutually disjoint English spellings":
        "DOCUMENTED, NOT FIXED. Deliberate: buildCompoundId is a pure function of "
        "the identifier string, so production fragments these identically. Merging "
        "would make the gold set disagree with production for a reason unrelated to "
        "extraction quality. The equivalence is written out to "
        "provenance/compounds-equivalence.json so a benchmark can join on it.",
}}
FIXED = FIXED_BY_PATENT.get(PATENT_ID, {})

lines = []
A = lines.append
A(f"# A5 adversarial audit of {PATENT_ID}\n")
_COUNT = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
          8: "Eight", 9: "Nine", 10: "Ten"}
A(f"{_COUNT.get(len(reports), len(reports))} independent audits, each in a fresh "
  f"context, each re-opening the page images.")
A("None of them produced the artifact it audited.\n")
sev = {}
for name, d in reports.items():
    c = {}
    for x in d.get("findings") or []:
        c[x.get("severity")] = c.get(x.get("severity"), 0) + 1
    sev[name] = c
A("| artifact | records | critical | major | minor | checks passed |")
A("|---|---:|---:|---:|---:|---:|")
for name, d in reports.items():
    c = sev[name]
    A(f"| `{name.replace('-report','')}` | {d.get('records_audited','?')} | "
      f"{c.get('critical',0)} | {c.get('major',0)} | {c.get('minor',0)} | "
      f"{len(d.get('checks_passed') or [])} |")
tot = {k: sum(v.get(k, 0) for v in sev.values()) for k in ("critical", "major", "minor")}
A(f"| **total** | | **{tot['critical']}** | **{tot['major']}** | **{tot['minor']}** | "
  f"**{sum(len(d.get('checks_passed') or []) for d in reports.values())}** |\n")

A("## Acted on\n")
if FIXED:
    for k, v in FIXED.items():
        A(f"- **{k}** - {v}")
else:
    A(f"Nothing recorded for {PATENT_ID}. Every finding below is outstanding.")
A("")

A("## Outstanding, by severity\n")
A("These are recorded and not yet acted on. They are real and a second pass should")
A("work through them.\n")
for want in ("critical", "major"):
    A(f"### {want}\n")
    n = 0
    for name, d in reports.items():
        for x in d.get("findings") or []:
            if x.get("severity") != want:
                continue
            if any(k in (x.get("problem") or "") for k in FIXED):
                continue
            n += 1
            A(f"{n}. **[{name.replace('-report','')}]** `{x.get('check')}` on "
              f"`{str(x.get('record'))[:60]}`")
            A(f"   {x.get('problem','')}")
            if x.get("quote"):
                A(f"   > line {x.get('source_line')}: {str(x['quote'])[:160]}")
            if x.get("should_be"):
                A(f"   fix: {str(x['should_be'])[:200]}")
    A("")

A("## Recall estimates\n")
A("| artifact | items found in text | present in artifact | missing |")
A("|---|---:|---:|---:|")
for name, d in reports.items():
    r = d.get("recall_estimate") or {}
    if r:
        A(f"| `{name.replace('-report','')}` | {r.get('found_in_text','?')} | "
          f"{r.get('present_in_artifact','?')} | {len(r.get('missing') or [])} |")
A("")

(REL / "AUDIT.md").write_text("\n".join(lines))
print(f"  AUDIT.md  ({len(lines)} lines)")

print(f"patent    : {PATENT_ID}")
print(f"output/relevant_output/ assembled: {len(copied)} files")
for c in copied:
    print(f"  {c}")
print(f"  FINDINGS.md  ({len(lines)} lines)")
print(f"  svg/  ({len(list((REL/'svg').glob('*.svg')))} diagrams, "
      f"{len(list((REL/'svg').glob('*.jpg')))} as jpg)")
print(f"  structures/  ({len(structures)} molecule drawings)")
