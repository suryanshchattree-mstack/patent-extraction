#!/usr/bin/env python3
"""Rasterise an SVG to JPG.

No cairo and no ImageMagick on this machine, so PyMuPDF does the work: it converts
the SVG to a one-page PDF and renders that.

One wrinkle worth knowing. Our SVGs carry `width="100%"` with no height, which is
what makes them scale in markdown and in a browser, but PyMuPDF reads width/height
to size the page and falls back to a default when they are relative. The result is
the drawing pinned to the top-left of an A4 page with the right-hand side cropped.
So the root attributes are rewritten to the viewBox's own dimensions before
conversion. The file on disk is untouched; only the copy handed to the converter
changes.

usage:  python3 svg2jpg.py [--dpi N] [--quality Q] file.svg [file.svg ...]
        python3 svg2jpg.py --all          # every svg in svg/
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent


def fix_root(svg: str) -> tuple[str, float, float]:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        raise SystemExit("no viewBox on the root element")
    w, h = float(m.group(1)), float(m.group(2))
    # replace a relative width, and add the height PyMuPDF needs
    svg = re.sub(r'\swidth="[^"]*"', "", svg, count=1)
    svg = svg.replace("<svg ", f'<svg width="{w}" height="{h}" ', 1)
    return svg, w, h


def convert(path: Path, dpi: int, quality: int) -> Path:
    svg, w, h = fix_root(path.read_text())
    doc = pymupdf.open(stream=svg.encode(), filetype="svg")
    pdf = pymupdf.open("pdf", doc.convert_to_pdf())
    pix = pdf[0].get_pixmap(dpi=dpi, alpha=False)
    out = path.with_suffix(".jpg")
    pix.pil_save(out, format="JPEG", quality=quality, optimize=True)
    print(f"  {path.name:30} {w:.0f}x{h:.0f} pt  ->  {out.name:30} "
          f"{pix.width}x{pix.height} px  {out.stat().st_size / 1024:.0f} KB")
    return out


def main() -> int:
    args = sys.argv[1:]
    dpi, quality = 200, 92
    if "--dpi" in args:
        i = args.index("--dpi"); dpi = int(args[i + 1]); del args[i:i + 2]
    if "--quality" in args:
        i = args.index("--quality"); quality = int(args[i + 1]); del args[i:i + 2]
    if "--all" in args:
        files = sorted((HERE / "svg").glob("*.svg"))
    else:
        # accept a bare filename and look in svg/ before giving up
        files = []
        for a in args:
            p = Path(a)
            files.append(p if p.exists() else HERE / "svg" / p.name)
    if not files:
        raise SystemExit(__doc__)
    print(f"rasterising at {dpi} dpi, quality {quality}:")
    for f in files:
        convert(f, dpi, quality)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
