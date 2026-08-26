# A5 adversarial audit of CN104292137A

4 independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 75 | 1 | 18 | 12 | 16 |
| `patent` | 1 | 0 | 5 | 5 | 8 |
| `pathways` | 5 | 2 | 2 | 7 | 11 |
| `reactions` | 33 | 0 | 12 | 7 | 18 |
| **total** | | **3** | **37** | **31** | **53** |

## Acted on

- **Three of the five pathways carry the identical pathway_uuid** - FIXED. finalise.py now seeds pathway_uuid the way PathwaysBuilder actually does, folding in the ordered step signature. The PathwayRecord javadoc we had transcribed is stale; the code carries a comment explaining that the endpoint-only seed lost 20 distinct routes across a ten-patent set.
- **abstract is null** - FIXED. A4 is given the abstract, it does not emit one, and finalise.py had no source wired. Now taken from the pass-V read of the front page.
- **ipc_codes is null** - FIXED. Both IPC classes were transcribed by pass V from the (51) field; finalise.py now reads them.
- **mutually disjoint English spellings** - DOCUMENTED, NOT FIXED. Deliberate: buildCompoundId is a pure function of the identifier string, so production fragments these identically. Merging would make the gold set disagree with production for a reason unrelated to extraction quality. The equivalence is written out to provenance/compounds-equivalence.json so a benchmark can join on it.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical

1. **[compounds]** `precision` on `2-chloro-6-(methanesulfonyl)toluene / 2-chloro-6-(methylsulf`
   The same Chinese name is resolved to two or three different English identifiers depending on which section it was extracted from, so the merge key never matches and one substance becomes two or three records with two or three different `id` join keys; 11 families are affected and 20 of the 75 records are surplus duplicates.
   > line 46: 用溶剂萃取，浓缩，得2-氯-6-甲磺酰基甲苯；
   fix: Render 甲磺酰基 one way throughout (pick one of methanesulfonyl / methylsulfonyl) so the finalise merge collapses each substance to a single record and a single id. Reported as one finding because it is o

### major

1. **[compounds]** `precision` on `2-chloro-6-(methanesulfonyl)toluene`
   Because the duplicate families never merged, only the Example 1 spelling of each intermediate carries the mass, yield, melting point and NMR; the Claims and Summary spellings are quantity-empty shells that an extractor can never match, which depresses precision on a benchmark for reasons unrelated to extraction quality.
   > line 187: 浓缩得淡黄的固体28.6g,收率84％。
   fix: After collapsing the duplicates per the previous finding, the single surviving record carries the Example 1 quantity and characterisation.
2. **[compounds]** `precision` on `methanesulfonyl chloride`
   section_label on a cross-section merged record names a section that does not contain the recorded quantity, so any section-level scoring is measuring the wrong section; 21 of the 43 records labelled 'Summary of the Invention' carry a quantity that appears only in Example 1.
   > line 187: 然后滴加甲磺酰氯25.25g(0.22mol)
   fix: Either set section_label to the section the surviving quantity came from (Example 1), or make section_label a list as compounds-sections.json already does. Same defect on 2-chlorotoluene, acetyl chlor
3. **[compounds]** `schema` on `tembotrione`
   Exactly one record in the whole artifact has is_section_product true and it sits on 'Technical Field', a section that only repeats the invention title; Example 1, Claims and Abstract each end with an isolated or named final product and none of them has a record flagged as the section product. raw-compounds.json had the flag true in five sections and the merge collapsed it to one.
   > line 253: 浓缩得米黄色固体188g,收率95％,熔点120-123℃。
   fix: Preserve the per-section flag: the merged tembotrione record should carry section_label 'Example 1' (the section that isolates it) or the flag should be carried per section alongside compounds-section
