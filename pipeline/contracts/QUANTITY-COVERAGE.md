# Quantity coverage: did we take what was on the line

The recall check that line coverage cannot perform, specified rather than described,
so it can be reimplemented from this document alone.

Measured against CN104292137A. Every rule below removed a false alarm that a version
without it produced, and the false alarm is named beside the rule, because a rule
whose motivation is lost gets deleted by the next person as an unnecessary special
case.

## Why it exists

Line coverage answers *did any record look at this line*. It cannot answer *did any
record take what was on it*. A line can be cited by one record while carrying three
facts with two of them dropped, and `uncited_with_chemistry` still reads zero.

On this patent line coverage returns a complete and empty census: 222 of 256 lines
cited, and not one uncited line carries chemistry. That is a true result and it is
also the weaker of the two questions. Quantity coverage over the same corpus finds
fifteen quantities the annotation does not hold.

## The algorithm

1. **Collect what is asserted.** Walk every claim. Keep only those with a non-null
   `claimed_value` AND a non-null `claimed_unit`. Index them by every line in
   `cited_lines` as a set of `(canonical unit, canonical value)`.

2. **Walk every cited line.** For each, tokenise the raw source text into
   `(value, unit)` pairs.

3. **Reduce to blocks.** A Chinese line and the English it was translated into are
   one block (see `SOURCE-PAIRING.md`). Deduplicate `(unit, value)` per block, so
   one printed quantity is counted once rather than twice.

4. **Match.** A token is accounted for when its `(canonical unit, canonical value)`
   appears in the union of what any record citing any line of that block asserts.

5. **Classify what is left.** Glassware first, then merge ranges, then resolve which
   field would have held it and why it did not.

## Rule 1: match against structured fields, never against quoted text

**This is the rule the check lives or dies by.**

Harvesting numbers out of `quote_zh`, `procedure_text` or `notes` as well as out of
`claimed_value` makes every quantity trivially covered, because the quotations
reproduce the source. A "16" occurring anywhere inside any quotation then counts as
coverage of a sixteen-hour reaction time. The sweep returns a clean zero and the zero
means nothing.

A first pass written that way reported zero unaccounted tokens on this patent. The
strict pass finds fifteen.

The reason is structural, not incidental: the whole point of the check is to find
facts that reached prose but not fields, and prose is exactly where they went.

## Rule 2: only tokens carrying a unit are quantities

A bare number is a locant (`2-chlorotoluene`), a ring label (`CDCl3`), an index
(`[0035]`), a date (`2015.01.21`), an IPC code (`C07C 317/24`) or an NMR proton count
(`3H`). Sweeping bare numbers reports the whole of Example 1 as dropped.

Units that count: `g`, `ml`, `mmol`, `%`, `C`, `h`, after canonicalisation.

**This also disposes of the NMR trap without an NMR exclusion.** A regex that reads
`2.64 (s, 3H)` as three hours produces six false alarms on this patent. Requiring a
unit removes them by construction, because `H` is not a unit. A tokeniser that also
refuses to attach a unit across a letter boundary never forms the token at all:

    "3H"        bare 3, next character is a letter  ->  no token
    "2.64(s,"   bare 2.64, next character is "("    ->  token, no unit, ignored

Excluding NMR *lines* as well is defensible belt-and-braces, but it is the weaker
mechanism: it depends on recognising the line, and a shift table without the letters
`NMR` above it would slip through.

## Rule 3: matching is unit-aware, and conversion happens before comparison

The source prints `25.3g(0.2mol)`. The annotation stores `mass_g: 25.3` and
`mmol: 200`. Comparing rendered strings, or comparing numbers without converting,
reports every molar amount in the patent as unrecorded: five false alarms, and worse,
the wrong conclusion that `mmol` is a derived field the patent never states.

It is not. It is quoted, in mol, 29 of 29 present once the comparison converts.

Canonicalisation used:

| printed | canonical |
|---|---|
| `kg`, `g`, `mg` | g |
| `L`, `ml` | ml |
| `mol`, `mmol` | mmol |
| `h`, `hr`, `hrs`, `min` | h |
| `%` | % |
| `℃`, `°C`, `degrees C`, `deg C` | C |

