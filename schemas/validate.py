#!/usr/bin/env python3
"""Validate the finalised artifacts against schemas/*.schema.json.

Needs jsonschema:  pip install jsonschema
Run after finalise.py. Exits non-zero on any violation.
"""
import json, sys
from pathlib import Path

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
sys.exit(1 if bad else 0)
