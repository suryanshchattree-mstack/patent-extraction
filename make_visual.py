#!/usr/bin/env python3
"""Visual evidence: put our structure next to the one the patent actually drew.

A reviewer who does not know chemistry cannot check a SMILES string. They can look at
two drawings side by side and say whether they are the same molecule, and that single
question catches the failure this whole annotation pack is exposed to: a vision pass
that read a drawing and wrote down the wrong compound. Everything here exists to put
that pair of pictures in front of them, plus the page the picture came from, plus the
places the patent's own drawing and the patent's own text already disagree.

Three artifacts, in the order they are worth:

1. `page-index.json` - the reviewer can reach the scanned page behind ANY claim, keyed
   by source line number and by paragraph marker. The page image is the ground truth
   and until now nothing surfaced it.
2. `comparisons/` and `crops/` - for each drawing in the patent, our RDKit rendering of
   the gold SMILES beside the region of the page where that structure is printed.
3. `drawing-claims.json` - the 41 drawing-versus-text conflicts the vision pass found
   and nothing has ever read, as tier-1 review claims.

## How the crop is located, and why it can be trusted

The PDF is a pure scan: nine page images, no text layer, so pymupdf offers no string
coordinates and there is no OCR in this environment. The crop is therefore found from
the ink itself, by a segmentation that is checked against something it did not produce:

* Rows of the binarised page are grouped into bands. Body text on this document sets a
  31 px band on a 50 px pitch; every structure drawing is a band of 145 px or more.
  Bands are grouped into a drawing when no text band separates them, which is what
  merges the four printed rows of a wrapped reaction scheme into the one scheme it is.
* Paragraph markers are found the same way. A paragraph starts with `[00NN]` at the
  left margin followed by white space, which no continuation line does.
* The two are then cross-checked. The vision pass independently recorded how many
  drawings each page carries and which two paragraph markers each one sits between.
  A crop is `exact` only when the detected band count matches the declared drawing
  count AND the band falls between the y positions of the two declared markers. Both
  numbers come from a source that never saw this segmentation.

Where that check does not close, the crop widens to the whole region between the two
markers and is labelled `coarse`, in English, on the asset itself. That direction is
deliberate: a crop that shows too much wastes the reviewer's time, a crop that shows
too little shows them a different molecule and invites them to reject a correct
extraction. Only the second one is dangerous.

Offline, deterministic, and it writes nothing outside output/relevant_output/visual/.

    python3 make_visual.py --patent-id CN104292137A
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from rdkit import Chem, RDLogger
from rdkit.Chem.Draw import rdMolDraw2D

import pipeline_context as ctx
import visual_text

RDLogger.DisableLog("rdApp.*")

HERE = Path(__file__).resolve().parent
INPUT = HERE / "input"
OUTPUT = HERE / "output"
REL = OUTPUT / "relevant_output"
VISUAL = REL / "visual"

ENGINE_VERSION = 1

# ---------------------------------------------------------------- page geometry
# All in pixels of the supplied 1653 x 2339 scans, but expressed as fractions of page
# height or width wherever a second patent might be scanned at another resolution.
INK_LEVEL = 200          # 8-bit grey below this counts as ink
MIN_ROW_INK = 3          # pixels of ink before a row counts as inked, kills scan speckle
BAND_GAP_FRAC = 0.0035   # vertical white run that still belongs to one band (~8 px)
DRAWING_H_FRAC = 0.025   # band this tall is a drawing, not a line of type (~59 px)
DRAWING_MIN_DENSITY = 15 # ink pixels per row; below this it is margin text, not a drawing
HEADER_FRAC = 0.068      # running header, excluded (~159 px)
FOOTER_FRAC = 0.915      # page number, excluded (~2140 px)
MARGIN_TOL_FRAC = 0.0025 # how far a line may start from the modal left margin (~4 px)
MARKER_GAP_FRAC = 0.024  # white run after the marker token (~40 px)
PAD_FRAC = 0.010         # padding around a crop (~23 px vertically)

# ---------------------------------------------------------------- asset layout
PANEL_W = 620
GUTTER = 26
EDGE = 26
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Verdana.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
FONT_BOLD_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

INK = (17, 17, 17)
PAPER = (255, 255, 255)
RULE = (140, 140, 140)
WASH = (243, 243, 243)


# ====================================================================== geometry

class Page:
    """One scanned page, segmented into bands of ink."""

    def __init__(self, path: Path, page_id: str):
        self.path = path
        self.page_id = page_id
        img = Image.open(path).convert("L")
        self.width, self.height = img.size
        self.ink = np.asarray(img) < INK_LEVEL
        self.row_ink = self.ink.sum(axis=1)
        self._bands = self._segment()
        self.text_bands = [b for b in self._bands if not self._is_drawing(b)]
        self.margin, self.token_w = self._left_geometry()
        self.marker_bands = self._marker_bands()
        self.drawing_bands = self._drawing_bands()

    # ------------------------------------------------------------- segmentation
    def _segment(self) -> list[tuple[int, int]]:
        gap = max(1, round(self.height * BAND_GAP_FRAC))
        inked = self.row_ink >= MIN_ROW_INK
        out, i, n = [], 0, len(inked)
        while i < n:
            if not inked[i]:
                i += 1
                continue
            j = k = i
            while j < n:
                if inked[j]:
                    k, j = j, j + 1
                    continue
                m = j
                while m < n and not inked[m]:
                    m += 1
                if m - j <= gap and m < n:
                    j = m
                else:
                    break
            out.append((i, k + 1))
            i = k + 1
        return out

    def _is_drawing(self, band: tuple[int, int]) -> bool:
        y0, y1 = band
        if y1 - y0 < self.height * DRAWING_H_FRAC:
            return False
        # A tall band of very sparse ink is the publication number set vertically up
        # the margin of the front page, not a structure.
        return self.row_ink[y0:y1].mean() >= DRAWING_MIN_DENSITY

    def _in_body(self, band: tuple[int, int]) -> bool:
        return (band[0] >= self.height * HEADER_FRAC
                and band[0] <= self.height * FOOTER_FRAC)

    def x_extent(self, y0: int, y1: int) -> tuple[int, int] | None:
        nz = np.nonzero(self.ink[y0:y1].sum(axis=0))[0]
        return (int(nz[0]), int(nz[-1]) + 1) if len(nz) else None

    # ------------------------------------------------------------ left geometry
    def _left_geometry(self) -> tuple[int, int]:
        """Modal left margin, and the width of the `[00NN]` token printed against it."""
        lefts: dict[int, int] = {}
        for y0, y1 in self.text_bands:
            ext = self.x_extent(y0, y1)
            if ext:
                lefts[ext[0]] = lefts.get(ext[0], 0) + 1
        if not lefts:
            return 0, 0
        margin = max(sorted(lefts), key=lambda x: (lefts[x], -x))
        tol = max(1, round(self.width * MARGIN_TOL_FRAC))
        want = max(1, round(self.width * MARKER_GAP_FRAC))
        offsets: dict[int, int] = {}
        for y0, y1 in self.text_bands:
            ext = self.x_extent(y0, y1)
            if not ext or abs(ext[0] - margin) > tol:
                continue
            cols = self.ink[y0:y1].sum(axis=0)[margin:margin + 5 * want]
            run = 0
            for idx, v in enumerate(cols):
                if v == 0:
                    run += 1
                    continue
                if run >= want:
                    offsets[idx - run] = offsets.get(idx - run, 0) + 1
                    break
                run = 0
        token = max(sorted(offsets), key=lambda x: (offsets[x], -x)) if offsets else 0
        return margin, token

    def _marker_bands(self) -> list[tuple[int, int]]:
        """Bands that open with a paragraph marker: token at the margin, then white."""
        if not self.token_w:
            return []
        tol = max(1, round(self.width * MARGIN_TOL_FRAC))
        want = max(1, round(self.width * MARKER_GAP_FRAC))
        out = []
        for y0, y1 in self.text_bands:
            if not self._in_body((y0, y1)):
                continue
            ext = self.x_extent(y0, y1)
            if not ext or abs(ext[0] - self.margin) > tol:
                continue
            start = self.margin + self.token_w
            # The token itself must be substantially inked, or a short continuation
            # line such as a trailing NMR fragment reads as a marker.
            if ext[1] < start - max(2, round(self.width * 0.006)):
                continue
            if self.ink[y0:y1, start:start + want].sum() == 0:
                out.append((y0, y1))
        return out

    # --------------------------------------------------------------- drawings
    def _drawing_bands(self) -> list[list[tuple[int, int]]]:
        """Tall bands, grouped so that one wrapped reaction scheme is one group."""
        groups: list[list[tuple[int, int]]] = []
        current: list[tuple[int, int]] = []
        for band in self._bands:
            if not self._in_body(band):
                continue
            if self._is_drawing(band):
                current.append(band)
            elif current:
                groups.append(current)
                current = []
        if current:
            groups.append(current)
        return [self._absorb_fragments(g) for g in groups]

    def _absorb_fragments(self, group: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Pull in the bits of the figure that sit in their own band.

        An atom label printed clear of the skeleton - the `Cl` above the ring on p06 -
        is separated from it by more white than the band segmenter tolerates and is far
        too short to be a drawing in its own right, so it is dropped and the crop cuts
        the chlorine off the molecule. That is the one failure mode that actively
        misleads: the reviewer compares our chlorinated structure against a picture with
        no chlorine in it and rejects a correct extraction.

        A band joins the figure only if it is indented well clear of the left text
        margin and sits horizontally inside the figure's own span. Body text on this
        document always starts at the margin, so no line of type can be swallowed, and
        the crop can only ever grow.
        """
        if not group:
            return group
        reach = round(self.height * 0.024)                  # about one line of type
        indent = self.margin + max(3 * self.token_w, round(self.width * 0.08))
        loose = [b for b in self._bands
                 if b not in group and self._in_body(b) and not self._is_drawing(b)]
        out = list(group)
        changed = True
        while changed:
            changed = False
            top, bottom = out[0][0], out[-1][1]
            span = [self.x_extent(a, b) for a, b in out]
            span = [s for s in span if s]
            if not span:
                break
            x0 = min(s[0] for s in span) - reach
            x1 = max(s[1] for s in span) + reach
            for band in list(loose):
                if not (top - reach <= band[1] and band[0] <= bottom + reach):
                    continue
                ext = self.x_extent(*band)
                if not ext or ext[0] < indent or ext[0] < x0 or ext[1] > x1:
                    continue
                loose.remove(band)
                out.append(band)
                out.sort()
                changed = True
        return out


