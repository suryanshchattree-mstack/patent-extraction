# A5 adversarial audit of CN112645853A

Four independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 280 | 0 | 12 | 17 | 12 |
| `patent` | 1 | 0 | 1 | 7 | 11 |
| `pathways` | 32 | 0 | 10 | 6 | 12 |
| `reactions` | 54 | 0 | 12 | 16 | 13 |
| **total** | | **0** | **35** | **46** | **48** |

## Acted on

Nothing recorded for CN112645853A. Every finding below is outstanding.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical


### major

1. **[compounds]** `fidelity` on `Example 3 / sodium hydroxide`
   purity_pct is null, so mass_g 14.0 and mmol 105.0 contradict each other by a factor of 3.3 within the same record.
   > line 325: 室温下将14g氢氧化钠(30％，0.105mol)滴入其中
   fix: purity_pct=30.0, matching the convention used for the 48 percent charge in Example 1 and the 96 percent charge in Example 4
2. **[compounds]** `fidelity` on `Example 6 / potassium hydroxide`
   purity_pct is null, so mass_g 6.6 implies 117.6 mmol of potassium hydroxide against the recorded 100.0 mmol.
   > line 379: 室温下将6.6g氢氧化钾(85％，0.1mol)滴入其中
   fix: purity_pct=85.0, as recorded for the identical 85 percent grade in Example 5 and Example 10
3. **[compounds]** `fidelity` on `Example 15 / sodium hydroxide`
   purity_pct is null, so mass_g 17.3 implies 432.5 mmol against the recorded 130.0 mmol.
   > line 533: 17.3g氢氧化钠溶液(30％，0.13mol)
   fix: purity_pct=30.0; the record note explains the omission but no structured field then carries the concentration that reconciles mass_g with mmol
4. **[compounds]** `fidelity` on `Example 16 / potassium hydroxide`
   purity_pct is null, so mass_g 26.1 implies 465.2 mmol against the recorded 140.0 mmol.
   > line 543: 26.1g氢氧化钾溶液(30％，0.14mol)
   fix: purity_pct=30.0
5. **[compounds]** `recall` on `Example 3 / sodium hydroxide`
   Example 3 charges sodium hydroxide twice and the artifact carries only the step (1) charge; the step (2) charge of 17.3 g and 0.13 mol survives only in the free-text notes and in no structured field.
   > line 331: 向反应釜中加入160mLDMF、11.6g三氟乙醇(99％，0.115mol)和17.3g氢氧化钠溶液(30％，0.13mol)
   fix: a second sodium hydroxide record for the step (2) charge, mass_g=17.3, mmol=130.0, purity_pct=30.0
6. **[compounds]** `recall` on `Example 6 / potassium hydroxide`
   Example 6 charges potassium hydroxide in both steps and the artifact carries only the step (1) charge; the step (2) charge of 26.1 g and 0.14 mol appears only in the notes.
   > line 386: 向反应釜中加入70mLDMF、12.6g三氟乙醇(99％，0.125mol)和26.1g氢氧化钾溶液(30％，0.14mol)
   fix: a second potassium hydroxide record for the step (2) charge, mass_g=26.1, mmol=140.0, purity_pct=30.0
7. **[compounds]** `recall` on `Example 7 / sodium tert-butoxide`
   Example 7 charges sodium tert-butoxide in both steps and the artifact carries only the step (1) charge; the step (2) charge of 11.8 g and 0.12 mol appears only in the notes.
   > line 405: 向反应釜中加入130mL THF、10.6g三氟乙醇(99％，0.105mol)和11.8g叔丁醇钠(98％，0.12mol)
   fix: a second sodium tert-butoxide record for the step (2) charge, mass_g=11.8, mmol=120.0, purity_pct=98.0
8. **[compounds]** `recall` on `None`
   The alkali metal alkoxide named as a reagent throughout the claims and the summary has no record in any section, although the parallel generic reagents basic substance and tertiary alcohol were both recorded.
   > line 47: 或者将2-氯-3-溴甲基-4-甲磺酰基苯甲酸盐与碱金属醇盐反应
   fix: one record per section that names it (Claims and Summary of the Invention) with identifier alkali metal alkoxide, identifier_type other, resolved false, role base or reactant