Compare with a relative epsilon (1e-6), not equality. `0.2 mol` becomes
`200.00000000000003 mmol` in binary floating point.

## Rule 4: a range is one fact

`回流反应1-10h` is a single statement. Queueing its endpoints separately hands a
reviewer one row for the 1 and another for the 10, doubling the queue to say one
thing twice. On this patent that is sixteen rows where eight are correct.

Tokenise ranges as ranges (so that the unit on the high end attaches to both
endpoints), then merge endpoints sharing a block and a unit into one entry carrying
both ends before anything is queued.

The merge also fixes a subtler problem: without it, `15-20℃` yields a bare 15 and a
20 with a unit, and a claim of `min_c: 15` reads as a value whose unit is not printed.

## Rule 5: glassware is not a charge

`500ml四口反应瓶` is a 500 ml four-necked reaction flask. The volume is the size of
the vessel, and `reactor_type` records the flask without its capacity, so every
glassware size in the document is unrecorded everywhere.

Six occurrences on this patent. Real, in that the number is genuinely not held; not
worth a second of a fifteen-minute review budget.

Detection: a token in `ml` whose following twelve characters contain a vessel word.
Count it, report the count, never queue it.

    vessel words: 反应瓶 反应容器 反应釜 四口 三口 烧瓶
                  flask reactor vessel autoclave necked

Counting rather than silently dropping matters: if a patent is ever written where the
charge really is stated as the flask volume, the count is the only thing that would
show it.

## Rule 6: a percentage is a yield or a concentration by its context, never by which field is free

`36％HCl` is the strength of the acid. `收率92％` is a yield. The schema has a
different field for each.

Choosing the holder by which field happens to be empty misdiagnoses this: on Example
1 step 6, `product_yield_pct` holds 92 and `conditions.concentration` is empty, so a
free-field rule assigns the 36% to the yield field, finds it occupied, and reports a
false second stage. The true finding is that the acid strength was dropped.

Decide from the twelve characters before the token:

    yield words: 收率 产率 得率 yield

Everything else is a concentration.

## Rule 7: say the quantity back in the unit the page prints

Line 227 says `滴加时间约50min`. Canonicalised that is 0.8333 h. Rendering it to the
reviewer as **"50 h"** is the matcher lying about the document, and it is the kind of
error that destroys trust in every other row on the screen.

Carry the raw unit alongside the canonical one on every token. Compare in canonical
units, display in printed units.

## Rule 8: attribute the loss to the record that could have fixed it

Several records cite any given line. Prefer the reaction record, because a reaction
owns the conditions of its own step while a compound record citing the same line owns
only its own row. Break ties on the lowest record id, so the choice is a function of
the inputs and the artifact is reproducible.

Then ask that record's schema what would have held the token, and what is in it.

## The four verdicts

The output is not one number. It is four, and the four need different fixes. This is
the part that makes the check worth running rather than merely worth counting.

| verdict | condition | `about` | what fixes it |
|---|---|---|---|
| `schema_loss_range` | the token is part of a range and the field is a single scalar with no min/max counterpart | `schema` | widen the schema |
| `schema_loss_second` | the field exists and already holds a different value | `schema` | make the field a list |
| `gap` | the field exists and is empty | `extraction` | re-extract |
| `unmapped` | no field of that kind on any record citing the line | `extraction` | design question |

The range test must consult the field's arity, not just the token's shape.
`conditions.temperature` carries `min_c` and `max_c` and CAN hold "15-20 degrees", so
a range missing there is an extraction gap. `conditions.time_h` is one float and
cannot hold "1-10 h" at all, so the same shape of loss there is the schema's fault.
Collapsing the two loses the only distinction the check exists to draw.

## Measured on CN104292137A

    126  distinct quantities on cited lines
     96  asserted by a claim
      6  glassware, counted and never queued
     12  schema could not hold it
      3  field exists and is empty