4. **[compounds]** `arithmetic` on `2-chloro-6-(methylsulfonyl)toluene`
   Step 1 does not close: 0.2 mol of 2-chlorotoluene gives 40.93 g of C8H9ClO2S (MW 204.67) at 100%, so 28.6 g is 69.9%, not the printed 84%; 28.6 g at 84% implies MW 170, which is the methylthio compound of the drawn prior-art route, not the sulfone. No note flags it, although the identical defect at step 3 was flagged.
   > line 187: 加入2-氯甲苯25.3g(0.2mol)...浓缩得淡黄的固体28.6g,收率84％。
   fix: Add to notes: 'INTERNALLY INCONSISTENT AS PRINTED: 28.6 g from a 0.2 mol charge is 69.9% of theory for C8H9ClO2S, not the stated 84%.' Do not change either number.
5. **[compounds]** `arithmetic` on `2-chloro-3-acetyl-6-(methylsulfonyl)toluene`
   Step 2 does not close: 0.2 mol charge gives 49.34 g of C10H11ClO3S (MW 246.71) at 100%, so 36.5 g is 74.0%, not the printed 86%. No note flags it.
   > line 197: 加入2-氯-6-甲磺酰基甲苯34.0g(0.2mol)...浓缩得白色固体2-氯-3-乙酰基-6-甲磺酰基甲苯36.5g，收率86％
   fix: Add an INTERNALLY INCONSISTENT note giving 74.0% computed against the stated 86%. Also note that the charge 34.0 g / 0.2 mol implies MW 170 while the named substrate C8H9ClO2S is 204.67.
6. **[compounds]** `arithmetic` on `methyl 2-chloro-3-methyl-4-(methylsulfonyl)benzoate`
   Step 4 does not close: 0.2 mol charge gives 52.54 g of C10H11ClO4S (MW 262.71) at 100%, so 44.2 g is 84.1%, not the printed 97%. No note flags it.
   > line 215: 加入2-氯-3-甲基-4-甲磺酰基苯甲酸42.8g(0.2mol)...得白色固体44.2g，收率97％
   fix: Add an INTERNALLY INCONSISTENT note giving 84.1% computed against the stated 97%. Also note the charge 42.8 g / 0.2 mol implies MW 214 while the named acid C9H9ClO4S is 248.68.
7. **[compounds]** `arithmetic` on `methyl 2-chloro-3-(bromomethyl)-4-(methylsulfonyl)benzoate`
   Step 5 does not close: 0.2 mol charge gives 68.32 g of C10H10BrClO4S (MW 341.60) at 100%, so 41.6 g is 60.9%, not the printed 70%. No note flags it.
   > line 227: 加入2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯43.6g(0.2mol)...干燥得固体41.6g,收率70％
   fix: Add an INTERNALLY INCONSISTENT note giving 60.9% computed against the stated 70%.
8. **[compounds]** `arithmetic` on `2-chloro-3-[(2,2,2-trifluoroethoxy)methyl]-4-(methylsulfonyl`
   Step 6 does not close: 0.2 mol charge gives 69.34 g of C11H10ClF3O5S (MW 346.70) at 100%, so 55.6 g is 80.2%, not the printed 92%. No note flags it.
   > line 236: 加入2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯55.8g(0.2mol)...浓缩得55.6g白色固体，收率92％
   fix: Add an INTERNALLY INCONSISTENT note giving 80.2% computed against the stated 92%. Also note the charge 55.8 g / 0.2 mol implies MW 279 while the named bromide C10H10BrClO4S is 341.60.
9. **[compounds]** `arithmetic` on `3-oxo-1-cyclohexen-1-yl 2-chloro-3-[(2,2,2-trifluoroethoxy)m`
   Step 7 does not close: 0.2 mol charge gives 88.16 g of C17H16ClF3O6S (MW 440.82) at 100%, so 72.8 g is 82.6%, not the printed 92%. No note flags it.
   > line 243: 加入2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸60.4g(0.2mol)...浓缩得油状物72.8g,收率92％。
   fix: Add an INTERNALLY INCONSISTENT note giving 82.6% computed against the stated 92%.
