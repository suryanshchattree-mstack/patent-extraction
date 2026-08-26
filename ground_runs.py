#!/usr/bin/env python3
r"""Score every extraction run against the PATENT, not against another run.

`extraction-approaches/compare.py` measures concordance: where two runs disagree
and by how much. Its own docstring is careful to say that nothing in it has read
the patent, so its numbers are agreement with a reference run and never accuracy
against truth. This file is the other half. It never compares two runs to each
other. It asks each run, on its own, two questions the patent can answer:

    grounding    is every number this run states actually printed in the patent?
    arithmetic   do the numbers it states about one molecule agree with each other?

Both are gold-free, both need no reference run, and both are directly comparable
across approaches because the patent does not change.

WHAT THIS CANNOT DO, AND WHY THE NUMBER IS NAMED THE WAY IT IS

`verify.py` asks the sharp question: is this value on the lines THIS RECORD ITSELF
CITES? That is the real grounding test and it catches a value that is in the
document but attached to the wrong molecule, which is the commonest defect.

It cannot be asked here. Only `A-sixpass-gold` carries line-level provenance;
`A-sixpass-raw`, `B-singlepass` and the three self-consistency replicates carry
none, and the replicates carry only `compounds.json`. With no citation there is
no line to check against, so the sharp question is not weakly answered here, it
is unanswerable.

So this asks the blunt one: does the value appear ANYWHERE in the 256 lines?
That is a floor, not a grade. It cannot see a real quantity bound to the wrong
compound, and on a document this size a two-digit number is quite likely to
appear somewhere by chance. A value that fails it is a strong signal - the run
states a number the patent never prints. A value that passes it has cleared a low
bar. The column is called `accounted` and never `grounded` for that reason.

A checker that never fires is not a checker that passes, so `--selftest` puts
known-real and known-invented quantities through the same detector and prints what
it says about each. Run it before believing a column of zeroes.

THE POPULATION MATTERS AS MUCH AS THE RATE

A run that extracts thirty numbers and grounds all thirty is not better than one
that extracts ninety and grounds eighty-eight. It is less useful and more
cautious. Both counts are printed side by side and no single score merges them,
because merging them is exactly how a timid extractor wins a benchmark it should
lose.

Usage:  python3 ground_runs.py
        python3 ground_runs.py --runs B-singlepass A-sixpass-gold
        python3 ground_runs.py --patent CN104292137A
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors

import verify as V

RDLogger.DisableLog("rdApp.*")

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "extraction-approaches" / "runs"

# Field -> the unit its value is stated in. The same table `verify.py` uses, kept
# here because these runs have no schema of their own to read it from.
COMPOUND_FIELDS = (("mass_g", "g"), ("volume_ml", "ml"), ("mmol", "mmol"),
                   ("yield_pct", "%"))

# Below this the arithmetic is not worth reporting: a 1.5% relative window on a
# molecular weight, floored, exactly as verify.py's mass_check does it.
REL_TOL, ABS_TOL_FLOOR = V.REL_TOL, V.ABS_TOL_FLOOR


def find_runs() -> list[Path]:
    """Every directory under runs/ holding at least a compounds.json."""
    out = []
    for path in sorted(RUNS.rglob("compounds.json")):
        out.append(path.parent)
    return out


def document_tokens(patent_id: str) -> dict[str, list[float]]:
    """Every (value, unit) the patent prints, canonicalised, bucketed by unit."""
    lines = V.read_numbered(patent_id)
    buckets: dict[str, list[float]] = {}
    for text in lines.values():
        for tok in V.tokenise(text):
            buckets.setdefault(tok.unit or "", []).append(tok.canonical())
    return {k: sorted(set(v)) for k, v in buckets.items()}


def in_document(buckets: dict, value: float, unit: str | None) -> str:
    """`printed`, `bare` or `absent`. The middle one is not a failure.

    Unit is canonical on both sides, so 0.2 mol on the page answers 200 mmol in
    the record.

    `bare` exists because this patent really does print quantities with no unit
    beside them. Line 243 reads "...71.4(0.6mol)", so thionyl chloride's 71.4 g
    is on the page with the g missing. Every run states it and a two-way check
    calls all of them fabricators. That was the first output of this file and it
    was wrong in exactly the way it was written to catch, so the third state is
    the fix rather than a softened threshold.
    """
    if unit is not None and any(V.same_number(v, value)
                                for v in buckets.get(unit, ())):
        return "printed"
    if any(V.same_number(v, value) for v in buckets.get("", ())):
        return "bare"
    if unit is None:
        return "printed" if any(any(V.same_number(v, value) for v in vals)
                                for vals in buckets.values()) else "absent"
    return "absent"


def claims_of(run: Path) -> list[dict]:
    """Every numeric assertion a run makes, whatever files it happens to carry."""
    out: list[dict] = []

    def add(where, field, value, unit):
        if value is None:
            return
        try:
            out.append({"where": where, "field": field,
                        "value": float(value), "unit": unit})
        except (TypeError, ValueError):
            pass

    compounds = load(run, "compounds.json") or []
    for c in compounds:
        name = c.get("identifier") or "(unnamed)"
        q = c.get("quantity") or {}
        for field, unit in COMPOUND_FIELDS:
            add(name, f"quantity.{field}", q.get(field), unit)
        mp = c.get("melting_point") or {}
        for bound in ("min_c", "max_c"):
            add(name, f"melting_point.{bound}", mp.get(bound), "C")
        add(name, "purity_pct", c.get("purity_pct"), "%")

    for r in load(run, "reactions.json") or []:
        step = f"{r.get('section_label')} {r.get('step_label')}"
        cond = r.get("conditions") or {}
        temp = cond.get("temperature") or {}
        for bound in ("value_c", "min_c", "max_c"):
            add(step, f"conditions.temperature.{bound}", temp.get(bound), "C")
        add(step, "conditions.time_h", cond.get("time_h"), "h")
        add(step, "product_yield_pct", r.get("product_yield_pct"), "%")
        for c in (r.get("compounds") or []):
            q = c.get("quantity") or {}
            ident = c.get("identifier") or "(unnamed)"
            for field, unit in COMPOUND_FIELDS:
                add(f"{step} / {ident}", f"quantity.{field}", q.get(field), unit)
    return out


def load(run: Path, name: str):
    path = run / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def molecular_weight(compound: dict) -> float | None:
    """The run's own molecular weight, from whichever it recorded.

    Taken from the run rather than from any gold, so the arithmetic below is the
    run checked against ITSELF and never against another run's chemistry.
    """
    mw = compound.get("molecular_weight")
    if isinstance(mw, (int, float)) and mw > 0:
        return float(mw)
    smiles = compound.get("smiles")
    if smiles and not V.has_chinese(str(smiles)):
        mol = Chem.MolFromSmiles(str(smiles))
        if mol is not None:
            return float(Descriptors.MolWt(mol))
    return None


def arithmetic(run: Path) -> tuple[int, list[dict]]:
    """Rows stating a mass AND a mole count: do they imply their own weight?"""
    checked, bad = 0, []
    for c in load(run, "compounds.json") or []:
        q = c.get("quantity") or {}
        mass, mmol = q.get("mass_g"), q.get("mmol")
        mw = molecular_weight(c)
        if mass is None or not mmol or mw is None:
            continue
        checked += 1
        implied = float(mass) / (float(mmol) / 1000.0)
        delta = implied - mw
        if abs(delta) > max(ABS_TOL_FLOOR, REL_TOL * mw):
            bad.append({"name": c.get("identifier"), "mass_g": float(mass),
                        "mmol": float(mmol), "mw": mw, "implied": implied,
                        "delta": delta,
                        "cl_for_h": abs(delta + V.CL_FOR_H) < V.CL_WINDOW})
    return checked, bad


SELFTEST = [(25.3, "g", "real, the 2-chlorotoluene charge", "printed"),
            (28.6, "g", "real, the step 1 product mass", "printed"),
            (84.0, "%", "real, the step 1 yield", "printed"),
            (71.4, "g", "real, but the page prints it with no unit", "bare"),
            (99.9, "g", "invented", "absent"),
            (1234.5, "g", "invented", "absent"),
            (0.5, "%", "invented", "absent")]


def selftest(buckets: dict) -> int:
    """Can the detector say `absent` at all? A column of zeroes has to earn it."""
    print("detector sensitivity, before believing any zero above:\n")
    bad = 0
    for value, unit, note, expected in SELFTEST:
        got = in_document(buckets, value, unit)
        ok = got == expected
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'}  {V.fmt_quantity(value, unit):>10} "
              f"-> {got:<8} expected {expected:<8}  {note}")
    print(f"\n{len(SELFTEST) - bad} of {len(SELFTEST)} as expected")
    return 1 if bad else 0


def main() -> int:
    argv = sys.argv[1:]
    patent_id = "CN104292137A"
    if "--patent" in argv:
        patent_id = argv[argv.index("--patent") + 1]
    runs = find_runs()
    if "--runs" in argv:
        wanted = argv[argv.index("--runs") + 1:]
        runs = [r for r in runs if r.name in wanted
                or str(r.relative_to(RUNS)) in wanted]
    if not runs:
        print(f"no runs found under {RUNS}", file=sys.stderr)
        return 2

    buckets = document_tokens(patent_id)
    if "--selftest" in argv:
        return selftest(buckets)
    total_tokens = sum(len(v) for v in buckets.values())
    print(f"patent   {patent_id}, {total_tokens} distinct printed quantities")
    print(f"runs     {RUNS}")
    print()
    print("Every number each run states, asked of the patent. `accounted` is a")
    print("FLOOR, not a grade: it cannot see a real value bound to the wrong")
    print("molecule, which needs the line-level citation only A-sixpass-gold has.")
    print()
    print(f"{'run':26}{'numbers':>9}{'printed':>9}{'bare':>7}{'ABSENT':>8}"
          f"{'accounted':>11}")
    print("-" * 70)

    absences: dict[str, list[dict]] = {}
    arith_checked = 0
    for run in runs:
        name = str(run.relative_to(RUNS))
        claims = claims_of(run)
        verdicts = [(c, in_document(buckets, c["value"], c["unit"]))
                    for c in claims]
        printed = sum(1 for _, v in verdicts if v == "printed")
        bare = sum(1 for _, v in verdicts if v == "bare")
        missing = [c for c, v in verdicts if v == "absent"]
        absences[name] = missing
        checked, _ = arithmetic(run)
        arith_checked += checked
        rate = (100.0 * (printed + bare) / len(claims)) if claims else 0.0
        print(f"{name:26}{len(claims):>9}{printed:>9}{bare:>7}"
              f"{len(missing):>8}{rate:>10.1f}%")

    print()
    print("A run stating fewer numbers is not a better run, it is a quieter one.")
    print("Read `numbers` and `accounted` together or a timid extractor wins both.")
    print()
    if not arith_checked:
        print("mass-against-moles: NOT COMPUTABLE for any run, and that is itself")
        print("  the finding. No run populates `molecular_weight` or `smiles` on a")
        print("  single compound, so a row stating both a mass and a mole count has")
        print("  nothing to be checked against. This is the arithmetic that found")
        print("  the des-chloro defect; none of these approaches can perform it on")
        print("  their own output without a structure-resolution pass they do not")
        print("  have. 10 rows per run state both and could be checked if they did.")

    for name, missing in absences.items():
        if not missing:
            continue
        print(f"\n{name}: {len(missing)} numbers the patent never prints")
        for c in missing[:12]:
            print(f"    {str(c['where'])[:44]:46} {c['field'][:26]:28} "
                  f"{V.fmt_quantity(c['value'], c['unit'])}")
        if len(missing) > 12:
            print(f"    ... and {len(missing) - 12} more")

    for run in runs:
        name = str(run.relative_to(RUNS))
        _, bad = arithmetic(run)
        if not bad:
            continue
        print(f"\n{name}: {len(bad)} rows whose mass and moles disagree with "
              f"their own molecular weight")
        for b in bad[:10]:
            tail = ("  consistent with chlorine-for-hydrogen" if b["cl_for_h"]
                    else "")
            print(f"    {str(b['name'])[:40]:42} {b['mass_g']:>8.2f} g / "
                  f"{b['mmol']:>7.1f} mmol implies {b['implied']:>8.2f} "
                  f"against {b['mw']:>7.2f}{tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
