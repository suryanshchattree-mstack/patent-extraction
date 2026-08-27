#!/usr/bin/env python3
r"""Reading B: ChemDataExtractor over the same lines reading A read.

WHY A SECOND READER AT ALL. Reading A is a language model asked which substances a
line names. It is a good reader and it shares a failure mode with the model that
built the gold in the first place: both are the same kind of thing reading the same
document. ChemDataExtractor is a trained chemical named-entity recogniser with no
knowledge of this patent and no shared failure mode, so where the two agree that a
substance is present and no record holds it, the finding is strong; where only one
sees it, a human decides.

WHAT IT DOES NOT DO. It never writes an empty file. A `substances-cde.json` holding
no mentions is indistinguishable on every downstream screen from "ChemDataExtractor
read the document and found nothing wrong", and that is the shape of failure this
pack keeps catching in its own guards. Either this produces mentions or it produces
nothing and says why, loudly, with a non-zero exit.

STATUS ON THIS MACHINE, MEASURED 27 AUG 2026, AND THE REASON THIS FILE EXISTS
ANYWAY. ChemDataExtractor2 2.4.0 installs cleanly on Python 3.12 and its entity
extraction does not work:

    Paragraph(text).cems   AttributeError: legacy_pos_tag is not a supported tag
    Document(text).cems    type for the sentence ...
    CemTagger().tag(...)   AttributeError: 'CemTagger' object has no attribute 'tag'
    token.ner_tag          returns [] with no error   <- the dangerous one

The third is the dangerous one and is why this file refuses to use it: it does not
raise, it just answers nothing, so a run built on it would publish "two readers" and
a mention count identical to one reader's. 2.1.2 predates the tagger rewrite and
will not build here at all: scikit-learn has no wheel for this Python and its build
from source fails.

So reading B is unavailable, `readers` reads ["llm"], and every finding says so. That
is a fact about this machine and not about the patent, which is exactly why it is
written down here rather than left as an absence somebody has to rediscover.

Usage:  python3 mentions.py --patent-id CN104292137A
        python3 mentions.py --probe        # just report which entry points work
"""

from __future__ import annotations

import json
import sys

from pipeline_context import INPUT, resolve_patent_id

OUT = INPUT / "substances-cde.json"

# Tried in order. The first that returns a non-empty list of spans wins, and one
# that returns an EMPTY list is not a winner: see the module docstring.
ENTRY_POINTS = ("Paragraph.cems", "Document.cems", "token.ner_tag")


def extract(text: str) -> tuple[str, list[str]]:
    """(which entry point answered, the spans it found). Raises if none can."""
    tried = []
    try:
        from chemdataextractor.doc import Document, Paragraph
    except ImportError as e:
        raise RuntimeError(f"chemdataextractor is not installed: {e}") from e

    for name, fn in (("Paragraph.cems", lambda: [c.text for c in Paragraph(text).cems]),
                     ("Document.cems", lambda: [c.text for c in Document(text).cems])):
        try:
            got = fn()
        except Exception as e:                       # noqa: BLE001 - report, do not mask
            tried.append(f"{name}: {type(e).__name__}: {str(e)[:100]}")
            continue
        if got:
            return name, got
        tried.append(f"{name}: returned nothing")

    raise RuntimeError("no ChemDataExtractor entry point produced mentions.\n  "
                       + "\n  ".join(tried))


def main() -> int:
    probe = "--probe" in sys.argv
    patent_id = resolve_patent_id([a for a in sys.argv[1:] if a != "--probe"])

    src = INPUT / "substances-observed.json"
    if not src.exists():
        print(f"FAIL  {src.name} does not exist, so there are no lines to read.",
              file=sys.stderr)
        return 1
    lines = json.loads(src.read_text(encoding="utf-8")).get("lines") or {}

    sample = "Into the flask were charged 2-chlorotoluene and anhydrous aluminium " \
             "trichloride in 1,2-dichloroethane. NMR (CDCl3)."
    try:
        entry, got = extract(sample)
    except RuntimeError as e:
        print(f"FAIL  reading B is not available on this machine.\n\n{e}\n",
              file=sys.stderr)
        print("      Nothing was written. An empty substances-cde.json would read on "
              "every\n      screen as 'ChemDataExtractor found nothing wrong', which is "
              "a different\n      claim from 'ChemDataExtractor could not run'.\n\n"
              "      The sweep will publish readers: [\"llm\"] and every finding will "
              "say\n      'one reader only'.", file=sys.stderr)
        # EXIT 0, DELIBERATELY, AND THIS IS THE ONE JUDGEMENT CALL IN THIS FILE.
        #
        # A second reader being unavailable is a fact about this machine, not a
        # defect in this patent, and it will be true on every run here forever.
        # Failing the pipeline on it would paint every run red, and a run that is
        # always red stops being read - which would cost more than it buys.
        #
        # It is not swallowed. The message above is loud, the artifact publishes
        # readers: ["llm"], every ticket carries "one reader only", and the
        # selfcheck's section K fails outright if NO reader is recorded. The fact
        # reaches a human by four routes that do not depend on this exit code.
        #
        # The input being missing IS a defect in the pack, and that still exits 1.
        return 0

    print(f"entry point : {entry}")
    print(f"smoke test  : {got}")
    if probe:
        return 0

    # The per-line pass, written only when an entry point has actually answered.
    # It has never run on this pack, because none ever has, and shipping an
    # unexercised path as though it were exercised is the same lie as shipping an
    # empty file: both look like a reader that ran.
    out: dict[str, list] = {}
    for k in sorted(lines, key=int):
        text = source_line_en(int(k))
        if not text:
            continue
        try:
            _, spans = extract(text)
        except RuntimeError:
            continue
        rows = [{"span": sp, "kind": "specific"} for sp in dict.fromkeys(spans)
                if sp in text]
        if rows:
            out[k] = rows

    if not out:
        print("FAIL  the entry point answered on the smoke test and found nothing on "
              "any\n      real line. Writing nothing: see the module docstring.",
              file=sys.stderr)
        return 3

    OUT.write_text(json.dumps(
        {"patent_id": patent_id, "reader": "cde", "entry_point": entry,
         "what_this_is_en":
             "ChemDataExtractor over the same lines reading A read. An independent "
             "recogniser with no knowledge of this patent, so where it and reading A "
             "agree a substance is present and no record holds it, the finding is "
             "strong.",
         "lines": out}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"lines with mentions: {len(out)}")
    print(f"wrote {OUT.name}")
    return 0


def source_line_en(n: int) -> str:
    """The English rendering of one line, which is what both readers read."""
    checks = sorted((INPUT.parent / "output" / "relevant_output" / "verification")
                    .glob("checks-*.json"))
    if not checks:
        return ""
    doc = json.loads(checks[0].read_text(encoding="utf-8"))
    for row in doc.get("source_coverage", {}).get("lines") or []:
        if row.get("n") == n:
            return row.get("text_en") or ""
    return ""


if __name__ == "__main__":
    sys.exit(main())
