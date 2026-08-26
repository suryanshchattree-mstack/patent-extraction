#!/usr/bin/env python3
"""One poster diagram of the whole approach, plus a JPG of it.

Kept separate from make_svgs.py because this is the summary artefact rather than
one of the explanatory figures.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_svgs import (Canvas, BLUE, ORANGE, GREEN, VERM, PURPLE, SKY,
                       INK, MUTE, PAPER, LINE, OUT)

W, H = 1460, 800


def approach():
    c = Canvas(W, H, "ap", "How the gold annotation of CN104292137A was built",
               "A left-to-right pipeline of six stages: a scanned PDF with no text "
               "layer, vision agents reading the rendered pages, assembly into "
               "enriched markdown in production's format, five extraction passes, "
               "deterministic post-processing, and four adversarial audits. Below, "
               "the discarded OCR branch, the resulting gold set, and the three "
               "findings only a vision pass reaches.")

    c.text(W / 2, 40, "How the gold annotation was built", size=25, weight="700")
    c.text(W / 2, 68, "CN104292137A  ·  9 scanned pages  ·  zero text layer  ·  DOCDB family 52312131",
           size=13, fill=MUTE)

    stages = [
        ("1", "The input", VERM, [
            "9-page CNIPA scan",
            "0 characters of text",
            "the route is drawn,",
            "not written",
        ], "there is nothing to parse"),
        ("2", "Look at it", ORANGE, [
            "render 200 dpi PNG",
            "9 vision agents,",
            "one per page,",
            "reading pixels",
        ], "not OCR: OCR loses the drawings"),
        ("3", "Assemble", SKY, [
            "verbatim zh + [00NN]",
            "+ inline",
            "[IMAGE_EXTRACT:...]",
            "spans, RDKit-checked",
        ], "byte-for-byte production's format"),
        ("4", "Extract", BLUE, [
            "A0 sections",
            "A1 compounds",
            "A2 reactions",
            "A3 pathways · A4 patent",
        ], "our own prompts, their schemas"),
        ("5", "Compute", GREEN, [
            "ids, uuids, rollup",
            "biblio merge",
            "reproducing",
            "PersistentRecordBuilder",
        ], "never ask a model for a join key"),
        ("6", "Attack it", PURPLE, [
            "4 audits, fresh context,",
            "re-opening the page",
            "images, told to assume",
            "the work is wrong",
        ], "this is what makes it gold"),
    ]

    x0, cw, gap, cy, ch = 34, 208, 28, 100, 214
    centres = []
    for i, (n, title, colour, body, why) in enumerate(stages):
        x = x0 + i * (cw + gap)
        centres.append(x + cw / 2)
        c.rect(x, cy, cw, ch, fill="#fcfcfc", stroke=colour, sw=2.2)
        c.rect(x, cy, cw, 38, fill=colour, stroke=colour, sw=2.2, rx=6)
        c.circle(x + 24, cy + 19, 12, "#ffffff", colour, 1.6)
        c.text(x + 24, cy + 23, n, size=12, weight="700", fill=colour, mono=True)
        c.text(x + 44, cy + 24, title, size=14, anchor="start", weight="700", fill="#ffffff")
        for j, ln in enumerate(body):
            c.text(x + 14, cy + 66 + j * 21, ln, size=11.4, anchor="start")
        c.line(x + 12, cy + 156, x + cw - 12, cy + 156, stroke=LINE, sw=1, marker=False)
        c.wrap(x + cw / 2, cy + 176, why, 30, size=10.6, fill=MUTE, lh=13)
        if i < len(stages) - 1:
            c.line(x + cw + 3, cy + ch / 2, x + cw + gap - 5, cy + ch / 2, sw=2)

    # ---- discarded branch, hanging off stage 2 -------------------------------
    bx, by = centres[1] - 122, cy + ch + 44
    c.path(f"M {centres[1]} {cy + ch + 4} L {centres[1]} {by - 6}",
           stroke=MUTE, sw=1.6, dash="5 4")
    c.rect(bx, by, 244, 76, fill="#f7f7f7", stroke=MUTE, sw=1.4, dash="5 4")
    c.text(bx + 14, by + 24, "tried and discarded", size=11.5, anchor="start",
           weight="700", fill=MUTE)
    c.text(bx + 14, by + 43, "Apple Vision OCR, zh-Hans", size=11, anchor="start", fill=MUTE)
    c.text(bx + 14, by + 60, "read the prose, lost every scheme", size=11, anchor="start", fill=MUTE)
    cx2 = bx + 244 - 22
    c.circle(cx2, by + 40, 15, "#ffffff", VERM, 1.8)
    c.line(cx2 - 6, by + 34, cx2 + 6, by + 46, stroke=VERM, sw=2.4, marker=False)
    c.line(cx2 + 6, by + 34, cx2 - 6, by + 46, stroke=VERM, sw=2.4, marker=False)

    # ---- what came out ------------------------------------------------------
    ry = by + 108
    c.text(34, ry, "What came out", size=15, anchor="start", weight="700")
    c.line(34, ry + 10, W - 34, ry + 10, stroke=LINE, sw=1, marker=False)

    results = [("75", "compounds"), ("33", "reactions"), ("5", "pathways"),
               ("1", "patent record"), ("18", "structures read\noff the drawings"),
               ("28.40%", "cumulative yield,\nExample 1")]
    rx, rw = 34, 190
    for i, (num, lab) in enumerate(results):
        x = rx + i * (rw + 14)
        c.rect(x, ry + 24, rw, 84, fill="#f4faf7", stroke=GREEN, sw=1.6)
        c.text(x + rw / 2, ry + 60, num, size=25, weight="700", fill=GREEN)
        for j, part in enumerate(lab.split("\n")):
            c.text(x + rw / 2, ry + 82 + j * 14, part, size=10.8, fill=MUTE)

    c.rect(rx + 6 * (rw + 14), ry + 24, 152, 84, fill="#fdf3ee", stroke=VERM, sw=1.6)
    c.text(rx + 6 * (rw + 14) + 76, ry + 60, "24 / 33", size=21, weight="700", fill=VERM)
    c.text(rx + 6 * (rw + 14) + 76, ry + 82, "reactions carry a", size=10.4, fill=MUTE)
    c.text(rx + 6 * (rw + 14) + 76, ry + 96, "validation flag", size=10.4, fill=MUTE)

    # ---- the payoff ---------------------------------------------------------
    fy = ry + 138
    c.text(34, fy, "Three findings that only a pass which looks at the page can reach",
           size=15, anchor="start", weight="700")
    c.line(34, fy + 10, W - 34, fy + 10, stroke=LINE, sw=1, marker=False)

    finds = [
        ("The molar masses are des-chloro",
         "Every printed mass/mole pair across Example 1 implies a weight ~34.5 lower "
         "than the compound named and drawn. That is exactly Cl-for-H. The reagent "
         "charges are all correct; only the chlorinated aromatics carry the offset."),
        ("The drawn route is not the written one",
         "The scheme starts from 2,6-dichlorotoluene with CH3SNa, which the text says "
         "the invention replaced, and contains an oxidation it says was eliminated. "
         "Yet it also uses Br2, claimed as the invention's own improvement."),
        ("The catalyst is drawn as (CH3)2C(CN)OH",
         "Acetone cyanohydrin, drawn. The text names cyanoacetone, a different "
         "molecule. Nothing that reads only characters could ever see this."),
    ]
    fw = 456
    for i, (t, b) in enumerate(finds):
        x = 34 + i * (fw + 12)
        c.rect(x, fy + 24, fw, 116, fill="#fbfbfb", stroke=PURPLE, sw=1.6)
        c.circle(x + 22, fy + 48, 12, PURPLE)
        c.text(x + 22, fy + 52, str(i + 1), size=12, weight="700", fill="#ffffff", mono=True)
        c.wrap(x + 42, fy + 52, t, 40, size=12.4, weight="700", anchor="start", lh=14)
        c.wrap(x + 16, fy + 82, b, 66, size=10.5, fill=MUTE, anchor="start", lh=13)

    c.text(W / 2, H - 14,
           "Nothing was corrected. Where the patent does not close, the numbers are recorded as printed and a flag is raised.",
           size=11, fill=MUTE)
    return c.save("approach.svg")


if __name__ == "__main__":
    print("generating:")
    raise SystemExit(0 if approach() else 1)
