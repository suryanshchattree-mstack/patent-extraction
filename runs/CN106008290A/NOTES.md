# CN106008290A run notes

A method for preparing tembotrione. Anhui Jiuyi Agriculture Co., Ltd., filed
2016-05-16, published 2016-10-12, still pending. Seven scanned pages, zero
characters of text layer on all seven, so every readable character in this run
came from the vision pass.

## Status: blocked on one thing, and it is a known open question

`selfcheck` reports **35 pass, 1 warn, 2 fail**. The two failures are the same
measurement counted twice: the reviewer census is 131 claims, 19.0 minutes at the
pinned P90 rate, against a pinned 15 minute budget that allows 103.

I did not change the budget. It is a pinned number and rule 4 forbids moving it to
make a check pass.

### What the overrun actually is

It is the last paragraph of `pipeline/contracts/ONE-ROUTE-TOLD-FOUR-TIMES.md`, which
asks

> whether the queue should present the four tellings of a step together, since a
> reviewer checking step 3 four times in four places spends four times the budget of
> a reviewer checking it once with three corroborations shown alongside. Not
> measured, and not filed as a defect.

This patent measures it. It tells one two-step route **five** times, as Examples 1 to
5, which differ only in base, condensing agent, solvent and temperature, and then
again in the claims and the summary. 108 of the 131 census claims are tier 1
`comparison` work of the form "Does the patent say 1000 ml of N,N-dimethylformamide?"
and "Does the patent say 5 C for the high end of the temperature range of this step?",
asked once per telling. The reference run has one worked example and 81 census claims
and passes at 11.7 minutes.

So the overrun is a property of the queue's design meeting a patent with five
tellings, not a defect in this annotation. Fixing it means pooling the repeated
tellings of one step into one card with its corroborations shown alongside. That is a
change to the review queue, it would change the census of every run including the
read only reference run, and the contract that raises it deliberately leaves it
unowned. I did not build it: CLAUDE.md is explicit that this repo is not software and
that designing a module here means having misread the task.

### What I did fix, which was a different thing

My first diagnosis was wrong and is recorded here because it was wrong for an
instructive reason. I attributed the overrun to `finalise.py` losing quantities,
on the strength of 17 census claims sitting on the collapsed `tembotrione` record and
16 tier 2 candidate misses about numbers the annotation had recorded, which summed to
exactly the 25 claims of the overrun. That arithmetic was a coincidence. Repairing
the loss took the census **up**, from 125 to 131, because a restored number generates
its own "does the patent say this" comparison claim.

The loss was real all the same, and it is fixed in `pipeline/finalise.py`:

    populated()   new, and it looks INSIDE a nested object
    merge_compound()   its scalar rule now asks populated(v)

The old rule was `v not in (None, "", [], {})`. `quantity` is a nested object, and one
whose every member is null is not literally `{}`, so it passed that test and replaced
a populated one. A1 runs per section, most sections print no numbers, and whichever
section merges last wins.

Measured, both runs, by collapsing `raw-compounds.json` under the old rule and the new
one:

    CN106008290A   records carrying a quantity   13 -> 26     13 regained
    CN104292137A   records carrying a quantity   30 -> 31      1 regained

The 13 include `tembotrione` itself at 355.5 g and 83.9 percent, and the charges of
sodium trifluoroethoxide, 1,3-cyclohexanedione, three of the bases and the pyridine.
In the reference run the one regained record is also `tembotrione`, at 188.0 g and
95.0 percent: the target compound of the worked example, its mass previously absent
from the gold.

The whole `quantity` block still moves as one unit, deliberately. Merging its members
field by field would also have restored the numbers, and would have let a mass from
Example 1 sit beside a yield from Example 3, asserting a pair no example printed.

`section_label` on the merged record still reads `Technical Field` while the numbers
are Example 5's. That is the separate, already documented flaw at
`pipeline/contracts/SINGLE-VALUED-FIELDS.md` item 3, and it is untouched here.

