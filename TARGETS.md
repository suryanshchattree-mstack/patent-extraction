# The twenty patents

One patent per person per sitting. Claim a row by putting your name in `owner`
and pushing that change **before** you start, so two people do not annotate the
same patent.

## How these twenty were chosen

The Day 2 golden set holds 84 rows for tembotrione. 50 are labelled Synthetic,
and of those 33 are patents. But 33 patents are only **26 inventions**: six
families publish the same disclosure in more than one jurisdiction, and
annotating both members of a family produces two datasets that agree by
construction and measure nothing. See `pipeline/contracts/DUPLICATE-FAMILIES.md`.

So the list is one representative per family, ranked by how close the patent
sits to the target molecule, cut at twenty. The six dropped families are all
`Molecule Substrate`: routes to commodity feedstocks such as
2,2,2-trifluoroethanol and 1,3-cyclohexanedione, which a route analysis buys
rather than makes. They are listed at the bottom so the cut is visible rather
than silent.

## The twenty

| # | patent | owner | status | family | jur | relevance | title |
|--:|---|---|---|---|---|---|---|
| 1 | [`CN104292137A`](https://patents.google.com/patent/CN104292137A/en) | **Yash** | done, reference run | 52312131 | CN | Exact Molecule | Process for synthesizing triketone herbicide cyclic sulcotrione |
| 2 | [`CN109678767A`](https://patents.google.com/patent/CN109678767A/en) | **Yash** | done | 66190615 | CN | Exact Molecule | A kind of synthesis technology of herbicide tembotrions |
| 3 | [`CN111440099B`](https://patents.google.com/patent/CN111440099B/en) | **Sathvik** | done | 71652835 | CN | Exact Molecule | Purification method of tembotrione product |
| 4 | [`EP2045236A1`](https://patents.google.com/patent/EP2045236A1/en) | **Sathvik** | done | 38984191 | EP | Exact Molecule | Thermodynamically stable crystal modification of 2-({2-chloro-4- <br>*same family, do not also annotate:* US8722582B2, WO2009027004A1 |
| 5 | [`US20100041557A1`](https://patents.google.com/patent/US20100041557A1/en) | **Sathvik** | claimed | 39415042 | US | Exact Molecule | Crystalline forms of 2-[2-chloro-4-methylsulfonyl-3-(2,2,2-trifl <br>*same family, do not also annotate:* US8309769B2 |
| 6 | [`WO2000021924A1`](https://patents.google.com/patent/WO2000021924A1/en) | **Tejas** | blocked | 7884081 | WO | Exact Molecule | Benzoylcyclohexandiones, method for the production and use there |
| 7 | [`WO2024109718A1`](https://patents.google.com/patent/WO2024109718A1/en) | **Tejas** | claimed | 91195273 | WO | Exact Molecule | Method for preparing cyclosulfonone, and intermediates |
| 8 | [`CN106008290A`](https://patents.google.com/patent/CN106008290A/en) |  |  | 57098239 | CN | Intermediate Molecule | Method for preparing tembotrions |
| 9 | [`CN112645853A`](https://patents.google.com/patent/CN112645853A/en) | **Suryansh** | blocked | 75343429 | CN | Intermediate Molecule | Preparation method of 2-chloro-3-alkoxymethyl-4-methylsulfonylbe <br>**Annotation complete; `selfcheck` cannot reach 0 fail. See the caveat below and `runs/CN112645853A/RUN-NOTES.md`.** |
| 10 | [`US20040236146A1`](https://patents.google.com/patent/US20040236146A1/en) |  |  | 7698422 | US | Intermediate Molecule | Method for producing 3-bromomethylbenzoic acids <br>*same family, do not also annotate:* WO2003022800A1 |
| 11 | [`CN102627591B`](https://patents.google.com/patent/CN102627591B/en) |  |  | 46586017 | CN | Molecule Class | Preparation method of 2-chloro-4-methylsulfonylbenzoic acid |
| 12 | [`DE10113137A1`](https://patents.google.com/patent/DE10113137A1/en) |  |  | 7677998 | DE | Molecule Class | Preparation of herbicidal substituted 2-benzoyl-1,3-cyclohexaned <br>*same family, do not also annotate:* DE10113137C2 <br>**German. See the caveat below before starting this one.** |
| 13 | [`EP0478390B1`](https://patents.google.com/patent/EP0478390B1/en) |  |  | 24360934 | EP | Molecule Class | Improved method for the preparation of 4-methylsulfonyl benzoic  <br>*same family, do not also annotate:* US5079381A |
| 14 | [`EP0805792A1`](https://patents.google.com/patent/EP0805792A1/en) |  |  | 10768537 | EP | Molecule Class | Process for the production of 2-(substituted benzoyl)1,3 cyclohe |
| 15 | [`EP1034159A1`](https://patents.google.com/patent/EP1034159A1/en) |  |  | 10822758 | EP | Molecule Class | Process for the preparation of acylated cyclic 1,3-dicarbonyl co <br>*same family, do not also annotate:* US6218579B1 |
| 16 | [`US10421714B2`](https://patents.google.com/patent/US10421714B2/en) |  |  | 53785074 | US | Molecule Class | Process for preparing mesotrione |
| 17 | [`US4774360A`](https://patents.google.com/patent/US4774360A/en) |  |  | 22073364 | US | Molecule Class | Converting enol ester precursor of a benzoyl-1,3-cycloalkyldione |
| 18 | [`US4780127A`](https://patents.google.com/patent/US4780127A/en) |  |  | 27408525 | US | Molecule Class | Certain 2-(substituted benzoyl)-1,3-cyclohexanediones and their  |
| 19 | [`US5728889A`](https://patents.google.com/patent/US5728889A/en) |  |  | 10768536 | US | Molecule Class | Process for the production of 2-(substituted benzoyl)-1,3 cycloh |
| 20 | [`WO2022024094A1`](https://patents.google.com/patent/WO2022024094A1/en) |  |  | 80036183 | WO | Molecule Class | Process for preparation of mesotrione and its intermediates |

## One note, on row 3

`CN111440099B` is `done`. `run_pipeline.py` reaches the end of all 18 stages and
`selfcheck` reports **35 pass, 3 warn, 0 fail**, inside the 15 minute reviewer budget at
13.8 minutes over 95 census claims. `validate.py` is clean. The structures gate passes
with **zero curated entries**: the drawn SMILES and OPSIN between them cover every
identifier that carries chemistry, so no SMILES was hand-authored on this patent at all.

`verify`'s grounding gate is red on 19 claims, which is the same state the reference run
is in and which `AGENT.md` describes as red on purpose. 16 of the 19 are one cause: the
patent prints its hold times as 保温一小时, one hour in the Chinese numeral, so no digit
appears on the line the record cites although the value is right. None is a value the
annotation invented, and all 19 are itemised in `runs/CN111440099B/NOTES.md`.

The most useful finding for anyone choosing what to annotate next: Example 6 charges
237.9 g of thionyl chloride, which is 2.000 mol, exactly three equivalents against the
benzoic acid and 3.149 against the benzoyl chloride the paragraph names.

## One note, on row 4

`EP2045236A1` is `done`. `run_pipeline.py` reaches the end of all 18 stages and
`selfcheck` reports **37 pass, 1 warn, 0 fail**, at 7.5 minutes of the 15 minute budget
over 52 census claims. `validate.py` is clean on all five artifacts. The structures gate
passes on **one** curated entry and the translations gate on zero.

**This is the first patent here that is neither Chinese nor a synthesis**, and both facts
matter to whoever takes row 5 or later. It discloses no chemistry in the usual sense: not
one bond is formed or broken. It is a polymorph patent, one molecule in three crystal
forms, and its three worked examples dissolve 2 g of tembotrione and cool it. Every
reaction record has the same substance on both sides. No yield, product mass or assay
purity is stated anywhere.

**The finding.** Tabelle 5 and Tabelle 6 print the same 49 two-theta values in the same
order, though captioned as the powder patterns of modifications I and II, and claim 5
recites the same list. The patent's own Tabelle 7 rules out a mislabelled caption: I is
orthorhombic Pna21 at cell volume 1788,91 and II is monoclinic P2(1)/n at 1814,21, and
two lattices cannot share a pattern. So modification II's powder pattern is disclosed
nowhere in this document while claim 5 recites one. Which table is the misprint is not
recoverable and the annotation decides nothing. Alongside it, modification III has a
melting point and two spectra and nothing else, and modifications I and II melt 0.1 K
apart on a 10 K/min DSC ramp.

**`verify` is red on 13 of 536 claims and the cause is one thing:** `verify.py`'s
tokeniser cannot read the German decimal comma, so `124,0°C` parses as 124 with no unit
plus a temperature of zero, and `1,637 Mg/m3` becomes the three numbers 1, 637 and 3.
Nine claims about melting points, densities and polymorphic purity cannot match the
values printed beside them. The honest fix is in `verify.py`, not in the gold.

**Read this before starting row 12, `DE10113137A1`.** The caveat below about
`resolve_translations.py` being blind to German is now confirmed by measurement rather
than inference: the gate passed this patent on **zero strings**, having checked nothing,
and reported it as clean. English was supplied by hand throughout instead. Two further
defects surfaced only because this patent's data is shaped unlike the reference's, and
are fixed in `pipeline/`: `verify.py` gave `1 g` and `1 kg` on one line the same claim
id, so a verdict on one would silently have answered the other; and its coverage sweep
counted every machine-translation line as uncited source, which on a German patent was 53
of 108 census claims and put the reviewer budget over the limit on duplicates alone.
`make_svgs.py` also could not lay out a product name long enough to wrap.

A third needed no code change and is the one that had damaged the deliverable.
`finalise.py:merge_compound` tests `v not in (None, "", [], {})`, and an all-null
`quantity` object is not equal to `{}`, so it overwrites a populated one from an earlier
section. The merged gold held **zero** compound records with a mass, though the patent
charges 2 g three times. Writing `null` instead, which A1 rule 17 already requires,
repairs it. **`runs/CN104292137A` and `runs/CN109678767A` may carry the same loss and
have not been checked.**

Full write-ups in `runs/CN111440099B/NOTES.md` and `runs/EP2045236A1/NOTES.md`.

## One caveat, on row 9

`CN112645853A` is annotated end to end. All 18 stages run, both coverage gates
pass, the `visual` gate passes and the manifest is clean, but `selfcheck` reports
2 fail and so the row is `blocked` rather than `done`.

Both failures are one number. The review census is 321 claims, 46.5 min at the
pessimistic rate against the 15.0 min budget `contracts/REVIEW-PROTOCOL.md` pins
from what the user said they would spend. Re-measured when row 4's verify.py
fixes landed; it was 322 claims and 46.7 min, and a Chinese patent barely moves
because most of its enriched lines are substitutions rather than paired
translations. This patent has **twenty** worked
examples where the reference run has one, so the same facts recur across them:
the water volume 18 times, the methyl ester mass 12 times, the yield identity 19
times. Tier 1 is 26% of claims against the reference's 19%, so the grounding is
comparable rather than broken, and it was measured that even eliminating every one
of the 217 tier-1 grounding failures would still leave about 105 census claims
against a budget of roughly 103.

So no change to this annotation can meet the budget without deleting true records,
and the pinned 15.0 must not be edited because it is a measurement rather than a
target. The fix belongs in the verification engine: pool claims that repeat across
structurally identical examples, as it already pools substance tickets. **Any
patent in this list with more than a handful of examples will hit the same wall.**

Three latent bugs in shared code were found and fixed on the way, each invisible
on the reference run and fatal on the second patent: `merge_stages.py` called
without `--patent-id`, disjoint assignee-type enums between the biblio and patent
schemas that made every company-assigned patent unvalidatable, and an m2-route
label collision for any target name longer than one line. `RUN-NOTES.md` has the
detail, along with three more issues left for an owner to decide on.

## One caveat, on row 12

`resolve_translations.py` gates on **Chinese specifically**: it finds runs of CJK
codepoints and refuses to pass while any of them can reach a screen. German is
Latin script, so that gate finds nothing in `DE10113137A1` and passes. It will
not be lying, exactly - there is no Chinese - but it is not answering the
question you want answered either, and untranslated German will reach the
reviewer with nothing flagging it.

This is the repo's own `GUARDS-THAT-PASS-ON-ABSENCE.md` pattern, with the
guard's subject being a script rather than a field. Take row 12 last, or skip
it, and raise it rather than working around it quietly.

## Dropped: the six substrate families

| patent | family | title |
|---|---|---|
| `EP1309538A2` | 7643384 | Method for the production of trifluoroethoxy-substituted benzoic acids |
| `US3363006A` | 26713736 | Bis(2,2,2-trifluoroethyl)ether and method of preparation |
| `US4590310A` | 24553736 | Process for the preparation of 2,2,2-trifluoroethanol |
| `US4695673A` | 27122042 | Process for the production of acylated 1,3-dicarbonyl compounds |
| `US5744648A` | 24773992 | Process for the manufacture of 1, 3-cyclohexanedione |
| `US6657074B1` | 23462840 | Process for the preparation of acylated 1,3-dicarbonyl compounds |

## One note, on row 6

`WO2000021924A1` is annotated end to end. Both gates pass, the deliverable is
assembled, and `runs/WO2000021924A1/NOTES.md` records the run. It is marked
`blocked` rather than `done` for one reason: `selfcheck` reports 2 fail, and both
are the same fact.

The review census is 178 claims, which at the pinned 8.7s P90 rate is 25.8 minutes
against a 15 minute budget, so tier 3 is sampled zero times and the verification
report carries no statistical bound. The budget is a pinned number and rule 4 of
CLAUDE.md forbids changing one to make a check pass, so it was left failing.

Re-measured when row 4's verify.py fixes landed. It was 281 claims and 40.7
minutes, and 103 of those claims were the machine's own English being counted as
uncited source, which is most of the gap and the reason a German patent felt so
much worse than a Chinese one. The remaining overrun is real.

The census is not inflated. 117 of the 178 claims are `not_checkable` judgements,
and per compound this run produces fewer census claims than the reference run.
The budget was calibrated on a 9 page patent with 75 compounds; this is a 112
page patent with 520. Any of the longer patents in this
list will hit the same wall, so the budget probably needs to be a function of the
gold's size rather than a constant. That is a maintainer's call.

`NOTES.md` also lists six defects this run found in the pipeline itself, three
fixed and three left alone, plus the fact that the row 12 translation caveat below
applies to this row too.

## Status vocabulary

Put one of these in `status`, and nothing else, so the deploy can count them:

| status | means |
|---|---|
| *(blank)* | nobody has started |
| `claimed` | owner set, not started |
| `passes` | the LLM annotation passes are done, gates not yet cleared |
| `gated` | stopped at a coverage gate, owner owes curated entries |
| `done` | `run_pipeline.py` reaches the end and `selfcheck` has 0 fail |
| `blocked` | something is wrong that you cannot fix; say what in a note |
