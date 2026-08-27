#!/usr/bin/env python3
"""Concatenate the per-section stage files into the raw arrays finalise.py consumes.

Kept separate from finalise.py so the stage folders stay the record of what each
pass actually returned. This script only concatenates and reports collisions; it
never edits a record.
"""
import json, sys
from collections import Counter
from pathlib import Path

from pipeline_context import RUN_ROOT
HERE = Path(__file__).resolve().parent
ST = RUN_ROOT / "output" / "stages"
OUT = RUN_ROOT / "output"


def gather(folder, key):
    recs, prov, seen = [], [], {}
    for f in sorted((ST / folder).glob("*.json")):
        d = json.loads(f.read_text())
        if f.stem.endswith("-provenance"):
            prov += d if isinstance(d, list) else [d]
            continue
        for r in d:
            k = r.get(key)
            if k in seen:
                print(f"  COLLISION on {key}={k!r}: {seen[k]} and {f.name}")
            seen[k] = f.name
            recs.append(r)
    return recs, prov


mols, mprov = gather("A1-compounds", "identifier")
rxns, rprov = gather("A2-reactions", "reaction_id")

(OUT / "raw-compounds.json").write_text(json.dumps(mols, indent=2, ensure_ascii=False))
(OUT / "raw-reactions.json").write_text(json.dumps(rxns, indent=2, ensure_ascii=False))
(OUT / "compounds-provenance.json").write_text(json.dumps(mprov, indent=2, ensure_ascii=False))
(OUT / "reactions-provenance.json").write_text(json.dumps(rprov, indent=2, ensure_ascii=False))

# Preliminary rollup for the A4 prompt. finalise.py recomputes the real one once
# pathways exist; this is only what A4 needs to write its narrative against.
roll = {
    "reaction_count": len(rxns),
    "compound_count": len(mols),
    "sections": dict(Counter(r.get("section_label") for r in rxns)),
    "reaction_classes": dict(Counter(r.get("reaction_class") for r in rxns).most_common()),
    "validation_flags": dict(Counter(f for r in rxns
                                     for f in (r.get("validation_flags") or [])).most_common()),
    "stated_yields_pct": [r.get("product_yield_pct") for r in rxns
                          if r.get("product_yield_pct") is not None],
    "target_compounds": sorted({r.get("product_name") for r in rxns
                                if r.get("is_section_product")} - {None}),
    "scale_distribution": dict(Counter(r.get("scale") for r in rxns)),
}
(OUT / "chemistry-rollup.json").write_text(json.dumps(roll, indent=2, ensure_ascii=False))

print(f"compounds : {len(mols):4}  ({len(mprov)} provenance entries)")
print(f"reactions : {len(rxns):4}  ({len(rprov)} provenance entries)")
dupes = [k for k, v in Counter(m['identifier'] for m in mols).items() if v > 1]
print(f"identifiers appearing in more than one section: {len(dupes)}")
print("  (expected: the same compound extracted independently per section)")
print(f"\nrollup written for A4: {roll['reaction_count']} reactions, "
      f"{roll['compound_count']} compounds")
