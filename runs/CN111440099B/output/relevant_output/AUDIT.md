# A5 adversarial audit of CN111440099B

Four independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 24 | 1 | 2 | 9 | 18 |
| `patent` | 1 | 0 | 4 | 10 | 16 |
| `pathways` | 11 | 2 | 3 | 7 | 19 |
| `reactions` | 38 | 1 | 5 | 11 | 18 |
| **total** | | **4** | **14** | **37** | **71** |

## Acted on

Nothing recorded for CN111440099B. Every finding below is outstanding.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical

1. **[compounds]** `fidelity` on `tembotrione`
   The merged record gives the compound's colour and appearance as the red-brown crude rearrangement residue, not the pale yellow solid the patent isolates, so the one field a scorer compares carries the wrong state of the compound.
   > line 278: 控温滴加10％盐酸水溶液调节PH为2重结晶后降温析晶得淡黄色固体，烘干得262.1g环磺酮，含量95％。
   fix: color pale yellow and appearance 淡黄色固体, the isolated material that this same record's mass_g 262.1, purity_pct 95.0 and nmr all come from, with the crude 红棕色固体 of [0029] and the first half of [0053] l
2. **[pathways]** `precision` on `scope=section / Claims :: Claims_Step 1`
   components lists the step's solvents, acids, bases, catalysts and adsorbents alongside its reactants, where A3 rule 12 asks for the reactants plus the product and nothing else.
   > line 54: 所述步骤1）中所述含水溶液，为乙腈、甲醇、乙醇、二甲基甲酰胺与水混合得到的溶液
   fix: ["tembotrione"]. The step's own compounds[] gives acetonitrile, methanol, ethanol, N,N-dimethylformamide and water role solvent, and reactant_names holds only tembotrione. components must be reactant_
3. **[pathways]** `precision` on `scope=patent / null :: Example 6_Step 2`
   components carries the step's by_product entries, which are neither reactants nor the product under any reading of rule 12, so a species the patent removes is presented as a component of the step.
   > line 273: 过滤出三乙胺盐，减压浓缩得红棕色固体环磺酮产品
   fix: Drop 'triethylamine salt' (role by_product in the step's own compounds[]; the text says it is filtered off). The same defect puts 'cyanide' into components on Example 1_Batch 1, Example 2_Batch 7, Exa
4. **[reactions]** `fidelity` on `Summary of the Invention_Step 3`
   The pH is written as the point value 3.0 where the paragraph gives only a one-sided bound, pH to below 3, and the sibling record annotating the identical wording in claim 1 leaves the same two fields null on the explicit ground that writing 3.0 would assert something the text does not.
   > line 117: [0016] 3)控温调节含水溶液pH至3以下，降温、从溶液中结晶出纯化的环磺酮。
   fix: Both null, as on Claims_Step 3, with the bound recorded in notes and in ph_target_stage.

### major

1. **[compounds]** `recall` on `tembotrione`
   The only paragraph in which the patent characterises tembotrione's own physical properties is represented nowhere in the merged artifact: white or off-white, and amorphous powder rather than solid, were both overwritten.
   > line 88: 化学性质：白色或类白色无定形粉末，几乎不溶于乙醇，极易溶于二氯甲烷，微溶于甲苯。
   fix: physical_form powder with colour white or off-white carried somewhere on the record, since 粉末 is a value of the A1 physical_form enum and [0006] is the specification's statement about the substance ra
2. **[compounds]** `fidelity` on `activated carbon`
   The merged mass is the single 5 g charge of Example 6, while all fifteen table batches that actually test the adsorbent charge 1 g, and four of the record's own merged notes state that the 1 g figure is not in dispute across the merge.
   > line 249: | 14 | 重排反应结束后，蒸馏脱溶后取产品5g溶解在20%含水甲醇中，升温至60℃，加入1g活性炭保温一小时后热过滤
   fix: mass_g 1.0, the charge stated identically in batches 1 to 6, 7 to 10, 11 to 13 and 14, with the 5 g of line 273 recorded in notes as the second, larger charge, exactly the way the 1,2-dichloroethane r
3. **[patent]** `schema` on `CN111440099B`
   The assignee type is 'company', which is not one of the six values patent.schema.json allows, and it is the one violation pipeline/schemas/validate.py reports on this artifact.
   > line 23: (73) 专利权人 利民化学有限责任公司
   fix: One of multinational_corp | sme | university | government | individual | null. The value originates in input/CN111440099B-biblio.json line 20 and finalise.py copies it through unchanged, so the correc
4. **[patent]** `precision` on `CN111440099B`
   patent_summary resolves claim 1's solvent enumeration to a disjunctive reading ('acetonitrile, methanol, ethanol or dimethylformamide') while novelty_claims in the same record states that this cannot be settled from the document, so the record both refuses and performs the same resolution.
   > line 54: 所述步骤1）中所述含水溶液，为乙腈、甲醇、乙醇、二甲基甲酰胺与水混合得到的溶液
   fix: Carry the enumeration without a conjunction in patent_summary as well, matching the Chinese enumeration comma and matching what novelty_claims says about it. The contrast is visible one line later at 
5. **[patent]** `recall` on `CN111440099B`
   parties.examiners is null although the front page prints an examiner and the schema has an array slot with a name property for exactly this.
   > line 37: [examiner] 审查员 靳贝贝
   fix: [{"name": "Jin Beibei"}]. The null is not a merge artifact: pipeline/finalise.py hardcodes "examiners": None in the parties block, so no biblio file can populate it. That hardcode is the shape CLAUDE.
