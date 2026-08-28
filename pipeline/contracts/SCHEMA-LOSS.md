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

---

# Addendum, 2026-08-27: the Cl-for-H reading tested against a rival, and what it does not explain

A second candidate arrived after the aromaticity note was written, so the conclusion had
to be re-tested rather than assumed to still hold.

## Where the rival came from

The `Summary of the Invention Scheme` telling of the route puts SMILES strings in the
`product_name` field for steps 1 and 2, and those SMILES are **methylthio**, not
methylsulfonyl:

    Scheme step 1   CSc1cccc(Cl)c1C          CS... = CH3-S-      thioether
    Scheme step 2   CSc1ccc(C(C)=O)c(Cl)c1C

The other three tellings say methyl**sulfonyl** at the same steps. Sulfone to thioether
is a loss of two oxygens, 31.998, which is close enough to the observed 34.7 to be worth
testing as an alternative to Cl minus H at 34.445.

## The test

Residual after subtracting each candidate from the true molecular weight. The patent
prints integers, so anything within about 0.5 is a fit and anything beyond it is not.

    compound                                       implied     true    Cl->H   SO2->S
    2-chloro-6-(methylsulfonyl)toluene              170.00   204.68    -0.23    -2.68
    2-chloro-3-acetyl-6-(methylsulfonyl)toluene     212.00   246.71    -0.27    -2.72
    2-chloro-3-methyl-4-(methylsulfonyl)benzoic ac  214.00   248.69    -0.24    -2.69
    methyl ...-3-methyl-4-(methylsulfonyl)benzoate  218.00   262.71   -10.27   -12.72
    methyl ...-3-(bromomethyl)-...benzoate          279.00   341.61   -28.17   -30.61
    2-chloro-3-[(trifluoroethoxy)methyl]-...acid    302.00   346.71   -10.26   -12.71

**The rival is refuted.** Sulfone to thioether leaves 2.68 to 2.72 on the three compounds
it would have to explain, which is five times the rounding budget. Cl minus H leaves 0.23
to 0.27 on the same three, inside it. The original reading survives a real challenge.

## What this addendum takes back

The three-for-three claim is correct and stays, but it was doing more work in the earlier
write-up than it should have. It covers the **first group only**.

The second group does not fit Cl minus H either:

    218, 302 and 396 leave a residual of -10.27, -10.26 and -10.38

Three compounds agreeing to within 0.12 is a pattern, not noise, and nothing in this
document explains it. No single-atom or single-group substitution I tested lands on
10.3. The bromomethyl compound at -28.17 is a third case and also unexplained.

So the honest state of the mass defect is:

    3 compounds    explained    Cl-for-H, demonstrated to the rounding limit
    3 compounds    unexplained  a consistent ~10.3 residual after Cl-for-H
    1 compound     unexplained  the bromomethyl outlier

Anyone reporting this must not round it up to "the mass defect is explained". Three of
seven are. The other four are a named, measured, still-open question, and the consistency
of the ~10.3 across three compounds is a lead rather than a conclusion.

---

# Addendum 2, 2026-08-27: a second arithmetic, and what it settles

The engine runs a second mass check that I had not used: product mass against the charge
and the stated yield, rather than a compound's own mass/mole pair. It takes the yield
figure as a new input, so it is partly independent of the first. Running it over Example 1:

    st  product                                mass_g  chg_mmol  yld%  implied     true   offset   after Cl-for-H
     1  2-chloro-6-(methylsulfonyl)toluene       28.6       200    84   170.24   204.68   -34.44     +0.01
     2  2-chloro-3-acetyl-6-(methylsulfonyl)..   36.5       200    86   212.21   246.71   -34.51     -0.06
     3  2-chloro-3-methyl-4-(methylsulfonyl)..   82.0       240    72   474.54   248.69  +225.85   see below
     4  methyl ..-3-methyl-4-(methylsulfonyl)..  44.2       200    97   227.84   262.71   -34.88     -0.43
     5  methyl ..-3-(bromomethyl)-..             41.6       200    70   297.14   341.61   -44.47    -10.02
     6  2-chloro-3-[(trifluoroethoxy)methyl]..   55.6       200    92   302.17   346.71   -44.54    -10.09
     7  3-oxo-1-cyclohexen-1-yl ..               72.8       200    92   395.65   440.82   -45.17    -10.73
     8  tembotrione                             188.0       500    95   395.79   440.82   -45.03    -10.59

