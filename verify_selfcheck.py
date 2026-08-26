#!/usr/bin/env python3
r"""Grade verify.py's output without trusting verify.py's exit code.

A verification engine that exits 0 has proved nothing. It may have written no
claims at all, written Chinese into a file whose entire promise is that a reader
with no Chinese can open it, drifted between runs so that a diff of two artifacts
is noise, or - the failure that matters most - lost the ability to notice a wrong
number. This script asks those four questions of the engine as it stands on disk
and answers them with counts rather than with adjectives.

Nothing here writes to gold/ or provenance/, and nothing writes the artifact. The
engine is driven IN PROCESS, so `assemble()` is called against inputs this script
holds in memory and the file on disk is never touched. That is what makes the
corruption test safe: the gold is mutated in a dict, never on disk.

    A  determinism      two builds, byte-identical claims[]
    B  no Chinese       zero Han characters in the serialised artifact
    C  sensitivity      corrupt one mass in a COPY of the gold; the claim that
                        cites it must stop saying `found`
    D  census           the real counts, per verdict, per tier, per stratum
    E  citation width   how many lines a claim cites, because `found` against a
                        72-line citation is not the same evidence as `found`
                        against one line, and the contract's confidence bound is
                        computed over claims that do not distinguish them
    F  agreement        the engine's quantity failures against the annotation's
                        own validation flags, all three ways round

Usage:  python3 verify_selfcheck.py            # defaults to CN104292137A
        python3 verify_selfcheck.py CN104292137A
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify as V  # noqa: E402  the engine under test

CJK = re.compile(r"[一-鿿]")

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str) -> None:
    results.append((name, status, detail))
    print(f"  [{status}] {name}: {detail}")


def build(patent_id: str, data: dict) -> dict:
    """One full engine run against `data`, in memory, writing nothing."""
    run = V.Run(patent_id, copy.deepcopy(data))
    run.build()
    return V.assemble(run)


def claims_bytes(artifact: dict) -> bytes:
    return json.dumps(artifact["claims"], indent=2, ensure_ascii=False,
                      sort_keys=True).encode("utf-8")


# ------------------------------------------------------------------ A, B, C

def test_determinism(patent_id: str, data: dict) -> dict:
    print("\nA  determinism")
    first = build(patent_id, data)
    second = build(patent_id, data)
    a, b = claims_bytes(first), claims_bytes(second)
    if a == b:
        record("claims[] byte-identical across two builds", PASS,
               f"{len(first['claims'])} claims, sha256 "
               f"{hashlib.sha256(a).hexdigest()[:16]}")
    else:
        ids_a = [c["claim_id"] for c in first["claims"]]
        ids_b = [c["claim_id"] for c in second["claims"]]
        record("claims[] byte-identical across two builds", FAIL,
               f"{len(a)} bytes vs {len(b)} bytes; "
               f"{'order differs' if set(ids_a) == set(ids_b) else 'membership differs'}")

    ids = [c["claim_id"] for c in first["claims"]]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    record("claim_id unique", PASS if not dupes else FAIL,
           f"{len(ids)} claims, {len(set(ids))} distinct ids"
           + ("" if not dupes else f", {len(dupes)} collide: {dupes[:5]}"))
    return first


def test_no_chinese(artifact: dict) -> None:
    print("\nB  no Chinese reaches the reviewer")
    body = json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True)
    runs = re.findall(CJK.pattern + "+", body)
    record("zero Han characters in the serialised artifact",
           PASS if not runs else FAIL,
           f"{len(runs)} runs found"
           + ("" if not runs else ": " + ", ".join(sorted(set(runs))[:10])))

    # The gate above is the one the contract states. This one is the reason it
    # exists: a string that is empty, or that says "[untranslated]", is not
    # Chinese but is also not evidence, and a reviewer meets it the same way.
    blank = [c["claim_id"] for c in artifact["claims"]
             if not (c.get("evidence_en") or "").strip()]
    record("every claim carries non-empty evidence_en",
           PASS if not blank else WARN,
           f"{len(blank)} of {len(artifact['claims'])} claims have empty evidence")

    # Passing the Han gate by DELETING the line is not passing it. A line the
    # engine gives up on is replaced wholesale by a sentence saying a Chinese
    # reader is needed, and a line that is 307 characters of English with one
    # Chinese term in it must never take that path: the reviewer is told the
    # evidence is unreadable when it is sitting right there.
    GAVE_UP = "[This source line is Chinese"
    raw = V.read_numbered(artifact["patent_id"])
    surrendered = [l["n"] for l in artifact["source_coverage"]["lines"]
                   if (l.get("text_en") or "").startswith(GAVE_UP)]
    affected = [c for c in artifact["claims"]
                if any((e.get("text_en") or "").startswith(GAVE_UP)
                       for e in c["evidence_lines"])]
    salvageable = []
    for n in surrendered:
        text = raw.get(n, "")
        han = sum(len(r) for r in re.findall(CJK.pattern + "+", text))
        latin = len(re.findall(r"[A-Za-z]", text))
        if latin > 2 * han:
            salvageable.append((n, han, latin))
    record("no source line is abandoned as untranslatable",
           PASS if not surrendered else WARN,
           f"{len(surrendered)} lines render as \"ask a Chinese reader\" "
           f"({', '.join(str(n) for n in surrendered[:10])}), reaching the "
           f"evidence panel of {len(affected)} claims")
    record("no line that is mostly English is abandoned",
           PASS if not salvageable else FAIL,
           "none" if not salvageable else
           "; ".join(f"line {n} is {latin} Latin characters against {han} Han"
                     for n, han, latin in salvageable))


def test_sensitivity(patent_id: str, data: dict, artifact: dict) -> None:
    """Corrupt one mass in a copy of the gold. The claim must stop saying found."""
    print("\nC  sensitivity: does the engine still notice a wrong number")

    target = None
    for c in data["compounds"]:
        q = c.get("quantity") or {}
        if q.get("mass_g") is not None:
            rid = V.safe_record_id(patent_id, c["id"], c["identifier"])
            cid = V.claim_id(rid, "quantity.mass_g")
            before = next((x for x in artifact["claims"]
                           if x["claim_id"] == cid), None)
            if before and before["auto"] == "found":
                target = (c["identifier"], rid, cid, float(q["mass_g"]))
                break
    if target is None:
        record("a found mass_g claim exists to corrupt", FAIL,
               "no compound record has a mass_g claim the engine calls found")
        return

    ident, rid, cid, real = target
    corrupt = copy.deepcopy(data)
    for c in corrupt["compounds"]:
        if c["identifier"] == ident:
            c["quantity"]["mass_g"] = 99.9
    after_art = build(patent_id, corrupt)
    after = next((x for x in after_art["claims"] if x["claim_id"] == cid), None)

    if after is None:
        record("the corrupted claim survives into the artifact", FAIL,
               f"claim {cid} vanished after corruption")
        return
    ok = after["auto"] == "not_found"
    record("a mass changed from the real value to 99.9 stops being found",
           PASS if ok else FAIL,
           f"{V.field_label('quantity.mass_g')} on record {rid}: "
           f"{real} g was {before_verdict(artifact, cid)}, 99.9 g is "
           f"{after['auto']}")
    if ok:
        record("and the engine says why in English", PASS,
               after["auto_reason_en"][:140])
    # The gold on disk was never touched; prove it rather than assert it.
    gold = json.loads((V.REL / "gold" / "compounds.json").read_text("utf-8"))
    on_disk = next((c.get("quantity", {}).get("mass_g") for c in gold
                    if c["identifier"] == ident), None)
    record("gold/compounds.json is unchanged on disk",
           PASS if on_disk == real else FAIL,
           f"{ident if not V.has_chinese(ident) else V.ascii_key(ident)} "
           f"still reads {on_disk} g")


def before_verdict(artifact: dict, cid: str) -> str:
    return next(x["auto"] for x in artifact["claims"] if x["claim_id"] == cid)


# ------------------------------------------------------------------ D, E, F

def test_census(artifact: dict) -> None:
    print("\nD  the real counts")
    claims = artifact["claims"]
    verdicts = Counter(c["auto"] for c in claims)
    print(f"     claims total            {len(claims)}")
    for v in ("found", "partial", "not_found", "not_checkable"):
        print(f"     {v:22}  {verdicts.get(v, 0)}")

    tiers = Counter(c.get("tier") for c in claims)
    print(f"     tier 1 (census, suspicious)   {tiers.get(1, 0)}")
    print(f"     tier 2 (census, candidate miss) {tiers.get(2, 0)}")
    print(f"     tier 3 (sampled, machine ok)  {tiers.get(3, 0)}")
    print(f"     tier unset                    {tiers.get(None, 0)}")

    record("every claim carries a tier",
           PASS if not tiers.get(None) else FAIL,
           f"{tiers.get(None, 0)} claims have no tier")
    record("every claim carries a stratum",
           PASS if all(c.get("stratum") for c in claims) else FAIL,
           f"{sum(1 for c in claims if not c.get('stratum'))} claims have none")
    record("every claim carries `about`",
           PASS if all(c.get("about") in ("extraction", "patent")
                       for c in claims) else FAIL,
           str(dict(Counter(c.get("about") for c in claims))))

    cov = artifact["source_coverage"]["summary"]
    uncited = cov.get("uncited_with_chemistry", 0)
    print(f"     uncited chemistry lines       {uncited}")
    tier2 = tiers.get(2, 0)
    record("tier 2 population equals the uncited chemistry lines",
           PASS if tier2 == uncited else FAIL,
           f"tier 2 has {tier2} claims, coverage reports {uncited} lines")

    # The protocol budgets tier 1 as a census inside 15 minutes at ~6s a claim.
    budget = 900 / 6
    record("tier 1 is small enough to be worked as a census",
           PASS if tiers.get(1, 0) <= budget else WARN,
           f"{tiers.get(1, 0)} claims at 6s each is "
           f"{tiers.get(1, 0) * 6 / 60:.0f} minutes of a 15 minute budget")

    strata = artifact["summary"].get("tier3_population_by_stratum")
    if strata:
        total = sum(strata.values()) if isinstance(strata, dict) else 0
        record("tier 3 stratum populations sum to the tier 3 count",
               PASS if total == tiers.get(3, 0) else FAIL,
               f"{total} across {len(strata)} strata vs {tiers.get(3, 0)} claims")
    else:
        record("summary carries tier3_population_by_stratum", FAIL,
               "absent, so the UI cannot compute a confidence denominator")


def test_citation_width(artifact: dict) -> None:
    print("\nE  how much evidence a `found` actually rests on")
    claims = artifact["claims"]
    buckets = defaultdict(int)
    for c in claims:
        n = len(c["cited_lines"])
        key = ("0" if n == 0 else "1-3" if n <= 3 else "4-10" if n <= 10
               else "11-30" if n <= 30 else "31+")
        buckets[key] += 1
    for key in ("0", "1-3", "4-10", "11-30", "31+"):
        print(f"     {key:>6} cited lines   {buckets[key]:>4}")

    found = [c for c in claims if c["auto"] == "found"]
    wide = [c for c in found if len(c["cited_lines"]) > 10]
    pct = 100.0 * len(wide) / len(found) if found else 0.0
    record("`found` mostly rests on a narrow citation",
           PASS if pct < 10 else WARN,
           f"{len(wide)} of {len(found)} found claims ({pct:.1f}%) matched "
           f"against more than 10 cited lines; widest is "
           f"{max((len(c['cited_lines']) for c in claims), default=0)} lines")


def test_agreement(artifact: dict, data: dict) -> None:
    print("\nF  the engine against the annotation's own flags")
    theirs = Counter()
    flagged_records: dict[str, set] = defaultdict(set)
    for r in data["reactions"]:
        for f in (r.get("validation_flags") or []):
            theirs[f] += 1
            flagged_records[f].add(r["id"])
    print("     the annotation's flags: "
          + ", ".join(f"{k}={v}" for k, v in sorted(theirs.items())))

    ours = {r["record_id"] for r in artifact["records"]
            for c in r["checks"]
            if c["family"] == "quantity" and c["status"] == "fail"}
    mm = flagged_records.get("molar_mass_inconsistent", set())
    both = ours & mm
    machine_only = ours - mm
    annotation_only = mm - ours
    print(f"     both flag it                {len(both)}")
    print(f"     engine flags, annotation did not  {len(machine_only)}"
          + (f"  {sorted(machine_only)}" if machine_only else ""))
    print(f"     annotation flags, engine passed   {len(annotation_only)}"
          + (f"  {sorted(annotation_only)}" if annotation_only else ""))

    reported = artifact["summary"].get("agreement_with_annotation")
    if reported:
        agrees = (reported.get("both") == len(both)
                  and reported.get("machine_only") == len(machine_only)
                  and reported.get("annotation_only") == len(annotation_only))
        record("summary.agreement_with_annotation matches a recount",
               PASS if agrees else FAIL,
               f"artifact says {reported}, recount says "
               f"{{'both': {len(both)}, 'machine_only': {len(machine_only)}, "
               f"'annotation_only': {len(annotation_only)}}}")
    else:
        record("summary carries an agreement matrix", FAIL, "absent")

    uncompared = {k: v for k, v in theirs.items()
                  if k != "molar_mass_inconsistent"}
    record("every annotation flag family has an engine check to compare against",
           WARN if uncompared else PASS,
           f"{sum(uncompared.values())} flags across "
           f"{len(uncompared)} families have no counterpart check: "
           + ", ".join(sorted(uncompared)))


# ------------------------------------------------------------------ main

def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    patent_id = args[0] if args else V.DEFAULT_PATENT_ID

    engine = (HERE / "verify.py").read_bytes()
    print(f"engine    verify.py  {len(engine)} bytes  sha256 "
          f"{hashlib.sha256(engine).hexdigest()[:16]}")
    print(f"patent    {patent_id}")

    data = V.load_inputs(patent_id)
    artifact = test_determinism(patent_id, data)
    test_no_chinese(artifact)
    test_sensitivity(patent_id, data, artifact)
    test_census(artifact)
    test_citation_width(artifact)
    test_agreement(artifact, data)

    print()
    tally = Counter(s for _, s, _ in results)
    print(f"{tally[PASS]} pass, {tally[WARN]} warn, {tally[FAIL]} fail")
    for name, status, detail in results:
        if status == FAIL:
            print(f"  FAIL  {name}: {detail}")
    return 1 if tally[FAIL] else 0


if __name__ == "__main__":
    raise SystemExit(main())
