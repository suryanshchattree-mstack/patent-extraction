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
| 3 | [`CN111440099B`](https://patents.google.com/patent/CN111440099B/en) |  |  | 71652835 | CN | Exact Molecule | Purification method of tembotrione product |
| 4 | [`EP2045236A1`](https://patents.google.com/patent/EP2045236A1/en) |  |  | 38984191 | EP | Exact Molecule | Thermodynamically stable crystal modification of 2-({2-chloro-4- <br>*same family, do not also annotate:* US8722582B2, WO2009027004A1 |
| 5 | [`US20100041557A1`](https://patents.google.com/patent/US20100041557A1/en) |  |  | 39415042 | US | Exact Molecule | Crystalline forms of 2-[2-chloro-4-methylsulfonyl-3-(2,2,2-trifl <br>*same family, do not also annotate:* US8309769B2 |
| 6 | [`WO2000021924A1`](https://patents.google.com/patent/WO2000021924A1/en) |  |  | 7884081 | WO | Exact Molecule | Benzoylcyclohexandiones, method for the production and use there |
| 7 | [`WO2024109718A1`](https://patents.google.com/patent/WO2024109718A1/en) |  |  | 91195273 | WO | Exact Molecule | Method for preparing cyclosulfonone, and intermediates |
| 8 | [`CN106008290A`](https://patents.google.com/patent/CN106008290A/en) |  |  | 57098239 | CN | Intermediate Molecule | Method for preparing tembotrions |
| 9 | [`CN112645853A`](https://patents.google.com/patent/CN112645853A/en) | **Suryansh** | blocked | 75343429 | CN | Intermediate Molecule | Preparation method of 2-chloro-3-alkoxymethyl-4-methylsulfonylbe <br>**Annotation complete; `selfcheck` cannot reach 0 fail. See the caveat below and `runs/CN112645853A/RUN-NOTES.md`.** |
| 10 | [`US20040236146A1`](https://patents.google.com/patent/US20040236146A1/en) | **Suryansh** | done | 7698422 | US | Intermediate Molecule | Method for producing 3-bromomethylbenzoic acids <br>*same family, do not also annotate:* WO2003022800A1 |
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

## One caveat, on row 9

`CN112645853A` is annotated end to end. All 18 stages run, both coverage gates
pass, the `visual` gate passes and the manifest is clean, but `selfcheck` reports
2 fail and so the row is `blocked` rather than `done`.

Both failures are one number. The review census is 322 claims, 46.7 min at the
pessimistic rate against the 15.0 min budget `contracts/REVIEW-PROTOCOL.md` pins
from what the user said they would spend. This patent has **twenty** worked
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

## One note, on row 10

`US20040236146A1` is `done`: all 18 stages run, both coverage gates and the `visual`
and `verify` gates pass, the manifest is clean and `selfcheck` reports 37 pass, 1
warn, 0 fail. The census is 47 claims at 6.8 minutes against the 15.0 budget, so it
does not hit the wall row 9 hit; it has two worked examples where CN112645853A has
twenty, which is the whole difference.

It is the pack's **first non-Chinese patent**, and that is worth reading before
taking another US or EP row. Three things assume Chinese:

- `resolve_translations.py` finds no CJK and reports "all 0 strings resolve". That is
  the row 12 caveat arriving early. It is not lying and it is not answering a
  question either.
- The `> EN:` line under each source line is a **repair of the same language** rather
  than a translation, because the text layer is OCR of a scan. Two shared-code checks
  read only the repair and rejected as-printed spans that were the only thing
  literally on their line. Both are fixed.
- The A5 prompt's translation check has no subject at all.

**Four latent bugs in shared code were found and fixed here, each with explicit
approval, and each invisible on the reference run.** The one that mattered most:
`finalise.py`'s `ASSIGNEE_TYPE` had no key for three of the six values
`biblio.schema.json` now allows and defaulted them to `sme`, so a correct biblio
shipped Bayer CropScience AG as a small enterprise. It survived two runs by
coincidence. The other three are the m2-route diagram overflowing on any long IUPAC
target name, the substance-span check above, and a drawing caption that told the
reviewer to look above a drawing printed below. See `runs/US20040236146A1/RUN-NOTES.md`.

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