# ================================================================ source mapping

PAGE_COMMENT = re.compile(r"<!--\s*page\s+(p\d+)\s*::")
NUMBERED = re.compile(r"^\s*(\d+)\s\|\s?(.*)$")
MARKER = re.compile(r"\[(\d{4})\]")


def read_numbered(path: Path) -> list[tuple[int, str]]:
    if not path.exists():
        return []
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = NUMBERED.match(raw)
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out


def line_page_map(lines: list[tuple[int, str]]) -> tuple[dict[int, str], dict[str, int]]:
    """Every source line to the scanned page it was read from, and each marker's line."""
    by_line: dict[int, str] = {}
    marker_line: dict[str, int] = {}
    page = None
    for n, text in lines:
        m = PAGE_COMMENT.search(text)
        if m:
            page = m.group(1)
        if page:
            by_line[n] = page
        for mk in MARKER.findall(text):
            marker_line.setdefault(f"[{mk}]", n)
    return by_line, marker_line


# ==================================================================== structures

class Gold:
    """The gold structure set, looked up by canonical SMILES."""

    def __init__(self, resolved: list[dict]):
        self.by_canonical: dict[str, dict] = {}
        for rec in resolved:
            smi = rec.get("smiles")
            if not smi:
                continue
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue
            self.by_canonical.setdefault(Chem.MolToSmiles(mol), rec)

    def find(self, smiles: str | None) -> dict | None:
        if not smiles:
            return None
        mol = Chem.MolFromSmiles(smiles)
        return self.by_canonical.get(Chem.MolToSmiles(mol)) if mol else None