10. **[compounds]** `arithmetic` on `tembotrione`
   Step 8 does not close and the record carries no quantity at all: 0.5 mol of the enol ester gives 220.41 g of C17H16ClF3O6S at 100%, so the isolated 188 g is 85.3%, not the printed 95% - yet the tembotrione record has quantity.mass_g and quantity.yield_pct null, so the final product of the whole route has no isolated mass or yield anywhere in the artifact.
   > line 253: 加入...3-氧代-1-环己烯酯198g(0.5mol)，0.2g氰基丙酮和三乙胺60.6(0.6mol)...浓缩得米黄色固体188g,收率95％,熔点120-123℃。
   fix: Populate mass_g 188.0 and yield_pct 95.0 on the tembotrione record from [0060], and add an INTERNALLY INCONSISTENT note giving 85.3% computed against the stated 95%. The merge that folded seven per-se
11. **[compounds]** `arithmetic` on `step-to-step continuity across Example 1`
   Five steps consume more material than the preceding step produced and no record flags the discontinuity: step 1 makes 28.6 g and step 2 charges 34.0 g; step 2 makes 36.5 g and step 3 charges 50.88 g; step 5 makes 41.6 g and step 6 charges 55.8 g; step 6 makes 55.6 g and step 7 charges 60.4 g; step 7 makes 72.8 g and step 8 charges 198 g. Recorded as one finding because it is a single omitted check applied along one chain.
   > line 243: 浓缩得油状物72.8g,收率92％。 ... 加入2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸3-氧代-1-环己烯酯198g(0.5mol)
   fix: Append 'DISCONTINUITY: the preceding step isolates less material than this step charges' to the notes of the five affected product records. Do not adjust any mass.
12. **[compounds]** `fidelity` on `bromine`
   The printed mass and mole figure for bromine are mutually inconsistent and nothing flags it: 39.6 g of Br2 (MW 159.81) is 248 mmol, not the printed 0.22 mol. Every other reagent mass/mol pair in the patent is internally consistent, so this one stands out.
   > line 227: 在室温下滴加39.6g(0.22mol)溴素，滴加时间约50min
   fix: Keep both values as printed (rule 12) and add 'INTERNALLY INCONSISTENT AS PRINTED: 39.6 g of Br2 is 0.248 mol, not the stated 0.22 mol' to notes.
13. **[compounds]** `fidelity` on `sodium hypochlorite`
   mass_g 500.0 is the mass of a 15% aqueous solution, not of sodium hypochlorite, so the numeric field on a record identified as the solute carries a value roughly 6.7x too high; the note says so but the number is what a benchmark reads.
   > line 206: 在室温下滴加15％的次氯酸钠溶液500g
   fix: Either leave mass_g null and keep 500 g of 15% solution in notes only, or make the identifier the solution. As it stands the field and the identifier disagree.
14. **[compounds]** `precision` on `methanesulfonyl chloride`
   The record's role contradicts its own notes: role is 'reagent' but the notes state it was recorded as reactant. The cross-section merge kept the Summary role and the Example 1 notes, so the artifact now asserts two different roles for one compound.
   > line 187: 然后滴加甲磺酰氯25.25g(0.22mol)
   fix: Pick one and make the notes agree. The Example 1 extraction said reactant; the sulfonyl group is incorporated into the product, so reactant is the better-supported value.
15. **[compounds]** `precision` on `acetyl chloride`
   role 'reagent' contradicts the record's own notes, which say it was recorded as reactant; the Example 1 extraction had role reactant and the merge overwrote it with the Summary value.
   > line 197: 滴加乙酰氯23.5g(0.3mol)
   fix: Set role to 'reactant' or delete the contradicting sentence from notes.
16. **[compounds]** `precision` on `methanol`
   role 'reagent' contradicts the record's own notes, which twice say reactant; two of the three per-section extractions (Claims, Example 1) had role reactant and the merge kept the minority value.
   > line 215: 对甲苯磺酸0.5g和200ml甲醇，加热回流搅拌10h
   fix: Set role to 'reactant'.
17. **[compounds]** `precision` on `sodium 2,2,2-trifluoroethoxide`
   role 'reagent' contradicts the record's own notes, which twice say reactant; two of three per-section extractions had role reactant.
   > line 236: 三氟乙醇钠28.1g(0.23mol)和100mlTHF溶剂中
   fix: Set role to 'reactant'.
