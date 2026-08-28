#!/usr/bin/env python3
"""Scaffold the run directory for a patent nobody has annotated yet.

    python3 pipeline/new_run.py US8309769B2

A run is `runs/<PATENT_ID>/`, and the id is the only thing that decides where it
lands, so two people working two patents in one checkout cannot collide. This
script creates that directory, writes the three hand-authored inputs as stubs
with their instructions inline, and then prints what a human still owes before
`run_pipeline.py` can do anything.

It refuses to touch a run that already exists. Overwriting somebody's curated
structures with an empty stub is silent, expensive and unrecoverable, and it is
exactly the kind of thing a scaffolder is tempted to do "helpfully".

What it deliberately does NOT do
--------------------------------
It does not download the PDF and it does not guess the bibliographic record.
Both are judgement: which of several publications in a family you actually want,
and whether the English title on the record is a translation or a mistranslation.
CN104292137A's own biblio carries a `title_en_note` explaining that Google's
English title names a different herbicide. A scaffolder that filled that field in
from an API would have written the wrong name and nothing would have said so.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pipeline_context import RUNS, shown

HERE = Path(__file__).resolve().parent
REFERENCE = "CN104292137A"

BIBLIO_STUB = {
    "_readme": [
        "Hand-authored. Every field below is required; grant_date may be null but",
        "the key must be present, because an application that was never granted is",
        "a fact worth stating rather than a field worth forgetting.",
        "",
        "title_en is the field most likely to be wrong. Machine translation of a",
        "Chinese chemical title routinely names a real and DIFFERENT compound. If",
        "the source's English title disagrees with the Chinese, follow the Chinese",
        "and record why in title_en_note.",
        "",
        "Delete this _readme block once the record is filled in.",
    ],
    "patent_id": "",
    "family_id": "",
    "title_en": "",
    "application_number": "",
    "publication_number": "",
    "publication_date": "",
    "priority_date": "",
    "filing_date": "",
    "grant_date": None,
    "jurisdiction": "",
    "language": "",
    # type must be one of the schema's six: multinational_corp, sme, university,
    # government, individual, consortium. It used to be pre-filled "company",
    # which is not one of them, so every new run started from a value that fails
    # validation. It never fired on the reference run, whose assignee is a
    # university.
    "assignees": [{"name": "", "country": "", "type": ""}],
    "inventors": [],
    "legal_status": "",
    "source": "",
    "retrieved": "",
}


def stub_from_reference(name: str, keep: tuple[str, ...]) -> dict:
    """An empty curated file that still carries the reference run's instructions.

    The `_readme` blocks in structures-curated.json and translations-curated.json
    are forty and sixty lines of hard-won rules about how to author an entry. A
    fresh stub without them is a file whose format nobody can guess, so they are
    copied across and everything patent-specific is dropped.
    """
    ref = RUNS / REFERENCE / "input" / name
    out: dict = {}
    if ref.exists():
        src = json.loads(ref.read_text(encoding="utf-8"))
        if "_readme" in src:
            out["_readme"] = src["_readme"]
    out["patent_id"] = ""
    for k in keep:
        out[k] = [] if k == "no_structure_needed" else {}
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(args) != 1:
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
        return 2
    pid = args[0]

    run = RUNS / pid
    if run.exists():
        print(f"FAIL  {shown(run)} already exists. Refusing to touch it.\n"
              f"      Delete it yourself if you really mean to start over.",
              file=sys.stderr)
        return 1

    for d in ("input/pdf", "input/pages", "input/vision", "output"):
        (run / d).mkdir(parents=True)

    biblio = dict(BIBLIO_STUB, patent_id=pid)
    (run / "input" / f"{pid}-biblio.json").write_text(
        json.dumps(biblio, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for name, keep in (("structures-curated.json", ("no_structure_needed", "entries")),
                       ("translations-curated.json", ("entries",))):
        d = stub_from_reference(name, keep)
        d["patent_id"] = pid
        (run / "input" / name).write_text(
            json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"created {shown(run)}/\n")
    print("What you owe before the pipeline can run:\n")
    print(f"  1. the PDF            -> {shown(run)}/input/pdf/{pid}.pdf")
    print(f"     From Google Patents. Check whether it has a text layer before you")
    print(f"     assume it needs the vision pass; a US or EP patent usually does and")
    print(f"     reading its pixels is the wrong tool.\n")
    print(f"  2. the biblio         -> {shown(run)}/input/{pid}-biblio.json")
    print(f"     Filled in by hand. Read the _readme in it first.\n")
    print(f"  3. the rendered pages -> python3 pipeline/render_pages.py --patent-id {pid}\n")
    print(f"  4. the LLM passes     -> python3 pipeline/run_pipeline.py --patent-id {pid}")
    print(f"     It will stop and tell you which passes are missing, which prompt")
    print(f"     produces each, and where the result must land.\n")
    print(f"  5. the two gates      -> structures-curated.json and translations-curated.json")
    print(f"     Both start empty. The pipeline stops at each gate and prints exactly")
    print(f"     which entries it still needs, as a stub ready to paste.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