The twelve schema losses:

    8   a reaction time printed as a range, against a single-float `time_h`.
        Claims steps 2, 4, 5, 6 and Summary steps 2, 4, 5, 6.
        1-5h, 1-10h, 1-10h, 1-4h. Every one of those eight records holds null
        and says so in its own notes.

    4   a second stage of a one-pot step, against a single-slot field.
        Example 1 step 1   value_c 5.0,  the 10 degrees C addition ceiling dropped
        Example 1 step 5   time_h 6.0,   the 50 min addition time dropped
        Example 1 step 6   time_h 4.0,   16 h of etherification dropped
        Example 1 step 7   time_h 8.0,   the 6 h reflux dropped

Example 1 step 6 is the one worth quoting to anyone who has to be convinced this
matters. One numbered step, two transformations in one flask: etherification at room
temperature for 16 h, then hydrolysis at reflux for 4 h. `time_h` holds 4.0 and the
16 h survives only in the record's prose notes. A consumer reads a four-hour step
where the truth is twenty hours over two stages. That is a factor of five on the most
expensive input to any throughput or cost model, and re-running the extraction would
not fix it, because the annotator did everything right.

The three gaps:

    line 46         0-15 degrees C, Claims Step 1, `conditions.temperature` empty.
                    Deliberate: the provenance records that the printed 0℃-15℃ is
                    numerically ambiguous (0 to 15, or 0 down to -15) and was left
                    unresolved. Worth a human's eye anyway, because Summary Step 1
                    DID record 0 and 15 for the same printed range. Two records of
                    one step disagree about whether it is recordable.
    lines 236, 253  36% HCl, `conditions.concentration` empty. The strength of the
                    workup acid is dropped. Minor and real.

## What this does NOT establish

Say this wherever the 96 of 126 is quoted, because the temptation to round it up to
"the extraction is correct" is strong.

**Matching is by VALUE, not by attachment.** It shows no quantity was ignored. It
does not show each quantity was attached to the right compound. "25.3 g" being
present somewhere in the annotation is not evidence that it was attached to
2-chlorotoluene rather than to the aluminium trichloride beside it. That is precisely
what the human reviewer is for, and it is why the tool exists.

Two smaller limits, for completeness:

- Deduplication is per block and per value. Two reagents charged at the same amount
  on one line are one token, so one of them being claimed covers both. Correct for
  the coverage question and another face of the attachment limit.
- Non-numeric content is out of scope. Reagent roles, reaction classes, solvent
  identities and conditions without numbers are untouched by a quantity sweep.

## Implementation notes

Where it sits in the pass order: after every claim has been built, because it reads
`claimed_value` off finished claims; before anything that scores or tiers them,
because it adds claims of its own.

What it needs that is not otherwise kept:

- `record_id -> the gold dict the record was built from`, so the verdict logic can
  ask a record which of its fields would have held a number. That is a question
  about the gold shape rather than about anything the engine keeps.
- the folded form of the line on each token, so the glassware and yield context tests
  can look at the characters around the token after full-width folding.

Output shape: each unaccounted quantity becomes a tier-2 claim with
`field: "__quantity__[<line>:<value><unit>]"`, `auto: "not_checkable"` and a
`quantity_verdict`, plus a check on the record in family `schema_loss` or
`completeness`. `summary.quantity_coverage` carries the tally and every finding.

`auto` is `not_checkable` and deliberately not `not_found`. `not_found` means the
annotation asserts something the source does not support, and it is the only signal
in the artifact that means that. A quantity going the other way, present in the
source and absent from the annotation, is the recall side and belongs in tier 2.
Letting it borrow the `not_found` badge would cost the badge the one thing that makes
it worth reading.

## The standing rule this document is an instance of

Run the check, read every failure by hand, and only then report the count.

The first version of this sweep reported 30 unaccounted tokens. Reading all 30 found
three defects in the sweep itself: a canonical unit rendered where a printed unit
belonged, a concentration misdiagnosed as a yield, and range endpoints queued twice.
Fixing those took 30 to 15 with no loss of signal, because all fifteen survivors are
real.

A number nobody has read the failures behind is not evidence.