9. **[compounds]** `recall` on `None`
   The generic basic substance is recorded in Beneficial Effects but omitted from Claims and Summary of the Invention, where it is named in almost every paragraph.
   > line 45: 原料2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯在碱性物质存在下于三级醇溶剂中发生酯解反应
   fix: a basic substance record in the Claims and Summary of the Invention sections as well, on the same convention
10. **[compounds]** `recall` on `Example 2, Example 6, Example 10 / 2-chloro-3-(bromomethyl)-`
   Three examples fold the generic step (1) heading name into the specific alkali salt record as an alias, while nine other examples emit it as a separate unresolved record and their notes state that collapsing it would be wrong; the two conventions cannot both be right.
   > line 298: (1)2-氯-3-溴甲基-4-甲磺酰基苯甲酸盐的制备，主要反应过程可以以如下反应方程式表示：
   fix: one convention applied to all twelve examples that print the heading; add the missing generic records to Examples 2, 6 and 10
11. **[compounds]** `precision` on `Example 8 / methyl 2-chloro-3-(bromomethyl)-4-(methanesulfon`
   The starting ester is marked commercially available in Example 8 alone; the other 24 records for the same identifier say false, and the preamble states the material is prepared by a cited literature route.
   > line 271: 2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的制备可参考CN105601548、CN104292137、US6376429、CN1146548或CN1323292所述的方法
   fix: commercially_available=false, matching the other 24 records
12. **[compounds]** `precision` on `Summary of the Invention / benzyl alcohol`
   resolved is true for the printed name 苄醇, which will resolve downstream to phenylmethanol, but in context 苄 denotes the benzylic position of the substrate and the compound meant is the 3-(hydroxymethyl) analogue of the substrate, as the accompanying dibenzyl ether structure at [0025] confirms.
   > line 182: 苄溴基团会参与反应生成大量的苄醇以及二苄醚类化合物
   fix: resolved=false, since the printed name does not identify one specific compound in this context; the record note already concedes the section does not state that it carries the rest of the aromatic rin
13. **[patent]** `precision` on `CN112645853A`
   The clause 'no methanol is present when the benzylic bromide is displaced' is an added mechanistic assertion; the document says only that the methoxy group is removed from the molecule before etherification, and never states that the etherification medium is methanol free.
   > line 181: This method removes the methoxy group before etherification, effectively avoiding the formation of the impurity 2-chloro-3-methoxymethyl-4-methylsulfonylbenzoic
   fix: Delete the clause 'and no methanol is present when the benzylic bromide is displaced', or replace it with the document's own claim, that the methoxy group is no longer in the molecule when the etherif
14. **[pathways]** `fidelity` on `section:Example 1 (2-step pathway, terminal step Example 1_S`
   The 93.8 percent is printed as a TWO-STEP yield calculated on the methyl ester, that is a whole-chain quantity, but it is carried only as the terminal step's yield while the pathway's own overall_yield_pct is null; the same misplacement recurs identically in all 24 two-step example pathways, and the patent's only stated overall yields are therefore all attached to single steps.
   > line 294: 之后经过滤、水淋洗、烘干得到产物32.9g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为98.7％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率93.8％。
   fix: Set overall_yield_pct = 93.8 on this pathway, and the corresponding printed two-step yield on each of the other 23 example pathways, since the patent states the number for the chain and not for the la
15. **[pathways]** `recall` on `patent (scope=patent, section_label=null)`
   The patent-scope pathway leaves both overall fields null although the description states, for the method as a whole, a maximum two-step yield of 93.8 percent and a maximum HPLC content of 98.7 percent.
   > line 265: 此方法的两步反应最高收率可达93.8％，HPLC检测含量最高达98.7％
   fix: Populate the patent-scope pathway with overall_yield_pct = 93.8 and overall_purity_pct = 98.7 from paragraph [0061], or record in a flag why a patent-level number printed in the description is not car
16. **[pathways]** `precision` on `patent (scope=patent, section_label=null)`
   The single patent-scope pathway is a byte copy of the Claims section pathway: identical steps Claims_Step 1 and Claims_Step 2, identical ksm, intermediates, product, tags and flags, with only scope and section_label differing. The patent's route is therefore anchored to the Markush generic acid and no patent-scope record reaches either of the two concrete target compounds the patent says it prepares.
   > line 121: 具体涉及2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸和2-氯-3-[(RS)-四氢呋喃-2-基甲氧基甲基]-4-甲磺酰基苯甲酸的制备方法。
   fix: Anchor the patent-scope pathway to a concrete terminal compound: one patent-scope pathway per named target, the trifluoroethoxy acid and the tetrahydrofurfuryloxy acid, built from the worked-example c
