# The schema is where this pipeline loses information

Measured over CN104292137A, 2026-08-27. Every number here was verified by hand against
the gold and the source.

## Why this document exists

The working assumption on this project has been that keeping the JSON schemas fixed is
what protects information: change them and you lose something important.

For this patent the opposite is true. **The extraction did not lose anything. The
schema did.** Of 126 distinct quantities printed on cited source lines:

    96   asserted by some claim
     6   glassware capacity, not a charge
    12   SCHEMA LOSS: the fact is real, and no field can hold it
     3   an extraction gap: a field exists and is empty

Zero were invented and zero were ignored. Twelve were understood, written down in
prose, and then dropped on the floor by the shape of the JSON.

## The 12, and the eight that share one cause

**Eight are ranges against a single-float `time_h`.** Claims steps 2, 4, 5 and 6, and
Summary steps 2, 4, 5 and 6, each print a reaction time as a range: `1-5h`, `1-10h`,
`1-10h`, `1-4h`. `conditions.time_h` is one float. So all eight hold `null`.

I checked all eight in the gold. Every one documents the loss in its own `notes`:

> "the claim states 1-10h, a range that time_h cannot hold as a single float, so
> time_h is null and the range is recorded here"

> "继续反应1-10h is a range, so time_h is null. catalyst_class is skipped rather than
> guessed"

**The annotator hit this eight times and wrote it down eight times.** Nobody was
careless. The field simply cannot represent the fact, and the only place left to put
it was prose that nothing downstream reads.

**Four are second stages of a one-pot step.**

    Example 1 step 6   time_h 4.0    the 16 h first stage dropped
    Example 1 step 7   time_h 8.0    the 6 h reflux dropped
    Example 1 step 5   time_h 6.0    the 50 minute addition dropped
    Example 1 step 1   value_c 5.0   the "not exceeding 10 degrees C" ceiling dropped

Step 6 is the one I found by hand. Step 7 is the second one-pot step. A single-valued
`time_h` cannot hold "16 hours at room temperature, then 4 hours at reflux" any more
than it can hold "1 to 10 hours".

## The size of it

`time_h` is null on **25 of 33 reactions**. Eight of those are documented range losses.
So on this patent the reaction time, which is one of the most load-bearing numbers in
any throughput or cost model, is absent from three quarters of the reaction records,
and in a third of the absences the patent plainly states it.

Anything downstream reading `time_h` on Example 1 step 6 sees a four-hour step. The
answer is twenty hours across two stages. That is a factor of five, on the input that
compounds hardest through a route.

## What would fix it

Eleven of the twelve close with one change:

    conditions.time_h: float | null
      ->
    conditions.time: { min_h, max_h, stages: [ { hours, temperature, note } ] } | null

`conditions.temperature` already has `min_c` and `max_c` and can hold a range, which is
why the temperature losses are only one of the twelve rather than nine. The precedent
for the fix is already inside the same object.

## The rule this suggests

A quantity check must consult the FIELD's arity, not the token's shape. A range printed
where the field has `min` and `max` is an extraction gap and someone should fix the
extractor. The same range printed where the field is one float is the schema's fault
and no amount of reviewing will close it.

Collapsing those two cases loses the only distinction the check exists to draw, and it
puts a reviewer in front of a claim they cannot act on: nothing here can be marked
wrong. It is a schema ticket, not a review decision.

## What this does NOT say

Matching is by VALUE, not by attachment. The 96 accounted-for quantities show that no
quantity was ignored. They do not show that each was attached to the right compound.
That remains the reviewer's job and it remains the reason the tool exists.