def label_for(rec: dict) -> str:
    """A name a human can read, never a SMILES string.

    Some gold records carry a SMILES as their own identifier, because the patent drew
    the molecule and never named it. Showing that string as the caption of a picture
    would defeat the purpose of the picture.
    """
    cands = [rec.get("identifier"), *(rec.get("aliases") or [])]
    for c in cands:
        if c and Chem.MolFromSmiles(c) is None:
            return c
    svg = rec.get("svg") or ""
    stem = Path(svg).stem
    return stem.replace("-", " ") if stem else (rec.get("identifier") or "unnamed structure")


def render_structure(smiles: str, size: tuple[int, int]) -> Image.Image | None:
    """One structure, drawn the way resolve_structures.py draws them: flat black."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    drawer = rdMolDraw2D.MolDraw2DCairo(size[0], size[1])
    opts = drawer.drawOptions()
    opts.useBWAtomPalette()
    opts.bondLineWidth = 2
    opts.padding = 0.08
    opts.addStereoAnnotation = False
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
    drawer.FinishDrawing()
    return Image.open(__import__("io").BytesIO(drawer.GetDrawingText())).convert("RGB")


# ======================================================================= drawing

def load_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default(size)


class Fonts:
    def __init__(self):
        self.h1 = load_font(FONT_BOLD_CANDIDATES, 26)
        self.h2 = load_font(FONT_BOLD_CANDIDATES, 19)
        self.body = load_font(FONT_CANDIDATES, 17)
        self.small = load_font(FONT_CANDIDATES, 15)
        self.tiny = load_font(FONT_CANDIDATES, 13)
        self.name = self.__class__.__name__


def wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        words, line = para.split(), ""
        for w in words:
            trial = f"{line} {w}".strip()
            if draw.textlength(trial, font=font) <= width or not line:
                line = trial
            else:
                lines.append(line)
                line = w
        lines.append(line)
    return lines


def text_block(draw, xy, text, font, width, fill=INK, leading=5) -> int:
    x, y = xy
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + leading
    return y


def dashed_rect(draw: ImageDraw.ImageDraw, box, fill, dash=9, gap=7, width=2):
    """Dashed frame. The crop's accuracy is carried by shape as well as by words, so
    that the distinction survives a greyscale print and a colourblind reader."""
    x0, y0, x1, y1 = box
    for x in range(x0, x1, dash + gap):
        draw.line([(x, y0), (min(x + dash, x1), y0)], fill=fill, width=width)
        draw.line([(x, y1), (min(x + dash, x1), y1)], fill=fill, width=width)
    for y in range(y0, y1, dash + gap):
        draw.line([(x0, y), (x0, min(y + dash, y1))], fill=fill, width=width)
        draw.line([(x1, y), (x1, min(y + dash, y1))], fill=fill, width=width)


def fit(img: Image.Image, width: int, max_h: int) -> Image.Image:
    scale = min(width / img.width, max_h / img.height, 1.0) if img.height else 1.0
    if scale >= 1.0 and img.width <= width:
        return img
    return img.resize((max(1, round(img.width * scale)),
                       max(1, round(img.height * scale))), Image.LANCZOS)


def ours_panel(structures: list[dict], fonts: Fonts, width: int) -> Image.Image:
    """Our gold structures, numbered in the order the patent prints them."""
    cell_w = width if len(structures) == 1 else (width - GUTTER) // 2
    cell_h = 250 if len(structures) == 1 else 190
    tiles = []
    scratch = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for i, s in enumerate(structures, 1):
        cap = f"{i}. {s['label_en']}"
        cap_lines = wrap(scratch, cap, fonts.tiny, cell_w - 8)
        cap_h = len(cap_lines) * (fonts.tiny.size + 3) + 6
        tile = Image.new("RGB", (cell_w, cell_h + cap_h), PAPER)
        d = ImageDraw.Draw(tile)
        img = render_structure(s["smiles"], (cell_w - 8, cell_h - 8)) if s.get("smiles") else None
        if img is not None:
            tile.paste(img, ((cell_w - img.width) // 2, 4))
        else:
            d.text((6, cell_h // 2), "no structure available", font=fonts.small, fill=INK)
        y = cell_h + 2
        for line in cap_lines:
            d.text((4, y), line, font=fonts.tiny, fill=INK)
            y += fonts.tiny.size + 3
        tiles.append(tile)

    cols = 1 if len(structures) == 1 else 2
    rows = (len(tiles) + cols - 1) // cols
    row_h = [max(t.height for t in tiles[r * cols:(r + 1) * cols]) for r in range(rows)]
    panel = Image.new("RGB", (width, sum(row_h) + 10 * rows), PAPER)
    y = 0
    for r in range(rows):
        x = 0
        for t in tiles[r * cols:(r + 1) * cols]:
            panel.paste(t, (x, y))
            x += cell_w + GUTTER
        y += row_h[r] + 10
    return panel


def compose(item: dict, ours: Image.Image, theirs: Image.Image | None,
            fonts: Fonts) -> Image.Image:
    """The side-by-side asset. Everything the reviewer needs is on the picture."""
    exact = item["crop_confidence"] == "exact"
    scratch = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    panel_h = max(ours.height, theirs.height if theirs else 0)
    ours_f = fit(ours, PANEL_W, panel_h)
    theirs_f = fit(theirs, PANEL_W, panel_h) if theirs else None
    body_h = max(ours_f.height, theirs_f.height if theirs_f else 220)

    title = item["title_en"]
    chip = "EXACT CROP" if exact else "COARSE CROP"
    question = item["question_en"]
    note = item["crop_confidence_note_en"]

    inner = PANEL_W * 2 + GUTTER
    head_h = 34 + len(wrap(scratch, title, fonts.h1, inner)) * (fonts.h1.size + 6) + 30
    q_lines = wrap(scratch, question, fonts.h2, inner)
    n_lines = wrap(scratch, note, fonts.small, inner)
    foot_h = 18 + len(q_lines) * (fonts.h2.size + 6) + 10 + len(n_lines) * (fonts.small.size + 4) + 14

    W = inner + EDGE * 2
    H = head_h + 34 + body_h + 34 + foot_h + EDGE
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # header: title, then the accuracy chip as words inside a frame whose line style
    # repeats the same fact, so nothing is carried by colour
    y = EDGE
    chip_w = round(d.textlength(chip, font=fonts.small)) + 20
    box = (W - EDGE - chip_w, y, W - EDGE, y + fonts.small.size + 12)
    if exact:
        d.rectangle(box, outline=INK, width=2)
    else:
        dashed_rect(d, box, INK)
    d.text((box[0] + 10, y + 6), chip, font=fonts.small, fill=INK)
    y = text_block(d, (EDGE, y), title, fonts.h1, inner - chip_w - 16, leading=6)
    y += 12
    d.line([(EDGE, y), (W - EDGE, y)], fill=RULE, width=2)
    y += 22

    for idx, (panel, heading, is_exact) in enumerate((
            (ours_f, "WHAT WE EXTRACTED", True),
            (theirs_f, "WHAT THE PATENT DRAWS", exact))):
        x = EDGE + idx * (PANEL_W + GUTTER)
        d.text((x, y), heading, font=fonts.h2, fill=INK)
        top = y + fonts.h2.size + 10
        frame = (x - 6, top - 6, x + PANEL_W + 6, top + body_h + 6)
        if panel is None:
            d.rectangle(frame, fill=WASH, outline=RULE, width=2)
            text_block(d, (x + 8, top + 14),
                       "The region of the page carrying this structure could not be "
                       "located. Open the full page instead.", fonts.small, PANEL_W - 16)
        else:
            if is_exact:
                d.rectangle(frame, outline=INK, width=2)
            else:
                dashed_rect(d, frame, INK)
            img.paste(panel, (x + (PANEL_W - panel.width) // 2, top))
    y += fonts.h2.size + 10 + body_h + 28

    d.line([(EDGE, y), (W - EDGE, y)], fill=RULE, width=2)
    y += 16
    y = text_block(d, (EDGE, y), question, fonts.h2, inner, leading=6)
    y += 8
    text_block(d, (EDGE, y), note, fonts.small, inner, leading=4)
    return img


# ========================================================================= build

def digest(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:16]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: Path) -> str:
    return str(p.relative_to(HERE))


def build(patent_id: str) -> int:
    vision_dir = INPUT / "vision"
    pages_dir = INPUT / "pages"
    if not vision_dir.is_dir() or not pages_dir.is_dir():
        print(f"visual: need {rel(vision_dir)} and {rel(pages_dir)}", file=sys.stderr)
        return 2

    scrub = visual_text.load(OUTPUT / "translations.json")
    resolved = json.loads((REL / "gold" / "structures-resolved.json").read_text("utf-8"))
    gold = Gold(resolved)
    compounds = json.loads((REL / "gold" / "compounds.json").read_text("utf-8"))
    numbered = read_numbered(ctx.enriched_numbered_path(patent_id))
    line_page, marker_line = line_page_map(numbered)
    line_text = {n: t for n, t in numbered}

    fonts = Fonts()
    VISUAL.mkdir(parents=True, exist_ok=True)
    (VISUAL / "comparisons").mkdir(exist_ok=True)
    (VISUAL / "crops").mkdir(exist_ok=True)

    vision_files = sorted(vision_dir.glob("p*.json"))
    pages_out, markers_out = [], {}
    items: list[dict] = []
    discrepancies: list[dict] = []

    for vf in vision_files:
        vis = json.loads(vf.read_text("utf-8"))
        page_id = Path(vis.get("page") or vf.stem).stem
        png = pages_dir / f"{page_id}.png"
        if not png.exists():
            continue
        page = Page(png, page_id)
        doc_part = (vis.get("doc_part") or "").replace("_", " ").strip() or "unknown"

        printed = [p for p in vis.get("paragraphs") or []
                   if re.fullmatch(r"\[\d{4}\]", (p.get("marker") or "").strip())]
        aligned = len(printed) == len(page.marker_bands)
        marker_y: dict[str, tuple[int, int]] = {}
        if aligned:
            for p, band in zip(printed, page.marker_bands):
                marker_y[p["marker"].strip()] = band

        for p in printed:
            mk = p["marker"].strip()
            band = marker_y.get(mk)
            markers_out[mk] = {
                "page": page_id,
                "page_number": int(re.sub(r"\D", "", page_id) or 0),
                "y_frac": round(band[0] / page.height, 5) if band else None,
                "y_px": band[0] if band else None,
                "line": marker_line.get(mk),
                "precision": "line_located" if band else "page_only",
                "precision_note_en": (
                    "The paragraph's own line was located on the scan."
                    if band else
                    "Only the page is known. The printed markers on this page could not "
                    "be counted off against the markers the vision pass recorded, so no "
                    "line position is claimed."),
            }

        pages_out.append({
            "page": page_id,
            "page_number": int(re.sub(r"\D", "", page_id) or 0),
            "src": rel(png),
            "width": page.width,
            "height": page.height,
            "doc_part_en": doc_part,
            "printed_markers": [p["marker"].strip() for p in printed],
            "marker_positions_available": aligned,
            "marker_positions_note_en": (
                f"{len(page.marker_bands)} paragraph openings were found on the scan and "
                f"the vision pass recorded {len(printed)} printed markers for this page; "
                + ("they agree, so each marker is placed on its own line."
                   if aligned else
                   "they disagree, so no marker on this page carries a line position.")),
            "drawing_count_detected": len(page.drawing_bands),
            "drawing_count_declared": len(vis.get("drawings") or []),
        })

        items.extend(_page_items(patent_id, page, vis, marker_y, gold, scrub, doc_part))
        for i, dsc in enumerate(vis.get("discrepancies") or []):
            discrepancies.append({"page": page_id, "index": i, "doc_part_en": doc_part,
                                  "raw": dsc})

    # ---- assets
    for item in items:
        crop = None
        if item["crop_box"]:
            x0, y0, x1, y1 = item["crop_box"]
            crop = Image.open(item["page_src_abs"]).convert("RGB").crop((x0, y0, x1, y1))
            crop.save(VISUAL / "crops" / f"{item['asset_stem']}.png")
            item["crop_src"] = rel(VISUAL / "crops" / f"{item['asset_stem']}.png")
        ours = ours_panel(item["structures"], fonts, PANEL_W)
        ours.save(VISUAL / "comparisons" / f"{item['asset_stem']}.ours.png")
        item["ours_src"] = rel(VISUAL / "comparisons" / f"{item['asset_stem']}.ours.png")
        compose(item, ours, crop, fonts).save(
            VISUAL / "comparisons" / f"{item['asset_stem']}.png")
        item["composite_src"] = rel(VISUAL / "comparisons" / f"{item['asset_stem']}.png")

    # ---- claims
    claims = [structure_claim(patent_id, it) for it in items]
    claims += [discrepancy_claim(patent_id, d, items, compounds, gold, scrub,
                                 marker_line, line_text, line_page, markers_out)
               for d in discrepancies]
    claims.sort(key=lambda c: (-c["risk"], c["claim_id"]))

    stamp = _stamp(vision_files + [p for p in pages_dir.glob("p*.png")])
    source = {"pages": len(pages_out),
              "vision_files": [rel(f) for f in vision_files],
              "page_images_sha256": {p.name: sha256_file(p)[:16]
                                     for p in sorted(pages_dir.glob("p*.png"))}}

    _write(VISUAL / "page-index.json", {
        "patent_id": patent_id,
        "engine_version": ENGINE_VERSION,
        "generated_at": stamp,
        "stage": "visual",
        "pages": pages_out,
        "markers": dict(sorted(markers_out.items())),
        "lines": {str(n): pg for n, pg in sorted(line_page.items())},
        "notes_en": [
            "`lines` maps a source line number in the numbered enriched text to the "
            "scanned page it was read from. Every claim carries cited_lines, so this is "
            "the general way to reach a page image from any claim.",
            "`markers[*].y_frac` is a fraction of page height and is present only where "
            "the paragraph's own line was located on the scan.",
            "`generated_at` is the newest modification time of the inputs, not the time "
            "of the run, so two runs over the same inputs produce the same bytes.",
        ],
    })

    _write(VISUAL / "drawing-claims.json", {
        "patent_id": patent_id,
        "engine_version": ENGINE_VERSION,
        "generated_at": stamp,
        "stage": "visual",
        "source": source,
        "summary": {
            "claims_total": len(claims),
            "tier_1": sum(1 for c in claims if c["tier"] == 1),
            "structure_comparisons": len(items),
            "structure_comparisons_exact": sum(1 for i in items
                                               if i["crop_confidence"] == "exact"),
            "structure_comparisons_coarse": sum(1 for i in items
                                                if i["crop_confidence"] == "coarse"),
            "structure_comparisons_no_crop": sum(1 for i in items if not i["crop_box"]),
            "drawing_text_conflicts": len(discrepancies),
            "structures_drawn": sum(len(i["structures"]) for i in items),
            "structures_matched_to_gold": sum(
                1 for i in items for s in i["structures"] if s["gold_record_id"]),
        },
        "claims": claims,
    })

    _write(VISUAL / "glossary.json", {
        "purpose_en": "Chinese fragments this stage translated itself because "
                      "output/translations.json does not carry them. Listed so every "
                      "English word on a reviewer's screen can be traced to its source.",
        "terms": visual_text.GLOSSARY,
        "unresolved": scrub.report_with_source(),
    })

    _readme(patent_id, items, discrepancies, pages_out, scrub, stamp)
    print(f"visual: {len(items)} comparisons, {len(claims)} claims -> {rel(VISUAL)}")
    return 0


def _stamp(paths: list[Path]) -> str:
    newest = max((p.stat().st_mtime for p in paths), default=0.0)
    return dt.datetime.fromtimestamp(newest, dt.timezone.utc).isoformat(timespec="seconds")


def _write(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2, sort_keys=False) + "\n",
                    encoding="utf-8")


# ---------------------------------------------------------------- per-page items

def _page_items(patent_id, page: Page, vis: dict, marker_y: dict,
                gold: Gold, scrub, doc_part: str) -> list[dict]:
    declared = vis.get("drawings") or []
    if not declared:
        return []
    groups = page.drawing_bands
    counts_agree = len(groups) == len(declared)
    pad = max(4, round(page.height * PAD_FRAC))
    page_no = int(re.sub(r"\D", "", page.page_id) or 0)
    out = []

    for n, drawn in enumerate(declared, 1):
        between = [str(m) for m in (drawn.get("between_markers") or [])]
        span = _marker_span(between, marker_y, page)
        band = groups[n - 1] if counts_agree else None

        box, confidence, why = None, "none", ""
        if band:
            y0 = max(0, band[0][0] - pad)
            y1 = min(page.height, band[-1][1] + pad)
            xs = [page.x_extent(a, b) for a, b in band]
            xs = [x for x in xs if x]
            x0 = max(0, min(x[0] for x in xs) - pad * 2) if xs else 0
            x1 = min(page.width, max(x[1] for x in xs) + pad * 2) if xs else page.width
            box = (x0, y0, x1, y1)
            inside = span is None or (y0 >= span[0] - pad * 3 and y1 <= span[1] + pad * 3)
            if inside:
                confidence = "exact"
                why = (f"The scan was segmented into bands of ink and this crop is one "
                       f"drawing-sized band group, {band[0][0]} to {band[-1][1]} pixels "
                       f"down a {page.height} pixel page. Two independent checks agree "
                       f"with it: the page carries exactly the "
                       f"{len(declared)} drawing{'' if len(declared) == 1 else 's'} the "
                       f"vision pass recorded for it, and the band falls between the two "
                       f"paragraph markers the vision pass said this drawing sits "
                       f"between{_between_phrase(between)}.")
            else:
                confidence = "coarse"
                box = (0, max(0, span[0] - pad), page.width, min(page.height, span[1] + pad))
                why = ("The band of ink that looks like this drawing does not fall "
                       "between the two paragraph markers the vision pass said it sits "
                       f"between{_between_phrase(between)}, so the crop was widened to "
                       "the whole region between those markers. It may include "
                       "neighbouring text or a neighbouring structure.")
        elif span:
            confidence = "coarse"
            box = (0, max(0, span[0] - pad), page.width, min(page.height, span[1] + pad))
            why = (f"{len(groups)} drawing-sized band"
                   f"{'' if len(groups) == 1 else 's'} were found on this page but the "
                   f"vision pass recorded {len(declared)}, so no single band could be "
                   f"tied to this drawing. The crop is the whole region between the two "
                   f"paragraph markers it sits between"
                   f"{_between_phrase(between)}, full page width. It may include "
                   "neighbouring text or a neighbouring structure.")
        else:
            why = ("Neither a matching band of ink nor both bounding paragraph markers "
                   "could be located on the scan, so no crop is offered. The full page "
                   "image is the evidence for this drawing.")

        structures = []
        for s in drawn.get("structures") or []:
            rec = gold.find(s.get("smiles"))
            structures.append({
                "position_en": scrub.en(s.get("position_in_drawing")),
                "drawn_name_en": scrub.en(s.get("name")),
                "drawn_smiles": s.get("smiles"),
                "vision_confidence": s.get("confidence"),
                "gold_record_id": f"{patent_id}_{rec['identifier']}" if rec else None,
                "label_en": label_for(rec) if rec else scrub.en(s.get("name")),
                "smiles": (rec or {}).get("smiles") or s.get("smiles"),
                "structure_svg_path": (f"output/relevant_output/{rec['svg']}"
                                       if rec and rec.get("svg") else None),
                "in_gold": bool(rec),
            })

        one = len(structures) == 1
        out.append({
            "record_id": f"{patent_id}_drawing_{page.page_id}_{n}",
            "asset_stem": f"{patent_id}-{page.page_id}-d{n}",
            "page": page.page_id,
            "page_number": int(re.sub(r"\D", "", page.page_id) or 0),
            "page_src": rel(page.path),
            "page_src_abs": page.path,
            "page_width": page.width,
            "page_height": page.height,
            "drawing_index": n,
            "drawing_count_on_page": len(declared),
            "kind_en": scrub.en(drawn.get("kind")) or "structure",
            "between_markers": between,
            "marker": next((m for m in between if re.fullmatch(r"\[\d{4}\]", m)), None),
            "doc_part_en": doc_part,
            "structures": structures,
            "crop_box": box,
            "crop_confidence": confidence,
            "crop_confidence_note_en": why,
            "title_en": (f"Patent {patent_id}, page {page_no}"
                         f" - drawing {n} of {len(declared)}"),
            "question_en": ("Do these two pictures show the same molecule?" if one else
                            f"Do these two pictures show the same {len(structures)} "
                            "molecules, in the same order? Ours are numbered left to "
                            "right, top to bottom, in the order the patent prints them."),
        })
    return out


def _between_phrase(between: list[str]) -> str:
    marks = [m for m in between if re.fullmatch(r"\[\d{4}\]", m)]
    if len(marks) == 2:
        return f", {marks[0]} and {marks[1]}"
    if len(marks) == 1:
        return f", one of which is {marks[0]}"
    return ""


def _marker_span(between: list[str], marker_y: dict, page: Page) -> tuple[int, int] | None:
    """The vertical region between the two markers a drawing is declared to sit between.

    Either end may be missing - a scheme that runs from the top of the page has no
    marker above it - and then the page edge stands in for it.
    """
    marks = [m for m in between if re.fullmatch(r"\[\d{4}\]", m)]
    top = round(page.height * HEADER_FRAC)
    bottom = round(page.height * FOOTER_FRAC)
    if len(between) == 2 and len(marks) == 2:
        a, b = marker_y.get(marks[0]), marker_y.get(marks[1])
        if a and b:
            return (a[1], b[0])
        return None
    if len(marks) == 1 and marks[0] in marker_y:
        band = marker_y[marks[0]]
        # One marker named, and the other end of the span is a page edge. Which edge
        # depends on whether the marker was printed before or after the drawing.
        return (top, band[0]) if between and between[-1] == marks[0] else (band[1], bottom)
    return None


# ------------------------------------------------------------------- claim shapes

def _evidence(markers: list[str], marker_line, line_text, scrub) -> tuple[list[int], list[dict]]:
    lines, ev = [], []
    for mk in markers:
        n = marker_line.get(mk)
        if not n:
            continue
        lines.append(n)
        ev.append({"n": n, "text_en": scrub.en(line_text.get(n, "")), "is_translation": True})
    return lines, ev


def structure_claim(patent_id: str, it: dict) -> dict:
    field = f"__drawing_structure__:{it['page']}:d{it['drawing_index']}"
    primary = next((s for s in it["structures"] if s["in_gold"]), None) or (
        it["structures"][0] if it["structures"] else None)
    missing = [s for s in it["structures"] if not s["in_gold"]]
    reasons = []
    risk = 0.55
    if it["crop_confidence"] != "exact":
        reasons.append("The crop of the patent's own drawing is approximate, so judge it "
                       "against the full page if the two pictures disagree.")
        risk += 0.10
    if missing:
        reasons.append(f"{len(missing)} of the {len(it['structures'])} structures the "
                       "patent draws here have no matching record in our gold set.")
        risk += 0.25
    if len(it["structures"]) > 1:
        reasons.append(f"This is one scheme carrying {len(it['structures'])} structures, "
                       "so it is a longer look than a single comparison.")
        risk += 0.05
    if not reasons:
        reasons.append("Reading a drawn structure is the step in this pipeline with no "
                       "text to check it against, so it is reviewed even when nothing "
                       "else looks wrong.")

    return {
        "claim_id": digest(it["record_id"], field),
        "record_id": it["record_id"],
        "record_kind": "drawing",
        "about": "drawing",
        "record_label_en": f"Drawing {it['drawing_index']} on page {it['page']}",
        "field": field,
        "field_label_en": "Structure read off the patent's drawing",
        "question_en": it["question_en"],
        "claimed_en": "; ".join(f"{i}. {s['label_en']}"
                                for i, s in enumerate(it["structures"], 1)) or "nothing",
        "claimed_value": None,
        "claimed_unit": None,
        "cited_lines": [],
        "evidence_en": ("The patent prints this drawing on page "
                        f"{it['page']}{_between_phrase(it['between_markers'])}. The "
                        "picture on the right is that region of the scanned page."),
        "evidence_lines": [],
        "highlights": [],
        "auto": "not_checkable",
        "auto_reason_en": ("A drawn structure cannot be settled by matching strings. The "
                           "machine has put our rendering next to the patent's own "
                           "drawing so a human can settle it by looking."),
        "needs_human": True,
        "risk": round(min(risk, 0.99), 3),
        "risk_reasons_en": reasons,
        "structure_svg_path": (primary or {}).get("structure_svg_path"),
        "tier": 1,
        "stratum": f"drawing:{it['doc_part_en']}",
        "page": it["page"],
        "page_number": it["page_number"],
        "comparison": {
            "ours": {
                "src": (primary or {}).get("structure_svg_path") or it["ours_src"],
                "label_en": "What we extracted",
                "structures": [{"label_en": s["label_en"],
                                "src": s["structure_svg_path"],
                                "smiles": s["smiles"],
                                "gold_record_id": s["gold_record_id"],
                                "in_gold": s["in_gold"]} for s in it["structures"]],
                "sheet_src": it["ours_src"],
            },
            "theirs": ({
                "src": it["crop_src"],
                "label_en": "What the patent draws",
                "confidence": it["crop_confidence"],
                "confidence_note_en": it["crop_confidence_note_en"],
                "page": it["page"],
                "page_src": it["page_src"],
                "marker": it["marker"],
                "box": list(it["crop_box"]),
            } if it["crop_box"] else None),
            "composite_src": it["composite_src"],
        },
    }


_QUANT = re.compile(r"\b(mol|g\b|yield|molar mass|molecular weight|MW|%|implies)\b", re.I)


def discrepancy_claim(patent_id, d, items, compounds, gold, scrub,
                      marker_line, line_text, line_page, markers_out) -> dict:
    raw = d["raw"]
    page = d["page"]
    what = scrub.en(raw.get("what"))
    drawing_says = scrub.en(raw.get("drawing_says"))
    text_says = scrub.en(raw.get("text_says"))
    field = f"__drawing_discrepancy__:{page}:#{d['index']}"

    mentioned = sorted(set(f"[{m}]" for m in MARKER.findall(
        " ".join([raw.get("what") or "", raw.get("text_says") or "",
                  raw.get("drawing_says") or ""]))))
    lines, ev = _evidence(mentioned, marker_line, line_text, scrub)

    on_page = [it for it in items if it["page"] == page]
    related = []
    seen = set()
    for it in on_page:
        for s in it["structures"]:
            if s["gold_record_id"] and s["gold_record_id"] not in seen:
                seen.add(s["gold_record_id"])
                related.append({
                    "record_id": s["gold_record_id"],
                    "record_kind": "compound",
                    "label_en": s["label_en"],
                    "what_we_recorded_en": f"We recorded this molecule as {s['smiles']}, "
                                           f"drawn on page {page}.",
                    "structure_svg_path": s["structure_svg_path"],
                    "from_en": f"Drawing {it['drawing_index']} on page {page}",
                })

    has_drawing = bool(on_page) and not _is_text_only(raw)
    we_followed, followed_note = _we_followed(raw, has_drawing, related)

    risk = 0.60
    reasons = ["The patent's own drawing and the patent's own text disagree here, and "
               "nothing downstream has ever surfaced this conflict."]
    if has_drawing:
        risk += 0.15
        reasons.append("A drawing is involved, so the reviewer can settle it by eye "
                       "against the page image.")
    if _QUANT.search(f"{what} {text_says}"):
        risk += 0.15
        reasons.append("The conflict is arithmetic - masses, moles or a yield - so it "
                       "bears directly on numbers we recorded.")
    if not related:
        reasons.append("No gold record could be tied to this conflict automatically, so "
                       "the reviewer is deciding whether one should have been.")

    primary = related[0] if len(related) == 1 else None
    record_id = primary["record_id"] if primary else f"{patent_id}_page_{page}"

    return {
        "claim_id": digest(record_id, field),
        "record_id": record_id,
        "record_kind": "compound" if primary else "patent",
        "about": "patent",
        "record_label_en": primary["label_en"] if primary else f"Page {page}",
        "field": field,
        "field_label_en": "Conflict between the patent's drawing and the patent's text",
        "question_en": ("The patent contradicts itself here. " + what
                        + " Did we record this correctly?"),
        "claimed_en": (related[0]["what_we_recorded_en"] if related else
                       "No annotation record is tied to this conflict."),
        "claimed_value": None,
        "claimed_unit": None,
        "cited_lines": lines,
        "evidence_en": "\n".join(e["text_en"] for e in ev) if ev else
                       "The conflict is stated in full in the two quotations below.",
        "evidence_lines": ev + [
            {"n": lines[0] if lines else None, "text_en": f"The drawing says: {drawing_says}",
             "is_translation": True, "side_en": "drawing"},
            {"n": lines[0] if lines else None, "text_en": f"The text says: {text_says}",
             "is_translation": True, "side_en": "text"},
        ],
        "highlights": [],
        "auto": "not_checkable",
        "auto_reason_en": ("Two statements in the source disagree with each other. No "
                           "string match can say which one is right, so a human decides."),
        "needs_human": True,
        "risk": round(min(risk, 0.99), 3),
        "risk_reasons_en": reasons,
        "structure_svg_path": (primary or {}).get("structure_svg_path"),
        "tier": 1,
        "stratum": f"patent:{d['doc_part_en']}",
        "page": page,
        "page_number": int(re.sub(r"\D", "", page) or 0),
        "markers": mentioned,
        "disagreement": {
            "drawing_says_en": drawing_says,
            "text_says_en": text_says,
            "we_followed": we_followed,
            "we_followed_note_en": followed_note,
        },
        "related_records": related,
        "comparison": {
            "ours": ({"src": related[0]["structure_svg_path"],
                      "label_en": "What we extracted"} if related and
                     related[0]["structure_svg_path"] else None),
            "theirs": ({
                "src": on_page[0]["crop_src"],
                "label_en": "What the patent draws",
                "confidence": on_page[0]["crop_confidence"],
                "confidence_note_en": on_page[0]["crop_confidence_note_en"],
                "page": page,
                "page_src": on_page[0]["page_src"],
                "marker": on_page[0]["marker"],
            } if has_drawing and on_page[0].get("crop_src") else None),
        } if has_drawing else None,
    }


_TEXT_ONLY = re.compile(
    r"no drawing|n/a|text-internal|text-only|text-vs-text|no drawings|nothing\b",
    re.I)


def _is_text_only(raw: dict) -> bool:
    return bool(_TEXT_ONLY.search(raw.get("drawing_says") or ""))


def _we_followed(raw: dict, has_drawing: bool, related: list) -> tuple[str, str]:
    """Which side of the conflict our annotation took.

    Only claimed where it can be shown. When a drawing is involved and the structures
    on that page resolved into the gold set, the gold followed the drawing, because the
    SMILES in the gold is the one read off the drawing and it matched. Everything else
    is a judgement this stage is not entitled to make on the reviewer's behalf.
    """
    if has_drawing and related:
        return "drawing", ("Every structure drawn on this page resolved into our gold "
                           "set, so on the structural question our annotation follows "
                           "the drawing. Whether that was the right call for THIS "
                           "conflict is the question.")
    if _is_text_only(raw):
        return "text", ("There is no drawing at issue: both sides of this conflict are "
                        "prose, and our annotation was read from the prose. The reviewer "
                        "is deciding whether the right reading was taken.")
    return "unknown", ("This stage could not determine which side our annotation "
                       "followed. Read what we recorded, below, against the two "
                       "quotations.")


# ========================================================================== readme

def _readme(patent_id, items, discrepancies, pages_out, scrub, stamp) -> None:
    exact = [i for i in items if i["crop_confidence"] == "exact"]
    coarse = [i for i in items if i["crop_confidence"] == "coarse"]
    none_ = [i for i in items if not i["crop_box"]]
    rows = "\n".join(
        f"| `{i['asset_stem']}.png` | {i['page']} | {len(i['structures'])} | "
        f"{i['crop_confidence']} | {', '.join(i['between_markers']) or 'n/a'} |"
        for i in items)
    aligned = sum(1 for p in pages_out if p["marker_positions_available"])
    unresolved = scrub.report()

    (VISUAL / "README.md").write_text(f"""# Visual evidence for {patent_id}

