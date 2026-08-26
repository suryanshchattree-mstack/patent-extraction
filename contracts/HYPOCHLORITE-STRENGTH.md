# A concentration lost in translation, and 28 equivalents of oxidant

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
