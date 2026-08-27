#!/usr/bin/env python3
"""Export every reaction with the SMILES of its participants, joined.

    python3 pipeline/export_reactions.py --patent-id CN104292137A

WHY THIS IS A JOIN AND NOT A LOOKUP
-----------------------------------
The gold carries NO structures on the records. `reactions.json` has
`product_smiles`, `reactant_smiles` and `canonical_rxn` null on all 33 rows, and
`compounds.json` has `smiles`, `inchi_key` and `molecular_formula` null on all 75.
That is deliberate: structure resolution is a PubChem/OPSIN lookup rather than an
extraction, so a reference carrying it would be scoring the enrichment service
instead of the extractor. See the departures table in pipeline/README.md.

Structures live in a sidecar, `gold/structures-resolved.json`, one entry per
identifier, and this joins the two on `identifier`.

WHAT THE ORIGIN FIELD MEANS, AND THE TRAP IN IT
-----------------------------------------------
Every SMILES carries where it came from, and they are not equally strong:

    patent_scheme   the identifier string itself parsed as SMILES
    patent_drawing  matched to a structure DRAWN in this patent
    name_parsed     a grammar-based parser read the systematic name
    derived         matched to a synonym through the equivalence index
    curated         a human wrote it by hand and nothing else checked it
    none            no structure

`derived` is the trap: the donor of the synonym is NOT always drawn in the
patent, so counting `derived` as "drawn in the patent" overcounts. Drawn means
`patent_scheme` or `patent_drawing`, nothing else.

`curated` is the one to distrust on a new patent. There is no OPSIN and no
network in the structures gate, so a hand-authored SMILES is checked by nobody.

Both output files carry `origin` per participant so a consumer can filter.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from pipeline_context import ContextError, OUTPUT, resolve_patent_id, shown

REL = "relevant_output"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    try:
        pid = resolve_patent_id()
    except ContextError as e:
        print(f"FAIL  {e}", file=sys.stderr)
        return 2

    gold = OUTPUT / REL / "gold"
    for f in ("reactions.json", "structures-resolved.json"):
        if not (gold / f).exists():
            print(f"FAIL  {shown(gold / f)} not found. Run the pipeline first.",
                  file=sys.stderr)
            return 1

    rxns = load(gold / "reactions.json")
    structs = {e["identifier"]: e for e in load(gold / "structures-resolved.json")}

    out, complete = [], 0
    for r in rxns:
        parts = []
        for c in r.get("compounds") or []:
            ident = c.get("identifier")
            st = structs.get(ident) or {}
            parts.append({
                "identifier": ident,
                "role": c.get("role"),
                "is_product": bool(c.get("is_product")),
                "smiles": st.get("canonical") or st.get("smiles"),
                "formula": st.get("formula"),
                "mw": st.get("mw"),
                "origin": st.get("origin") or "none",
                "quantity": c.get("quantity"),
            })

        reactants = [p for p in parts if not p["is_product"]]
        products = [p for p in parts if p["is_product"]]
        # A reaction SMILES only where EVERY participant resolved. A partial one
        # reads as a complete reaction that happens to be wrong, which is worse
        # than an absent one, and a consumer cannot tell the two apart.
        rxn_smiles = None
        if parts and all(p["smiles"] for p in parts) and products:
            rxn_smiles = (".".join(p["smiles"] for p in reactants) + ">>"
                          + ".".join(p["smiles"] for p in products))
            complete += 1

        out.append({
            "reaction_id": r.get("reaction_id"),
            "section_label": r.get("section_label"),
            "step_label": r.get("step_label"),
            "reaction_class": r.get("reaction_class"),
            "named_reaction": r.get("named_reaction"),
            "is_one_pot": r.get("is_one_pot"),
            "conditions": r.get("conditions"),
            "reaction_smiles": rxn_smiles,
            "participants_total": len(parts),
            "participants_resolved": sum(1 for p in parts if p["smiles"]),
            "compounds": parts,
        })

    dest = OUTPUT / REL / "export"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"reactions-with-smiles-{pid}.json").write_text(
        json.dumps({"patent_id": pid, "reactions": out}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    # One row per reaction, for a spreadsheet. Participants collapse to a
    # semicolon-joined list because a chemist opening this wants to scan it, and
    # the JSON above is there for anything that needs the structure.
    csv_path = dest / f"reactions-with-smiles-{pid}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["reaction_id", "section", "step", "reaction_class", "named_reaction",
                    "reaction_smiles", "resolved/total",
                    "reactants", "reactant_smiles", "products", "product_smiles",
                    "origins"])
        for r in out:
            rs = [c for c in r["compounds"] if not c["is_product"]]
            ps = [c for c in r["compounds"] if c["is_product"]]
            j = lambda xs, k: "; ".join(str(x[k] or "") for x in xs)
            w.writerow([r["reaction_id"], r["section_label"], r["step_label"],
                        r["reaction_class"], r["named_reaction"] or "",
                        r["reaction_smiles"] or "",
                        f'{r["participants_resolved"]}/{r["participants_total"]}',
                        j(rs, "identifier"), j(rs, "smiles"),
                        j(ps, "identifier"), j(ps, "smiles"),
                        "; ".join(sorted({c["origin"] for c in r["compounds"]}))])

    total_parts = sum(r["participants_total"] for r in out)
    resolved = sum(r["participants_resolved"] for r in out)
    print(f"{len(out)} reactions -> {shown(dest)}/")
    print(f"  participants resolved to a structure   {resolved}/{total_parts}")
    print(f"  reactions with EVERY participant resolved  {complete}/{len(out)}")
    if complete < len(out):
        print(f"\n  {len(out) - complete} reaction(s) have no reaction SMILES because at least")
        print(f"  one participant has no structure. They are in the files with")
        print(f"  reaction_smiles null and the per-compound detail intact, rather")
        print(f"  than dropped or half-built.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
