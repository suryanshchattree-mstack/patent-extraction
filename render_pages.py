#!/usr/bin/env python3
"""Render every page of the patent PDF to PNG, which is the first physical step.

PIPELINE.md used to give this as a `pdftoppm -r 200 -png ...` one-liner. That is a
fine command and it is not installed here, which was found by following the document
on a clean pack: the very first command of the very first step is `command not found`
and the document offers no alternative and never mentions installing poppler.

It was also unnecessary. This pack already depends on PyMuPDF, because svg2jpg.py
cannot rasterise a diagram without it, so the dependency to do this was already
present and already required.

Pass V reads these pixels. It is worth checking, rather than assuming, that there is
nothing else to read: a CNIPA scan usually has no text layer at all, but a US or EP
patent is normally born digital and carries its full text, in which case reading
pixels is the wrong tool and the operator should know before they start.

Usage:  python3 render_pages.py [--patent-id ID] [--dpi N]
"""

from __future__ import annotations

import sys
from pathlib import Path

from pipeline_context import ContextError, resolve_patent_id, strip_patent_args

HERE = Path(__file__).resolve().parent


def main() -> int:
    try:
        pid = resolve_patent_id()
    except ContextError as e:
        print(f"FAIL  {e}", file=sys.stderr)
        return 2
    args = strip_patent_args(sys.argv[1:])
    dpi = 200
    if "--dpi" in args:
        dpi = int(args[args.index("--dpi") + 1])

    try:
        import pymupdf
    except ImportError:
        print("FAIL  PyMuPDF is required:  python3 -m pip install --user pymupdf\n"
              "      (or, if you have poppler:  "
              f"pdftoppm -r {dpi} -png input/pdf/{pid}.pdf input/pages/p)",
              file=sys.stderr)
        return 2

    pdf = HERE / "input" / "pdf" / f"{pid}.pdf"
    if not pdf.exists():
        print(f"FAIL  {pdf.relative_to(HERE)} not found.\n"
              f"      Download it from Google Patents or the issuing office; no login\n"
              f"      and no paid source is needed.", file=sys.stderr)
        return 2

    out = HERE / "input" / "pages"
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    chars = 0
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=dpi).save(out / f"p{i:02d}.png")
        chars += len(page.get_text().strip())

    print(f"patent    : {pid}")
    print(f"rendered  : {doc.page_count} pages at {dpi} dpi -> "
          f"{out.relative_to(HERE)}/p01.png ...")
    if chars == 0:
        print(f"text layer: none, 0 characters across {doc.page_count} pages. Pass V "
              f"is the only way to read this document.")
    else:
        print(f"text layer: {chars:,} characters ARE extractable from this PDF.\n"
              f"            Pass V still reads the drawings, which no text layer\n"
              f"            carries, but this document is not the pixels-only case\n"
              f"            the V prompt describes. Read that prompt with that in mind.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