17. **[pathways]** `linkage` on `section:Example 1 (2-step pathway, terminal step Example 1_S`
   The terminal step consumes sodium 2,2,2-trifluoroethoxide, which is verbatim the product of Example 1_Step 2a in the same section, yet that step is excluded from the chain, so a genuine precursor link exists nowhere in the pathway graph and the route is reported as 2-step and linear. The same omission recurs in Examples 2, 5, 8, 17, 18, 19 and 20.
   > line 292: 向反应釜中加入50mL三氟乙醇，开动搅拌，室温下投入5.2g氢化钠(60％，0.13mol)，搅拌至溶解完全，经脱溶后得到三氟乙醇醇钠固体，密封备用。
   fix: Include Example 1_Step 2a in the chain as a second branch feeding the terminal step, giving chain_length:3 and convergence:convergent with sodium 2,2,2-trifluoroethoxide among the intermediates. If re
18. **[pathways]** `precision` on `section:Example 1 (1-step pathway, step Example 1_Step 2a)`
   This pathway is seeded on a step whose product is consumed by another step of the same section, so it asserts a route whose terminal compound is not a route target, and the record itself says so through reagent_preparation_not_route_to_target. Eight such records exist (Examples 1, 2, 5, 8, 17, 18, 19, 20), each a fragment of the main chain of its own section.
   > line 292: 经脱溶后得到三氟乙醇醇钠固体，密封备用。
   fix: Do not emit a pathway whose terminal product is consumed by another step of the same section; fold the step into that section's chain. If the pass rule genuinely emits reagent preparations as pathways
19. **[pathways]** `arithmetic` on `section:Example 3 (2-step pathway, terminal step Example 3_S`
   The printed mass, assay and yield do not reconcile: 30.7 g at 95.8 percent is 29.41 g of the acid, which against 346.70 g/mol for C11H10ClF3O5S on the printed 0.1 mol of methyl ester is 84.8 percent, not the printed 84.4 percent, a gap of +0.4 points. Example 2 (+0.5) and Example 6 (+0.4) carry inconsistent_step_arithmetic for the same size of gap, and this pathway carries no arithmetic flag at all.
   > line 331: 之后经过滤、水淋洗、烘干得到产物30.7g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为95.8％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率84.4％。
   fix: Either raise inconsistent_step_arithmetic on this pathway as well, or drop it from Examples 2 and 6 and record the systematic bias once at artifact level. The flag must not fire on two of the six exam
20. **[pathways]** `arithmetic` on `section:Example 4 (2-step pathway, terminal step Example 4_S`
   The printed mass, assay and yield do not reconcile: 32.5 g at 98.0 percent is 31.85 g of the acid, which against 346.70 g/mol for C11H10ClF3O5S on the printed 0.1 mol of methyl ester is 91.9 percent, not the printed 91.4 percent, a gap of +0.5 points. Example 2 (+0.5) and Example 6 (+0.4) carry inconsistent_step_arithmetic for the same size of gap, and this pathway carries no arithmetic flag at all.
   > line 349: 之后经过滤、水淋洗、烘干得到产物32.5g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为98.0％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率91.4％。
   fix: Either raise inconsistent_step_arithmetic on this pathway as well, or drop it from Examples 2 and 6 and record the systematic bias once at artifact level. The flag must not fire on two of the six exam
21. **[pathways]** `arithmetic` on `section:Example 8 (2-step pathway, terminal step Example 8_S`
   The printed mass, assay and yield do not reconcile: 32.6 g at 98.2 percent is 32.01 g of the acid, which against 346.70 g/mol for C11H10ClF3O5S on the printed 0.1 mol of methyl ester is 92.3 percent, not the printed 91.9 percent, a gap of +0.4 points. Example 2 (+0.5) and Example 6 (+0.4) carry inconsistent_step_arithmetic for the same size of gap, and this pathway carries no arithmetic flag at all.
   > line 425: 之后经过滤、水淋洗、烘干得到产物32.6g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为98.2％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率91.9％。
   fix: Either raise inconsistent_step_arithmetic on this pathway as well, or drop it from Examples 2 and 6 and record the systematic bias once at artifact level. The flag must not fire on two of the six exam
