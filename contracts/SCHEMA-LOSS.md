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

---

# Addendum: the mass-balance failures are two causes, not eight findings

Found by reading the exported report as its recipient, then verified here.

The engine prints an "implied" molecular weight for each failing mass check and labels
each one "Unexplained offset", queueing eight separate items for a human.

**All eight implied values are exact integers to three decimal places.**

    implied    true    offset
    170.000  204.680  +34.68
    212.000  246.710  +34.71
    214.000  248.690  +34.69
    218.000  262.710  +44.71
    302.000  346.710  +44.71
    396.000  440.820  +44.82
    279.000  341.610  +62.61
    180.000  159.810  -20.19   (bromine, already known)

Eight integers do not happen by chance. **The patent computed with rounded, integer
molecular weights**, which means the raw offsets are contaminated by up to half a unit
of rounding and should never be read as chemical differences directly.

Correct for that and the first band becomes exact. Take the true molecular weight,
subtract Cl minus H = 34.445, and round:

    204.68 - 34.445 = 170.235  ->  170   the patent's implied value
    246.71 - 34.445 = 212.265  ->  212   the patent's implied value
    248.69 - 34.445 = 214.245  ->  214   the patent's implied value

**Three for three.** That is not "consistent with a chlorine-for-hydrogen
substitution", it is a demonstration that the patent computed those three masses from
the integer molecular weight of the des-chloro analogue.

The second band is consistent and unexplained. Removing the same rounding leaves a
residual of about 44.46, 44.46 and 44.57 on three steps. That is not a single chlorine
and this document does not guess at it. It is one question for a chemist, not three.

## Why this matters more than the arithmetic

The report presented these as **eight** unexplained items for a reviewer to read one at
a time. They are **two** questions: one already answered by the project's own notes,
and one genuinely open. A chemist would see the clustering in about fifteen seconds and
wonder why the tool did not.

Worse, the answer was already in the project. `RESUME.md` records "3 consistent with
Cl-for-H" and the exported report contains **zero occurrences of the string Cl-for-H**.
An explanation the team already had did not reach the deliverable.

**Group findings by their shared cause before listing them.** Eight items at maybe
thirty seconds each is four minutes of a fifteen-minute budget spent rediscovering one
pattern. Two grouped questions is under a minute, and the second one is the only one
that actually needs a human.


---

# The offset is confined to the aromatics, and that localises it

Measured over every Example 1 compound carrying both a mass and a mole count, with the
molecular weight computed from the resolved structure.

    compound                                       aromatic   implied     true     diff
    aluminium trichloride                                no    135.00   133.34    +1.66
    bromine                                              no    180.00   159.81   +20.19
    2-chloro-6-(methylsulfonyl)toluene                  YES    170.00   204.68   -34.68
    2-chloro-3-acetyl-6-(methylsulfonyl)toluene         YES    212.00   246.71   -34.71
    2-chloro-3-methyl-4-(methylsulfonyl)benzoic acid    YES    214.00   248.69   -34.69
    methyl ...-3-methyl-4-(methylsulfonyl)benzoate      YES    218.00   262.71   -44.71
    methyl ...-3-(bromomethyl)-...-benzoate             YES    279.00   341.61   -62.61
    2-chloro-3-[(trifluoroethoxy)methyl]-...-acid       YES    302.00   346.71   -44.71
    3-oxo-1-cyclohexen-1-yl ...-benzoate                YES    396.00   440.82   -44.82

**Every aromatic intermediate is short. Both non-aromatic reagents are not.**

Aluminium trichloride at +1.66 is rounding: the patent computed with 135 where the true
weight is 133.34. Bromine at +20.19 is the separate, already-known defect - 39.6 g
recorded as 220 mmol when 39.6 g of Br2 is 247.8 mmol.

So the patent's arithmetic is not uniformly wrong. **It is wrong precisely on the
chlorinated aromatic intermediates it makes, and right on the reagents it buys.** That
is a much more specific claim than "the mass balances do not close", and it is what
makes the des-chloro reading credible rather than merely arithmetically available: a
transcription error would not sort itself by aromaticity.

Within the aromatics the offsets fall into three groups:

    -34.68, -34.71, -34.69    exactly Cl minus H at 34.445, plus integer rounding
    -44.71, -44.71, -44.82    a consistent residual near 44.5, unexplained
    -62.61                    one outlier, the bromomethyl compound

The first group is demonstrated rather than suggested: subtract 34.445 from the true
weight and round, and you get the patent's implied value exactly, three times running.
The second and third are for a chemist. This document does not guess at them.
