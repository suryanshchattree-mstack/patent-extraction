# Is the annotation complete? What can actually be shown

Measured against CN104292137A on 2026-08-27, by hand, independently of the engine
that produced the artifact. Every number here was recomputed rather than read off a
report.

## The two questions

A reviewer asking "is this extraction complete" is really asking two things, and they
need different evidence:

1. **Did we invent anything?** (precision)
2. **Did we miss anything?** (recall)

Most verification effort goes to the first because it is easier. The second is the one
that costs money when it is wrong, and it is the one nothing in the pipeline could
answer until now.

## 1. Did we invent anything? No.

416 claims. 12 came back `not_found`. All 12 were hand-checked against the source and
none is a fabricated value. See `NOT-FOUND-TRIAGE.md`. In summary:

    3   a derived field checked as if it were quoted. 28.4% is the product
        of the eight step yields the patent states, exactly.
    5   a real molar ratio cited to the wrong paragraph of the right section
    4   a correct citation to the drawn scheme, with a quote borrowed from
        adjacent prose
    0   a value that is not in the patent

## 2. Did we miss anything? Not at line level, and not at quantity level.

**Line coverage.** 256 source lines, 222 cited by at least one record, 34 not. Of the
34, fourteen are blank and seven are page headings. The thirteen remaining content
lines were read individually and every one is a section title ("Technical field",
"Background art", "Specific embodiments"), a paragraph marker, the scheme lead-in
("The reaction equations involved in the present invention are as follows:"), or the
boilerplate sentence that the examples do not limit the invention.

**No uncited line carries chemistry.** That was checked two ways: against the engine's
signal detector, and by reading all thirteen.

**Quantity coverage, which is the stronger test.** Line coverage is not fact coverage:
a line can be cited by one record while carrying three facts, two of them dropped. So
every quantity token on every cited line was extracted and matched against the values
the claims assert.

The first pass of this reported zero unaccounted tokens. That pass was WRONG, and
generously so: it harvested numbers out of quoted text as well as out of structured
fields, so a "16" appearing anywhere inside any quote counted as coverage of a 16-hour
reaction time. Redone strictly, against only the values claims structurally assert:

    distinct values asserted as structured claims    66
    quantity tokens on cited lines with no claim     10

Those ten were then read one at a time, which is the only step that makes the number
mean anything:

    3 h, 1 h, 2 h      NOT REAL. My regex read the "3H" of an NMR proton count
                       ("2.64 (s, 3H)") as three hours. Six occurrences, all NMR.
    0.22 mol, 0.3 mol  NOT REAL, and the same mistake twice. The source prints mol,
    0.23, 0.6, 0.24    the annotation stores mmol, and my test compared rendered
                       strings instead of quantities. 0.22 mol IS recorded, as
                       220 mmol. This also means my earlier claim that `mmol` is a
                       derived field was WRONG: it is quoted, in mol, 29 of 29
                       present once the comparison is unit-aware.
    250 ml             NOT REAL, and arguable. It is the size of the flask, not a
                       charge. `reactor_type` records "four-necked flask" without
                       its capacity, so the glassware size is dropped everywhere.
    16 h               REAL, and the interesting one. See below.

So: **one genuine loss out of 256 quantity tokens, and it is a schema limitation
rather than an extraction failure.**

## The one real loss, and why it matters more than its size

Example 1 step 6 is one numbered step containing two sequential transformations in the
same flask: etherification with sodium trifluoroethoxide at room temperature for
**16 h**, then hydrolysis with sodium hydroxide at reflux for **4 h**.

`conditions.time_h` is a single float. It holds 4.0. The 16 h survives only in the
record's prose `notes`, where the annotator wrote the two stages out in full and
explicitly flagged it as "THE FIRST OF THE TWO ONE-POT STEPS".

The annotator did everything right. The SCHEMA cannot represent it.

This is worth stating carefully, because it cuts against the assumption that keeping
the JSON schemas fixed is what preserves information. Here the schema is what loses
it. A downstream consumer reading `time_h` sees a four-hour step; the real answer is
twenty hours across two stages, and the difference is a factor of five on the most
expensive input to any throughput or cost model. The information is not gone, but it
has moved to prose, where nothing downstream can read it.

There are nine `no_conditions` reactions and two one-pot steps in this patent, so this
is unlikely to be the only instance. It is the first thing I would look at before
running a second patent through.

## What this does NOT establish

Say this plainly wherever the numbers are quoted, because the temptation to round it
up to "the extraction is correct" will be strong.

- Matching is by VALUE, not by attachment. It shows no quantity was ignored. It does
  not show each quantity was attached to the right compound. "25.3 g" being present in
  the annotation somewhere is not evidence that it was attached to 2-chlorotoluene.
  **That is precisely what the human reviewer is for, and it is why the tool exists.**
- Nine of the twelve `not_found` are real provenance defects. Minor, but real: someone
  tracing the evidence lands somewhere that does not support the claim.
- Non-numeric content is out of scope here. Reagent roles, reaction classes, solvent
  identities and conditions without numbers are not covered by a quantity sweep. The
  80 `not_checkable` claims are largely this, and no string match will ever settle
  them.
- One patent. Nothing here generalises until a second one has been through.

## The honest headline

> Nothing in this extraction was invented, and no quantity in the patent was dropped.
> Whether each quantity is attached to the right molecule is the open question, and it
> is the one a human still has to answer.