22. **[pathways]** `arithmetic` on `section:Example 9 (2-step pathway, terminal step Example 9_S`
   The printed mass, assay and yield do not reconcile: 32.4 g at 96.5 percent is 31.27 g of the acid, which against 346.70 g/mol for C11H10ClF3O5S on the printed 0.1 mol of methyl ester is 90.2 percent, not the printed 89.7 percent, a gap of +0.5 points. Example 2 (+0.5) and Example 6 (+0.4) carry inconsistent_step_arithmetic for the same size of gap, and this pathway carries no arithmetic flag at all.
   > line 439: 之后经过滤、水淋洗、烘干得到产物32.4g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为96.5％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率89.7％。
   fix: Either raise inconsistent_step_arithmetic on this pathway as well, or drop it from Examples 2 and 6 and record the systematic bias once at artifact level. The flag must not fire on two of the six exam
23. **[pathways]** `recall` on `section:Summary of the Invention (terminal step Summary of t`
   The section states the second variant of step (2), reaction of the salt with an alkali metal alkoxide obtained from the alcohol and sodium or potassium metal, but the step's compound list carries only the alcohol plus base variant. The parallel Claims_Step 2 record does carry sodium metal and potassium metal as alkoxide_precursor, so two records of the same disclosure disagree.
   > line 226: 优选地，所述碱金属为金属钠或金属钾。
   fix: Add sodium metal and potassium metal (role alkoxide_precursor, as in Claims_Step 2) to the Summary terminal step, so the alkoxide branch of the invention's step (2) is present at both scopes.
24. **[reactions]** `arithmetic` on `Example 3_Step 2`
   The printed two-step yield cannot be reproduced from the printed mass, content and charge, by the same margin that earned Example 2_Step 2 and Example 6_Step 2 a mass_balance_implausible flag, yet no flag is raised here.
   > line 332: 之后经过滤、水淋洗、烘干得到产物30.7g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为95.8％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率84.4％。
   fix: Add "mass_balance_implausible". 30.7 g at 95.8 percent is 29.411 g of C11H10ClF3O5S (346.703), i.e. 0.084830 mol, which on the 0.09984 mol the 34.8 g at 98 percent charge actually contains is 84.97 pe
25. **[reactions]** `arithmetic` on `Example 4_Step 2`
   Same unreproducible printed yield as Examples 2 and 6, same magnitude, no mass_balance_implausible flag.
   > line 350: 之后经过滤、水淋洗、烘干得到产物32.5g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为98.0％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率91.4％。
   fix: Add "mass_balance_implausible". 32.5 g at 98.0 percent is 31.850 g, 0.091865 mol, 92.02 percent on 0.09984 mol against a printed 91.4 percent, a gap of +0.62 points.
26. **[reactions]** `arithmetic` on `Example 8_Step 3`
   Same unreproducible printed yield as Examples 2 and 6, same magnitude, no mass_balance_implausible flag.
   > line 426: 之后经过滤、水淋洗、烘干得到产物32.6g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为98.2％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率91.9％。
   fix: Add "mass_balance_implausible". 32.6 g at 98.2 percent is 32.013 g, 0.092335 mol, 92.49 percent on 0.09984 mol against a printed 91.9 percent, a gap of +0.59 points.
27. **[reactions]** `arithmetic` on `Example 9_Step 2`
   Same unreproducible printed yield as Examples 2 and 6, the largest gap of the six, and validation_flags is empty.
   > line 440: 之后经过滤、水淋洗、烘干得到产物32.4g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为96.5％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率89.7％。
   fix: Add "mass_balance_implausible". 32.4 g at 96.5 percent is 31.266 g, 0.090180 mol, 90.33 percent on 0.09984 mol against a printed 89.7 percent, a gap of +0.63 points. is_complete then becomes false.
28. **[reactions]** `arithmetic` on `Example 6_Step 2`
   The reasoning given for raising the flag here rather than elsewhere is factually wrong about the distribution of the discrepancy, and it is the reason four sibling records were left unflagged.
   > line 386: 得到产物32.4g，HPLC定量得目标化合物2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸含量为96.0％，以2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯计两步反应收率89.3％。
   fix: The bias does not recur across the examples. Recomputed for all twenty, the deviation of the printed two-step yield from the value implied by the printed mass, content and 0.09984 mol charge is +0.56 