Put our structure next to the structure the patent actually drew, and let a reviewer
who does not know chemistry answer one question by looking: **do these show the same
molecule?**

Generated by `make_visual.py --patent-id {patent_id}`. Offline, deterministic, reads
`input/` and `output/` and writes only into this directory. `generated_at` in the JSON
is the newest input modification time ({stamp}), not the clock, so a diff between two
runs means something.

## What is here

| file | what it is |
|---|---|
| `page-index.json` | source line number to page, paragraph marker to page and position, page to image and size |
| `comparisons/<id>.png` | the side-by-side asset: our structures on the left, the patent's own drawing on the right |
| `comparisons/<id>.ours.png` | just our half, if a UI wants to lay the two out itself |
| `crops/<id>.png` | just the patent's half |
| `drawing-claims.json` | {len(items)} structure comparisons and {len(discrepancies)} drawing-versus-text conflicts, as tier-1 review claims |
| `glossary.json` | every Chinese fragment this stage translated itself, and what it rendered it as |

## What is exact and what is a guess

There is no text layer in the PDF - all nine pages are scans - and no OCR in this
environment, so nothing here comes from string coordinates. Regions are found from the
ink, then checked against facts the segmentation did not produce.

**Band segmentation.** Rows of the binarised page are grouped into bands of ink. Body
text sets a 31 px band on a 50 px pitch; every structure on this document is a band of
145 px or more. Consecutive tall bands with no text between them are one drawing, which
is what makes the four printed rows of the wrapped scheme on p06 a single scheme.