## What it settles

**Cl-for-H is corroborated, tightly.** Steps 1 and 2 come back at +0.01 and -0.06 after
subtracting 34.445. A second calculation over partly different inputs landing within
0.06 of the first is much harder to explain as an artefact of how one formula was written
than three clean hits from a single calculation were.

**The second band is real.** Steps 5, 6, 7 and 8 give -10.02, -10.09, -10.73 and -10.59.
Four values inside 0.71 of each other, from an independent arithmetic, on the same steps
where the first calculation found a consistent residual near 10.3. It is a pattern, not
noise, and **it is still unexplained.** No single-atom or single-group substitution I have
tested lands on 10.3. Recording it as a measured open question rather than reaching for a
reading that fits three of the four.

**The two arithmetics disagree about two compounds, and each fits exactly three.**

CORRECTION, and the error is mine. An earlier version of this section said "three by one
arithmetic and four by the other". That four was the UNION across both checks, not either
check's own count, and lane-report caught it while building the report off this file rather
than using a different number quietly. Recomputed:

    compound                                   true  m/mol resid  m/c*y resid  seen by
    2-chloro-6-(methylsulfonyl)toluene       204.68       -0.23        +0.01  both
    2-chloro-3-acetyl-6-(methylsulfonyl)tol  246.71       -0.27        -0.06  both
    2-chloro-3-methyl-4-(msulfonyl)benzoic   248.69       -0.24            -  m/mol only
    methyl ..-3-methyl-4-..benzoate          262.71      -10.27        -0.43  both
    methyl ..-3-(bromomethyl)-..benzoate     341.61      -28.17       -10.02  both
    2-chloro-3-[(trifluoroethoxy)m]benzoic   346.71      -10.26       -10.09  both
    3-oxo-1-cyclohexenyl ..benzoate          440.82      -10.38       -10.73  both
    tembotrione                              440.82           -        -10.59  m/c*y only

An earlier version of this table showed only the first six rows, which understated the
picture: the two checks see **eight** compounds between them, six of which both can read.
Caught by lane-report while building the report off this file. Fit means within 0.5 of
Cl-for-H, so the fits are rows 1, 2 and 3 on mass/mole and rows 1, 2 and 4 on the second.

The last two rows carry the same molecular weight because they are isomers: the Fries
rearrangement converts the enol ester to the C-acylated dione without changing the
formula. That is chemistry, not a duplicated row.

    fit by mass/mole             3
    fit by mass/(charge x yield) 3
    fit by BOTH                  2
    fit by EITHER, the union     4

So the honest sentence is: **each arithmetic fits three, they agree about two, and four
distinct compounds fit somewhere.** Not "three and four".

**Two compounds change group depending on which arithmetic weighs them**, not one:

    methyl ..-3-methyl-4-..benzoate     open band  ->  Cl-for-H
    methyl ..-3-(bromomethyl)-..        outlier    ->  open band

The benzoic acid can only ever be classified by mass and moles, because step 3's product
mass is impossible and no mass/charge/yield reading of it means anything.

**That is an ABSENCE, not a conflict, and the difference matters.** Two compounds genuinely
conflict: both checks return a number and the numbers land in different groups. The benzoic
acid is a third case where one check simply cannot speak. Reading it as a disagreement
would invent a conflict where there is nothing to disagree with. Tembotrione is the mirror,
readable only by the second check.

    8 compounds across both checks, 6 readable by both
    2 real conflicts   the methyl ester and the bromomethyl ester
    2 absences         the benzoic acid (m/mol only), tembotrione (m/c*y only)