18. **[compounds]** `precision` on `N,N-dimethylformamide`
   role 'catalyst' is an inference the text does not support, and it contradicts the record's own Claims-section note, which concluded 'the most the text supports is additive'. The Claims extraction had role additive and the merge overwrote it.
   > line 243: N,N-二甲基甲酰胺(0.05g)和100ml二氯甲烷
   fix: Set role to 'additive', which is the most specific value the text supports (rule 9), or make the notes stop asserting otherwise.
19. **[patent]** `translation` on `CN104292137A`
   The title names a different herbicide from the one the document is about: 'cyclic sulcotrione' is Google's character-by-character gloss of 环磺草酮 (环 = cyclic, 磺草酮 = sulcotrione) and is not a compound, while sulcotrione itself is a real and different triketone.
   > line 107: [0002] 除草剂环磺草酮(Tembotrione)，化学名称：2-(2-氯4-甲磺酰基-3-[(2,2,2-三氟乙氧基)甲基]苯甲酰基)环己烷-1,3-二酮。由拜耳公司2007年研制的三酮类玉米田除草剂
   fix: Follow the Chinese. [0002] gives the chemical name 2-(2-chloro-4-methylsulfonyl-3-[(2,2,2-trifluoroethoxy)methyl]benzoyl)cyclohexane-1,3-dione and attributes it to Bayer in 2007, which is tembotrione 
20. **[patent]** `arithmetic` on `CN104292137A`
   compound_count 75 is arithmetically correct against compounds.json but is inflated by roughly 16 records, because eight molecules are each held three times under three different English spellings of the same Chinese name.
   > line 197: 在装有搅拌器，温度计和回流冷凝管的500ml四口反应瓶中加入2-氯-6-甲磺酰基甲苯34.0g(0.2mol)
   fix: The count faithfully reports len(compounds.json), so the arithmetic passes; the defect is upstream. Normalising '(methanesulfonyl)' / '(methylsulfonyl)' / 'methylsulfonyl' spellings collapses 24 recor
21. **[patent]** `schema` on `CN104292137A`
   The pointer ca46f39f-6f64-5bfd-bd5d-256718ff1ac6 is not unique to the winning pathway - three pathways share it, and two of those three have overall_yield_pct null.
   > line 0: N/A - finalise.py:229 keys pathway_uuid on (patent_id, scope, ksm, product) with no section_label; finalise.py:239 picks best = max(...) which resolves the 28.4
   fix: Resolve the pathway_uuid collision first (see pathways-report.json finding 1). Until then a consumer dereferencing this uuid gets three pathways back, two of which contradict the 28.4 it is attached t
22. **[pathways]** `vocabulary` on `Claims_Step 1, Claims_Step 2, Claims_Step 3, Claims_Step 5, `
   Rule 11 requires steps[] fields to be copied verbatim from the reaction record, but 10 step projections carry role values that reactions.json no longer holds and that finalise.py itself declares outside CompoundRecord's enum.
   > line 0: N/A - finalise.py:94 VALID_ROLES = {"product", "reactant", "reagent", "solvent", "catalyst", "ligand", ...}; normalise_role() at line 101 is called from finalis
   fix: Apply normalise_role to steps[].compounds in finalise_pathways so the projections match reactions.json: water->'other' or 'solvent', hydrochloric acid->'acid', ethyl ...benzoate->'reactant'.
23. **[pathways]** `schema` on `30 of the 41 step projections across all five pathways`
   Rule 12 defines components as 'the identifiers of that step's reactants plus its product', but components carries reagents as well, and does so inconsistently between pathways that describe the same reaction.
   > line 62: 将2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯溶于溶剂中，加入适量的过氧苯甲酸，在回流的条件下，滴加溴素，滴完后继续反应1-10h
   fix: Either apply rule 12 mechanically (role=='reactant' plus is_product) in every step, or state the widened definition once and apply it uniformly. The current field cannot be reproduced by any single ru
