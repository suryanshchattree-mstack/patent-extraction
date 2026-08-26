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
from pipeline_context import ContextError, resolve_patent_id

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "output"
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
for art, sch in PAIRS:
    a = OUT / art
    if not a.exists():
        print(f"  {art:22} not produced yet")
        continue
    v = Draft202012Validator(json.loads((HERE / sch).read_text()))
    errs = sorted(v.iter_errors(json.loads(a.read_text())), key=lambda e: list(e.path))
    print(f"  {art:22} {'ok' if not errs else f'{len(errs)} violations'}")
    for e in errs[:15]:
        print(f"      {'.'.join(str(p) for p in e.path) or '<root>'}: {e.message[:110]}")
    bad += len(errs)

# ---------------------------------------------------------------- identity
# Every record must be about the patent this run is about, and about the same
# patent as every other record. No schema expresses this.
scope = 0
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

print(f"  {'patent identity':22} "
      f"{'ok, every record is about ' + PATENT_ID if not scope else f'{scope} violations'}")
sys.exit(1 if bad or scope else 0)
