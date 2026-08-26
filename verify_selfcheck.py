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
    G  contract        the claim shape against VERIFICATION-CONTRACT.md
    H  blind spot      the arithmetic the engine cannot currently see, and
                        whether it explains what F says it missed

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
    record("every claim carries a documented `about`",
           PASS if all(c.get("about") in SUBJECTS for c in claims) else FAIL,
           str(dict(Counter(c.get("about") for c in claims))))
    record("every claim carries a severity",
           PASS if all(c.get("severity") for c in claims) else FAIL,
           str(dict(Counter(c.get("severity") for c in claims))))

    # Tier 2 is the recall census and it now has TWO feeders: whole lines nobody
    # cites, and single quantities on a cited line that no claim asserts. The
    # denominator comes from the tallies and never from counting the queue,
    # because a queue counting itself cannot detect a claim that failed to be
    # emitted at all, which is the exact failure this check exists for.
    cov = artifact["source_coverage"]["summary"]
    qty = artifact["summary"].get("quantity_coverage") or {}
    uncited = cov.get("uncited_with_chemistry", 0)
    unaccounted = sum(qty.get(k, 0) for k in ("gap", "schema_loss", "unmapped"))
    print(f"     uncited chemistry lines       {uncited}")
    print(f"     unaccounted quantities        {unaccounted}"
          f"  (of {qty.get('tokens', 0)} tokens, {qty.get('accounted', 0)} "
          f"accounted, {qty.get('vessel', 0)} glassware)")
    tier2 = tiers.get(2, 0)
    record("tier 2 population equals its two feeders",
           PASS if tier2 == uncited + unaccounted else FAIL,
           f"tier 2 has {tier2} claims; {uncited} uncited lines plus "
           f"{unaccounted} unaccounted quantities is {uncited + unaccounted}")

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


# Exactly the keys VERIFICATION-CONTRACT.md puts on a claim, plus the four the
# review protocol added. A key outside this set is either an undocumented feature
# the UI cannot know about, or a working variable that leaked into a 3 MB file.
CONTRACT_CLAIM_KEYS = {
    "claim_id", "record_id", "record_kind", "rec", "rec_field",
    "record_label_en", "section_en", "about", "field", "field_label_en",
    "question_en", "claimed_en", "claimed_value", "claimed_unit", "basis",
    "cited_lines", "evidence_en", "evidence_lines", "highlights", "auto",
    "auto_reason_en", "needs_human", "load_bearing", "risk", "risk_reasons_en",
    "structure_svg_path", "tier", "stratum", "severity", "severity_action_en",
}

# Documented, but only on the claims it applies to, so not required of all of them.
OPTIONAL_CLAIM_KEYS = {"quantity_verdict"}

# `schema` is the third subject: the annotation read the page correctly and the
# field it had to put the answer in could not hold it. Nobody is wrong and
# re-extracting fixes nothing, which is why it cannot be folded into `extraction`.
SUBJECTS = {"extraction", "patent", "schema"}


def test_contract_shape(artifact: dict) -> None:
    print("\nG  the artifact against VERIFICATION-CONTRACT.md")
    keys: Counter = Counter()
    for c in artifact["claims"]:
        keys.update(c.keys())
    n = len(artifact["claims"])

    missing = {k for k in CONTRACT_CLAIM_KEYS if keys.get(k, 0) < n}
    record("every contract key is on every claim",
           PASS if not missing else FAIL,
           "all present" if not missing else
           ", ".join(f"{k} on {keys.get(k, 0)}/{n}" for k in sorted(missing)))

    extra = {k: v for k, v in keys.items()
             if k not in CONTRACT_CLAIM_KEYS and k not in OPTIONAL_CLAIM_KEYS}
    record("no key outside the contract reaches the artifact",
           PASS if not extra else WARN,
           "none" if not extra else
           ", ".join(f"{k} on {v}/{n}" for k, v in sorted(extra.items())))

    private = {k: v for k, v in extra.items() if k.startswith("_")}
    record("no working variable leaked into the artifact",
           PASS if not private else FAIL,
           "none" if not private else ", ".join(sorted(private)))

    for key in ("summary", "records", "source_coverage", "completeness",
                "source", "patent_id", "engine_version", "generated_at"):
        if key not in artifact:
            record(f"top level carries `{key}`", FAIL, "absent")


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

    # The engine compares against the UNION of the two flags that are about
    # arithmetic. Recounted the same way, because a recount that uses a
    # different definition is not a check on the engine, it is a second opinion
    # about what the question was.
    ARITHMETIC_FLAGS = ("molar_mass_inconsistent", "mass_balance_implausible")
    ours = {r["record_id"] for r in artifact["records"]
            if r["record_kind"] == "reaction"
            for c in r["checks"]
            if c["family"] == "quantity" and c["status"] == "fail"}
    annotated = set().union(*(flagged_records.get(f, set())
                              for f in ARITHMETIC_FLAGS))
    both, machine_only = ours & annotated, ours - annotated
    annotation_only = annotated - ours
    print(f"     both flag it                      {len(both)}")
    print(f"     engine flags, annotation did not  {len(machine_only)}")
    print(f"     annotation flags, engine passed   {len(annotation_only)}"
          + (f"  {sorted(annotation_only)}" if annotation_only else ""))

    reported = artifact["summary"].get("agreement_with_annotation")
    if reported:
        def size(v):
            return len(v) if isinstance(v, list) else v
        agrees = (size(reported.get("both")) == len(both)
                  and size(reported.get("machine_only")) == len(machine_only)
                  and size(reported.get("annotation_only")) == len(annotation_only))
        record("summary.agreement_with_annotation matches an independent recount",
               PASS if agrees else FAIL,
               f"engine says both={size(reported.get('both'))} "
               f"machine_only={size(reported.get('machine_only'))} "
               f"annotation_only={size(reported.get('annotation_only'))}; "
               f"recount says both={len(both)} machine_only={len(machine_only)} "
               f"annotation_only={len(annotation_only)}")
    else:
        record("summary carries an agreement matrix", FAIL, "absent")

    # `annotation_only` is the honest half: a defect the annotator saw and this
    # engine did not. It is graded as a warning rather than a pass because the
    # engine having missed it is the finding.
    record("the engine sees every arithmetic defect the annotation saw",
           PASS if not annotation_only else WARN,
           f"{len(annotation_only)} reaction(s) the annotation flags as "
           f"{' or '.join(ARITHMETIC_FLAGS)} pass every engine quantity check")

    uncompared = {k: v for k, v in theirs.items() if k not in ARITHMETIC_FLAGS}
    record("every annotation flag family has an engine check to compare against",
           WARN if uncompared else PASS,
           f"{sum(uncompared.values())} flags across "
           f"{len(uncompared)} families have no counterpart check: "
           + ", ".join(sorted(uncompared)))
    return annotation_only


