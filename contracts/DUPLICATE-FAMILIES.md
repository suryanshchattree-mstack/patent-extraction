# 75 compound records, 58 to 61 substances

The audit's one CRITICAL outstanding finding, measured independently.

## What is there

    gold compound records                                        75
    Chinese names resolving to MORE THAN ONE English identifier   12
    surplus records if every family collapsed                     17
    substances implied                                            58

The cause is one word rendered three ways. 甲磺酰基 comes out as `methanesulfonyl`,
`methylsulfonyl`, and unbracketed `methylsulfonyl`, depending on which section the
record was extracted from, so the merge key never matches and one substance becomes
three records with three different join keys:

    2-氯-6-甲磺酰基甲苯  ->  2-chloro-6-(methanesulfonyl)toluene
                            2-chloro-6-(methylsulfonyl)toluene
                            2-chloro-6-methylsulfonyltoluene

Five families of three, seven of two.

**This is the same variation the self-consistency runs showed.** Three replicates of one
prompt produced those same three spellings for the same molecule, which took naive
name-keyed agreement from 88% down to 59%. So it is not a one-off slip: it is what the
model does with this term, run to run and section to section.

## Not fixing it is a defensible decision, and it is documented

`FINDINGS.md` records this as DOCUMENTED, NOT FIXED, deliberately:

> "buildCompoundId is a pure function of the identifier string, so production fragments
> these identically. Merging would make the gold set disagree with production for a
> reason unrelated to extraction quality."

That is right. A gold set that silently merges what production splits measures the
merge, not the extraction. The mitigation is `provenance/compounds-equivalence.json`,
so a benchmark can join across the variants.

## The mitigation covers 8 of the 12 families, and that is CORRECT

I checked which families the equivalence file covers. It covers 8, holding 24
identifiers. Three families are entirely absent:

    无水三氯化铝   aluminium trichloride  /  anhydrous aluminium trichloride
    冰水          water                  /  ice water
    环己二酮       cyclohexane-1,3-dione  /  cyclohexanedione

**These three are not spelling variants and must not be merged.**

- **Ice water is not water.** It is a workup medium at a specified temperature, and the
  procedures pour reaction mixtures into it deliberately.
- **Anhydrous aluminium trichloride is not aluminium trichloride.** Anhydrous is a
  specification, not a description: the hydrate does not catalyse a Friedel-Crafts
  reaction. This is the same distinction whose loss in translation is written up in
  `HYPOCHLORITE-STRENGTH.md`.
- **`cyclohexanedione` is ambiguous where `cyclohexane-1,3-dione` is not.** The 1,2-
  and 1,3- isomers are different compounds and only one of them makes this product. A
  reviewer flagged exactly this: the screen asks whether cyclohexanedione is a compound
  the patent names, which is trivially yes, while the field it answers is whether this
  is a definite molecule, which needs the locants.

So the honest count is not 58. Excluding the three legitimate distinctions:

    genuine duplicate families          9
    genuine surplus records            14
    substances, counting the three
    specification pairs as distinct    61

## What to do about it

Nothing, for now, and that is the finding rather than a punt.

The decision not to merge is correct and reasoned. The equivalence file is correctly
scoped. What is missing is only that **anything reporting a record count should say
which number it is using and why**: 75 records, 61 substances, 9 duplicate families
mitigated by an equivalence join.

The concrete risk is a benchmark quoting 75 against another system's 61 and calling it
a recall difference. That is precisely the trap the approach comparison hit from the
other direction, where the gold's 75 against a raw run's 143 looked like 52% recall and
was actually the dedupe step.
