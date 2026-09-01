# US20100041557A1 run notes

BASF SE, "Crystalline forms of tembotrione". US national phase of WO 2007/003332,
published 2010-02-18. English throughout, 786 enriched source lines, 23 pages.

This is the third annotated run and the second polymorph patent, so it is the first
chance to see which of EP2045236A1's numbers were properties of that patent and which
were properties of the pipeline. Several were the latter. See the table in
`pipeline/contracts/PACE-MEASUREMENT.md`.

## Where the run stopped

`run_pipeline.py` reaches the end. All 18 stages ran.

    structures     [gate]  PASS   4 identifiers carry chemistry, all 4 resolve
    translations   [gate]  PASS   0 Chinese strings, 786 lines come out in English
    validate               ok     7 artifacts, 425 records, all about this patent
    verify         [gate]  FAIL   grounding gate, 45 claims for a human to read
    selfcheck              33 pass, 3 warn, 2 fail
    manifest               233 artifacts over 18 stages, 31.1 MB

**The run is not clean and is not marked done.** Both selfcheck failures are one
measurement: the reviewer census is 104 claims, which is 15.1 min at the 8.7 s p90
against a 15.0 min budget. One claim over. At the per-kind medians it is 10.5 min and
fits.

The 104 are itemised in PACE-MEASUREMENT.md. In short: 23 are unit conversions the A2
prompt mandates and the engine cannot ground by construction, 22 are step 6's own
findings which are a census by design, 6 are OPSIN disagreements rule 8 says to record
and never resolve, and 5 are crystallographic angles the engine tokenises as
temperatures. The budget was not changed and the annotation was not thinned.

The verify grounding gate failing is the gate working. It reports the claims a human
must read; it is not a defect count.

## Which model produced what

Every artifact below was produced by **Claude Opus 5** (`claude-opus-5[1m]`) driving
scripted generators. No other model was used at any point, and that is the important
part of this section.

| pass | artifact | how |
|---|---|---|
| V | `input/vision/p01..p15.json` | 15 agents, one per page, fresh context each |
| A0 | `output/stages/00-sections.json` | 49 sections over 786 lines |
| A1 | `output/stages/A1-compounds/` | 49 per-section files, 498 records -> 306 unique |
| A2 | `output/stages/A2-reactions/` | 16 per-section files, 61 records |
| A3 | `output/stages/A3-pathways/` | 58 pathways |
| A4 | `output/stages/patent-llm.json` | one patent record |
| A5 | `output/stages/A5-verify/` | 4 audits, each in a fresh context |
| step 6 | `input/substances-observed.json` | 752 keys, 1604 mentions, read independently |

**The independence is weaker than the word implies.** The vision pass, the seven
extraction passes, the four audits and the independent read in step 6 are all the same
model. Where the extraction missed something and the independent read also missed it,
nothing in this pipeline can see that, and it reports as clean. CLAUDE.md says to say
this in the run notes, and this is that sentence: **one reader, four times, is not four
readers.** The substance sweep publishes `readers: ["llm"]` and says so on all 22 of its
tickets, because ChemDataExtractor is not installed on this machine and `mentions.py`
correctly refused to write an empty file rather than let a screen read "found nothing".

## Hand authored, and what checks it

**Structures: one curated entry, covering three identifiers.** Forms A, B and C of
tembotrione, all carrying the same SMILES:

    CS(=O)(=O)c1ccc(C(=O)C2C(=O)CCCC2=O)c(Cl)c1COCC(F)(F)F
    name implies    C17 H16 Cl F3 O6 S
    SMILES implies  C17H16ClF3O6S, MW 440.82
    they agree

Not authored fresh. This is the structure drawn on page 4 and read into the enriched
source at line 74, verified atom by atom against the page by three A5 auditors
independently, and it is byte identical after RDKit canonicalisation to the entry in
CN104292137A, CN111440099B and EP2045236A1.

**The limit, recorded because the structure cannot record it:** polymorphism is a
property of the solid, not of the molecule. Forms A, B and C are one compound in three
lattices, so no structure in this pipeline distinguishes them. What distinguishes them
here is the X-ray powder diffraction pattern, carried in `analytics[]` on the compound
records. A consumer treating a structural match between two of these as evidence that
two records describe the same FORM is wrong.

