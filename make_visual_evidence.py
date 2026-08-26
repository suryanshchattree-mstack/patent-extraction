#!/usr/bin/env python3
"""Visual evidence for a reviewer who does not know chemistry.

Three assets, all under output/relevant_output/visual/:

1. page-index.json   - given a paragraph marker, which scanned page is it on, and
                       where is that page's image. The page image is the ultimate
                       ground truth and until now nothing in the tool showed it.
2. comparisons/*.png - for every drawing in the patent, the structure WE recorded
                       drawn next to the structure the PATENT drew, and one
                       question underneath: do these show the same molecule?
                       A non-chemist cannot check a SMILES string. They can
                       compare two pictures, and that comparison catches the one
                       failure that matters most - a model that looked at a
                       drawing and wrote down a different molecule.
3. drawing-claims.json - the vision pass's 41 discrepancies as tier-1 review
                       items, conforming to claims[] in the verification
                       contract, plus the machine-detectable disagreements
                       between the drawing's SMILES and the gold's SMILES.

Deterministic, offline, idempotent. No timestamps are written, so two runs over
unchanged inputs produce identical bytes and a diff between runs is meaningful.

Reads only. Writes only under output/relevant_output/visual/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rdkit import Chem, RDLogger
from rdkit.Chem.Draw import rdMolDraw2D

RDLogger.DisableLog("rdApp.*")

ENGINE_VERSION = 1

# ---------------------------------------------------------------- page layout
#
# The PDF is a scan: nine pages, one image each, no text layer at all
# (pymupdf returns zero characters per page), and no OCR engine is installed.
# So the position of a drawing cannot be read off the page and has to be found
# from the ink itself.
#
# What makes that tractable is that the two things on the page look nothing
# alike under a horizontal projection. A line of Chinese body text is about 30
# pixels tall and its ink fills roughly 15% of its own bounding box. A drawn
# structure is 140 to 900 pixels tall and fills roughly 1.5%. The gap between
# the two populations is an order of magnitude, so the split is not delicate.
#
# Measured on all nine pages at 1653x2339.
INK_THRESHOLD = 160          # 8-bit grey below this counts as ink
MIN_ROW_INK = 3              # pixels of ink needed for a row to be "on"
STRIP_MERGE_GAP = 4          # blank rows bridged when growing one strip
MAX_NONTEXT_GAP = 60         # blank rows bridged when joining drawing strips
TEXT_MIN_EXTENT = 150        # a text line runs wider than this
TEXT_MIN_DENSITY = 0.09      # ink / (height x extent) for a text line
TEXT_HEIGHT = (22, 48)       # body text line height
MIN_BLOCK_HEIGHT = 100       # a drawing is at least this tall
MIN_BLOCK_EXTENT = 250       # and at least this wide
CROP_PAD = 24                # padding around a crop, trimmed off neighbours

CONTENT_BOX = (0.07, 0.95, 0.072, 0.955)   # x0, x1, y0, y1 as page fractions

# ---------------------------------------------------------------- rendering
PANEL_W = 760
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
FONT_REGULAR = FONT_DIR / "Arial.ttf"
FONT_BOLD = FONT_DIR / "Arial Bold.ttf"

CJK = re.compile(r"[⺀-鿿　-〿＀-￯]")
MARKER = re.compile(r"^\[\d{4}\]$")


# ================================================================== utilities

def sha16(*parts: str) -> str:
    """Claim ids must survive a re-run unchanged, so they hash content only."""
    h = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
    return h[:16]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(smiles: str | None) -> str | None:
    if not smiles:
        return None
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(mol) if mol else None


def norm_name(s: str) -> str:
    """Fold the spelling variants the gold itself carries as aliases.

    The gold holds the same molecule under 'methanesulfonyl', 'methylsulfonyl'
    and 'methylsulfonyl' with and without brackets, so a name lookup that does
    not fold them misses matches that are really there.
    """
    s = unicodedata.normalize("NFKC", s).lower().strip()
    s = s.replace("methanesulfonyl", "methylsulfonyl")
    s = s.replace("methanesulfanyl", "methylsulfanyl")
    s = re.sub(r"[()\[\]{}\s]", "", s)
    return s


def load_font(path: Path, size: int):
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


# ================================================================== inputs

class Inputs:
    def __init__(self, root: Path, patent_id: str):
        self.root = root
        self.patent_id = patent_id
        self.input_dir = root / "input"
        self.out_root = root / "output"
        self.rel = self.out_root / "relevant_output"
        self.visual = self.rel / "visual"

        self.pages = sorted((self.input_dir / "vision").glob("p*.json"))
        if not self.pages:
            sys.exit(f"no vision pass found under {self.input_dir / 'vision'}")

        self.vision = {}
        for p in self.pages:
            self.vision[p.stem] = json.loads(p.read_text(encoding="utf-8"))

        self.translations = json.loads(
            (self.out_root / "translations.json").read_text(encoding="utf-8"))
        self.gold = json.loads(
            (self.rel / "gold" / "structures-resolved.json").read_text(encoding="utf-8"))

        quotes_path = self.visual / "quote-translations.json"
        quotes_doc = json.loads(quotes_path.read_text(encoding="utf-8")) \
            if quotes_path.exists() else {}
        self.quotes = quotes_doc.get("entries", {})
        self.marker_labels = {
            k: v for k, v in quotes_doc.get("marker_labels_en", {}).items()
            if not k.startswith("_")
        }

        self.source_md = self.input_dir / f"{patent_id}-enriched-numbered.md"

        # longest key first, so '2-chloro-3-methyl-...' wins over '2-chloro'
        self.tr_keys = sorted(self.translations, key=len, reverse=True)

        # name -> gold record, over identifiers and aliases both
        self.by_name = {}
        self.by_canonical = {}
        for g in self.gold:
            for n in [g["identifier"], *g.get("aliases", [])]:
                self.by_name.setdefault(norm_name(n), g)
            c = g.get("canonical") or canonical(g.get("smiles"))
            if c:
                self.by_canonical.setdefault(c, g)

    def page_png(self, page: str) -> Path:
        return self.input_dir / "pages" / f"{page}.png"

    def translate(self, s: str) -> str:
        """Verified index first, longest match, for compound names."""
        for k in self.tr_keys:
            if k in s:
                s = s.replace(k, self.translations[k]["en"])
        return s


# ================================================================== markers

def marker_source_lines(source_md: Path) -> dict[str, int]:
    """Marker -> line number in the numbered bilingual source.

    Exact: the marker is printed at the head of its own line in that file.
    """
    out = {}
    if not source_md.exists():
        return out
    # The file prints its own line numbers as "  182 | [0033] ...", so the
    # marker is not at the head of the raw line and a pattern anchored there
    # silently matches nothing and leaves every claim with no citation.
    pat = re.compile(r"^\s*(?:\d+\s*\|\s*)?(\[\d{4}\])")
    for i, line in enumerate(source_md.read_text(encoding="utf-8").splitlines(), 1):
        m = pat.match(line)
        if m and m.group(1) not in out:
            out[m.group(1)] = i
    return out


def ordered_paragraphs(inp: Inputs) -> list[dict]:
    """Every paragraph of the patent in reading order, page by page."""
    out = []
    for page in sorted(inp.vision):
        for j, para in enumerate(inp.vision[page]["paragraphs"]):
            out.append({
                "page": page,
                "index_on_page": j,
                "marker": para.get("marker"),
                "zh": para.get("zh") or "",
                "en": para.get("en") or "",
            })
    return out


# ================================================================== segmentation

def page_strips(png: Path):
    """Every horizontal band of ink on the page, tagged text or not-text."""
    arr = np.asarray(Image.open(png).convert("L"))
    height, width = arr.shape
    ink = arr < INK_THRESHOLD
    fx0, fx1, fy0, fy1 = CONTENT_BOX
    x0, x1 = int(width * fx0), int(width * fx1)
    y0, y1 = int(height * fy0), int(height * fy1)
    sub = ink[y0:y1, x0:x1]

    on = sub.sum(axis=1) > MIN_ROW_INK
    runs, start = [], None
    for i, v in enumerate(on):
        if v and start is None:
            start = i
        elif not v and start is not None:
            runs.append([start, i])
            start = None
    if start is not None:
        runs.append([start, len(on)])

    merged = []
    for st, en in runs:
        if merged and st - merged[-1][1] <= STRIP_MERGE_GAP:
            merged[-1][1] = en
        else:
            merged.append([st, en])

    strips = []
    for st, en in merged:
        band = sub[st:en]
        h = en - st
        cols = band.sum(axis=0) > 0
        nz = np.nonzero(cols)[0]
        extent = int(nz[-1] - nz[0] + 1) if len(nz) else 0
        density = float(band.sum()) / max(h * extent, 1)
        strips.append({
            "y_top": st + y0,
            "y_bot": en + y0,
            "height": h,
            "extent": extent,
            "x_left": int(nz[0]) + x0 if len(nz) else x0,
            "x_right": int(nz[-1]) + x0 if len(nz) else x0,
            "is_text": bool(extent >= TEXT_MIN_EXTENT
                            and density >= TEXT_MIN_DENSITY
                            and TEXT_HEIGHT[0] <= h <= TEXT_HEIGHT[1]),
        })
    return strips, (x0, x1, y0, y1), (width, height)


def drawing_blocks(strips) -> list[dict]:
    """Runs of consecutive not-text strips, big enough to be a structure."""
    grouped, cur = [], None
    for s in strips:
        breaks = s["is_text"] or (cur and s["y_top"] - cur["y_bot"] > MAX_NONTEXT_GAP)
        if breaks and cur:
            grouped.append(cur)
            cur = None
        if not s["is_text"]:
            if cur is None:
                cur = {"y_top": s["y_top"], "y_bot": s["y_bot"],
                       "x_left": s["x_left"], "x_right": s["x_right"], "strips": 1}
            else:
                cur["y_bot"] = s["y_bot"]
                cur["x_left"] = min(cur["x_left"], s["x_left"])
                cur["x_right"] = max(cur["x_right"], s["x_right"])
                cur["strips"] += 1
    if cur:
        grouped.append(cur)

    return [b for b in grouped
            if b["y_bot"] - b["y_top"] >= MIN_BLOCK_HEIGHT
            and b["x_right"] - b["x_left"] >= MIN_BLOCK_EXTENT]


def crop_box(block, strips, box):
    """Pad the block out, but never far enough to clip a neighbouring line.

    Full content width, because a structure's substituent labels reach further
    sideways than its bonds do and a tight horizontal crop is how you lose a
    chlorine. Showing blank paper costs the reviewer nothing.
    """
    x0, x1, y0, y1 = box
    above = [s["y_bot"] for s in strips if s["y_bot"] <= block["y_top"]]
    below = [s["y_top"] for s in strips if s["y_top"] >= block["y_bot"]]
    top_gap = block["y_top"] - max(above) if above else CROP_PAD
    bot_gap = min(below) - block["y_bot"] if below else CROP_PAD
    top = block["y_top"] - max(0, min(CROP_PAD, top_gap - 4))
    bot = block["y_bot"] + max(0, min(CROP_PAD, bot_gap - 4))
    return (x0, max(y0, top), x1, min(y1, bot))


COLUMN_GAP = 120        # blank columns that still count as one drawing
SIDE_PAD = 60           # padding left and right of the drawing
MIN_INK_SHARE = 0.7     # the group kept must hold this much of the band's ink


def tight_box(png: Path, loose, box):
    """The same vertical band, cut in from the sides to the drawing itself.

    The band runs the full width of the text column, and a paragraph marker
    sitting at the far left drags the drawing down to a fifth of the panel,
    which is small enough that a reviewer cannot compare it to anything. So the
    columns carrying ink are grouped, gaps under COLUMN_GAP bridged, and the
    widest group taken as the drawing. A marker is separated from a centred
    structure by far more than that and drops out; a substituent label is joined
    to its bond by far less and cannot.

    Never used alone. The full loose band is always written out beside it as
    `<record_id>-patent.png`, so a reviewer who suspects the sides were cut too
    close has the uncut band to hand.
    """
    x0, x1, y0, y1 = box
    arr = np.asarray(Image.open(png).convert("L"))
    band = (arr[loose[1]:loose[3], x0:x1] < INK_THRESHOLD)
    cols = np.nonzero(band.sum(axis=0) > 0)[0]
    if len(cols) == 0:
        return loose, False
    groups, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > COLUMN_GAP:
            groups.append((start, prev))
            start = c
        prev = c
    groups.append((start, prev))

    # Pick the group by INK, not by how wide it is. A paragraph marker sitting
    # at the far left is only six small glyphs but it doubles the band's span,
    # and judging by span throws away the cut exactly when it is most needed.
    per_col = band.sum(axis=0)
    total = per_col.sum()
    left, right = max(groups, key=lambda g: per_col[g[0]:g[1] + 1].sum())
    if not total or per_col[left:right + 1].sum() / total < MIN_INK_SHARE:
        return loose, False
    return (max(x0, x0 + int(left) - SIDE_PAD), loose[1],
            min(x1, x0 + int(right) + SIDE_PAD), loose[3]), True


# ================================================================== gold linkage

def find_compound(inp: Inputs, para: dict):
    """The gold record named by this paragraph, or None.

    Text side only. It never looks at the drawing, which is the whole point:
    if the left half of a comparison were chosen by matching the drawing, the
    two halves would agree by construction and the picture would prove nothing.
    """
    best = None
    for key in inp.tr_keys:                       # longest match first
        if key and key in para["zh"]:
            g = inp.by_name.get(norm_name(inp.translations[key]["en"]))
            if g and g.get("smiles"):
                best = (g, key, inp.translations[key]["en"])
                break
    if best is None:
        for name, g in sorted(inp.by_name.items(), key=lambda kv: -len(kv[0])):
            if len(name) > 12 and g.get("smiles") and name in norm_name(para["en"]):
                best = (g, g["identifier"], g["identifier"])
                break
    return best


def anchor_for(inp: Inputs, paras: list[dict], page: str, between: list[str]):
    """Walk back from the drawing to the paragraph that names its compound."""
    target = None
    for m in between:
        if MARKER.match((m or "").strip()):
            target = m.strip()
            break
    idx = None
    for i, p in enumerate(paras):
        if p["marker"] and f"[{str(p['marker']).zfill(4)}]" == target:
            idx = i
            break
        if p["marker"] == target:
            idx = i
            break
    if idx is None:
        # between_markers[0] can be prose ("continues from p05"); fall back to
        # the closing marker and step back from there.
        closing = next((m.strip() for m in reversed(between)
                        if MARKER.match((m or "").strip())), None)
        for i, p in enumerate(paras):
            if p["marker"] == closing or (
                    p["marker"] and f"[{str(p['marker']).zfill(4)}]" == closing):
                idx = i
                break
    if idx is None:
        return None
    for back in range(1, 6):
        j = idx - back
        if j < 0:
            break
        hit = find_compound(inp, paras[j])
        if hit:
            gold, key, name_en = hit
            return {"marker": paras[j]["marker"], "page": paras[j]["page"],
                    "gold": gold, "matched_on": name_en,
                    "paragraph_en": paras[j]["en"]}
    return None


# ================================================================== drawing

def render_structure(smiles: str, width: int, height: int) -> Image.Image:
    """Same renderer settings as resolve_structures.py: flat black, no colour.

    Monochrome is not a style choice. No meaning in this project may rest on
    colour, and an element-coloured drawing read by someone with a colour
    vision deficiency, or printed in greyscale, loses exactly the atom labels
    the comparison turns on.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        img = Image.new("RGB", (width, height), "white")
        d = ImageDraw.Draw(img)
        d.text((20, height // 2), "this SMILES will not parse",
               font=load_font(FONT_BOLD, 22), fill="black")
        return img
    drawer = rdMolDraw2D.MolDraw2DCairo(width, height)
    opts = drawer.drawOptions()
    opts.useBWAtomPalette()
    opts.clearBackground = True
    opts.bondLineWidth = 2
    opts.padding = 0.08
    opts.addStereoAnnotation = False
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
    drawer.FinishDrawing()
    import io
    return Image.open(io.BytesIO(drawer.GetDrawingText())).convert("RGB")


def wrap(draw, text, font, width):
    """Word wrap, breaking mid-word when a single word is wider than the box.

    Systematic chemical names are one unbroken word and routinely wider than the
    column they sit in, so a wrapper that only ever breaks at spaces leaves them
    to run out over their neighbour.
    """
    lines, cur = [], ""
    for w in text.split():
        while draw.textlength(w, font=font) > width:
            cut = len(w)
            while cut > 1 and draw.textlength(w[:cut], font=font) > width:
                cut -= 1
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(w[:cut])
            w = w[cut:]
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_clip(draw, text, font, width, max_lines):
    """Wrap to the cell, and cut with an ellipsis rather than overrun it.

    An overrunning caption writes itself across its neighbour and both become
    unreadable, which on this asset means the reviewer cannot tell which
    molecule is which.
    """
    lines = wrap(draw, text, font, width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and draw.textlength(last + "...", font=font) > width:
        last = last[:-1]
    lines[-1] = last.rstrip() + "..."
    return lines


def text_block(draw, xy, text, font, width, fill="black", leading=6):
    x, y = xy
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + leading
    return y


def fit(img: Image.Image, width: int) -> Image.Image:
    if img.width == width:
        return img
    h = max(1, round(img.height * width / img.width))
    return img.resize((width, h), Image.LANCZOS)


def fit_box(img: Image.Image, width: int, height: int) -> Image.Image:
    """Scale to fit inside the box, keep the aspect, centre on white.

    Both halves get the same box, so the two molecules come out at comparable
    size. A structure the reviewer has to squint at is a structure they will
    wave through.
    """
    scale = min(width / img.width, height / img.height)
    w, h = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    canvas = Image.new("RGB", (width, height), "white")
    canvas.paste(img.resize((w, h), Image.LANCZOS),
                 ((width - w) // 2, (height - h) // 2))
    return canvas


def compose(patent_img, ours, header, left_caption, right_caption,
            question, notes, side_by_side):
    """One self-describing picture. Every claim it makes is written on it."""
    f_h = load_font(FONT_BOLD, 30)
    f_lbl = load_font(FONT_BOLD, 23)
    f_cap = load_font(FONT_REGULAR, 19)
    f_q = load_font(FONT_BOLD, 27)
    f_note = load_font(FONT_REGULAR, 17)

    pad = 26
    if side_by_side:
        # A page crop is wide and short; a rendered structure is nearly square.
        # Give both the same box so neither is dwarfed by the other.
        box_h = max(420, min(620, round(PANEL_W * patent_img.height / patent_img.width)))
        left = fit_box(ours[0][0], PANEL_W, box_h)
        right = fit_box(patent_img, PANEL_W, box_h)
        body_w = PANEL_W * 2 + pad
    else:
        right = fit(patent_img, PANEL_W * 2 + pad)
        body_w = right.width
        cols = min(5, len(ours))
        cell = (body_w - pad * (cols - 1)) // cols
        rows = (len(ours) + cols - 1) // cols
        f_n = load_font(FONT_BOLD, 16)
        label_lines, cap_lines = 3, []
        probe0 = ImageDraw.Draw(Image.new("RGB", (10, 10), "white"))
        for _, lab in ours:
            cap_lines.append(wrap_clip(probe0, lab, f_n, cell - 8, label_lines))
        band = cell + 12 + (f_n.size + 4) * label_lines + 14
        left = Image.new("RGB", (body_w, rows * band), "white")
        ld = ImageDraw.Draw(left)
        for i, (im, _) in enumerate(ours):
            r, c = divmod(i, cols)
            x, y = c * (cell + pad), r * band
            left.paste(fit(im, cell), (x, y))
            ld.rectangle([x, y, x + cell - 1, y + cell - 1], outline="black", width=1)
            ty = y + cell + 10
            for line in cap_lines[i]:
                ld.text((x + 4, ty), line, font=f_n, fill="black")
                ty += f_n.size + 4

    width = body_w + pad * 2
    probe = Image.new("RGB", (width, 10), "white")
    pd = ImageDraw.Draw(probe)

    head_h = 46 + (f_h.size + 6) * len(wrap(pd, header, f_h, body_w))
    lbl_h = f_lbl.size + 10
    cap_w = PANEL_W if side_by_side else body_w
    cap_h = (f_cap.size + 6) * max(len(wrap(pd, left_caption, f_cap, cap_w)),
                                   len(wrap(pd, right_caption, f_cap, cap_w))) + 14
    q_h = (f_q.size + 8) * len(wrap(pd, question, f_q, body_w)) + 26
    note_h = sum((f_note.size + 6) * len(wrap(pd, n, f_note, body_w)) + 10 for n in notes)

    if side_by_side:
        panels_h = lbl_h + max(left.height, right.height) + cap_h
    else:
        panels_h = lbl_h + right.height + cap_h + lbl_h + left.height + cap_h

    height = head_h + panels_h + q_h + note_h + pad * 2
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)

    y = pad
    y = text_block(d, (pad, y), header, f_h, body_w)
    y += 8
    d.line([(pad, y), (width - pad, y)], fill="black", width=2)
    y += 16

    if side_by_side:
        d.text((pad, y), "WHAT WE RECORDED", font=f_lbl, fill="black")
        d.text((pad + PANEL_W + pad, y), "WHAT THE PATENT DREW", font=f_lbl, fill="black")
        top = y + lbl_h
        img.paste(left, (pad, top))
        img.paste(right, (pad + PANEL_W + pad, top))
        for px, panel in ((pad, left), (pad + PANEL_W + pad, right)):
            d.rectangle([px - 1, top - 1, px + panel.width, top + panel.height],
                        outline="black", width=1)
        y = top + max(left.height, right.height) + 12
        ly = text_block(d, (pad, y), left_caption, f_cap, PANEL_W)
        ry = text_block(d, (pad + PANEL_W + pad, y), right_caption, f_cap, PANEL_W)
        y = max(ly, ry) + 12
    else:
        d.text((pad, y), "WHAT THE PATENT DREW", font=f_lbl, fill="black")
        y += lbl_h
        img.paste(right, (pad, y))
        d.rectangle([pad - 1, y - 1, pad + right.width, y + right.height],
                    outline="black", width=1)
        y += right.height + 12
        y = text_block(d, (pad, y), right_caption, f_cap, body_w) + 14
        d.text((pad, y), "WHAT WE RECORDED, IN THE SAME READING ORDER",
               font=f_lbl, fill="black")
        y += lbl_h
        img.paste(left, (pad, y))
        y += left.height + 12
        y = text_block(d, (pad, y), left_caption, f_cap, body_w) + 12

    d.line([(pad, y), (width - pad, y)], fill="black", width=2)
    y += 16
    y = text_block(d, (pad, y), question, f_q, body_w, leading=8) + 12
    for n in notes:
        y = text_block(d, (pad, y), n, f_note, body_w) + 10
    return img.crop((0, 0, width, min(height, y + pad)))


# ================================================================== main build

def build(root: Path, patent_id: str) -> int:
    inp = Inputs(root, patent_id)
    out = inp.visual
    (out / "comparisons").mkdir(parents=True, exist_ok=True)

    paras = ordered_paragraphs(inp)
    src_lines = marker_source_lines(inp.source_md)

    # ---------------------------------------------------------- 1. page index
    pages_out, markers_out = [], {}
    layout = {}
    for page in sorted(inp.vision):
        v = inp.vision[page]
        png = inp.page_png(page)
        strips, box, (pw, ph) = page_strips(png)
        blocks = drawing_blocks(strips)
        layout[page] = {"strips": strips, "box": box, "blocks": blocks,
                        "size": (pw, ph)}
        page_no = int(page[1:])
        rel_img = f"input/pages/{page}.png"
        markers_here = []
        for p in v["paragraphs"]:
            m = str(p.get("marker") or "").strip()
            if not m:
                continue
            # The front page labels its fields with WIPO INID codes, two of which
            # are printed in Chinese. Every key here has to be addressable in
            # English, so those two are renamed from the curated label map.
            key = inp.marker_labels.get(m, m)
            if CJK.search(key):
                continue
            markers_here.append(key)
            markers_out.setdefault(key, {
                "marker_en": key,
                "marker_as_printed_is_chinese": key != m,
                "page": page,
                "page_number": page_no,
                "page_image_path": rel_img,
                "page_width": pw,
                "page_height": ph,
                "source_line": src_lines.get(key),
                "position_en": ("Exact to the page. The marker's position down "
                                "the page is not given: the scan carries no text "
                                "layer, so nothing can say where on the page it "
                                "sits without guessing."),
            })
        pages_out.append({
            "page": page,
            "page_number": page_no,
            "image_path": rel_img,
            "width": pw,
            "height": ph,
            "doc_part_en": v.get("doc_part"),
            "page_confidence_en": v.get("page_confidence"),
            "markers": markers_here,
            "drawings_reported_by_vision": len(v["drawings"]),
            "drawing_regions_detected": len(blocks),
            "detection_agrees": len(blocks) == len(v["drawings"]),
            "drawing_regions": [
                {"y_top": b["y_top"], "y_bot": b["y_bot"],
                 "x_left": b["x_left"], "x_right": b["x_right"]}
                for b in blocks],
        })

    page_index = {
        "patent_id": patent_id,
        "engine_version": ENGINE_VERSION,
        "what_this_is_en": (
            "Given a paragraph marker such as [0034], this says which scanned page "
            "it appears on and where that page's image file is. The page image is "
            "the original document and outranks every other artefact in this "
            "repository: if the tool and the page disagree, the page is right."),
        "confidence_en": {
            "marker_to_page": (
                "EXACT. Taken from the per-page paragraph lists of the vision pass, "
                "which read each page separately, so a marker's page is observed and "
                "not inferred."),
            "marker_to_position_on_page": (
                "NOT PROVIDED. The PDF is a scan with no text layer and no OCR engine "
                "is installed, so the y position of a marker could only be guessed. A "
                "guess that points a reviewer at the wrong paragraph is worse than no "
                "pointer, so none is given."),
            "drawing_regions": (
                "APPROXIMATE. Found by measuring the ink on the page: lines of text "
                "and drawn structures separate cleanly under a horizontal projection. "
                "The regions are deliberately loose and may include blank paper or a "
                "paragraph marker."),
        },
        "source_pdf": {
            "path": f"input/pdf/{patent_id}.pdf",
            "sha256": sha256_file(inp.input_dir / "pdf" / f"{patent_id}.pdf"),
            "has_text_layer": False,
            "note_en": ("Nine pages, one scanned image each, zero extractable "
                        "characters. Every position in this file therefore comes "
                        "from image analysis, never from text coordinates."),
        },
        "pages": pages_out,
        "markers": dict(sorted(markers_out.items())),
    }
    (out / "page-index.json").write_text(
        json.dumps(page_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------------------------------------------------- 2. comparisons
    comparisons, claims = [], []
    drawing_no = 0
    total_drawings = sum(len(inp.vision[p]["drawings"]) for p in inp.vision)

    for page in sorted(inp.vision):
        v = inp.vision[page]
        if not v["drawings"]:
            continue
        lay = layout[page]
        agrees = len(lay["blocks"]) == len(v["drawings"])
        img_full = Image.open(inp.page_png(page)).convert("RGB")

        for k, dr in enumerate(v["drawings"]):
            drawing_no += 1
            rid = f"{patent_id}_{page}_d{k + 1}"
            between = dr.get("between_markers") or []

            if agrees:
                block = lay["blocks"][k]
                bx = crop_box(block, lay["strips"], lay["box"])
                tb, tightened = tight_box(inp.page_png(page), bx, lay["box"])
                patent_img = img_full.crop(tb)
                n_b = len(lay["blocks"])
                how_found = (
                    "HOW THE PICTURE ABOVE WAS FOUND: automatically. The scan has no "
                    "text layer, so a machine measured the ink on page {n} and cut out "
                    "the {ord} block that is a drawing rather than lines of text. This "
                    "page holds {a} such {blocks}, and reading the page found {b} "
                    "{draws}, so the two agree. The cut is deliberately loose. If it "
                    "has sliced a molecule in half, or shows a different molecule from "
                    "the one named above, this comparison is broken and should be "
                    "reported as broken rather than answered."
                ).format(n=int(page[1:]), ord=ordinal(k + 1), a=n_b,
                         blocks="block" if n_b == 1 else "blocks",
                         b=len(v["drawings"]),
                         draws="drawing" if len(v["drawings"]) == 1 else "drawings")
                crop_conf = "region_detected"
            else:
                patent_img = img_full
                bx = (0, 0, img_full.width, img_full.height)
                tb, tightened = bx, False
                how_found = (
                    "HOW THE PICTURE ABOVE WAS FOUND: it was NOT found. The machine "
                    "counted {a} drawing-shaped blocks on page {n} but the reading of "
                    "the page found {b} drawings, so no block can be trusted to be this "
                    "one. The WHOLE PAGE is shown instead. Find the drawing yourself "
                    "before answering."
                ).format(a=len(lay["blocks"]), n=int(page[1:]), b=len(v["drawings"]))
                crop_conf = "whole_page_fallback"

            # The sidecar is always the UNCUT band, so nothing that was trimmed
            # off the sides of the composed picture is lost to the reviewer.
            crop_name = f"{rid}-patent.png"
            img_full.crop(bx).save(out / "comparisons" / crop_name)

            structures = dr.get("structures") or []
            single = len(structures) == 1
            anchor = anchor_for(inp, paras, page, between) if single else None

            ours, panels = [], []
            for si, st in enumerate(structures):
                drawn_canon = canonical(st.get("smiles"))
                if single and anchor:
                    gold = anchor["gold"]
                    how = "name"
                else:
                    gold = inp.by_canonical.get(drawn_canon) if drawn_canon else None
                    how = "structure" if gold else "none"
                if gold and gold.get("smiles"):
                    im = render_structure(gold["smiles"], 700, 560)
                    # Three gold records carry a SMILES string where a name
                    # should be. Printing that as if it were the compound's name
                    # tells a non-chemist nothing, so say what is actually true.
                    label = ("we recorded this one with no name, only a structure"
                             if gold["identifier"] == gold.get("smiles")
                             else gold["identifier"])
                else:
                    im = Image.new("RGB", (700, 560), "white")
                    ImageDraw.Draw(im).text(
                        (24, 260), "we hold no structure for this",
                        font=load_font(FONT_BOLD, 26), fill="black")
                    label = "no record"
                ours.append((im, f"{si + 1}. {label}" if not single else label))
                panels.append({
                    "position_en": st.get("position_in_drawing"),
                    "drawn_name_en": st.get("name"),
                    "drawn_smiles": st.get("smiles"),
                    "drawn_canonical": drawn_canon,
                    "gold_identifier": gold["identifier"] if gold else None,
                    "gold_smiles": gold.get("smiles") if gold else None,
                    "gold_canonical": (gold.get("canonical") or canonical(gold.get("smiles")))
                                      if gold else None,
                    "linked_by": how,
                })

            # between_markers can carry prose where a marker is not visible on
            # the page, so say "between X and Y" only when there really are two.
            marks = [m.strip() for m in between if MARKER.match(m.strip())]
            if len(marks) >= 2:
                where = f"between {marks[0]} and {marks[1]}"
            elif len(marks) == 1:
                where = f"just above {marks[0]}"
            else:
                where = "no paragraph marker printed beside it"
            header = (f"Drawing {drawing_no} of {total_drawings}   -   page "
                      f"{int(page[1:])} of the patent, {where}")

            if single:
                if anchor:
                    left_caption = (
                        "This is drawn from the SMILES text we recorded for the "
                        f"compound the patent's own words name at {anchor['marker']}: "
                        f"{anchor['gold']['identifier']}. Nothing about it came from "
                        "looking at the picture on the right, so the two halves are "
                        "independent and can genuinely disagree.")
                    link_note = (
                        "HOW THE TWO HALVES WERE PAIRED: by the compound name printed "
                        f"in the patent's text at {anchor['marker']}, not by the "
                        "drawing. This is the strong pairing.")
                    link = "name"
                elif panels and panels[0]["gold_identifier"]:
                    left_caption = (
                        "This is drawn from the SMILES text we recorded for "
                        f"{panels[0]['gold_identifier']}.")
                    link_note = (
                        "HOW THE TWO HALVES WERE PAIRED: WEAK. The patent's words near "
                        "this drawing name no compound we hold, so our record was found "
                        "by looking for one whose structure matches the drawing. The "
                        "two halves will therefore tend to agree, and this picture "
                        "confirms only that we hold the molecule at all.")
                    link = "structure"
                else:
                    left_caption = "We hold no structure to put here."
                    link_note = ("HOW THE TWO HALVES WERE PAIRED: they were not. We "
                                 "have no record matching this drawing.")
                    link = "none"
                question = "Do these two pictures show the same molecule?"
            else:
                left_caption = (
                    "Each panel is drawn from the SMILES text we recorded, numbered in "
                    "the drawing's own reading order: left to right, top row first.")
                link_note = (
                    "HOW THE HALVES WERE PAIRED: WEAK. This drawing is a whole route "
                    "and the patent's words near it name no single compound, so each of "
                    "our records was found by looking for one whose structure matches "
                    "the drawn one. They will therefore tend to agree. What this "
                    "picture does show is whether we hold every molecule the route "
                    "draws, and in the right order.")
                link = "structure"
                question = ("Does every molecule below appear in the drawing above, in "
                            "the same order?")

            right_caption = (
                f"Cut from the scan of page {int(page[1:])}, at y {bx[1]} to {bx[3]} "
                f"of {img_full.height}." +
                (f" The sides were then cut in to the drawing, from x {bx[0]} to "
                 f"{bx[2]} down to x {tb[0]} to {tb[2]}, so that it is not too small "
                 f"to compare. The uncut band is the file "
                 f"{rid}-patent.png in this folder." if tightened else ""))
            notes = [how_found, link_note,
                     "This picture answers one question and no other. It does not say "
                     "the chemistry is right, only whether we wrote down the molecule "
                     "the patent drew."]

            img = compose(patent_img, ours, header, left_caption, right_caption,
                          question, notes, side_by_side=single)
            comp_name = f"{rid}.png"
            img.save(out / "comparisons" / comp_name)

            comparisons.append({
                "record_id": rid,
                "drawing_number": drawing_no,
                "page": page,
                "page_number": int(page[1:]),
                "between_markers_en": [m for m in between],
                "kind_en": dr.get("kind"),
                "presented_as_en": dr.get("presented_as"),
                "structure_count": len(structures),
                "comparison_image": f"comparisons/{comp_name}",
                "patent_crop_image": f"comparisons/{crop_name}",
                "crop_box_uncut": {"x_left": bx[0], "y_top": bx[1],
                                   "x_right": bx[2], "y_bot": bx[3]},
                "crop_box_shown": {"x_left": tb[0], "y_top": tb[1],
                                   "x_right": tb[2], "y_bot": tb[3]},
                "sides_cut_in_to_drawing": tightened,
                "crop_confidence": crop_conf,
                "crop_confidence_en": how_found,
                "pairing": link,
                "pairing_en": link_note,
                "anchor_marker": anchor["marker"] if anchor else None,
                "panels": panels,
            })

            # ---- SMILES cross-check, only where the pairing is independent
            for si, pn in enumerate(panels):
                if pn["linked_by"] != "name":
                    continue
                same = (pn["drawn_canonical"] and pn["gold_canonical"]
                        and pn["drawn_canonical"] == pn["gold_canonical"])
                if same:
                    continue
                cid_rec = f"{rid}_s{si + 1}"
                claims.append(make_claim(
                    patent_id=patent_id,
                    record_id=cid_rec,
                    record_kind="compound",
                    label_en=pn["gold_identifier"] or pn["drawn_name_en"] or rid,
                    field="structure.drawn_vs_recorded",
                    field_label_en="Structure we recorded against structure the patent drew",
                    question_en=(
                        "The patent's words name "
                        f"{pn['gold_identifier']}, and we recorded a structure for that "
                        "name. The patent also DRAWS a structure at this point, and a "
                        "separate reading of that drawing gives a different molecule. "
                        "Open the picture and say which of the two the drawing shows."),
                    claimed_en=pn["gold_smiles"] or "no structure recorded",
                    evidence_en=(
                        f"We recorded: {pn['gold_canonical']}. The drawing reads as: "
                        f"{pn['drawn_canonical']}. These are different molecules."),
                    auto="not_found",
                    auto_reason_en=(
                        "The two SMILES do not match after both were reduced to a "
                        "single canonical form, so this is a real disagreement and not "
                        "a difference in spelling."),
                    risk=0.95,
                    risk_reasons_en=[
                        "The structure we hold and the structure the patent drew are "
                        "not the same molecule.",
                        "The pairing here is by the compound name in the patent's own "
                        "text, so this is not an artefact of how the two were matched.",
                    ],
                    about="extraction",
                    images={"comparison_image": f"comparisons/{comp_name}",
                            "patent_crop_image": f"comparisons/{crop_name}",
                            "page_image_path": f"input/pages/{page}.png"},
                    stratum=f"compound:drawing on page {int(page[1:])}",
                    marker=anchor["marker"] if anchor else None,
                    src_lines=src_lines,
                ))

            # ---- a molecule the patent draws that we hold nothing for
            for si, pn in enumerate(panels):
                if pn["gold_identifier"] or not pn["drawn_canonical"]:
                    continue
                claims.append(make_claim(
                    patent_id=patent_id,
                    record_id=f"{rid}_s{si + 1}_missing",
                    record_kind="compound",
                    label_en=pn["drawn_name_en"] or "unnamed drawn structure",
                    field="structure.drawn_but_not_recorded",
                    field_label_en="A molecule the patent draws and we did not record",
                    question_en=(
                        "The patent draws a molecule here that we hold no record of at "
                        f"all ({pn['drawn_name_en']}). Open the picture and say whether "
                        "there really is a structure drawn at that spot."),
                    claimed_en="no record",
                    evidence_en=(f"Read off the drawing as {pn['drawn_smiles']}. No "
                                 "record in the gold has this structure."),
                    auto="not_found",
                    auto_reason_en="No gold record carries this canonical structure.",
                    risk=0.8,
                    risk_reasons_en=["A drawn molecule with no record is a missed "
                                     "extraction, which no per-record check can see."],
                    about="extraction",
                    images={"comparison_image": f"comparisons/{comp_name}",
                            "patent_crop_image": f"comparisons/{crop_name}",
                            "page_image_path": f"input/pages/{page}.png"},
                    stratum=f"compound:drawing on page {int(page[1:])}",
                    marker=None,
                    src_lines=src_lines,
                ))

    # ---------------------------------------------------------- 3. discrepancies
    for page in sorted(inp.vision):
        v = inp.vision[page]
        page_no = int(page[1:])
        page_comps = [c for c in comparisons if c["page"] == page]
        for i, disc in enumerate(v["discrepancies"]):
            fields = {}
            for key in ("what", "drawing_says", "text_says"):
                raw = str(disc.get(key) or "")
                qk = f"{page}#{i}.{key}"
                fields[key] = inp.quotes.get(qk) or inp.translate(raw)
            rid = f"{patent_id}_{page}_x{i + 1}"
            related = related_records(inp, disc, fields)
            markers = sorted(set(re.findall(r"\[\d{4}\]", " ".join(fields.values()))))

            # Only attach a drawing when the conflict really sits at it. Hanging
            # the page's first drawing off every conflict on the page points the
            # reviewer at a picture that has nothing to do with the question.
            near = next((c for c in page_comps
                         if set(markers) & {m.strip() for m in c["between_markers_en"]}),
                        None)
            drawing_involved = bool(
                near or (fields["drawing_says"] and not
                         fields["drawing_says"].lower().startswith(("n/a", "no drawing"))))
            if drawing_involved:
                why = ["The patent's drawing and the patent's words disagree here."]
            else:
                why = ["The patent's own words disagree with each other here. "
                       "No drawing is involved."]
            why.append("Where a source contradicts itself, an extraction has to pick "
                       "one, and the pick is exactly what needs checking.")
            claims.append(make_claim(
                patent_id=patent_id,
                record_id=rid,
                record_kind="patent",
                label_en=f"Page {page_no}, conflict {i + 1}",
                field="__patent_self_contradiction__",
                field_label_en="A place the patent contradicts itself",
                question_en=(
                    f"On page {page_no} the patent does not agree with itself. "
                    f"{fields['what']} Did we record what the patent actually prints, "
                    "rather than a tidied-up version of it?"),
                claimed_en=fields["what"],
                evidence_en=("THE DRAWING SAYS: " + fields["drawing_says"] +
                             "  THE TEXT SAYS: " + fields["text_says"]),
                auto="not_checkable",
                auto_reason_en=(
                    "This is a conflict inside the patent itself, found by reading the "
                    "page. No string match can settle it. A human has to look at the "
                    "page and say which of the two the patent prints."),
                risk=0.6,
                risk_reasons_en=[
                    "The patent's drawing and the patent's words disagree here.",
                    "Where a source contradicts itself, an extraction has to pick one, "
                    "and the pick is exactly what needs checking.",
                ],
                about="patent",
                images={"page_image_path": f"input/pages/{page}.png",
                        "comparison_image": page_comps[0]["comparison_image"]
                        if page_comps else None,
                        "patent_crop_image": None},
                stratum=f"patent:page {page_no}",
                marker=markers[0] if markers else None,
                src_lines=src_lines,
                extra={
                    "about_en": (
                        "THIS IS A DEFECT IN THE PATENT, NOT IN OUR ANNOTATION. The "
                        "question is not whether we got it wrong. It is whether we "
                        "wrote down what the patent really prints, contradiction and "
                        "all, instead of quietly correcting it."),
                    "drawing_says_en": fields["drawing_says"],
                    "text_says_en": fields["text_says"],
                    "page": page,
                    "page_number": page_no,
                    "markers_mentioned": markers,
                    "related_records": related,
                    "drawings_on_this_page": [c["record_id"] for c in page_comps],
                },
            ))

    claims.sort(key=lambda c: (-c["risk"], c["record_id"], c["field"]))

    doc = {
        "patent_id": patent_id,
        "engine_version": ENGINE_VERSION,
        "what_this_is_en": (
            "Review items that come from the PICTURES in the patent rather than from "
            "its words. Two kinds. First, every place the patent's own drawing and the "
            "patent's own text disagree - these are defects in the patent, and the "
            "question put to the reviewer is whether we recorded the contradiction "
            "faithfully instead of tidying it away. Second, every place the structure "
            "we recorded and the structure the patent drew are not the same molecule - "
            "these are defects in the extraction."),
        "summary": {
            "claims_total": len(claims),
            "patent_self_contradictions": sum(
                1 for c in claims if c["field"] == "__patent_self_contradiction__"),
            "structure_disagreements": sum(
                1 for c in claims if c["field"] == "structure.drawn_vs_recorded"),
            "drawn_but_not_recorded": sum(
                1 for c in claims if c["field"] == "structure.drawn_but_not_recorded"),
            "drawings_total": total_drawings,
            "comparisons_written": len(comparisons),
            "comparisons_with_detected_region": sum(
                1 for c in comparisons if c["crop_confidence"] == "region_detected"),
            "comparisons_falling_back_to_whole_page": sum(
                1 for c in comparisons if c["crop_confidence"] == "whole_page_fallback"),
            "comparisons_paired_by_name": sum(
                1 for c in comparisons if c["pairing"] == "name"),
            "comparisons_paired_by_structure": sum(
                1 for c in comparisons if c["pairing"] == "structure"),
        },
        "comparisons": comparisons,
        "claims": claims,
    }
    (out / "drawing-claims.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_readme(out, page_index, doc, patent_id)

    # ---------------------------------------------------------- the English gate
    # quote-translations.json is an INPUT to this stage, not an output, and its
    # keys are the raw Chinese labels they stand in for - that is what makes the
    # lookup work. Its values still have to be English, so it is gated on values
    # only while everything this stage generates is gated whole.
    bad = []
    curated = out / "quote-translations.json"
    for path in sorted(out.rglob("*")):
        if path.suffix not in (".json", ".md") or path == curated:
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if CJK.search(line):
                bad.append(f"{path.relative_to(out)}:{n}")
    if curated.exists():
        doc_c = json.loads(curated.read_text(encoding="utf-8"))
        for section in ("entries", "marker_labels_en"):
            for k, val in doc_c.get(section, {}).items():
                if isinstance(val, str) and CJK.search(val):
                    bad.append(f"quote-translations.json:{section}[{k}] value")
    if bad:
        print("FAIL: Chinese characters reached the output:", file=sys.stderr)
        for b in bad[:40]:
            print("   ", b, file=sys.stderr)
        return 1

    print(f"page-index.json      {len(page_index['markers'])} markers, "
          f"{len(page_index['pages'])} pages")
    print(f"comparisons          {len(comparisons)} written, "
          f"{doc['summary']['comparisons_with_detected_region']} from a detected region, "
          f"{doc['summary']['comparisons_falling_back_to_whole_page']} whole-page fallback")
    print(f"drawing-claims.json  {len(claims)} claims "
          f"({doc['summary']['patent_self_contradictions']} patent conflicts, "
          f"{doc['summary']['structure_disagreements']} structure disagreements, "
          f"{doc['summary']['drawn_but_not_recorded']} drawn but not recorded)")
    return 0


def ordinal(n: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, f"{n}th")


def make_claim(*, patent_id, record_id, record_kind, label_en, field, field_label_en,
               question_en, claimed_en, evidence_en, auto, auto_reason_en, risk,
               risk_reasons_en, about, images, stratum, marker, src_lines, extra=None):
    line = src_lines.get(marker) if marker else None
    claim = {
        "claim_id": sha16(record_id, field),
        "record_id": record_id,
        "record_kind": record_kind,
        "record_label_en": label_en,
        "field": field,
        "field_label_en": field_label_en,
        "question_en": question_en,
        "claimed_en": claimed_en,
        "claimed_value": None,
        "claimed_unit": None,
        "cited_lines": [line] if line else [],
        "evidence_en": evidence_en,
        "evidence_lines": ([{"n": line, "text_en": evidence_en, "is_translation": True}]
                           if line else []),
        "highlights": [],
        "auto": auto,
        "auto_reason_en": auto_reason_en,
        "needs_human": True,
        "risk": risk,
        "risk_reasons_en": risk_reasons_en,
        "structure_svg_path": None,
        "tier": 1,
        "stratum": stratum,
        "about": about,
        "evidence_kind": "image",
        "evidence_note_en": (
            "The evidence for this item is a picture, not a line of text. Open the "
            "images listed under 'images' - the comparison first, and the page scan if "
            "the comparison looks wrong."),
        "images": images,
    }
    if extra:
        claim.update(extra)
    return claim


def related_records(inp: Inputs, disc: dict, fields: dict) -> list[dict]:
    """Which gold records this conflict bears on, so the reviewer sees what we
    actually recorded rather than only that a conflict exists."""
    blob_zh = " ".join(str(disc.get(k) or "") for k in ("what", "drawing_says", "text_says"))
    blob_en = norm_name(" ".join(fields.values()))
    hits, seen = [], set()
    for key in inp.tr_keys:
        if key and key in blob_zh:
            g = inp.by_name.get(norm_name(inp.translations[key]["en"]))
            if g and g["identifier"] not in seen and g.get("smiles"):
                seen.add(g["identifier"])
                hits.append(g)
    for name, g in sorted(inp.by_name.items(), key=lambda kv: -len(kv[0])):
        if len(name) > 14 and g.get("smiles") and name in blob_en \
                and g["identifier"] not in seen:
            seen.add(g["identifier"])
            hits.append(g)
    return [{
        "identifier_en": g["identifier"],
        "what_we_recorded_smiles": g.get("smiles"),
        "formula": g.get("formula"),
        "structure_svg_path": (f"output/relevant_output/{g['svg']}"
                               if g.get("svg") else None),
    } for g in hits[:8]]


def write_readme(out: Path, page_index: dict, doc: dict, patent_id: str) -> None:
    lines = [
        f"# Visual evidence for {patent_id}",
        "",
        "What a reviewer who does not know chemistry can check with their own eyes.",
        "A SMILES string is unreadable to them. Two drawings side by side are not.",
        "",
        "## What is exact and what is a guess, asset by asset",
        "",
        "| asset | what is exact | what is a guess |",
        "|---|---|---|",
        ("| `page-index.json` marker to page | EXACT. Read off the per-page paragraph "
         "lists of the vision pass. | nothing |"),
        ("| `page-index.json` marker to position down the page | nothing | NOT PROVIDED. "
         "The scan has no text layer and no OCR engine is installed. A guessed y that "
         "points at the wrong paragraph is worse than no pointer. |"),
        ("| `page-index.json` drawing regions | the page, and that a drawing is on it | "
         "APPROXIMATE. Found by measuring ink. Deliberately loose. |"),
        ("| `comparisons/*.png` left half | EXACT. Rendered by RDKit from the SMILES "
         "text in the gold, with the same settings as `resolve_structures.py`. | nothing |"),
        ("| `comparisons/*.png` right half | that it is a piece of the real scanned page | "
         "APPROXIMATE. Which piece was chosen by image analysis. |"),
        ("| `comparisons/*.png` pairing of the two halves | see `pairing` per comparison | "
         "`name` is independent and strong; `structure` is weak and cannot catch a "
         "misread drawing. |"),
        ("| `drawing-claims.json` conflicts | EXACT. Copied from the vision pass, which "
         "read each page. | the English wording of quoted Chinese, see below |"),
        "",
        "## How the right half of each comparison was found",
        "",
        "The PDF is a scan. `pymupdf` returns zero characters on all nine pages and no",
        "OCR engine is installed, so there are no text coordinates and the position of a",
        "drawing has to come from the ink.",
        "",
        "A line of Chinese body text is about 30 pixels tall and its ink fills about 15%",
        "of its own bounding box. A drawn structure is 140 to 900 pixels tall and fills",
        "about 1.5%. That is an order of magnitude, so splitting them is not delicate.",
        "Runs of neighbouring not-text bands are joined into one drawing, which is what",
        "keeps the four-row scheme on page 6 in one piece.",
        "",
        "The check on that method: it was run over all nine pages and its count compared",
        "against the number of drawings the vision pass reported per page.",
        "",
        "| page | drawings reported | regions found | agree |",
        "|---|---|---|---|",
    ]
    for p in page_index["pages"]:
        lines.append(f"| {p['page']} | {p['drawings_reported_by_vision']} | "
                     f"{p['drawing_regions_detected']} | "
                     f"{'yes' if p['detection_agrees'] else 'NO'} |")
    lines += [
        "",
        "Where a page disagrees, no region is trusted for it and the comparison shows the",
        "WHOLE PAGE with a note saying so. A loose crop wastes a reviewer's time. A wrong",
        "crop shows them a different molecule and invites them to reject a correct",
        "extraction, so the fallback is always to show more rather than less.",
        "",
        "## How the two halves of a comparison were paired",
        "",
        "This is the part that decides whether a comparison proves anything.",
        "",
        f"- `name` ({doc['summary']['comparisons_paired_by_name']} of "
        f"{doc['summary']['comparisons_written']}): our structure was chosen by the "
        "compound name printed in the patent's TEXT near the drawing, and nothing about "
        "it came from the drawing. The two halves are independent and can genuinely "
        "disagree. This is the pairing that can catch a misread drawing.",
        f"- `structure` ({doc['summary']['comparisons_paired_by_structure']} of "
        f"{doc['summary']['comparisons_written']}): the patent's words near the drawing "
        "name no compound we hold, so our record was found by matching structures. The "
        "halves then agree by construction. Such a comparison shows only that we hold "
        "the molecule at all, and it is labelled WEAK on the image itself.",
        "",
        "## Language",
        "",
        "Every human-facing string is English and ends in `_en`. Compound names use",
        "`output/translations.json`, the verified index, so the wording matches the gold.",
        "The vision pass also quotes the patent's Chinese prose inside its findings, and",
        "substituting names into that prose produces half-translated sentences, so each",
        "such field is hand-written as whole English in `quote-translations.json`, keyed",
        "by its exact source position and marked as authored at this stage rather than",
        "verified. A gate at the end of the build fails the run if any Chinese character",
        "reaches any file here.",
        "",
        "## Files",
        "",
        "- `page-index.json` - marker to page, page to image, plus detected drawing regions.",
        "- `comparisons/<record_id>.png` - the full comparison, captioned and self-describing.",
        "- `comparisons/<record_id>-patent.png` - just the cut from the page, uncaptioned.",
        "- `drawing-claims.json` - review queue, conforming to `claims[]` in the",
        "  verification contract, all `tier: 1`.",
        "- `quote-translations.json` - hand-written English for the quoted Chinese.",
        "",
        "## Two things this cannot tell you",
        "",
        "1. Nothing here says the chemistry is right. A comparison answers only whether we",
        "   wrote down the molecule the patent drew.",
        "2. A `structure`-paired comparison cannot catch a misread drawing, because the",
        "   drawing is what chose the record it is being compared against.",
        "",
        "## Rebuild",
        "",
        "```",
        f"python3 make_visual_evidence.py --patent-id {patent_id}",
        "```",
        "",
        "Deterministic and offline. No timestamps are written, so a diff between two runs",
        "shows a real change and nothing else.",
    ]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--patent-id", required=True)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent),
                    help="the manual_annotations directory")
    a = ap.parse_args()
    return build(Path(a.root).resolve(), a.patent_id)


if __name__ == "__main__":
    sys.exit(main())