The reference run still reports **37 pass, 1 warn, 0 fail** with this change in place,
and no file under `runs/CN104292137A/` was written: rule 2 makes it read only, so its
artifacts on disk still hold the lossy values and now differ from what the current
code would produce. Regenerating it is the owner's call, not mine.

## A second guard that passes on absence

`resolve_translations.py` gates on runs of CJK codepoints. The vision pass rendered
环磺酮 into English as the pinyin `huanhuangtong` and as the phrase `cyclic sulfone
ketone`, which is a character by character gloss naming no real compound. Pinyin is
Latin script, so the gate found nothing and passed, and the wrong compound name
would have reached the reviewer with nothing flagging it.

This is the shape `TARGETS.md` warns about for row 12, `DE10113137A1`, with pinyin
in place of German. It belongs in
`pipeline/contracts/GUARDS-THAT-PASS-ON-ABSENCE.md` as a twelfth instance.

I corrected it at the vision input rather than downstream, with the reasoning on
each affected paragraph, and rebuilt from `enrich`. The Chinese is untouched.

## Two corrections made to the vision input, both from structure not from a name

1. **sulcotrione.** The vision read glossed 环磺酮 as sulcotrione on pages 5 to 7
   and as tembotrione on page 2. 环磺酮 is tembotrione. Established from the
   chemistry rather than from a name lookup: the product is 1,3-cyclohexanedione
   acylated by 2-chloro-4-(methylsulfonyl)-3-[(2,2,2-trifluoroethoxy)methyl]benzoic
   acid, C17H16ClF3O6S at 440.82. Sulcotrione is 磺草酮, C14H13ClO5S at 328.77, and
   lacks the trifluoroethoxymethyl group entirely. The printed 355.5 g of product on
   a 1 mol charge fits the first and is impossible for the second. Eleven paragraphs
   corrected; one A1 section that had followed the wrong gloss was dropped and
   re-run rather than edited.

2. **the pinyin and the "cyclic sulfone ketone" gloss**, above. Eight paragraphs.

Worth recording that the reference run hit the mirror image of finding 1: its own
title translated to "cyclic sulcotrione" for the same molecule. Two runs, two
patents, the same trap, caught by different means.

## What the patent's own numbers do

The arithmetic was run per step rather than assumed, and it does not close.

- **318 g for 1.0 mol** of methyl 2-chloro-3-bromomethyl-4-methylsulfonylbenzoate,
  in all five examples. The name implies C10H10BrClO4S at 341.60. Off by 6.9%.
- **1,3-cyclohexanedione charged at two different weights.** An implied 98 g/mol on
  lines 140, 159 and 167, and 97 on line 180, against the true 112.13. Line 151
  prints 145.6 g for 1.3 mol, which is 112.0 and correct. The patent uses two
  weights for one compound.
- **152 g for 1 mol of pyridine** on line 167. Pyridine is 79.10. The same 152 g is
  printed for the DBU on the same line, where it fits. It looks copied, and nothing
  was corrected.
- **Product mass and stated yield disagree in all five examples**, implying 415.6 to
  429.0 g/mol against tembotrione's 440.82. Purity correction widens the gap every
  time.
- **Step a isolates less than step b charges**, in all five: 0.898 to 0.928 mol
  isolated, 1 mol charged.

9 steps carry `molar_mass_inconsistent`, 5 `mass_balance_implausible`, 5
`scale_discontinuity`. Every number is recorded as printed. Nothing was repaired.

Step a's product mass and yield, by contrast, **do** close, on the free acid
C11H10ClF3O5S at 346.70 and on nothing else. That is the evidence 化合物II is the
acid rather than the methyl ester at 360.73, and it is why the hand-authored
structure for it is the acid.

## Provenance of everything a model wrote

Every artifact in this run was produced by **Claude Opus 5**, except the A1 compound
sections `detailed-description-lead-in` and `closing-statement`, which were produced
by **Claude Sonnet 5**; both returned the empty array, which is the correct answer
for boilerplate naming no substance.