def test_missed_arithmetic(data: dict, artifact: dict, missed: set) -> None:
    """Why the engine passed a step the annotation flagged, and what would not.

    `mass_check` needs a mass AND a mole count ON THE SAME ROW, so a product row
    that states a mass and no moles is invisible to it. That is not a rare shape:
    it is how every one of this patent's example steps writes its product. The
    arithmetic those rows DO support is the yield identity

        limiting reactant mmol  x  yield  x  MW(product)  =  product mass

    which needs no mole count on the product row at all. Measured here rather
    than asserted, because the claim being made is that adding it would close
    the gap, and that claim is checkable.
    """
    print("\nH  the arithmetic the engine cannot currently see")
    structures = {e["identifier"]: e for e in data["structures"]}
    label = {r["record_id"]: r["label_en"] for r in artifact["records"]}

    rows, unusable = [], 0
    for r in data["reactions"]:
        product = mass = None
        reactant_mmol = []
        for c in (r.get("compounds") or []):
            q = c.get("quantity") or {}
            if c.get("role") == "product" and q.get("mass_g") is not None:
                product, mass = c.get("identifier"), float(q["mass_g"])
            elif c.get("role") == "reactant" and q.get("mmol"):
                reactant_mmol.append(float(q["mmol"]))
        yield_pct = r.get("product_yield_pct")
        mw = (structures.get(product) or {}).get("mw") if product else None
        if not (product and mass and reactant_mmol and yield_pct and mw):
            unusable += 1
            continue
        limiting = min(reactant_mmol)
        predicted = limiting / 1000.0 * mw * (yield_pct / 100.0)
        rows.append((r["id"], product, mw, mass, predicted,
                     mass / (limiting / 1000.0 * yield_pct / 100.0)))

    off = [t for t in rows if abs(t[3] / t[4] - 1) > 0.02]
    print(f"     reactions the identity can be applied to   {len(rows)}"
          f"  ({unusable} lack a product mass, a reactant mole count, a yield "
          f"or a resolved structure)")
    print(f"     of those, product mass disagrees by >2%    {len(off)}")
    for rid, product, mw, mass, predicted, implied in off:
        delta = implied - mw
        note = ("  consistent with chlorine-for-hydrogen"
                if abs(delta + V.CL_FOR_H) < V.CL_WINDOW else "")
        print(f"       {label.get(rid, rid)[:42]:44} stated {mass:7.2f} g, "
              f"identity predicts {predicted:7.2f} g, implied MW "
              f"{implied:7.2f} against {mw:7.2f}{note}")

    would_catch = {t[0] for t in off}
    closed = missed & would_catch
    record("the yield identity would close the annotation_only gap",
           PASS if not missed or closed == missed else WARN,
           "nothing was missed" if not missed else
           f"{len(closed)} of {len(missed)} missed reactions "
           f"({', '.join(sorted(label.get(i, i) for i in closed))[:90]}) "
           f"disagree under the yield identity")


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
    test_contract_shape(artifact)
    test_citation_width(artifact)
    missed = test_agreement(artifact, data)
    test_missed_arithmetic(data, artifact, missed)

    print()
    tally = Counter(s for _, s, _ in results)
    print(f"{tally[PASS]} pass, {tally[WARN]} warn, {tally[FAIL]} fail")
    for name, status, detail in results:
        if status == FAIL:
            print(f"  FAIL  {name}: {detail}")
    return 1 if tally[FAIL] else 0


if __name__ == "__main__":
    raise SystemExit(main())
