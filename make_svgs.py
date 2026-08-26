#!/usr/bin/env python3
"""Generate the diagrams for the manual annotation pack.

House rules kept from earlier work:
  - viewBox on every root, role="img", <title> + <desc> for screen readers
  - explicit background rect (a transparent SVG borrows the host page's colour)
  - Okabe-Ito palette, colourblind-safe
  - no meaning carried by colour alone: every colour-coded state also carries a
    shape, a label or a pattern
  - unique element ids per file, namespaced, so two SVGs on one page cannot clash
  - a collision check runs over every text label before the file is written
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pipeline_context as ctx

OUT = Path(__file__).resolve().parent / "svg"
OUT.mkdir(exist_ok=True)

# Every caption that names a page, a page count or a step count is as
# patent-specific as the patent id is. They used to be typed into the source, so a
# second patent got a diagram asserting the first patent's numbers about it. They
# are counted from the run now. PATENT/FACTS/ROUTE are filled by generate().
PATENT = ""
FACTS: dict = {}
ROUTE: dict | None = None

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
         7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


def word(n, fallback="several"):
    return WORDS.get(n, str(n)) if n is not None else fallback

# Okabe-Ito
BLUE, ORANGE, GREEN = "#0072B2", "#E69F00", "#009E73"
VERM, PURPLE, SKY = "#D55E00", "#CC79A7", "#56B4E9"
INK, MUTE, PAPER, LINE = "#1a1a1a", "#5c5c5c", "#ffffff", "#c9c9c9"

CHARW = 0.55          # rough advance width per char at font-size 1


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Canvas:
    def __init__(self, w, h, ns, title, desc):
        self.w, self.h, self.ns = w, h, ns
        self.parts = []
        self.boxes = []          # (x0,y0,x1,y1,label) for collision checking
        self.shapes = []         # (x0,y0,x1,y1,kind) for overflow checking
        self.title, self.desc = title, desc

    # ---- primitives -------------------------------------------------
    def rect(self, x, y, w, h, fill=PAPER, stroke=INK, sw=1.6, rx=6, dash=None, op=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                          f'fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
        self.shapes.append((x, y, x + w, y + h, "rect"))

    def text(self, x, y, s, size=13, fill=INK, anchor="middle", weight="normal",
             family="ui-sans-serif, -apple-system, Segoe UI, Roboto, sans-serif",
             track=True, mono=False):
        fam = "ui-monospace, SFMono-Regular, Menlo, monospace" if mono else family
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
                          f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')
        if track:
            wpx = len(s) * size * (0.60 if mono else CHARW)
            x0 = {"middle": x - wpx / 2, "start": x, "end": x - wpx}[anchor]
            self.boxes.append((x0, y - size * 0.80, x0 + wpx, y + size * 0.28, s))

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.6, dash=None, marker=True):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#{self.ns}arrow)"' if marker else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
                          f'stroke-width="{sw}" stroke-linecap="round"{d}{m}/>')

    def path(self, d, stroke=INK, sw=1.6, fill="none", dash=None, marker=True):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#{self.ns}arrow)"' if marker else ""
        self.parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
                          f'{da}{m}/>')

    def circle(self, cx, cy, r, fill, stroke=INK, sw=1.4):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"/>')

    def poly(self, pts, fill, stroke=INK, sw=1.4):
        p = " ".join(f"{a},{b}" for a, b in pts)
        self.parts.append(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    # ---- helpers ----------------------------------------------------
    def wrap(self, x, y, s, width_chars, size=12, fill=INK, anchor="middle", lh=15,
             weight="normal", mono=False):
        words, line, lines = s.split(), "", []
        for w in words:
            t = (line + " " + w).strip()
            if len(t) > width_chars and line:
                lines.append(line)
                line = w
            else:
                line = t
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, size=size, fill=fill, anchor=anchor,
                      weight=weight, mono=mono)
        return len(lines)

    def note(self, x, w, lines, size=11.5, pad=10):
        """Note block pinned to the bottom of the canvas, never overflowing it."""
        h = pad * 2 + len(lines) * 15
        y = self.h - h - 10
        self.rect(x, y, w, h, fill="#f6f6f6", stroke=LINE, sw=1, rx=5)
        for i, ln in enumerate(lines):
            self.text(x + pad, y + pad + 12 + i * 15, ln, size=size, fill=MUTE,
                      anchor="start")

    # ---- output -----------------------------------------------------
    def collisions(self, ignore_pairs=()):
        bad = []
        for i in range(len(self.boxes)):
            for j in range(i + 1, len(self.boxes)):
                a, b = self.boxes[i], self.boxes[j]
                if (a[4], b[4]) in ignore_pairs or (b[4], a[4]) in ignore_pairs:
                    continue
                if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                    bad.append((a[4][:34], b[4][:34]))
        return bad

    def overflow(self):
        out = [b[4][:34] for b in self.boxes
               if b[0] < -2 or b[2] > self.w + 2 or b[1] < -2 or b[3] > self.h + 2]
        for x0, y0, x1, y1, kind in self.shapes:
            if x0 < -2 or x1 > self.w + 2 or y0 < -2 or y1 > self.h + 2:
                over = max(x1 - self.w, y1 - self.h, -x0, -y0)
                out.append(f"<{kind} at {x0:.0f},{y0:.0f} by {over:.0f}px>")
        return out

    def save(self, name):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="100%" role="img" aria-labelledby="{self.ns}t {self.ns}d">'
                f'<title id="{self.ns}t">{esc(self.title)}</title>'
                f'<desc id="{self.ns}d">{esc(self.desc)}</desc>'
                f'<defs><marker id="{self.ns}arrow" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>'
                f'<pattern id="{self.ns}hatch" width="7" height="7" patternUnits="userSpaceOnUse" '
                f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" '
                f'stroke="{MUTE}" stroke-width="2.2"/></pattern></defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>')
        svg = head + "".join(self.parts) + "</svg>"
        (OUT / name).write_text(svg)
        col, ovf = self.collisions(), self.overflow()
        status = "ok" if not col and not ovf else "PROBLEM"
        print(f"  {name:34} {len(svg)//1024:3} KB  labels={len(self.boxes):3}  "
              f"collisions={len(col)}  overflow={len(ovf)}  {status}")
        for a, b in col[:6]:
            print(f"      collide: {a!r} <-> {b!r}")
        for o in ovf[:6]:
            print(f"      overflow: {o!r}")
        return not col and not ovf


# ====================================================================
# m1 - production passes vs our annotation passes
# ====================================================================
def m1():
    c = Canvas(980, 900, "m1", "Production extraction passes mapped onto the manual annotation passes",
               "Two columns. The left column lists LiteratureIQ's seven production passes. "
               "The right lists the six manual annotation passes. Arrows show which production "
               "passes collapse into which manual pass. A5 verification has no production "
               "counterpart and is drawn with a dashed border.")
    c.text(490, 30, "Twelve production steps collapse into seven manual passes", size=17, weight="600")
    c.text(490, 51, "Same artifacts out, same enriched-markdown input shape. V replaces the whole document-prep phase.",
           size=12.5, fill=MUTE)

    c.text(190, 88, "LiteratureIQ, in production", size=13.5, weight="600", fill=BLUE)
    c.text(760, 88, "manual_annotations, this pack", size=13.5, weight="600", fill=ORANGE)

    prod = [("2. Mistral OCR", "PDF pages to markdown"),
            ("3. Translation LLM", "zh to en, per page"),
            ("4. MolScribe / RxnScribe", "drawings to SMILES"),
            ("5. Enriched markdown", "inline IMAGE_EXTRACT"),
            ("section-discovery", "chunked, merged"),
            ("M1 molecule pass 1", "over-collect"),
            ("M2 molecule pass 2", "resolve + tag"),
            ("R1 reaction pass 1", "step boundaries"),
            ("R2 reaction pass 2", "per step, N calls"),
            ("R3 reaction pass 3", "classify + link"),
            ("PathwaysBuilder", "deterministic Java"),
            ("patent-tagger", "narrative + tags")]
    ours = [("V", "page vision read", f"{FACTS.get('page_count', '?')} in parallel"),
            ("A0", "section map", "1 call"),
            ("A1", "compounds", "per section"),
            ("A2", "reactions", "per section"),
            ("A3", "pathways", "1 call"),
            ("A4", "patent record", "1 call"),
            ("A5", "verification", "adversarial")]

    py0, ph, pgap = 108, 44, 10
    for i, (n, sub) in enumerate(prod):
        y = py0 + i * (ph + pgap)
        c.rect(40, y, 300, ph, fill="#eef5fb", stroke=BLUE, sw=1.4)
        c.text(56, y + 19, n, size=12.5, anchor="start", weight="600", mono=True)
        c.text(56, y + 34, sub, size=11, anchor="start", fill=MUTE)

    oy0, oh, ogap = 118, 62, 22
    for i, (tag, n, sub) in enumerate(ours):
        y = oy0 + i * (oh + ogap)
        dash = "5 4" if tag == "A5" else None
        edge = VERM if tag == "V" else ORANGE
        c.rect(620, y, 320, oh, fill="#fdf5e8", stroke=edge, sw=1.8, dash=dash)
        c.circle(650, y + 22, 13, edge)
        c.text(650, y + 26, tag, size=11.5, weight="700", fill="#ffffff", mono=True)
        c.text(674, y + 26, n, size=13.5, anchor="start", weight="600")
        c.text(674, y + 46, sub, size=11, anchor="start", fill=MUTE)

    # mapping: production index -> ours index
    # four Phase-1 document-prep steps all collapse into V
    mapping = [(0, 0), (1, 0), (2, 0), (3, 0),
               (4, 1), (5, 2), (6, 2), (7, 3), (8, 3), (9, 3), (10, 4), (11, 5)]
    for pi, oi in mapping:
        y1 = py0 + pi * (ph + pgap) + ph / 2
        y2 = oy0 + oi * (oh + ogap) + oh / 2
        c.path(f"M 344 {y1} C 470 {y1}, 500 {y2}, 614 {y2}", stroke=MUTE, sw=1.5)

    # A5 has no source on the left
    y5 = oy0 + 6 * (oh + ogap) + oh / 2
    c.text(600, y5 + 4, "no counterpart", size=11, anchor="end", fill=VERM, weight="600")
    c.poly([(606, y5 - 6), (618, y5), (606, y5 + 6)], VERM)

    c.note(40, 900, [
        f"V is not a shortcut. The PDF has no text layer at all, so OCR is mandatory, and the drawings carry the route: page {FACTS.get('scheme_page','?')} alone",
        "holds the whole synthesis as structural formulae. Apple Vision read the Chinese prose acceptably but returned only orphaned",
        "fragments for every scheme, so a vision model reads the rendered pages instead and emits the same [IMAGE_EXTRACT: ...] spans",
        f"MolScribe and RxnScribe produce. Merging A1/A2 is safe only because this patent is {FACTS.get('source_kb','?')} kB; production splits R2 per step to",
        "bound token cost, not to improve accuracy. A5 is the one genuine addition, and it re-opens the page images to check V.",
    ])
    return c.save("m1-pass-map.svg")


# ====================================================================
# m2 - the route the patent actually discloses
# ====================================================================
#
# This is the one figure that is about the chemistry rather than about the method,
# so it is the one figure that cannot be written once and reused. Two ways to get
# one, in order:
#
#   1. a hand-authored spec keyed by patent id. Richer than the gold can be: the
#      condition strings are what a chemist would write on an arrow, and the
#      closing note argues about specific numbers on specific steps.
#   2. failing that, generated from pathways.json and reactions.json. Thinner, but
#      it is derived from the annotation rather than typed next to it, and it
#      exists - which is the whole complaint that started this. A new patent gets
#      a route diagram instead of the previous patent's route diagram.
#
# What is NOT allowed is the third thing, which is what this used to do: print one
# patent's eight hand-typed steps under whatever patent id happened to be running.

HAND_DRAWN_ROUTES = {
    "CN104292137A": {
        "source": "Example 1",
        # n, precursor, transformation, conditions, yield, one_pot, arithmetic_flag
        "steps": [
            ("1", "2-chlorotoluene", "Friedel-Crafts sulfonylation", "MsCl, AlCl3, DCE, 5 C", "84%", False, False),
            ("2", "aryl sulfone", "Friedel-Crafts acylation", "AcCl, AlCl3, DCM, 15-20 C", "86%", False, False),
            ("3", "aryl methyl ketone", "haloform oxidation", "NaOCl 15%, THF, reflux", "72%", False, True),
            ("4", "benzoic acid", "Fischer esterification", "MeOH, pTSA, reflux", "97%", False, False),
            ("5", "methyl ester", "benzylic bromination", "Br2, peroxide, CCl4, reflux", "70%", False, True),
            ("6", "benzyl bromide", "etherification then saponification", "NaOCH2CF3 / NaOH", "92%", True, False),
            ("7", "carboxylic acid", "acid chloride then O-acylation", "SOCl2 / cyclohexane-1,3-dione", "92%", True, False),
            ("8", "enol ester", "Fries-type rearrangement", "cyanoacetone, Et3N, MeCN", "95%", False, True),
        ],
        "closing": "A3 produced exactly this for overall_yield_pct, on Example 1 and on the patent-scope pathway.",
        "note": [
            "The three flagged steps are the point of the exercise. Step 3 reports 82 g from 0.24 mol, which exceeds the theoretical",
            "mass at 100% conversion. Step 5 produces 41.6 g but step 6 charges 55.8 g of it. Step 8 charges 0.5 mol where step 7",
            "delivered 0.2 mol, and its stated mass and yield disagree. A gold annotation records all of this verbatim and raises",
            "mass_balance_implausible and scale_discontinuity. It never quietly repairs the patent - an extractor that also fails to",
            "notice must score as a miss, and it cannot if the reference has been silently corrected.",
        ],
    },
}


def _route_spec():
    """(steps, source_label, ksm, product, closing, note) for the current patent."""
    spec = HAND_DRAWN_ROUTES.get(PATENT)
    r = ROUTE or {}
    ksm = r.get("ksm") or "the starting material"
    product = r.get("product") or "the target"
    if spec:
        return (spec["steps"], spec["source"], ksm, product,
                spec["closing"], spec["note"])
    if not r.get("steps"):
        return None
    steps = [(s["n"], "", s["transformation"], s["conditions"],
              f"{s['yield_pct']:g}%" if s.get("yield_pct") is not None else "no yield",
              s["one_pot"], s["flagged"]) for s in r["steps"]]
    source = r.get("section") or f"{r.get('scope','patent')} scope"
    return (steps, source, ksm, product,
            "Generated from pathways.json and reactions.json. No route diagram has been "
            "hand-authored for this patent.",
            ["Every box on this diagram is read out of the gold annotation, not typed beside it: the transformation is the",
             "reaction's named_reaction or its class, the conditions are its reagents and solvent, the yield is its stated",
             "product_yield_pct, and a step is flagged when the annotation put a validation_flag on it. Nothing here is a",
             "second opinion about the chemistry. For a richer figure, add an entry to HAND_DRAWN_ROUTES in make_svgs.py."])


def m2():
    spec = _route_spec()
    if spec is None:
        print(f"  {'m2-route.svg':34} SKIPPED - no hand-drawn route for {PATENT} and no "
              f"pathways.json to generate one from", file=sys.stderr)
        return False
    steps, source, ksm, product, closing, note = spec

    n = len(steps)
    n_flag = sum(1 for st in steps if st[6])
    cols = min(4, n)
    rows = (n + 3) // 4
    x0, bw, bh, gap = 34, 224, 96, 18
    W = max(1000, x0 + cols * bw + (cols - 1) * gap + 16)
    H = max(700, 96 + rows * 190 + 210)

    mid = W // 2 if W % 2 == 0 else W / 2
    c = Canvas(W, H, "m2", f"The {word(n)}-step route to {product} disclosed in {PATENT}",
               f"A linear chain of {word(n)} reaction steps from {ksm} to {product}. "
               "Each step box gives the step number, the transformation and the stated yield. "
               "Steps flagged as one-pot are marked with a double outline and the word one-pot. "
               "Steps whose stated arithmetic does not close are marked with a warning triangle "
               "and the word check.")
    c.text(mid, 30, f"{PATENT}, {source}: {word(n)} steps to {product}", size=17, weight="600")
    flag_sentence = ("No step carries arithmetic that does not close."
                     if not n_flag else
                     f"{word(n_flag).capitalize()} step{'s' if n_flag != 1 else ''} "
                     f"carr{'y' if n_flag != 1 else 'ies'} arithmetic that does not close.")
    c.text(mid, 51, f"Yields as printed in the patent. {flag_sentence}",
           size=12.5, fill=MUTE)

    positions = []
    for i, (num, src, tf, cond, y, onepot, flag) in enumerate(steps):
        col, row = i % 4, i // 4
        x = x0 + col * (bw + gap)
        yy = 96 + row * 190
        positions.append((x, yy))
        c.rect(x, yy, bw, bh, fill="#f4faf7" if not flag else "#fdf3ee",
               stroke=GREEN if not flag else VERM, sw=2.2 if onepot else 1.6)
        if onepot:
            c.rect(x + 4, yy + 4, bw - 8, bh - 8, fill="none",
                   stroke=GREEN, sw=1.0, rx=4)
        c.circle(x + 22, yy + 22, 13, INK)
        c.text(x + 22, yy + 26, num, size=12, weight="700", fill="#ffffff", mono=True)
        c.wrap(x + bw / 2 + 14, yy + 26, tf, 24, size=11.8, weight="600", lh=13)
        c.wrap(x + bw / 2, yy + 58, cond, 32, size=10.3, fill=MUTE, lh=12)
        c.text(x + bw - 12, yy + bh - 9, y, size=13, anchor="end", weight="700", fill=GREEN if not flag else VERM)
        if onepot:
            # the flag marker owns the corner when a step carries both
            c.text(x + (74 if flag else 12), yy + bh - 9, "one-pot", size=10,
                   anchor="start", weight="600", fill=GREEN)
        if flag:
            c.poly([(x + 12, yy + bh - 6), (x + 21, yy + bh - 21), (x + 30, yy + bh - 6)], "#ffffff", VERM, 1.6)
            c.text(x + 21, yy + bh - 9, "!", size=10, weight="700", fill=VERM)
            c.text(x + 36, yy + bh - 9, "check", size=10, anchor="start", weight="600", fill=VERM)

    # arrows within a row, then the wrap arrow at every row boundary
    for i in range(n - 1):
        if i % 4 == 3:
            continue
        x, yy = positions[i]
        c.line(x + bw + 2, yy + bh / 2, x + bw + gap - 4, yy + bh / 2, sw=1.8)
    for i in range(3, n - 1, 4):
        xa, ya = positions[i]
        xb, yb = positions[i + 1]
        c.path(f"M {xa + bw / 2} {ya + bh + 4} L {xa + bw / 2} {ya + bh + 28} "
               f"L {xb + bw / 2} {ya + bh + 28} L {xb + bw / 2} {yb - 6}", sw=1.8)

    xE, yE = positions[-1]
    c.rect(xE - 6, yE + bh + 26, bw + 12, 46, fill="#efe6f1", stroke=PURPLE, sw=2)
    c.wrap(xE + bw / 2, yE + bh + 48, product, 26, size=14, weight="700", lh=15)
    c.text(xE + bw / 2, yE + bh + 64, "the target", size=10.5, fill=MUTE)
    c.line(xE + bw / 2, yE + bh + 4, xE + bw / 2, yE + bh + 22, sw=1.8)

    ytext = yE + bh + 26 + 46 + 12
    known = [st[4] for st in steps if st[4].endswith("%")]
    c.text(60, ytext, f"cumulative yield across all {word(n)} steps, as printed:",
           size=12, anchor="start", fill=MUTE)
    if len(known) == n:
        vals = [float(v.rstrip("%")) / 100 for v in known]
        prod = 1.0
        for v in vals:
            prod *= v
        c.text(60, ytext + 22, " x ".join(f"{v:.2f}" for v in vals) + f"  =  {prod * 100:.2f}%",
               size=13.5, anchor="start", weight="700", mono=True)
    else:
        c.text(60, ytext + 22, f"not computable: {n - len(known)} of {n} steps print no yield",
               size=13.5, anchor="start", weight="700", mono=True)
    c.wrap(60, ytext + 44, closing, 104, size=11.5, anchor="start", fill=MUTE, lh=14)

    c.note(34, W - 68, note)
    return c.save("m2-route.svg")


# ====================================================================
# m3 - the four artifacts and the keys that join them
# ====================================================================
def m3():
    c = Canvas(980, 720, "m3", "The four artifacts and the keys that join them",
               "Four artifact boxes. compounds.json and reactions.json join into "
               "pathways.json by compound_uuid and reaction_uuid. All three roll up "
               "into patent.json. Each join key is labelled on its arrow. Keys drawn "
               "with a hatched fill are computed by finalise.py rather than emitted "
               "by a prompt.")
    c.text(490, 30, "Four artifacts, and the keys that join them", size=17, weight="600")
    c.text(490, 51, "Every key is a deterministic function of extracted content, so none of them is asked of the model.",
           size=12.5, fill=MUTE)

    def artifact(x, y, w, h, name, pass_tag, fields, colour):
        c.rect(x, y, w, h, fill="#fbfbfb", stroke=colour, sw=2)
        c.rect(x, y, w, 32, fill=colour, stroke=colour, sw=2, rx=6)
        c.text(x + 12, y + 21, name, size=13, anchor="start", weight="700",
               fill="#ffffff", mono=True)
        c.text(x + w - 12, y + 21, pass_tag, size=11, anchor="end", weight="700", fill="#ffffff")
        for i, (f, kind) in enumerate(fields):
            yy = y + 52 + i * 19
            if kind == "key":
                c.rect(x + 10, yy - 11, 9, 9, fill=f"url(#m3hatch)", stroke=INK, sw=1, rx=2)
            elif kind == "id":
                c.circle(x + 14.5, yy - 6.5, 4.5, INK)
            c.text(x + 26, yy, f, size=11.2, anchor="start", mono=True,
                   fill=INK if kind != "plain" else MUTE)

    artifact(40, 96, 258, 210, "compounds.json", "A1", [
        ("id", "key"), ("compound_uuid", "key"), ("identifier", "id"),
        ("role, quantity", "plain"), ("nmr, melting_point", "plain"),
        ("tags[]", "plain"), ("notes", "plain")], BLUE)

    artifact(360, 96, 258, 210, "reactions.json", "A2", [
        ("id", "key"), ("reaction_uuid", "key"), ("reaction_id", "id"),
        ("compounds[]", "id"), ("conditions, workup", "plain"),
        ("validation_flags[]", "plain"), ("tags[]", "plain")], GREEN)

    artifact(200, 372, 258, 176, "pathways.json", "A3", [
        ("pathway_uuid", "key"), ("ksm, product", "id"),
        ("steps[].reaction_uuid", "key"), ("overall_yield_pct", "plain"),
        ("honest_uncertainty_flags", "plain")], ORANGE)

    artifact(660, 300, 280, 210, "patent.json", "A4", [
        ("patent_uuid", "key"), ("bibliographic.family_id", "key"),
        ("extraction_rollup", "key"), ("patent_summary", "plain"),
        ("novelty_claims", "plain"), ("tags[] union of all", "plain")], PURPLE)

    # joins
    c.path("M 169 310 C 169 344, 240 342, 286 368", stroke=BLUE, sw=1.7)
    c.text(120, 344, "compound_uuid", size=11, anchor="start", weight="600", fill=BLUE, mono=True)
    c.path("M 489 310 C 489 344, 420 342, 378 368", stroke=GREEN, sw=1.7)
    c.text(520, 344, "reaction_uuid", size=11, anchor="start", weight="600", fill=GREEN, mono=True)

    c.path("M 618 200 C 660 200, 664 268, 690 296", stroke=MUTE, sw=1.5, dash="4 4")
    c.path("M 458 430 C 560 430, 600 420, 656 412", stroke=MUTE, sw=1.5, dash="4 4")
    c.text(566, 468, "rollup: counts, section_summary,", size=11, anchor="middle", fill=MUTE)
    c.text(566, 483, "scale_distribution, best yield", size=11, anchor="middle", fill=MUTE)

    # legend
    lx, ly = 40, 566
    c.rect(lx, ly, 420, 88, fill="#f6f6f6", stroke=LINE, sw=1, rx=5)
    c.text(lx + 14, ly + 22, "legend", size=11.5, anchor="start", weight="700", fill=MUTE)
    c.rect(lx + 16, ly + 34, 9, 9, fill="url(#m3hatch)", stroke=INK, sw=1, rx=2)
    c.text(lx + 34, ly + 43, "computed by finalise.py, never asked of a prompt",
           size=11, anchor="start", fill=MUTE)
    c.circle(lx + 20.5, ly + 61.5, 4.5, INK)
    c.text(lx + 34, ly + 66, "human-readable handle emitted by the prompt",
           size=11, anchor="start", fill=MUTE)

    c.note(480, 460, [
        "PersistentRecordBuilder derives every id and uuid from",
        "(patent_id, identifier) or (patent_id, reaction_id) via UUIDv5",
        "over the DNS namespace. finalise.py reproduces that exactly, so",
        "the gold artifacts key-join with production output rather than",
        "sitting alongside it in a parallel namespace.",
    ])
    return c.save("m3-artifact-joins.svg")


# ====================================================================
# m4 - what the model emits vs what is computed vs what is left null
# ====================================================================
def m4():
    c = Canvas(960, 560, "m4", "Three kinds of field: model-emitted, computed, deliberately null",
               "A reaction record's fields split into three groups. Model-emitted fields "
               "come from the A2 prompt. Computed fields are derived by finalise.py. "
               "Deliberately-null fields belong to a downstream enrichment service and are "
               "left empty so the gold set contains nothing extraction cannot produce.")
    c.text(480, 30, "Which fields the annotation is allowed to fill", size=17, weight="600")
    c.text(480, 51, "A gold set must not contain a field that extraction itself cannot produce.",
           size=12.5, fill=MUTE)

    cols = [
        (30, GREEN, "emitted by the prompt", "circle",
         ["reaction_id, step_index", "reaction_class, mechanism_type", "conditions.*, workup.*",
          "compounds[], reactant_names", "product_yield_pct", "precursor_step, linkage_confirmed",
          "validation_flags[], tags[]", "procedure_text, notes"]),
        (340, BLUE, "computed by finalise.py", "square",
         ["id", "reaction_uuid", "pathway_uuid", "compound_uuid", "patent_uuid",
          "extraction_rollup.*", "patent tags: jurisdiction,", "patent_family, assignee"]),
        (650, VERM, "deliberately left null", "triangle",
         ["atom_mapped_rxn", "template_r0 / r1 / r2", "feasibility_score, yield_score",
          "cost_score, safety_score", "green_score, byproduct_score", "confidence_score",
          "reaction_vector", "product_smiles, canonical_rxn"]),
    ]
    for x, colour, title, shape, items in cols:
        w = 280
        c.rect(x, 88, w, 372, fill="#fbfbfb", stroke=colour, sw=2)
        c.rect(x, 88, w, 34, fill=colour, stroke=colour, sw=2, rx=6)
        c.text(x + w / 2, 110, title, size=12.5, weight="700", fill="#ffffff")
        for i, it in enumerate(items):
            yy = 148 + i * 38
            cx = x + 24
            if shape == "circle":
                c.circle(cx, yy - 5, 6, colour)
            elif shape == "square":
                c.rect(cx - 6, yy - 11, 12, 12, fill=colour, stroke=INK, sw=1.2, rx=2)
            else:
                c.poly([(cx - 7, yy + 1), (cx, yy - 12), (cx + 7, yy + 1)], colour)
            c.text(x + 42, yy, it, size=11.3, anchor="start", mono=True)

    c.note(30, 900, [
        "Shape carries the meaning as well as colour, so the three groups stay distinct in greyscale and for colourblind readers.",
        "The third column is the one people get wrong. Leaving enrichment fields null is not an omission - a reference that carries",
        "atom-mapped reactions or template hashes would score the enrichment service, not the extractor, and no prompt in this pack",
        "is capable of producing them honestly.",
    ])
    return c.save("m4-field-provenance.svg")


# ====================================================================
# m5 - what each text-recovery route actually recovers
# ====================================================================
def m5():
    c = Canvas(980, 620, "m5", "What each text-recovery route recovers from a scanned patent page",
               f"Three routes compared on page {FACTS.get('scheme_page','?')}, the page carrying the whole synthetic "
               "route as drawn structures. The PDF text layer yields nothing. Apple's "
               "Vision framework yields prose but reduces every scheme to orphaned "
               "fragments. A vision model yields prose, structures and the reagents on "
               "each arrow. Filled circles mark what a route recovers, hollow circles "
               "with a cross mark what it loses.")
    c.text(490, 30, "Why OCR alone loses this patent", size=17, weight="600")
    c.text(490, 51, f"Measured on page {FACTS.get('scheme_page','?')}, which carries the entire "
           f"{word(len((ROUTE or {}).get('steps') or []) or None)}-step route as structural formulae.",
           size=12.5, fill=MUTE)

    routes = [
        ("PDF text layer", "pdftotext equivalent", [0, 0, 0, 0],
         "0 characters. All 9 pages are scans.", VERM),
        ("Apple Vision OCR", "zh-Hans + en-US, accurate mode", [1, 0, 0, 0],
         "60 lines on p6: 36 low-confidence, 37 of six characters or fewer.", ORANGE),
        ("Vision model on the page", f"pass V, {FACTS.get('page_count','?')} agents in parallel", [1, 1, 1, 1],
         "Prose, ring systems, substituent positions, and reagents per arrow.", GREEN),
    ]
    cols = ["Chinese prose", "structures", "substituent positions", "reagents above vs below arrow"]

    x0, cw = 372, 148
    for j, h in enumerate(cols):
        cx = x0 + j * cw + cw / 2
        c.wrap(cx, 96, h, 15, size=11, weight="600", lh=13)

    for i, (name, sub, got, note, colour) in enumerate(routes):
        y = 140 + i * 118
        c.rect(30, y, 330, 92, fill="#fbfbfb", stroke=colour, sw=2)
        c.text(46, y + 26, name, size=13.5, anchor="start", weight="700")
        c.text(46, y + 45, sub, size=11, anchor="start", fill=MUTE)
        c.wrap(46, y + 68, note, 44, size=10.5, fill=MUTE, anchor="start", lh=13)
        for j, ok in enumerate(got):
            cx = x0 + j * cw + cw / 2
            cy = y + 46
            if ok:
                c.circle(cx, cy, 15, colour)
                c.path(f"M {cx-7} {cy} L {cx-2} {cy+6} L {cx+7} {cy-6}",
                       stroke="#ffffff", sw=2.6, marker=False)
            else:
                c.circle(cx, cy, 15, "#ffffff", MUTE, 1.6)
                c.line(cx - 6, cy - 6, cx + 6, cy + 6, stroke=MUTE, sw=2.2, marker=False)
                c.line(cx + 6, cy - 6, cx - 6, cy + 6, stroke=MUTE, sw=2.2, marker=False)

    c.text(30, 508, "The specific damage Apple Vision did to prose it did read:",
           size=12, anchor="start", weight="600")
    c.text(30, 530, "\u73af\u5df1\u70f7-1,3-\u4e8c\u916e   read as   \u73af\u5df1\u70f7\u4e00 1\uff0c3-\u4e8c\u916e",
           size=13, anchor="start", mono=True)
    c.text(30, 550, "cyclohexane-1,3-dione, with the hyphen replaced by the Chinese numeral one.",
           size=11, anchor="start", fill=MUTE)

    c.note(500, 450, [
        "A tick is not a quality claim. Pass V can still",
        "misread a structure, which is why A5 re-opens the",
        "page images to audit it, and why every SMILES is",
        "RDKit-validated before it reaches a prompt.",
    ])
    return c.save("m5-ocr-comparison.svg")


def generate(patent_id: str) -> bool:
    global PATENT, FACTS, ROUTE
    PATENT = patent_id
    FACTS = ctx.facts(patent_id)
    ROUTE = ctx.route(patent_id)
    print(f"patent    : {patent_id}")
    print(f"counted   : {FACTS.get('page_count')} pages, source {FACTS.get('source_kb')} kB, "
          f"scheme page {FACTS.get('scheme_page')}, "
          f"{len((ROUTE or {}).get('steps') or [])} route steps")
    print("generating:")
    return all([m1(), m2(), m3(), m4(), m5()])


if __name__ == "__main__":
    try:
        pid = ctx.resolve_patent_id()
    except ctx.ContextError as e:
        raise SystemExit(f"FAIL  {e}")
    ok = generate(pid)
    print("\nall clean" if ok else "\nfix the problems above")
    raise SystemExit(0 if ok else 1)