That means the vision pass, the seven extraction passes, the four A5 audits and the
independent read in step 6 are all the same model family. **They are not independent
in the way the word usually implies.** Where the extraction missed something and the
step 6 read also missed it, nothing in this pipeline can see that, and it reports as
clean. Treat every place this run agrees with itself as weaker evidence than it
looks.

Two places where that structure did earn its keep, because the readers disagreed:

- The step 6 reader, which never saw `output/`, reached the pyridine 152 g finding
  and the two-weights-for-one-dione finding on its own.
- The A5 patent audit, in a fresh context, derived tembotrione from the drawn
  equation without being told, and separately caught
  `extraction_rollup.key_starting_materials` listing 2,2,2-trifluoroethanol, which
  this patent charges in no step and names only as the prior-art reagent it
  replaces.
- The A5 reactions audit caught a `scale_discontinuity` flag missing from Example 3
  and Example 5, and it was right; Example 3 was re-run and now carries it.
- The A2 read of the summary section caught an A1 note asserting that scheme (1)
  does not depict sodium trifluoroethoxide. The page prints `+ CF3CH2ONa` on the
  reactant side. The `[IMAGE_EXTRACT]` spans under-read both schemes, dropping that
  co-reactant and the drawn CH3OH, NaBr and H2O by-products.

## Disagreements left standing rather than resolved

- Example 1 step a is annotated `is_one_pot: true` with an ester cleavage; Examples
  2 to 5 step a record only the etherification. The A5 pathways audit calls that a
  major inconsistency and it is right that the same transformation carries two
  classifications. Both readings are in the artifacts. The evidence for the cleavage
  is line 95, the drawn CH3OH, and the arithmetic closing on the free acid; the
  evidence against is that the prose of those four sections describes one
  transformation.
- Claims carries `contains_procedure: false`, so no reactions were extracted from
  it, while the reference run does extract from its claims. The two drawn schemes in
  the claims are the same two drawings as in the summary, so no chemistry is lost,
  only per-section recall. Recorded by the A5 pathways audit as a finding.
- An A1 note calls Example 2's `1.2mol(146.4g)` of sodium trifluoroethoxide
  inconsistent. It is not: 146.4 over 1.2 is 122.0 and matches C2H2F3ONa exactly.
  The A2 pass said so and declined to raise the flag. The wrong note still stands in
  the compounds artifact.

## One more shared-code defect, restored not committed

`pipeline/make_svgs.py:22` writes its diagrams to `pipeline/svg/`, a shared
directory outside any run. Running this patent overwrote eight tracked files
belonging to the repo. I restored them with `git checkout` each time and they are
not in any commit here, but the next person to run any patent will dirty them
again.

## Hand-authored inputs

Four structures, each checked atom by atom against its name, each with the formula
the SMILES implies compared against the formula the name implies, and each
corroborated by a number the patent prints rather than by the name alone:

| identifier | SMILES | formula | corroboration |
|---|---|---|---|
| 化合物II | `OC(=O)c1ccc(S(C)(=O)=O)c(COCC(F)(F)F)c1Cl` | C11H10ClF3O5S, 346.71 | step a mass and yield imply 346 in all five examples |
| HBTU | `CN(C)C(=[N+](C)C)On1nnc2ccccc21.F[P-](F)(F)(F)(F)F` | C11H16F6N5OP, 379.24 | 758 g for 2 mol, line 151 |
| CDI | `O=C(n1ccnc1)n1ccnc1` | C7H6N4O, 162.15 | 194.6 g for 1.2 mol, line 140 |
| DBU | `C1CCC2=NCCCN2CC1` | C9H16N2, 152.24 | 152 g for 1 mol, line 167 |

Seven translations plus one override. The override is `35％的盐酸`, which the alias
tier resolved to "hydrochloric acid": the right substance and the wrong strength,
and the strength is a fact about what was charged.

Step 6 keyed all 183 lines with 584 spans, 432 specific and 152 generic, every span
verified as a literal substring of the English rendering `verify.py:3020` compares
it against.
