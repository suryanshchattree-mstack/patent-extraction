# Visual evidence for CN104292137A

What a reviewer who does not know chemistry can check with their own eyes.
A SMILES string is unreadable to them. Two drawings side by side are not.

## What is exact and what is a guess, asset by asset

| asset | what is exact | what is a guess |
|---|---|---|
| `page-index.json` marker to page | EXACT. Read off the per-page paragraph lists of the vision pass. | nothing |
| `page-index.json` marker to position down the page | nothing | NOT PROVIDED. The scan has no text layer and no OCR engine is installed. A guessed y that points at the wrong paragraph is worse than no pointer. |
| `page-index.json` drawing regions | the page, and that a drawing is on it | APPROXIMATE. Found by measuring ink. Deliberately loose. |
| `comparisons/*.png` left half | EXACT. Rendered by RDKit from the SMILES text in the gold, with the same settings as `resolve_structures.py`. | nothing |
| `comparisons/*.png` right half | that it is a piece of the real scanned page | APPROXIMATE. Which piece was chosen by image analysis. |
| `comparisons/*.png` pairing of the two halves | see `pairing` per comparison | `name` is independent and strong; `structure` is weak and cannot catch a misread drawing. |
| `drawing-claims.json` conflicts | EXACT. Copied from the vision pass, which read each page. | the English wording of quoted Chinese, see below |

## How the right half of each comparison was found

The PDF is a scan. `pymupdf` returns zero characters on all nine pages and no
OCR engine is installed, so there are no text coordinates and the position of a
drawing has to come from the ink.

A line of Chinese body text is about 30 pixels tall and its ink fills about 15%
of its own bounding box. A drawn structure is 140 to 900 pixels tall and fills
about 1.5%. That is an order of magnitude, so splitting them is not delicate.
Runs of neighbouring not-text bands are joined into one drawing, which is what
keeps the four-row scheme on page 6 in one piece.

The check on that method: it was run over all nine pages and its count compared
against the number of drawings the vision pass reported per page.

| page | drawings reported | regions found | agree |
|---|---|---|---|
| p01 | 0 | 1 | NO |
| p02 | 0 | 0 | yes |
| p03 | 0 | 0 | yes |
| p04 | 0 | 0 | yes |
| p05 | 0 | 0 | yes |
| p06 | 2 | 2 | yes |
| p07 | 3 | 3 | yes |
| p08 | 3 | 3 | yes |
| p09 | 1 | 1 | yes |

Where a page disagrees, no region is trusted for it and the comparison shows the
WHOLE PAGE with a note saying so. A loose crop wastes a reviewer's time. A wrong
crop shows them a different molecule and invites them to reject a correct
extraction, so the fallback is always to show more rather than less.

## How the two halves of a comparison were paired

This is the part that decides whether a comparison proves anything.

- `name` (8 of 9): our structure was chosen by the compound name printed in the patent's TEXT near the drawing, and nothing about it came from the drawing. The two halves are independent and can genuinely disagree. This is the pairing that can catch a misread drawing.
- `structure` (1 of 9): the patent's words near the drawing name no compound we hold, so our record was found by matching structures. The halves then agree by construction. Such a comparison shows only that we hold the molecule at all, and it is labelled WEAK on the image itself.

## Language

Every human-facing string is English and ends in `_en`. Compound names use
`output/translations.json`, the verified index, so the wording matches the gold.
The vision pass also quotes the patent's Chinese prose inside its findings, and
substituting names into that prose produces half-translated sentences, so each
such field is hand-written as whole English in `quote-translations.json`, keyed
by its exact source position and marked as authored at this stage rather than
verified. A gate at the end of the build fails the run if any Chinese character
reaches any file here.

## Files

- `page-index.json` - marker to page, page to image, plus detected drawing regions.
- `comparisons/<record_id>.png` - the full comparison, captioned and self-describing.
- `comparisons/<record_id>-patent.png` - just the cut from the page, uncaptioned.
- `drawing-claims.json` - review queue, conforming to `claims[]` in the
  verification contract, all `tier: 1`.
- `quote-translations.json` - hand-written English for the quoted Chinese.

## Two things this cannot tell you

1. Nothing here says the chemistry is right. A comparison answers only whether we
   wrote down the molecule the patent drew.
2. A `structure`-paired comparison cannot catch a misread drawing, because the
   drawing is what chose the record it is being compared against.

## Rebuild

```
python3 make_visual_evidence.py --patent-id CN104292137A
```

Deterministic and offline. No timestamps are written, so a diff between two runs
shows a real change and nothing else.
