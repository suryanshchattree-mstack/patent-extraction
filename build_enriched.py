#!/usr/bin/env python3
"""Merge the per-page vision reads into one enriched markdown document.

Output format is deliberately identical to what LiteratureIQ's Phase 1 produces,
so the annotation passes consume exactly the shape production's own passes do:

    OCR markdown  +  [IMAGE_EXTRACT: {...}]  =  enriched/en/markdown.md

In production, step 2 is Mistral OCR and step 4 is MolScribe / RxnScribe. Here both
are done by a vision model reading the rendered page, because the PDF has no text
layer and neither service is reachable. The output format is the same either way,
which is the point: an annotation built on a different input shape would not be
comparable.

Two IMAGE_EXTRACT forms, matching LiteratureExtractionWorkflow.transformImageExtract:
  single structure -> {"molecules":[{smiles, molecular_formula, inchi_key}, ...]}
  reaction scheme  -> {"reactions":[{step_id, reactants[], conditions[], products[]}]}

SMILES are canonicalised with RDKit, mirroring buildMoleculeEntry's use of
chemstack-toolkit. Anything RDKit rejects is reported and dropped from the
IMAGE_EXTRACT block rather than passed through, because a malformed SMILES reaching
a downstream pass is worse than an absent one. It is still preserved in
structures.json with the parse failure recorded.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE / "input" / "vision"
OUT = HERE / "input"

try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import rdMolDescriptors, inchi
    RDLogger.DisableLog("rdApp.*")
except ImportError:
    sys.exit("rdkit required:  python3 -m pip install --user rdkit")

BAD: list[tuple[str, str]] = []


def mol_entry(smiles, where):
    """buildMoleculeEntry: canonical smiles + formula + inchi key, or None."""
    if not smiles or not str(smiles).strip():
        return None
    m = Chem.MolFromSmiles(str(smiles).strip())
    if m is None:
        BAD.append((where, str(smiles)))
        return None
    can = Chem.MolToSmiles(m)
    e = {"smiles": can}
    try:
        e["molecular_formula"] = rdMolDescriptors.CalcMolFormula(m)
        e["inchi_key"] = inchi.MolToInchiKey(m)
    except Exception:
        pass
    return e


ORD = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6, "7th": 7,
       "8th": 8, "9th": 9, "10th": 10, "11th": 11, "12th": 12,
       "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
       "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}


def ordinal(label):
    """Reduce a position label to its ordinal.

    The vision pass labels structures descriptively ("1st, row 1 far left") but
    references them tersely from arrows ("1st"). An exact-string join therefore
    matches nothing and silently produces empty reactants/products, which is exactly
    the kind of quiet data loss this whole exercise exists to catch. Match on the
    leading ordinal token instead, and report anything that still fails to resolve.
    """
    if not label:
        return None
    head = str(label).strip().lower().replace(",", " ").split()
    for tok in head[:2]:
        if tok in ORD:
            return ORD[tok]
        if tok.isdigit():
            return int(tok)
    return None


UNMATCHED: list[str] = []
ANCHOR_FAIL: list[str] = []


def image_extract_block(dr, page):
    """Render one drawing as production's inline IMAGE_EXTRACT span."""
    where = f"{page}:{dr.get('kind')}"
    if dr.get("kind") == "scheme" and dr.get("arrows"):
        structs = dr.get("structures") or []
        by_pos = {}
        for i, st in enumerate(structs, 1):
            by_pos[ordinal(st.get("position_in_drawing")) or i] = st
        steps = []
        for i, a in enumerate(dr["arrows"], 1):
            src = by_pos.get(ordinal(a.get("from_structure")))
            dst = by_pos.get(ordinal(a.get("to_structure")))
            if src is None and a.get("from_structure"):
                UNMATCHED.append(f"{page} arrow {i} from={a.get('from_structure')!r}")
            if dst is None and a.get("to_structure"):
                UNMATCHED.append(f"{page} arrow {i} to={a.get('to_structure')!r}")
            reactants = [x for x in [mol_entry((src or {}).get("smiles"), where)] if x]
            products = [x for x in [mol_entry((dst or {}).get("smiles"), where)] if x]
            conds, reagent_mols = [], []
            for r in (a.get("reagents_above") or []) + (a.get("reagents_below") or []):
                conds.append({"text": r})
            # RxnScribe moves any condition carrying a structure into reactants;
            # our vision pass reports reagents as text, so they stay conditions.
            steps.append({"step_id": i, "reactants": reactants + reagent_mols,
                          "conditions": conds, "products": products})
        return {"reactions": steps}

    mols = [m for m in (mol_entry(s.get("smiles"), where)
                        for s in dr.get("structures") or []) if m]
    return {"molecules": mols}