29. **[reactions]** `linkage` on `Example 13_Step 1`
   The record asserts a cross-section link in its tags while precursor_step is null and linkage_confirmed is false, and the referenced step is present in this same artifact.
   > line 497: (1)与实施例1所述步骤相同，得到含量为98.2％的2-氯-3-溴甲基-4-甲磺酰基苯
   fix: Set precursor_step to "Example 1::Step 1" per A2 rule 23 and linkage_confirmed to true, since the text names the step explicitly and Example 1_Step 1 is a record in this artifact. Either that, or drop
30. **[reactions]** `linkage` on `Example 13_Step 1`
   conditions_unresolved and cross_reference_unresolved are raised on eight records whose reference does in fact resolve, inside this same artifact and to a fully stated procedure, which suppresses eight otherwise complete records.
   > line 280: 向反应瓶中加入叔丁醇200mL，开动搅拌，室温下将8.8g氢氧化钠(48％，0.105mol)滴入其中，待氢氧化钠分散均匀后，控制釜温在25℃
   fix: A2 rule 27 defines conditions_unresolved as claiming inherited conditions when the referenced record was not found. Example 1_Step 1 was found: 200 mL tert-butanol, NaOH 8.8 g at 48 percent, 25 C, 7 h
31. **[reactions]** `recall` on `Summary of the Invention_Step 2`
   The record omits the alkali metal alkoxide alternative of step (2) entirely, together with the sodium and potassium metal it is made from, although the prose gives both and the scheme draws the alternative below the arrow.
   > line 224: [0042] 优选地，步骤(2)中所述碱金属醇盐为醇和碱金属反应得到。 / [0043] 优选地，所述碱金属为金属钠或金属钾。
   fix: Add the alkali metal alkoxide as a reactant and sodium metal and potassium metal with role alkoxide_precursor, exactly as the parallel Claims_Step 2 record already does from claim 7. Page p06 [0021] w
32. **[reactions]** `recall` on `None`
   No record exists for the side reaction the specification describes and draws, in which conventional ester hydrolysis of the starting material consumes the benzylic bromide to give benzyl alcohol and a bis-benzyl ether.
   > line 182: 常规的酯的水解手段在本发明中不可行，苄溴基团会参与反应生成大量的苄醇以及二苄醚类化合物，结构式如下：
   fix: Emit one record for this transformation under Summary of the Invention, with the bis-benzyl ether drawn at line 185 and verified on page p06 as a product, benzyl alcohol as the second named product, n
33. **[reactions]** `recall` on `Example 6_Step 2`
   Water and hydrochloric acid are absent from compounds although the record's own workup narrative names both and eighteen sibling etherification records carry them.
   > line 386: 反应完毕，负压脱溶，釜残加水120mL，搅拌溶解后滴加浓盐酸将体系pH值酸化至2
   fix: Add water with volume_ml 120.0 and hydrochloric acid, matching the eighteen sibling records. Example 7_Step 2 has the same omission at line 405.
34. **[reactions]** `recall` on `Example 7_Step 2`
   Water and hydrochloric acid are absent from compounds although the workup narrative names both.
   > line 405: 反应完毕，负压脱溶，釜残加水120mL，搅拌溶解后滴加浓盐酸将体系pH值酸化至2
   fix: Add water with volume_ml 120.0 and hydrochloric acid.
35. **[reactions]** `drawings` on `None`
   Four IMAGE_EXTRACT spans in the enriched markdown under-read the page: they report no product, or no molecules at all, where the page plainly draws them.
   > line 143: [IMAGE_EXTRACT: {"reactions": [{"step_id": 1, "reactants": [...], "conditions": [{"text": "ROH"}, {"text": "碱 (base)"}], "products": []}, {"step_id": 2, "reacta
   fix: Page p05 [0008] draws all four structures: the methyl ester with CH2Br, the methyl ester with CH2-O-R, the same as arrow 2's reactant, and the free acid with CH2-O-R. Page p05 [0017] draws the MO2C pr

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 291 | 280 | 14 |
| `patent` | 22 | 15 | 7 |
| `pathways` | 24 | 32 | 5 |
| `reactions` | 56 | 54 | 3 |
