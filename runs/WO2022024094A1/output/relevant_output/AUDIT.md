# A5 adversarial audit of WO2022024094A1

Four independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 43 | 0 | 8 | 11 | 15 |
| `patent` | 1 | 0 | 1 | 9 | 16 |
| `pathways` | 16 | 0 | 4 | 5 | 15 |
| `reactions` | 24 | 0 | 1 | 6 | 21 |
| **total** | | **0** | **14** | **31** | **67** |

## Acted on

Nothing recorded for WO2022024094A1. Every finding below is outstanding.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical


### major

1. **[compounds]** `recall` on `mesotrione`
   The record for the patent's target compound carries no mass and no yield although Example 7 prints both, because the cross-section merge overwrote Example 7's quantity object with the empty quantity of an alphabetically later section while keeping Example 7's melting point and appearance.
   > line 331: HPLC purity >95%; Yield: 17g (85%); Melting point of the solid was 155-157°C;and solvent recovery: > 85%.
   fix: quantity.mass_g 17.0 and quantity.yield_pct 85.0; fix finalise's merge so the most complete quantity survives (A1 rule 4), not by hand-editing the artifact. Note that the reference run runs/CN10429213
2. **[compounds]** `recall` on `enol ester of formula (II)`
   Same merge defect: the enol ester record carries no mass, mmol or yield although three examples print its isolated mass and yield and Example 7 prints its charge.
   > line 318: HPLC purity > 85%; Yield: 22.8g (66%). Melting point 157-163°C and Solvent recovery >85%.
   fix: quantity.mass_g 22.8 and quantity.yield_pct 66.0 (Example 6, the last example section that makes it a product); the Example 4, 5 and 7 numbers remain in reactions.json
3. **[compounds]** `recall` on `2-nitro-4-methylsulphonyl benzoic acid`
   Same merge defect: no mass, mmol or yield on the NMSBA record although it is charged by mass in Examples 4 to 6 and produced with a stated yield in Examples 1 to 3.
   > line 316: dichloromethane (100mL) NMSBA (25g, 0.10mol) and 1, 3-cyclohexanedione (12g, 0.11mol) were added under stirring
   fix: quantity.mass_g 25.0 and quantity.mmol 100.0 (Example 6, the last section that gives it a quantity)
4. **[compounds]** `recall` on `2-nitro-4-methylsulfonyl toluene`
   Same merge defect: the starting material carries no mass or mmol although every one of Examples 1 to 3 charges it by mass and moles.
   > line 285: NMST (20g, 0.088mol), sodium hypochlorite (150ml, 0.222mol) and ruthenium oxide (0.5g, 0.004mol) were charged into a 500ml round bottomed flask.
   fix: quantity.mass_g 20.0 and quantity.mmol 88.0 (Example 3, the last example section)
5. **[compounds]** `recall` on `2-nitro-4-methylsulphonyl benzoic acid`
   Example 2's melting point is absent from every delivered artifact: melting_point is a single object, the merge kept only 210-214 from Examples 1 and 3, and reactions.json has no melting point field at all, so 207-210 survives nowhere outside the pre-merge raw dump.
   > line 279: HPLC purity > 92%; Yield: 67%; and Melting point: 207-210°C.
   fix: carry the second range as well, or record it in notes; the minimal fix is a note on this record naming 207-210°C as Example 2's value. Do not overwrite the surviving range.
6. **[compounds]** `recall` on `enol ester of formula (II)`
   Two of the three printed melting point ranges for the enol ester are absent from every delivered artifact for the same single-slot reason.
   > line 302: HPLC purity >85%; Yield: 25.4g (68%); Melting point: 158-163°C and Solvent recovery: >85%.
   fix: record the other two ranges in notes on this record (Example 4: 158-163°C, Example 5: 152-158°C)
7. **[compounds]** `precision` on `mesotrione`
   The notes assert a disagreement between two sections that does not exist anywhere in the annotation: no record in any artifact carries a triketone family tag, and the Claims record tags chemical_family:cyclohexanedione, identical to Background.
   > line 40: Abstract: The present disclosure provides a new and improved process for preparation of intermediate compounds and synthesis of mesotrione therefrom.
   fix: delete the clause about the Claims section, or correct it: grep for 'triketone' across output/ returns only this note. A false statement in the field the repo relies on to carry disagreements is worse