def main() -> int:
    files = sorted(VIS.glob("p*.json"))
    if not files:
        print(f"no vision output in {VIS} yet")
        return 1

    pages = []
    for f in files:
        try:
            pages.append((f.stem, json.loads(f.read_text())))
        except json.JSONDecodeError as e:
            print(f"  {f.name}: INVALID JSON - {e}")
            return 1

    body, structures = [], []
    n_img = n_par = 0

    body.append(f"# CN104292137A\n")
    for stem, p in pages:
        body.append(f"\n<!-- page {stem} :: {p.get('page_label','')} :: "
                    f"{p.get('doc_part','')} :: confidence={p.get('page_confidence','')} -->\n")

        marks = {par.get("marker") for par in p.get("paragraphs") or []
                 if par.get("marker")}

        # Anchor each drawing to a paragraph on THIS page.
        #
        # between_markers is [marker_before, marker_after]. A drawing at the top of a
        # page has no marker before it on this page - the vision pass says so in prose
        # ("(page top, continues from p05)"), which is not a marker. Anchoring only on
        # the first element silently dropped those drawings to the END of the page.
        # That put the nine-arrow overview scheme after Example 1 step 1's procedure
        # instead of before [0031], which would have handed A2 a prior-art overview
        # scheme as if it belonged to the first experimental step.
        after, before = {}, {}
        orphan = []
        for d in p.get("drawings") or []:
            bm = d.get("between_markers") or []
            prev = bm[0] if len(bm) > 0 else None
            nxt = bm[1] if len(bm) > 1 else None
            if prev in marks:
                after.setdefault(prev, []).append(d)
            elif nxt in marks:
                before.setdefault(nxt, []).append(d)
            else:
                orphan.append(d)
                ANCHOR_FAIL.append(f"{stem}: {bm} matched no paragraph on the page")

        def emit(drawings):
            nonlocal n_img
            for d in drawings:
                blk = image_extract_block(d, stem)
                body.append(f"[IMAGE_EXTRACT: {json.dumps(blk, ensure_ascii=False)}]\n")
                n_img += 1
                structures.append({"page": stem, **d})

        emit(orphan)                          # unanchored: page top, and reported
        for par in p.get("paragraphs") or []:
            n_par += 1
            emit(before.pop(par.get("marker"), []))
            body.append(f"{par.get('marker','')} {par.get('zh','')}".strip())
            if par.get("en"):
                body.append(f"    > EN: {par['en']}")
            emit(after.pop(par.get("marker"), []))
        assert not before and not after, "anchored drawing was never emitted"

    text = "\n".join(body)
    numbered = "\n".join(f"{i:4} | {ln}" for i, ln in enumerate(text.split("\n"), 1))

    (OUT / "CN104292137A-enriched.md").write_text(text)
    (OUT / "CN104292137A-enriched-numbered.md").write_text(numbered)
    (HERE / "output" / "structures.json").write_text(
        json.dumps(structures, indent=2, ensure_ascii=False))

    disc = [(stem, d) for stem, p in pages for d in (p.get("discrepancies") or [])]
    illeg = [(stem, x) for stem, p in pages for x in (p.get("illegible") or [])]

    print(f"pages merged        : {len(pages)}")
    print(f"paragraphs          : {n_par}")
    print(f"IMAGE_EXTRACT blocks: {n_img}")
    print(f"structures recorded : {sum(len(s.get('structures') or []) for s in structures)}")
    print(f"enriched doc        : {len(text):,} chars, {text.count(chr(10))+1} lines")
    print(f"\npage confidence:")
    for stem, p in pages:
        print(f"  {stem}  {p.get('page_confidence','?'):7} "
              f"{len(p.get('paragraphs') or []):3} paras  "
              f"{len(p.get('drawings') or []):2} drawings")
    if ANCHOR_FAIL:
        print(f"\ndrawings with no anchor on their own page ({len(ANCHOR_FAIL)}), "
              f"placed at page top:")
        for a in ANCHOR_FAIL:
            print(f"  {a}")
    if UNMATCHED:
        print(f"\narrow endpoints that did not resolve to a structure ({len(UNMATCHED)}):")
        for u in UNMATCHED:
            print(f"  {u}")
    if BAD:
        print(f"\nSMILES RDKit could not parse ({len(BAD)}), dropped from IMAGE_EXTRACT:")
        for w, s in BAD:
            print(f"  {w}: {s[:70]}")
    if disc:
        print(f"\ndiscrepancies reported by the vision pass ({len(disc)}):")
        for stem, d in disc:
            print(f"  [{stem}] {d.get('what','')}")
            print(f"        drawing: {str(d.get('drawing_says',''))[:80]}")
            print(f"        text   : {str(d.get('text_says',''))[:80]}")
    if illeg:
        print(f"\nillegible regions ({len(illeg)}):")
        for stem, x in illeg:
            print(f"  [{stem}] {str(x)[:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