6. **[patent]** `precision` on `CN111440099B`
   Both narrative fields cite description paragraphs that the A4 prompt's declared input never supplied, and with no provenance sidecar and no run notes there is nothing that records what the model actually saw or which model it was.
   > line 137: [0026] 本发明的磺酮产品的纯化方法，可大大降低磺酮产品中氰化物杂质的含量
   fix: Either the rendered A4 prompt understates what was passed, in which case the prompt should state the full input, or the narrative was written with access to the whole description, in which case the re
7. **[pathways]** `schema` on `scope=section / Synthesis Scheme`
   Both steps of this pathway carry validation_flags route_attribution_unclear and drawing_text_conflict, and nothing in honest_uncertainty_flags records either, so rule 16 is not met and the drawn route reads as cleanly attributed to the invention.
   > line 153: [IMAGE_EXTRACT: {"reactions": [{"step_id": 1, "reactants": [{"smiles": "CS(=O)(=O)c1ccc(C(=O)O)c(Cl)c1COCC(F)(F)F"
   fix: Add a flag recording the attribution problem, e.g. route_attribution_unclear or scheme_reprinted_from_background. I opened p03 and p05 and magnified both schemes from the PDF at 8x: the [0031] scheme 
8. **[pathways]** `schema` on `scope=section / Example 2`
   Two of this pathway's three steps carry validation_flags drawing_text_conflict and reagent_written_not_drawn and the third is clean, so the pathway presents no problem at all beyond the missing yields, which rule 16 forbids.
   > line 145: 向三口烧瓶加入的2‑氯‑3‑(2,2,2‑三氟乙氧基)甲基‑4‑甲磺酰基苯甲酰氯，1,2‑二氯乙烷，保温15℃搅拌。缓慢加入氯化亚砜。
   fix: Add a flag reflecting drawing_text_conflict, e.g. drawing_text_conflict_in_chain. The prose at line 145 charges the acyl chloride and then adds thionyl chloride while the drawing at line 153 starts fr
9. **[pathways]** `arithmetic` on `scope=section / Example 1`
   The chain splices a 5 g lab aliquot onto a scheme that prints no charge at all, which is exactly rule 15's scale_discontinuity_in_chain, and the flag is absent from all five Example 1 to Example 5 pathways.
   > line 163: 重排反应结束后，蒸馏脱溶后取环磺酮产品5g溶解在20%含水甲醇中
   fix: Add scale_discontinuity_in_chain. Synthesis Scheme_Step 2 has scale not_specified and, per reactions-provenance.json, [0029] prints not one quantity; the terminal batch has scale lab and consumes 5 g 
10. **[reactions]** `fidelity` on `Example 1_Batch 1`
   The 20% of 20%含水甲醇 is assigned to the methanol, which states a medium of 20% methanol in water, the inverse of what the document defines; [0018] and claim 1 both define the figure as the water content of the aqueous solution, and the 13 batch records of Examples 2 to 5 assign the identical phrase to water. Batches 2 to 6 of this section carry the same inverted assignment.
   > line 163: | 1 | 重排反应结束后，蒸馏脱溶后取环磺酮产品5g溶解在20%含水甲醇中，升温至60℃，加入1g活性炭保温一小时后热过滤，控温滴加10%稀盐酸调节PH为2，逐渐降温至15℃，过滤得纯化环磺酮。 | 1327 | 47 | 98% |
   fix: reagent "water", value 20.0, as Example 2_Batch 7 through Example 4_Batch 15 already have it (see [0018] at line 121, 含水量为20％～40％).
11. **[reactions]** `fidelity` on `Example 6_Step 3`
   Same inversion at the only pilot-scale purification: the 40% of 40％含水甲醇 is assigned to the methanol, so the record states a 40% methanol medium where the document means 40% water, the top of claim 1's 20% to 40% water range.
   > line 273: 环磺酮产品中加入40％含水甲醇，升温至60℃后加入5g活性炭保温1h，热过滤
   fix: reagent "water", value 40.0.
12. **[reactions]** `precision` on `Synthesis Scheme_Step 2`
   reactant_names carries the by-product that the step filters off and the intermediate it never isolates, so two of its seven entries are not reactants at all; the same one-pot step in Example 6 lists neither.
   > line 145: 过滤出三乙胺盐，减压浓缩得红棕色固体。
   fix: Drop "triethylamine salt" and "enol ester" from reactant_names; they remain in compounds[] with their own roles.
13. **[reactions]** `precision` on `Example 6_Step 3`
   reactant_names carries four compounds that are not reactants: two solvents, the adsorbent and the acid. The 19 batch records annotating the same purification list only tembotrione, and the reference run at runs/CN104292137A keeps solvents, adsorbents and workup acids out of this field, so a field-by-field comparison scores four false reactants on this record.
   > line 273: 环磺酮产品中加入40％含水甲醇，升温至60℃后加入5g活性炭保温1h，热过滤
   fix: reactant_names = ["tembotrione"], as on Example 1_Batch 1 through Example 5_Batch 19.
14. **[reactions]** `schema` on `Example 6_Step 3`
   Four compound entries carry quantity as JSON null instead of the quantity object with null members that rule 6 specifies and that the other 210 entries use, so any consumer reading quantity.mass_g on them fails rather than reading a null mass.
   > line 273: 重新加入新的1,2‑二氯乙烷500ml和三乙胺200g，投入1,3环己二酮92g和丙酮氰醇0.5g，40℃保温6h。
   fix: quantity: {"mass_g": null, "volume_ml": null, "mmol": null, "equivalents": null, "yield_pct": null} on all four entries.

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 24 | 24 | 0 |
| `patent` | 24 | 20 | 4 |
| `pathways` | 26 | 11 | 18 |
| `reactions` | 38 | 38 | 5 |