**Translations: none.** The document is English. The translations gate is blind to
German and would be blind to anything but Chinese (`resolve_translations.py:127`), which
did not matter here and did matter on EP2045236A1.

## Three defects found in the annotation, and fixed at the input

None of these was fixed by editing `output/`. Each was fixed in the generator that
produces the stage file, and the stage re-run.

1. **A2 put a coined composition description in `product_name` on 10 formulation
   records.** `resolve_structures.py:371` enters whatever that field holds into the set
   of identifiers that must resolve to a molecule, so the structures gate asked a human
   to hand-author the SMILES of a water-dispersible powder. `product_name` is one string
   and a formulation has two alternative products ("form A or form C"), which is why the
   pass reached for prose. Both forms were already carried in `compounds[]` with
   `is_product` true, so the field is now null and nothing is lost.

2. **A2 did the same on 22 comparative and stability records.** The tables print the
   Modification cell as `A + B`; `mixture of tembotrione crystalline form A and
   tembotrione crystalline form B` was a coined expansion, as was `... both unchanged`
   for [0085], which says only that the pure modifications were recovered unchanged. A1
   rule 2 wants the identifier exactly as written and rule 3 forbids inventing one, and
   an invented compound counts against precision exactly as a missed one counts against
   recall.

3. **A3 took its pathway product from `product_name`,** so all three coined strings
   reached 32 pathways. It now derives the product from the terminal step's `is_product`
   compounds when there is exactly one, and emits `product: null` with a flag naming the
   reason when there are two.

Confirmation that these were real: after the fix the curated table **refused** the three
coined aliases, because they are no longer identifiers anywhere in the gold.

A fourth, smaller one: the claim 16 provenance row quoted all nine of its 2theta
reflections while citing only the first of the nine table rows. Rows 2 to 9 now cited.

## Two engine defects, fixed in pipeline/verify.py

Both approved before the change. Both inflated this run's census and neither is specific
to it. Measured effect: 197 -> 112 claims. Full write-up in PACE-MEASUREMENT.md.

- `build_coverage` tested `kind == "translation"`, which sees only the first line of a
  translation block, so the English copy of every duplicated table counted as uncited
  source. It now consults `en_hint`, the paragraph walk that already existed for this.
- `promoted_fields` treated an empty `about_fields` as "every field", so one fieldless
  failing check pulled all 33 claims on the tembotrione record into the census.

Re-measured after the change, with no other input touched:

    EP2045236A1    37 pass, 1 warn, 0 fail   census 52 -> 32
    CN111440099B   35 pass, 3 warn, 0 fail   census 53
    CN104292137A   not touched. It is read only.

## Outstanding, and deliberately not acted on

- **The `ureas` identifier collision.** Urea the fertiliser at line 564 and the
  substituted-urea herbicide class at line 708 are one identifier string, and
  `finalise.py` keys on that string, so they merge into one record. This is the one item
  here I would call a real defect in the deliverable.
- **`benzoic acid` and five other acid class names at line 708** are named in the patent
  and have no compound record. Step 6 found them; ticket 13 of the substance sweep.
- **`heptadecanols, hexadecanols, octadecanols` at line 579**, same.
- **The `[0162]` roughly 50 class terms.** Whether a list of herbicide classes should
  become 50 compound records is undecided and is a policy question, not a reading.
- **The stability study records four experiments as three.** [0085] reports pure A and
  pure C as one record because the paragraph is the document's own delimiter. The
  alternative reading is recorded on the record rather than chosen silently.
- **A third join defect in the substance sweep,** recorded in PACE-MEASUREMENT.md and
  not fixed: it requires an alias to sit on a record citing the line, rather than
  consulting `compounds-equivalence.json`, so seven tickets report the systematic name of
  tembotrione as unaccounted when it is already an alias on the tembotrione record.
- **`aluminum` and `polystyrene`** are apparatus, an aluminium DSC cup and a polystyrene
  container, and my step 6 read over-collected them. Left in the sweep as unaccounted
  rather than deleted, so the over-collection stays visible.

## Two OCR facts worth keeping

The text layer moves the PCT number out of field (86) and prints it under the (30)
heading, and it drops brackets rather than flattening them, so the title arrives as
`2-2-CHLORO...` and not `2-[2-CHLORO...`. Both are recorded in
`input/US20100041557A1-biblio.json` under `ocr_structural_note` and `title_en_note`.
This is why the vision pass runs even on a patent that carries a text layer.