**Paragraph markers.** A paragraph opens with `[00NN]` at the left margin followed by
white space; no continuation line does that. On {aligned} of the {len(pages_out)} pages
the number of openings found equals the number of markers the vision pass recorded, and
on those pages each marker carries a line position. On the rest only the page is known,
and `page-index.json` says so per page.

**The check that earns the word `exact`.** A crop is `exact` only when the page carries
exactly as many drawing-sized band groups as the vision pass declared drawings for it,
AND the band falls between the y positions of the two paragraph markers the vision pass
said that drawing sits between. The declared count and the bounding markers come from a
pass that never saw this segmentation, so agreement is genuine corroboration rather than
a heuristic agreeing with itself.

**When that fails.** The crop widens to the whole region between the two markers, at
full page width, and is labelled `coarse` - in the JSON, and in English on the asset
itself, inside a dashed frame rather than a solid one so the distinction survives a
greyscale print. Showing too much costs the reviewer a few seconds. Showing too little
would show them a different molecule and invite them to reject a correct extraction, so
every fallback here widens.

- exact: **{len(exact)}**
- coarse: **{len(coarse)}**
- no crop offered: **{len(none_)}**

## The assets

| asset | page | structures | crop | between markers |
|---|---|---|---|---|
{rows}

## English only

Every human-facing string ends in `_en` and holds no Chinese. `output/translations.json`
resolves most of it; `visual_text.py` carries a declared glossary for the chemistry and
boilerplate fragments the index does not have, and anything neither covers becomes an
English placeholder rather than passing through. Unresolved fragments remaining:
**{len(unresolved)}**. Two upstream defects were found doing this and are not fixed here:
`output/translations.json` has `en` values that still contain Chinese, and the vision
pass wrote Chinese into its own `en` fields.

## Reading the claims

`drawing-claims.json` follows `contracts/VERIFICATION-CONTRACT.md`. Every claim is
`tier: 1`, `auto: "not_checkable"`, `needs_human: true` - none of this can be settled by
matching strings, which is exactly why it needs eyes. Two kinds:

- `field` starting `__drawing_structure__` - one per drawing. Carries `comparison.ours`,
  `comparison.theirs` with its own `confidence`, and `comparison.composite_src`.
- `field` starting `__drawing_discrepancy__` - one per conflict the vision pass found.
  Carries `disagreement.drawing_says_en`, `disagreement.text_says_en`, and
  `disagreement.we_followed`, plus `related_records[]` showing what we actually recorded.
  `we_followed` is `drawing`, `text`, or `unknown`; `unknown` means this stage would have
  had to guess, and did not.
""", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n")[0])
    ap.add_argument("--patent-id", dest="patent_id", default=None)
    args, _ = ap.parse_known_args()
    patent_id = args.patent_id or ctx.resolve_patent_id()
    return build(patent_id)


if __name__ == "__main__":
    raise SystemExit(main())
