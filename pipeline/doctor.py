#!/usr/bin/env python3
"""Check this machine can actually run the pipeline, before anyone spends a day on it.

    python3 pipeline/doctor.py

Every failure here is one somebody would otherwise hit several hours in, after
the expensive part. The vision pass is 9 agent invocations and the extraction
passes another 18; discovering that RDKit will not import at the structures gate
means all 27 were spent before anything said so.

Reports every problem it finds rather than stopping at the first, because
"install this, run again, install the next one" is four round trips for what is
one message.

Exit 0 when the pipeline can run, 1 when it cannot.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# Only what a stage actually imports. Checked by importing rather than by reading
# requirements.txt, because a satisfied requirements file and a working import are
# different claims and it is the second one that matters.
NEEDED = [
    ("pymupdf", "render_pages.py cannot turn the PDF into page images",
     "python3 -m pip install pymupdf"),
    ("rdkit", "no structure resolution, no molecular formula, no drawings",
     "python3 -m pip install rdkit"),
    ("jsonschema", "no artifact validation and no biblio contract",
     "python3 -m pip install jsonschema"),
    ("numpy", "make_visual_evidence.py cannot build the page crops",
     "python3 -m pip install numpy"),
]

OK, BAD = "  ok  ", "  FAIL"


def main() -> int:
    problems: list[str] = []
    print(f"python  {sys.version.split()[0]}  ({sys.executable})")
    if sys.version_info < (3, 12):
        problems.append(f"Python {sys.version_info.major}.{sys.version_info.minor} "
                        f"is too old. The pipeline is written against 3.12.")
        print(f"{BAD}  need 3.12 or newer")
    else:
        print(f"{OK}  3.12 or newer")

    print("\nimports")
    for mod, why, fix in NEEDED:
        try:
            importlib.import_module(mod)
            print(f"{OK}  {mod}")
        except Exception as e:                       # noqa: BLE001 - any import failure counts
            print(f"{BAD}  {mod}: {type(e).__name__}")
            problems.append(f"{mod} does not import, so {why}.\n        Fix: {fix}")

    print("\nnetwork")
    # One stage needs it and only on a cold cache, so this is a warning and never
    # a failure. Somebody on a train can still do everything except resolve_names.
    try:
        import urllib.request
        urllib.request.urlopen("https://opsin.ch.cam.ac.uk/opsin/water", timeout=8).read(64)
        print(f"{OK}  OPSIN reachable")
    except Exception:                                # noqa: BLE001
        print("  warn  OPSIN not reachable. resolve_names.py is the second reader")
        print("        and needs it once per patent; every answer is then cached in")
        print("        the run's input/opsin-cache.json. Everything else works offline.")

    print("\nruns")
    runs = sorted(d.name for d in (REPO / "runs").iterdir()
                  if d.is_dir() and (d / "input").is_dir()) if (REPO / "runs").is_dir() else []
    if not runs:
        problems.append("no runs under runs/. Expected at least the reference run,\n"
                        "        CN104292137A. Is this a complete clone?")
        print(f"{BAD}  none found")
    else:
        for r in runs:
            print(f"{OK}  {r}")

    # The reference run is the worked example everything else is checked against.
    # If it does not validate on this machine, nothing produced here can be trusted
    # either, and that is worth knowing in the first minute rather than the last.
    if "CN104292137A" in runs:
        print("\nthe reference run validates")
        r = subprocess.run(
            [sys.executable, str(HERE / "schemas" / "validate.py"),
             "--patent-id", "CN104292137A"],
            capture_output=True, text=True)
        if r.returncode == 0:
            print(f"{OK}  schemas and patent identity")
        else:
            print(f"{BAD}  validate.py exited {r.returncode}")
            for line in (r.stdout + r.stderr).strip().splitlines()[-6:]:
                print(f"        {line}")
            problems.append("the reference run does not validate on this machine.\n"
                            "        Something is wrong with the clone or the environment,\n"
                            "        not with your patent. Raise it rather than working around it.")

    print()
    if problems:
        print(f"{len(problems)} problem(s) to fix before starting:\n")
        for i, p in enumerate(problems, 1):
            print(f"  {i}. {p}\n")
        return 1
    print("Ready. Claim a patent in TARGETS.md, then run:  /run-pipeline <PATENT_ID>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
