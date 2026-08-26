# All 12 `not_found` claims, hand-checked

Engine run of 2026-08-27 over CN104292137A: 416 claims, 314 found, 12 not_found,
10 partial, 80 not_checkable, 102 needing a human.

`not_found` is the hallucination signal, so every one of the 12 was checked by hand
against the source. The headline:

> **No value in this annotation is fabricated.** Every `not_found` is either a derived
> field the checker treated as if it were quoted, or a citation pointing a few lines
> away from the text that supports it. Nothing was invented.

That is a strong result for the annotation and it should be said plainly. It is also
the reason the checker needs the three-way split below rather than one verdict.

## Group A - derived, not quoted. FALSE ALARM. 3 of 12.

Claims 1, 11 and 12: `overall_yield_pct = 28.4%` and `best_overall_yield_pct = 28.4%`.

The string "28.4" appears NOWHERE in the source. It is computed. Example 1 states
eight step yields and their product is exactly 28.40%:

    84 x 86 x 72 x 97 x 70 x 92 x 92 x 95  ->  28.40%

So the value is correct and correctly derived, and the checker was asking the wrong
question. This is the same class as `mmol`, which is also never quoted and always
derived from mass and molecular weight.

**Rule.** A derived field gets a DERIVATION check, never a grounding check. Infer the
classification from the data rather than hardcoding a field list: a field where no
value appears literally across all records is derived. Then it holds for the next
patent, whose conventions may differ.

## Group B - right value, wrong paragraph cited. TRUE but minor. 5 of 12.

Claims 2 to 6, all `molar_ratio_text` on Summary-of-the-Invention step records.

Example. The step 1 record cites lines 117-120, which are paragraphs [0006] and
[0007], the Summary's account of step 1. The ratio `1:1-3:1-2` is real and is in the
same section, but it is stated in paragraph [0022] on line 154, and again in claim 2
on line 77. The record never cites either.

So the fact is right and the pointer is off by a few paragraphs. A reader tracing the
provenance lands somewhere that does not support the claim, which is exactly the
failure this tool exists to catch, but it is not an invented number.

## Group C - quote does not come from the cited line. TRUE but minor. 4 of 12.

Claims 7 to 10, all Summary-of-the-Invention SCHEME steps citing line 174.

Line 174 is `[IMAGE_EXTRACT: {...}]`, the machine-readable reading of the drawn
scheme. Citing it for a scheme step is correct. But the `quote` field on these records
holds prose borrowed from nearby lines: 168 ("The reaction equations involved in the
present invention are as follows"), 176 (the beneficial-effects paragraph), and one
that splices two fragments from lines 74 and 113.

So the citation is right and the quote is loose. Arguably the defect is that a scheme
record has a prose quote at all.

## What this means for the queue

Three severities, and they must not share one label:

| group | severity | what a reviewer should do |
|---|---|---|
| A, derived | none | should never have been shown to them |
| B, wrong paragraph | low | fix the citation; the fact stands |
| C, quote off the cited line | low | fix the quote or drop it; the citation stands |
| a fabricated value | critical | none found in this patent |

A queue that shows all four as "not found in the patent" trains the reviewer to
discount the label, and the label is the only thing standing between the team and a
fabricated number in a future run. Keep the severity distinct so that when a real
fabrication does appear, it does not arrive wearing the same badge as a citation that
is four paragraphs out.
