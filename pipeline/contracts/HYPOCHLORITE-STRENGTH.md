# Seven facts lost in translation, and 28 equivalents of oxidant

Found by the name-fidelity gate. Verified here against the source and the arithmetic.

## What the patent prints

Line 207, Example 1 step 3:

> "...2-chloro-3-acetyl-6-(methylsulfonyl)toluene 50.88 g (0.24 mol) and 200 ml of
> tetrahydrofuran solution; at room temperature **500 g of 15% sodium hypochlorite
> solution** was added dropwise..."

## What the gold records

    sodium hypochlorite    mass_g = 500.0

The strength is gone. The number is the mass of the SOLUTION and it is attached to the
name of the SOLUTE.

## Why it matters, in equivalents

    as recorded   500 g NaOCl              6.72 mol    28.0 equivalents
    as printed    500 g of a 15% solution  1.01 mol     4.2 equivalents

A haloform oxidation needs three equivalents of hypochlorite. **4.2 is a sensible
excess. 28 is absurd**, and no chemist reading the gold would believe it.

So this is a real extraction defect with a real chemical consequence, and it sits on a
step already carrying `molar_mass_inconsistent`, `mass_balance_implausible` and
`scale_discontinuity`. The `scale_discontinuity` flag is triggered by precisely this
number: 500 g charged against a previous step that produced far less.

## How it was found, which is the transferable part

Not by a chemistry check. By a **translation** check.

`36％的盐酸` was resolving to "hydrochloric acid" and `15％的次氯酸钠溶液` to "sodium
hypochlorite". Right substance, strength discarded. The gate that caught it asks a
narrow question: does an English rendering lose a **percentage** that the Chinese
carries?

The scoping is the whole design. A naive "does it lose a digit" rule finds a third hit:

    2-(2-氯-4-甲磺酰基-3-[(2,2,2-三氟乙氧基)甲基]苯甲酰基)环己烷-1,3-二酮  ->  tembotrione

which loses nine locants and is entirely correct, because a common name discards
locants. **A locant is not a quantity.** Restricting to percent signs finds exactly the
two real cases at any key-length bound, with no false positives.

## What it does not explain

Step 3's product mass is still unaccounted for: 0.24 mol at the stated 72% against a
product of molecular weight 248.69 predicts 42.97 g, and the patent prints 82.0 g, a
factor of 1.9. The hypochlorite strength does not touch that. It is a separate defect
and it remains open.

## The general point

A lost unit is a silent defect that reads as clean data. Nothing in a schema check, a
grounding check or a mass-balance check would have flagged `mass_g = 500.0`: it is a
number, in the right field, on the right compound, quoted from the right line. Only a
check comparing the two languages could see that the number had been detached from the
word that qualified it.


---

# The other five, and the class the first rule could not see

The percent-sign rule found two concentrations. It was scoped to **numbers**, so a
qualifier that is a WORD went straight past it. Generalising to a small table of
name-prefixes, applied only to `gold_alias` entries, found four more:

    无水三氯化铝  ->  "aluminium trichloride"   lost 无水, anhydrous
    无水硫酸镁    ->  "magnesium sulfate"       lost 无水, anhydrous
    饱和碳酸氢钠  ->  "sodium bicarbonate"      lost 饱和, saturated
    稀盐酸       ->  "hydrochloric acid"        lost 稀, dilute

**The first one is not cosmetic.** Anhydrous aluminium trichloride is the Friedel-Crafts
catalyst in steps 1 and 2. Anhydrous is not a description of it, it is a statement
about whether the step works: the hydrate does not catalyse the reaction. Dropping the
word turns a specification into a substance.

**In three of the four the gold's own record already carried the fuller English.** The
fact was never missing from the annotation. Tier 2 derives its answer from the gold and
picked the shorter of two aliases, so the loss happened between the annotation and the
index rather than between the patent and the annotation.

Worth noting while here: the gold carries TWO records for this substance, one
`anhydrous aluminium trichloride` with `role: catalyst` and one `aluminium trichloride`
with `role: reagent`, both aliasing 无水三氯化铝. That split is part of why the shorter
form was reachable at all, and whether the two records are one substance used twice or
a genuine duplicate is a question for the consistency checks.

## The scoping is the whole design, again

Applied to every entry rather than to names only, the prefix test is useless: 浓 also
opens 浓缩, "to concentrate", which begins a dozen procedure quotations that resolve to
whole paragraphs, where a prefix test means nothing. Names only keeps it at four hits
instead of twenty.

The same lesson as the locants: **a naive version of each of these gates reports
roughly five times as many hits, and every extra one is correct behaviour being flagged
as a defect.** A gate that reports 18 differences gets muted within a day. The same
gate scoped properly reports 4 and gets obeyed. The difference between those two
outcomes is entirely in the scoping, and the first number a new check produces is
almost never the right one.