24. **[reactions]** `arithmetic` on `Example 1_Step 4`
   scale_discontinuity is deliberately not raised, but on a molar basis this step charges 0.200 mol of a material of which step 3 states it isolated only 0.1728 mol (0.24 mol x 72%), a 15.7% over-draw; the record's own justification rests on the 82 g figure that the same record declares irreconcilable on any reading.
   > line 215: 在250ml的四口反应瓶中加入2-氯-3-甲基-4-甲磺酰基苯甲酸42.8g(0.2mol)
   fix: add 'scale_discontinuity' to validation_flags and record the molar comparison (step 3 output 0.1728 mol vs step 4 input 0.200 mol) alongside the mass comparison; do not alter any printed number.
25. **[reactions]** `vocabulary` on `Claims_Step 8`
   The same final transformation is classified 'other' here but 'acylation' in Summary of the Invention_Step 8, Example 1_Step 8 and Summary of the Invention_Scheme Step 9, and the two notes give directly opposing reasons for the same decision, so a gold set carries two contradictory labels for one reaction.
   > line 74: 8)在装有干燥管的反应瓶中加入2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸3-氧代-1-环己烯酯、氰基丙酮和三乙胺溶于溶剂中在室温持续搅拌
   fix: pick one value for this transformation and use it in all four records; the reasoning in notes must not contradict itself between sections.
26. **[reactions]** `vocabulary` on `Summary of the Invention_Step 6`
   is_one_pot is false here but true in Claims_Step 6 and Example 1_Step 6 for the same two-transformation step, and the stated reason (an interposed water wash and concentration) is present in all three source recitations, so the same evidence produces opposite answers in different sections.
   > line 144: 将2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯溶于溶剂中，加入2,2,2-三氟乙醇钠，在室温下搅拌，然后水洗，浓缩得2-氯-3-(2,2,2-三氟乙氧基）甲基-4-甲磺酰基苯甲酸乙酯，将残余物溶于溶剂中
   fix: apply one one-pot test to all three recitations of step 6; if the interposed 水洗/浓缩 defeats one-pot it defeats it in Claims and Example 1 too.
27. **[reactions]** `vocabulary` on `Summary of the Invention_Step 5`
   named_reaction is null here but 'Wohl-Ziegler bromination' in Claims_Step 5 and Example 1_Step 5 for the same bromine-plus-peroxide benzylic bromination, and the notes argue the case both ways in different records.
   > line 140: 将2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯溶于溶剂中，加入适量的过氧苯甲酸，在回流的条件下，滴加溴素
   fix: one value across the three records, and one line of reasoning; the corresponding named_rxn tag must follow it.
28. **[reactions]** `fidelity` on `Claims_Step 1`
   The identical Chinese sentence is recorded as type 'range' with min_c and max_c null here, but as min_c 0.0 / max_c 15.0 in Summary of the Invention_Step 1, so one printed temperature range has two different structured values in the gold set.
   > line 46: 在0℃-15℃间滴加甲磺酰氯
   fix: use one reading in both records. Rule 29 (record as printed) favours min_c 0.0 / max_c 15.0 with the sign ambiguity noted, but either choice is acceptable provided the two records agree.
29. **[reactions]** `recall` on `Summary of the Invention_Step 1`
   The three permitted solvents are named at line 154, inside this record's own section (lines 111-175), and Claims_Step 1 records all three as solvent compounds from the identical recitation, but this record carries no solvent compound at all.
   > line 154: [0022] 按上述方案，步骤1)中2-氯甲苯，催化剂无水三氯化铝和甲磺酰氯的摩尔配比为1:1-3:1-2，所述溶剂为二氯甲烷、氯仿或1,2-二氯乙烷。
   fix: add dichloromethane, chloroform and 1,2-dichloroethane with role solvent, as Claims_Step 1 does, or drop them from Claims_Step 1; the two sections must not disagree on the same content.