## Step 3 is not an offset, it is impossible

Line 206 charges 50.88 g (0.24 mol) of the acetyl compound and reports 82 g of the acid at
72% yield.

The charge is consistent with everything else here: 50.88 / 0.24 = 212.0, which is the
Cl-for-H implied weight for that compound, 246.71 - 34.445 = 212.27.

The product is not consistent with anything. The acid's true weight is 248.69 and its
des-chloro reading is 214.2. **0.24 mol at 100% yield is at most 59.7 g of the true
compound or 51.4 g of the des-chloro one.** The patent claims 82 g at 72%. That is not a
molecular weight discrepancy, it is more product than the charge can supply, and no reading
of the molecular weight rescues it.

This is already caught. `CN104292137A_Example_1_Step_3`, field `yield_identity`, asks a
reviewer directly: "Does the page really print 82 g of 2-chloro-3-methyl-4-(methylsulfonyl)
benzoic acid from 240 mmol at 72%?" The check found it without needing any of the analysis
above.

## Standing count

    3 by each     explained by Cl-for-H; the two checks agree about 2 and 4 compounds
                  fit somewhere. Not "3 or 4" and never "4 by one check".
    4 of 8        a consistent residual near 10.3, confirmed twice, unexplained
    1             bromine, over rather than short, a separate case
    1             step 3, arithmetically impossible rather than merely offset

Nobody should report this as "the mass defect is explained".

## The container test, measured: it ate the only quantity in a patent

This file already records that `finalise.py:merge_compound` ends with

    elif v not in (None, "", [], {}):
        out[k] = v

and that an all-null dict is not equal to `{}`, so it survives the test and overwrites
a populated value from an earlier section. Until `EP2045236A1` that was a described
hazard. Here is what it costs.

`EP2045236A1` states exactly one mass in the whole document: 2 g of tembotrione,
charged in each of its three worked examples. `tembotrione` is recorded in 19 sections.
Three carry the real `quantity` with `mass_g: 2.0`. The other sixteen carried
`{"mass_g": null, "volume_ml": null, "mmol": null, "equivalents": null,
"yield_pct": null}`, and `merge_compound` walks the sections in alphabetical filename
order, so `formulation-...`, `mixtures-...`, `suitability-...` and `table-...` all sort
after `example-...`.

Measured on the merged deliverable:

    compound records in output/relevant_output/gold/compounds.json
    carrying a mass_g:  0

Every quantity in the patent, gone. The engine then failed its own sensitivity test,
"a found mass_g claim exists to corrupt", because there was no found mass claim left in
the gold to corrupt. That is the only reason it surfaced at all: no check anywhere
compares a merged record against the section records it came from, so on a patent with
several masses the loss would have been partial and invisible.

**The fix needed no code change.** A1 rule 17 already says "Set every characterisation
field you cannot support to `null`. An empty object is not the same as null; use null."
Writing `null` makes `v` `None`, the branch is skipped, and the populated value
survives. 21 files were converted and the repair was verified by importing the real
`merge_compound` and merging all 25 section files for `tembotrione`: the 2.0 survives.

So rule 17 is not a style preference. It is the only thing standing between this branch
and silent data loss, and it was written before anyone knew that.

**The blast radius is narrower than it looks, and worth stating precisely.**
`_UNION = ("aliases", "tags", "analytics")` and that branch reads
`existing.get(k) or []`, which treats `[]` and `None` identically. So an empty
`analytics` or `aliases` never overwrote anything. **The damage is `quantity` alone**,
because it is a plain dict outside `_UNION`. Any future plain-dict field added to a
compound record inherits the same hazard.

`runs/CN104292137A` and `runs/CN109678767A` have not been checked for the same loss.
