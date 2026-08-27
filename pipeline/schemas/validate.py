#!/usr/bin/env python3
"""Validate the finalised artifacts against schemas/*.schema.json.

Needs jsonschema:  pip install jsonschema
Run after finalise.py. Exits non-zero on any violation.

Two kinds of check, and the second one is not in any schema.

JSON Schema can say a record HAS a patent_id. It cannot say that patent_id is the
one this run is about, or the same one every other record carries. That gap let a
run on a second patent publish 75 compound records whose ids were built from the
new patent and whose patent_id fields still named the old one: every schema passed,
because each record was individually well formed. So the cross-record identity
check lives here, in code, next to the schema check rather than inside it.

Usage:  python3 schemas/validate.py [--patent-id ID]
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline_context import ContextError, OUTPUT, resolve_patent_id, shown

HERE = Path(__file__).resolve().parent
# The run's output, NOT `HERE.parent / "output"`. Code moved under pipeline/ and
# data under runs/<id>/, and the old expression kept resolving to a directory that
# no longer exists. It did not error: every artifact read as "not produced yet",
# the identity check ran over zero records and announced that all of them were
# about the right patent, and the whole script exited 0. See MISSING below and
# contracts/GUARDS-THAT-PASS-ON-ABSENCE.md form 11.
OUT = OUTPUT
PAIRS = [("00-sections.json", "sections.schema.json"),
         ("compounds.json", "compounds.schema.json"),
         ("reactions.json", "reactions.schema.json"),
         ("pathways.json", "pathways.schema.json"),
         ("patent.json", "patent.schema.json")]

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("pip install jsonschema")

try:
    PATENT_ID = resolve_patent_id()
except ContextError as e:
    sys.exit(f"FAIL  {e}")

bad = 0
missing: list[str] = []
for art, sch in PAIRS:
    a = OUT / art
    if not a.exists():
        print(f"  {art:22} MISSING")
        missing.append(art)
        continue
    v = Draft202012Validator(json.loads((HERE / sch).read_text()))
    errs = sorted(v.iter_errors(json.loads(a.read_text())), key=lambda e: list(e.path))
    print(f"  {art:22} {'ok' if not errs else f'{len(errs)} violations'}")
    for e in errs[:15]:
        print(f"      {'.'.join(str(p) for p in e.path) or '<root>'}: {e.message[:110]}")
    bad += len(errs)

# ---------------------------------------------------------------- the input
# The biblio is an input rather than an artifact, and the runner checks it before
# any stage runs. Checked here too so that running this script standalone covers
# every schema the pack has, not just the ones downstream of finalise.
from pipeline_context import validate_biblio
biblio_problems = validate_biblio(PATENT_ID)
print(f"  {'biblio (input)':22} {'ok' if not biblio_problems else f'{len(biblio_problems)} violations'}")
for x in biblio_problems[:10]:
    print(f"      {x}")
bad += len(biblio_problems)

# ---------------------------------------------------------------- identity
# Every record must be about the patent this run is about, and about the same
# patent as every other record. No schema expresses this.
scope = 0
checked = 0
patent = None
if (OUT / "patent.json").exists():
    patent = json.loads((OUT / "patent.json").read_text())
    if patent.get("patent_id") != PATENT_ID:
        print(f"  patent.json            patent_id is {patent.get('patent_id')!r}, "
              f"this run is {PATENT_ID!r}")
        scope += 1

for art in ("compounds.json", "reactions.json", "pathways.json"):
    a = OUT / art
    if not a.exists():
        continue
    recs = json.loads(a.read_text())
    checked += len(recs) if isinstance(recs, list) else 0
    ids = sorted({r.get("patent_id") for r in recs if isinstance(r, dict)} - {None})
    wrong = [i for i in ids if i != PATENT_ID]
    if wrong:
        n = sum(1 for r in recs if r.get("patent_id") in wrong)
        print(f"  {art:22} {n} of {len(recs)} records carry patent_id "
              f"{', '.join(wrong)}, this run is {PATENT_ID!r}")
        scope += 1
    # a record whose id is built from one patent and whose patent_id is another is
    # the exact chimera this check exists to catch, so say it in those words
    for r in recs if isinstance(recs, list) else []:
        rid, rpid = r.get("id"), r.get("patent_id")
        if isinstance(rid, str) and isinstance(rpid, str) and not rid.startswith(rpid):
            print(f"  {art:22} id {rid[:60]!r} is not built from its own "
                  f"patent_id {rpid!r}")
            scope += 1
            break

if scope:
    print(f"  {'patent identity':22} {scope} violations")
else:
    # "every record is about the right patent" over ZERO records is the sentence
    # this check must never be allowed to print. Say the count, always, so that a
    # green line cannot mean "there was nothing to look at".
    print(f"  {'patent identity':22} ok, all {checked} record(s) are about {PATENT_ID}")

if missing:
    print(f"\nFAIL  {len(missing)} artifact(s) not present, so nothing validated them:")
    for art in missing:
        print(f"        {shown(OUT / art)}")
    print("      An artifact that is absent has not passed. Run finalise first,\n"
          "      or pass --allow-missing if you are deliberately validating a\n"
          "      partial run.")

sys.exit(1 if bad or scope or (missing and "--allow-missing" not in sys.argv) else 0)
