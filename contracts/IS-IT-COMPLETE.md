# Is the tembotrione extraction complete?

The question this project was set: for CN104292137A, is the annotation of the chemistry
complete. Answered 2026-08-27, verified independently rather than taken from the
pipeline's own reporting.

## The answer

**Yes on coverage. No on fidelity, and the losses are in the schema and the translation
rather than in the extraction.**

Nothing was invented and nothing chemistry-bearing was skipped. Nineteen facts that the
patent states are not recoverable from the extracted record, and none of them were lost
by the extractor: eight are a schema with one slot for two values, four are a translation
that dropped a qualifier, and the rest are the same two causes elsewhere.

## What "complete" was tested to mean, and how each was checked

**1. Is anything fabricated?  No.**
All 12 `not_found` records hand-checked against the source. Zero claims state a value
that is absent from the patent. The same holds across all six alternative extraction runs.

**2. Is any quantity dropped?  No.**
Every quantity token on every cited line is accounted for. One correction to an earlier
sweep: my first pass harvested numbers from quoted text as well as structured fields and
reported zero misses. The strict version found ten candidates; reading all ten left one
real, a 16 h that the schema could not hold.

**3. Are all the worked examples covered?  Yes, and there is only one.**
The patent contains exactly one example, 实施例1. There is no 实施例2, no 对比例 and no
制备例. All eight of its steps are extracted, with quantities. This is worth stating
because "examples covered" sounds like a sampling question and here it is not one.

**4. Is the whole route covered?  Yes, four times over.**
The patent states its route in the claims, in the summary, in a drawn scheme and in
Example 1. All four are extracted, 33 reaction records in total. See
`ONE-ROUTE-TOLD-FOUR-TIMES.md`.

**5. Was any part of the document never looked at?  No part that carries chemistry.**
This is the check that had not been done, and it is the one that could have overturned
everything above: verifying "every quantity on every cited line" cannot distinguish a
complete extraction from one that never opened a section.

Of 116 lines containing Chinese in the numbered source, 41 are cited by no record. Every
one of the 41 was classified and read:

    13   bibliographic front matter (application number, applicant, inventors, agent)
    12   compound-name gloss lines added by the enrichment pass
     8   page markers, which are HTML comments
     4   section headings
     2   section lead-ins carrying no chemistry
     1   prior-art comparator and weed genus names
     1   an English gloss line whose Chinese original IS cited

**Zero chemistry-bearing lines are uncited.**

## What is lost, and by what

**The schema loses 12 facts the extraction captured.** `conditions.time_h` is a single
float, so a step running 16 h then 4 h holds 4.0, and eight records that print a range
hold null. Three tickets. `SCHEMA-LOSS.md`.

**The translation loses 7 more**, two of them with chemical consequences:

- 500 g of **15%** hypochlorite recorded as 500 g of hypochlorite. A haloform oxidation
  needs three equivalents; unqualified, the number reads as 28.
- **Anhydrous** aluminium trichloride recorded as aluminium trichloride. Anhydrous is not
  a description of the reagent, it is a statement about whether the step works.

The second of these now has a check. It did not when it shipped.

**75 compound records are 61 substances.** Not merging is a correct and documented
decision, not a defect.

## Two things that are wrong and are not ours

**The patent's own arithmetic does not close, and it sorts by aromaticity.** Every
Example 1 aromatic intermediate implies a molecular weight short of the true value; both
non-aromatic reagents are clean. Three of the seven offsets are exactly
`true MW - (Cl - H)` at 34.445, to the rounding limit. Four are not, and this document
does not explain them: three share a consistent residual near 10.3 and one is the
bromomethyl outlier. A rival explanation, sulfone read as thioether, was tested and
refuted. **Three of seven explained, four open.**

**The patent's drawn scheme contradicts its own text.** The scheme draws a thioether
route that [0031] says the invention eliminates, and the final-step reagent is
cyanoacetone in three tellings and acetone cyanohydrin in the drawn one. The extraction
caught both, flagged `drawing_text_conflict`, and refused to invent the missing oxidant.

## The honest limit on all of this

Everything above is about whether the extraction faithfully represents the document. None
of it establishes that the document is right, and none of it is a substitute for a chemist
reading the route. The one number that matters for that is delivery, not detection:
**of four defects planted in a lab copy, one reached a reviewer.** Fixes landed since that
measurement and it is being re-run; until that finishes, one in four is the number to
quote. `DELIVERY-TEST.md`.

Detection has been consistently stronger than any hand spot-check of it predicted. Three
separate things I went looking for this session turned out to be already caught, already
classified and already phrased for a non-chemist. The weakness in this system has never
been what it notices. It is what it manages to hand to a person.