30. **[reactions]** `recall` on `Summary of the Invention_Step 2`
   The three permitted solvents for step 2 are named at line 156, inside this record's own section, and Claims_Step 2 records all three, but this record carries no solvent compound.
   > line 156: [0023] 按上述方案，步骤2)中2-氯-6-甲磺酰基甲苯，无水三氯化铝和乙酰氯的摩尔配比为1:1-5:1-2，所述溶剂为二氯甲烷、氯仿或1,2-二氯乙烷。
   fix: add dichloromethane, chloroform and 1,2-dichloroethane with role solvent, matching Claims_Step 2.
31. **[reactions]** `recall` on `Summary of the Invention_Step 5`
   The four permitted solvents for step 5 are named at line 158, inside this record's own section, and Claims_Step 5 records all four, but this record carries no solvent compound.
   > line 158: [0024] 按上述方案，步骤5)中2-氯-4-甲磺酰基-3-甲基苯甲酸甲酯与溴素反应的摩尔配比为1:1-1.5，所述的溶剂为四氯化碳，氯仿，二氯甲烷或1,2-二氯乙烷。
   fix: add carbon tetrachloride, chloroform, dichloromethane and 1,2-dichloroethane with role solvent, matching Claims_Step 5.
32. **[reactions]** `recall` on `Summary of the Invention_Step 6`
   The four permitted solvents for step 6 are named at line 160, inside this record's own section, and Claims_Step 6 records all four, but this record carries no solvent compound.
   > line 160: [0025] 按上述方案，步骤6)中2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯与三氟乙醇钠的摩尔配比为1:1-1.5，所述的溶剂为四氢呋喃，乙腈，二氯甲烷或甲苯。
   fix: add tetrahydrofuran, acetonitrile, dichloromethane and toluene with role solvent, matching Claims_Step 6.
33. **[reactions]** `recall` on `Summary of the Invention_Step 7`
   This record carries no base compound at all, although its own procedure text charges 碱 as part of a mixture with the dione and the six permitted bases are named at lines 162-167 inside this same section; Claims_Step 7 records all six from the identical recitation.
   > line 164: [0027] 按上述方案，所述的无机碱为碳酸钠，碳酸钾，氢氧化钠或氢氧化钾.
   fix: add sodium carbonate, potassium carbonate, sodium hydroxide, potassium hydroxide, pyridine and triethylamine with role base, matching Claims_Step 7, or at minimum a generic base entry for the 碱 the st
34. **[reactions]** `recall` on `Summary of the Invention_Step 1 through Step 8`
   Quench, acidification and wash agents (ice water, hydrochloric acid, water) are excluded from compounds[] by a convention declared in the Summary records' notes, but the Claims records and every Example 1 record put the same species in compounds[]; one convention decision, applied to eight records, makes the gold set score identical extractor behaviour as correct in two sections and incorrect in the third. Reported as one finding because it is one decision, not eight independent omissions.
   > line 123: 反应完毕，将反应物倒入冰水和盐酸的混合物中，分出有机层，水层用溶剂萃取，合并有机层，水洗
   fix: adopt one rule for whether workup species appear in compounds[] and apply it to all 24 prose records; affected Summary records are Steps 1, 2, 3, 6, 7 and 8.
35. **[reactions]** `precision` on `Example 1_Step 1 through Step 8`
   All eight Example 1 records carry computed molecular weights, molecular formulae and derived percentages that appear nowhere in the patent (9 to 15 such numbers per record, e.g. 204.67, 246.71, 474.5, 44.71, 69.9, plus formulae C8H9ClO2S ... C17H16ClF3O6S), which violates A2 rule 32 ('Introduce no number that is absent from the text'), the A2 output rule that the arithmetic_check 'never enters reactions.json', and the A5 precision rule that this annotation may contain no molecular weights or formulae.
   > line 187: 浓缩得淡黄的固体28.6g,收率84％。
   fix: keep the derivation in reactions-provenance.json arithmetic_check, where it already exists in full, and reduce the notes to the qualitative statement plus the printed numbers; the validation_flags alr

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 59 | 57 | 2 |
| `patent` | 14 | 11 | 4 |
| `pathways` | 5 | 5 | 0 |
| `reactions` | 33 | 33 | 9 |