8. **[compounds]** `recall` on `None`
   The equivalence side channel is an empty object, so a consumer reads it as 'no fragmentation', yet at least two pairs of records in compounds.json are one molecule under two spellings: '(CH3CH2 )3N' and 'triethylamine', and 'cyclohexanedione' and '1,3-cyclohexanedione', which carry the identical SMILES alias O=C1CCCC(=O)C1 on both records.
   > line 68: "conditions": [{"text": "(CH3CH2 )3N"}, {"text": "Solvent"}]
   fix: list the two groups in compounds-equivalence.json. What would settle whether this is a generator limitation rather than an omission: whether finalise's equivalence key looks only at normalised names (
9. **[patent]** `precision` on `WO2022024094A1`
   chemistry_focus names halogenation as one of this patent's five chemistry classes, but the only halogenation reaction annotated for this document is a prior-art step recited in the background, the very step the invention's stated contribution consists of avoiding.
   > line 64: [005] The United States Patent No. 7,820,863 describes a process for preparation of mesotrione. In this patent reference, mesotrione is prepared by (i) oxidatio
   fix: Exclude section_type 'background' from the reaction_class counter in pipeline/finalise.py rollup(), as is already done for best_overall_yield_pct and key_starting_materials, giving ["oxidation", "este
10. **[pathways]** `vocabulary` on `pathways[13] Example 6 / step Example 6_Step 1`
   Two role values in this pathway step are outside CompoundRecord's role enum and disagree with the same entries in reactions.json, which carries 'other' for both.
   > line 316: To this mixture, N,N’-dicyclohexylcarbodiimide(DCC) (21g, 0.10mol) was added and stirred for about 2 hours at 25-30°C.
   fix: Carry the reaction record's value ('other' for both), per A3 rule 11 'copy verbatim ... do not re-derive, re-word or re-classify'. Root cause: pipeline/finalise.py calls normalise_role from finalise_r
11. **[pathways]** `vocabulary` on `pathways[14] Example 7 / step Example 7_Step 1`
   The quench water carries role 'quenching_agent', outside CompoundRecord's role enum, where reactions.json carries 'other' for the same entry.
   > line 329: The reaction mixture is cooled at 10-15°C and maintained for about 2 hours and quenched with water (100mL).
   fix: 'other', matching the reaction record and Example 4. Same root cause as the Example 6 finding: normalise_role is not applied to pathway steps.
12. **[pathways]** `recall` on `pathways[0] Background of the Invention (and pathways[5], [6`
   One molecule is carried under two identifiers across pathway records with no equivalence entry anywhere on disk, so the fragmentation is undetected rather than recorded.
   > line 64: (iii) reacting cyclohexanedione with 2-nitro-4-methylsulphonyl benzoyl chloride (NMSBC) to form an enol ester
   fix: The three groups belong in compounds-equivalence.json so a benchmark can join on them. The keeping-apart of the identifiers is correct (production keys on the identifier string, and the unlocanted nam
13. **[pathways]** `recall` on `pathways[6] Detailed Description of the Invention and pathwa`
   Both sections recite processes whose endpoint is not mesotrione and for which no pathway is emitted, and neither record says so, although the Claims pathway does say exactly that for the equivalent case.
   > line 211: [0038] In certain embodiments, there is provided a process for preparation of enol ester of formula (II) using 2-nitro-4-methylsulfonyl toluene (NMST) of formul
   fix: Add an equivalent flag to pathways[6] for [0038]'s two-step NMST to enol ester process at lines 211-215, and to pathways[5] for [0015] at line 109 (NMSBA alone) and [0016] at line 113 (enol ester alon
14. **[reactions]** `linkage` on `Example 7_Step 1`
   The experimental chain is left entirely unlinked: Example 7 charges a reactant whose identifier is character-for-character the product identifier of Examples 4, 5 and 6, yet precursor_step is null.
   > line 329: A mixture of enol ester (20g, 0.06mol) and dichloromethane (60mL) taken in a clean, pre-dried 250mL round bottomed flask
   fix: Set precursor_step to "Example 4::Step 1" (or the candidate the reviewer selects) with linkage_confirmed left false, so the document's own supply of the material is visible in a structured field rathe

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 44 | 43 | 1 |
| `patent` | 19 | 10 | 9 |
| `pathways` | 22 | 16 | 7 |
| `reactions` | 24 | 24 | 2 |
