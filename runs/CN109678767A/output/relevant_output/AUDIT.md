# A5 adversarial audit of CN109678767A

Four independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 66 | 1 | 12 | 14 | 18 |
| `patent` | 1 | 1 | 4 | 10 | 12 |
| `pathways` | 14 | 5 | 4 | 8 | 13 |
| `reactions` | 36 | 2 | 14 | 11 | 19 |
| **total** | | **9** | **34** | **43** | **62** |

## Acted on

Nothing recorded for CN109678767A. Every finding below is outstanding.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical

1. **[compounds]** `precision` on `hydrobromic acid`
   Seventeen of the twenty-four records that carry a quantity are labelled section 'Summary of the Invention', a section (lines 109-155) that prints no absolute charge anywhere and gives only molar ratio ranges; the quantity on each of those records was in fact printed in Example 3 or Example 4, so any section-level scoring reads the wrong section and any consumer that trusts section_label reads a charge into a section that has none.
   > line 129: [0019] 优选的，步骤1)中，2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯、催化剂、氢溴酸、双氧水的摩尔比为1:0.01～0.1:1～2:1～2。
   fix: Set section_label on each merged record to the section that actually contains the surviving quantity (Example 4 for fifteen of the seventeen, Example 3 for DMF and m-chloroperoxybenzoic acid), or leav
2. **[patent]** `fidelity` on `CN109678767A`
   best_overall_yield_pct 75.2 is not this patent's yield at all: it is the yield of the competing Heilongjiang University NBS route that [0006] quotes in order to criticise it, and the uuid beside it points at a one-step Background pathway.
   > line 98: 黑龙江大学的专利号CN105601548A报道了以3-氯-2-甲基苯胺为起始原料合成环磺酮的工艺在制备2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的时候，也是以昂贵NBS为溴化剂，会有大量固废产生，且收率偏低，只有75.2％。
   fix: 69.88, pointing at a0f0bd17-4bd9-5be2-aab9-02c121628d45 (scope patent) or 3f019f3d-7b62-5de4-9e56-6f36ce71bffb (Example 1), which are the invention's own best. I dereferenced b97dc161 in pathways.json
3. **[pathways]** `precision` on `scope=section / Background, 77ebc24a-6046-5af2-bf1f-ae79e5b3`
   The KSM of this chain is NBS, which rule 3 names as exactly the thing a KSM is not: the brominating reagent that decorates the substrate, while the text names the route's starting material two clauses earlier.
   > line 96: 拜耳公司的专利号CN1323292A报道了以2,6-二氯甲苯为起始原料合成环磺酮的工艺，在制备2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的时候，以NBS为溴化剂
   fix: ksm.identifier = '2,6-dichlorotoluene', the compound the sentence calls 起始原料 (starting material). That record already exists in compounds.json with tags ['compound_class:starting_material'], so no new
4. **[pathways]** `precision` on `scope=section / Background, b97dc161-e773-5a6e-b7bd-6f7e7024`
   Same defect on the Heilongjiang University route: the KSM is the brominating reagent NBS, not the aniline the sentence names as the starting material.
   > line 98: 黑龙江大学的专利号CN105601548A报道了以3-氯-2-甲基苯胺为起始原料合成环磺酮的工艺在制备2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的时候，也是以昂贵NBS为溴化剂
   fix: ksm.identifier = '3-chloro-2-methylaniline', which is already in compounds.json tagged compound_class:starting_material.
5. **[pathways]** `precision` on `scope=section / Background, 8b8007ba-ee51-5b01-ba9c-4835da7a`
   The KSM of the three-step CN104292137A chain is elemental bromine, the brominating agent, while the same sentence names 2-chlorotoluene as the route's starting material.
   > line 100: 武汉工程大学的专利号CN104292137A报道了以2-氯甲苯为起始原料合成环磺酮的工艺，在制备2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的时候，以危险性较大的溴素为溴化剂，收率偏低，只有70％
   fix: ksm.identifier = '2-chlorotoluene', already present in compounds.json tagged compound_class:starting_material. Bromine contributes one bromine atom and no part of the carbon skeleton that survives to 
6. **[pathways]** `precision` on `scope=section / Background, 817d72e8-87a8-55e6-810f-735bfb64`
   The KSM of the 《农药》 chain is elemental bromine, the brominating agent, and here the text names no starting material at all, so the field was filled from the only compound the step recorded.
   > line 107: 《农药》第56卷第5期报道了玉米田除草剂环磺酮的合成工艺，在合成2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的时候，以危险性较大的溴素为溴化剂
   fix: ksm.identifier = null, or the aryl substrate 'methyl 2-chloro-3-methyl-4-methylsulfonylbenzoate' that the bromination must consume. Unlike lines 96, 98 and 100 this paragraph names no 起始原料, so there i
7. **[pathways]** `precision` on `scope=section / Background, 8d20cf23-4de3-552a-9d60-36928229`
   The KSM of the CN106008290A chain is sodium 2,2,2-trifluoroethoxide, an etherification reagent that contributes only the OCH2CF3 side chain, not the benzoyl backbone that survives into tembotrione.
   > line 102: 安徽久易农业股份有限公司的专利号CN106008290A报道了环磺酮的合成工艺，在制备2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸的时候，所用2,2,2-三氟乙醇钠目前无法大规模生产，买不到原料
   fix: ksm.identifier = null, or the bromo ester substrate. Rule 3 resolves ties by carbon skeleton, not by role label: the ring you can still see in tembotrione comes from the benzoate, so the alkoxide is t
8. **[reactions]** `fidelity` on `Example 1_Step 1`
   The only numeric temperature the step prints, 75 to 80 C, is dropped from the structured temperature block, which is left type not_specified with all three bounds null, although the identical 在X～Y℃滴加 construction is read into conditions.temperature on all ten other records in the artifact that carry one.
   > line 181: 加入500ml反应瓶中，在75～80℃滴加20.6g双氧水(30％、0.182mol)
   fix: set {"type":"range","min_c":75.0,"max_c":80.0} as Example 2_Step 1 (45-50), Example 3_Step 1 (50-55) and Example 4_Step 1 (60-65) all do from the same construction, or else strip the range from those 
9. **[reactions]** `fidelity` on `Example 1_Step 3`
   The only numeric temperature the step prints, 25 to 30 C for the triethylamine addition, is dropped from the structured temperature block, although Example 2_Step 3 (20-25), Example 3_Step 3 (0-5) and Example 4_Step 3 (5-10) all populate it from the identical construction in the identical position of the identical procedure.
   > line 200: 100ml二氯乙烷加入反应瓶，在25～30℃滴加18.5g三乙胺(99％、0.18mol)
   fix: set {"type":"range","min_c":25.0,"max_c":30.0}, matching the three sibling Step 3 records.

### major

1. **[compounds]** `recall` on `methyl 2-chloro-3-(bromomethyl)-4-(methylsulfonyl)benzoate`
   The document contains four worked examples and a comparative example, and the artifact retains exactly one charge, one isolated mass and one yield per compound; every surviving mass and yield comes from Example 3 or Example 4, the only quantity uniquely traceable to Example 1 is the 200 ml of tetrahydrofuran, and nothing is uniquely traceable to Example 2. Fifteen of the seventeen product masses and yields printed in the document are absent.
   > line 181: 异丙醇进行重结晶、过滤、烘干得46.67g白色粉末，纯度99.0％，收率89％。
   fix: Either emit one record per (compound, section) so each example keeps its own charges, or carry a per-section quantity list on the merged record. A single scalar quantity cannot represent five experime
2. **[compounds]** `precision` on `azobisisobutyronitrile`
   Read as one set, the artifact describes an experiment that was never run: it gives charges for azobisisobutyronitrile (1.66 g, Example 4) and for m-chloroperoxybenzoic acid (0.174 g, Example 3) at the same time, although claim 3 makes them alternatives for the same step 1 catalyst, and it gives volumes for tetrahydrofuran (200 ml, Example 1), acetone (200 ml, Example 3) and DMF (200 ml, Example 2 or 4) at the same time, although claim 7 makes them alternatives for the same step 2 solvent.
   > line 131: [0020] 进一步的，步骤1)中，所述催化剂为偶氮二异丁腈或间氯过氧苯甲酸；双氧水的滴加温度为45～80℃。
   fix: Keep the charges of mutually exclusive alternatives on separate per-example records so they are never asserted together.
3. **[compounds]** `recall` on `tembotrione`
   The final product of the whole route carries no mass and no yield although five sections print both, yet purity_pct 98.7 did survive the merge, so the record is not simply quantity-free: it asserts one example's purity next to an empty quantity.
   > line 286: 加乙醇进行重结晶，过滤，烘干得38.1g米黄色结晶粉末，纯度98.7％，收率85.4％。
   fix: Populate mass_g and yield_pct from the same passage the surviving purity came from (38.1 g and 85.4% at line 286, or 37.94 g and 85% at line 256), or null the purity too so the record does not mix a p
4. **[compounds]** `arithmetic` on `2-chloro-3-[(2,2,2-trifluoroethoxy)methyl]-4-(methylsulfonyl`
   Step-to-step continuity fails in Examples 3 and 4 and nothing in the artifact flags it, because the charged mass of each isolated intermediate is not recorded at all: only the isolated mass survives, so the discrepancy is invisible. Example 4 step 1 makes 30.66 g of the bromo ester and step 2 charges 34.2 g of it; step 2 makes 31.1 g of the acid and step 3 charges 34.72 g of it. Example 3 shows the same pattern (31.33 g made, 34.5 g charged; 31.58 g made, 34.75 g charged).
   > line 279: [0076] 将34.2g  2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯(99.8％、0.1mol)，27.88g碳酸钾(99％、0.2mol)
   fix: Add a note on both intermediate records recording that the mass charged into the next step exceeds the mass the previous step isolated, with both figures, and do not correct either.
5. **[compounds]** `recall` on `bromine`
   Bromine is charged once in the whole document, at 8.8 g (0.055 mol), and the record carries no quantity at all; the merge kept the quantity-free mention from the closing comparison instead.
   > line 298: 升温回流，滴加8.8g(0.055mol)溴素，保温反应4h
   fix: Set mass_g 8.8 and mmol 55.0 from line 298 and section_label 'Comparative Example'.
6. **[compounds]** `recall` on `sodium methoxide`
   Sodium methoxide is charged once in the whole document, at 5.4 g (0.1 mol), and the record carries no quantity; as with bromine the merge kept the quantity-free closing-comparison mention.
   > line 305: [0086] 将5.4g(0.1mol)甲醇钠称于120mLDMF中，加入四口烧瓶中，冷却至15℃
   fix: Set mass_g 5.4 and mmol 100.0 from line 305 and section_label 'Comparative Example'.
7. **[compounds]** `precision` on `1,3-cyclohexanedione / cyclohexane-1,3-dione`
   Three substances are split across two records each because two English renderings of the same Chinese name were used in different sections, and unlike the three benzene-ring intermediates these three have no entry in compounds-equivalence.json, so nothing downstream can collapse them: 1,3-环己二酮 is 1,3-cyclohexanedione in the abstract and summary but cyclohexane-1,3-dione in the claims and every example; DMF is DMF in the summary, beneficial effects and Example 3 but N,N-dimethylformamide in the claims, Examples 1, 2 and 4 and the comparative example; 间氯过氧苯甲酸 is 3-chloroperoxybenzoic acid in the claims but m-chloroperoxybenzoic acid in the summary and Example 3. Each member lists the other's identifier in its own aliases, so the artifact itself asserts the identity it then splits.
   > line 59: 将1,3-环己二酮、溶剂加入反应瓶，在30℃以下滴加三乙胺
   fix: Render each Chinese name one way throughout so finalise collapses each substance to a single record, or add the three groups to compounds-equivalence.json. Reported as one finding because it is one ro
8. **[compounds]** `precision` on `水`
   Water exists twice because one section kept the Chinese 水 as the identifier instead of resolving it, which A1 rule 6 requires for an unambiguous Chinese chemical name; the two records disagree on identifier_type and on role, and each carries the other's identifier as an alias.
   > line 40: 反应后水洗、浓缩、重结晶
   fix: Resolve 水 to water in the abstract record and keep 水 as an alias, so the two collapse to one record.
9. **[compounds]** `fidelity` on `tembotrione`
   The tembotrione record combines a physical form taken from the abstract and claims with a purity taken from an example, and no passage states that combination: the abstract and claims print 米黄色固体 (beige solid) with no purity, while Examples 3 and 4, which print 98.7%, both isolate 米黄色结晶粉末 (beige crystalline powder). Five of the record's own note segments say the form is powder.
   > line 256: 加甲醇进行重结晶，过滤，烘干得37.94g米黄色结晶粉末，纯度98.7％，收率85％。
   fix: Take physical_form, appearance and purity_pct from the same passage: either physical_form 'powder' with appearance '米黄色结晶粉末' and purity 98.7, or keep the abstract's 米黄色固体 and null the purity.
10. **[compounds]** `precision` on `hydrobromic acid`
   The record's role contradicts its own notes: role is 'reagent' while four of the merged note segments state the compound was recorded as reactant. The merge kept the abstract, claims and summary reading and the example notes, so the artifact now asserts two different roles for one compound.
   > line 272: 33.75g氢溴酸(48％、0.2mol)加入500ml反应瓶中
   fix: Pick one role for the merged record and drop the note segments that assert the other, or keep per-section records so each role stays attached to the section that supports it.
11. **[compounds]** `precision` on `N,N-dimethylformamide`
   The record contradicts its own notes and loses the only quantities DMF has as a catalyst. Its notes say the step 3 catalyst charge is the more completely stated of the two and is kept, so role and quantity follow it, yet the record has role 'solvent' and quantity volume_ml 200.0, which is the step 2 solvent charge. The DMF catalyst charges of 0.2 g (Ex1), 0.3 g (Ex2) and 0.74 g (Ex4) appear on neither DMF record; only Example 3's 0.074 g survives, on the separate 'DMF' record.
   > line 286: 0.74g  DMF(99％、0.01mol)，24g氯化亚砜(99％、0.2mol)
   fix: Make role and quantity agree with each other and with the note that explains them, and record the step 3 catalyst charge somewhere.
12. **[compounds]** `schema` on `tembotrione`
   Exactly one record in the artifact has is_section_product true and it sits on 'Technical Field', a section that only repeats the invention title. The abstract, the claims, each of the four examples and the comparative example each end with an isolated or named final product, and none of them has a record flagged as the product of that section, so a consumer cannot tell what any example produced.
   > line 200: 加甲醇进行重结晶，过滤，烘干得30.3g米黄色结晶粉末，纯度98.6％，收率86％。
   fix: is_section_product is not well defined on a cross-section merged record. Either keep per-section records so the flag survives on each example's product, or move the flag to the record that carries an 
13. **[patent]** `precision` on `CN109678767A`
   Four of the nine key starting materials are the feedstocks of the prior-art routes the background attacks, not of this invention: 2,6-dichlorotoluene, 3-chloro-2-methylaniline, 2-chlorotoluene and sodium methoxide.
   > line 96: 拜耳公司的专利号CN1323292A报道了以2,6-二氯甲苯为起始原料合成环磺酮的工艺
   fix: The invention's starting materials are methyl 2-chloro-3-methyl-4-(methanesulfonyl)benzoate, 2,2,2-trifluoroethanol and 1,3-cyclohexanedione. 2,6-dichlorotoluene is CN1323292A's ([0005] line 96), 3-ch
14. **[patent]** `precision` on `CN109678767A`
   The nine entries are only five distinct molecules, because two molecules are each held twice under two English spellings of one Chinese name.
   > line 181: 将40g  2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯(99.6％、0.152mol)
   fix: 2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯 appears once in the document and must be one record; (methanesulfonyl) and (methylsulfonyl) are two renderings of 甲磺酰基. Likewise 1,3-环己二酮 is one molecule and 1,3-cyclohexanedione 
15. **[patent]** `precision` on `CN109678767A`
   The summary describes step 3 as an O-acylation followed by an acetone-cyanohydrin-mediated rearrangement, a two-stage mechanism that neither the prose nor the drawn scheme states.
   > line 59: 将1,3-环己二酮、溶剂加入反应瓶，在30℃以下滴加三乙胺，LC跟踪至反应完全；反应完全后，加入丙酮氰醇，LC跟踪至反应完全
   fix: Say what the document says: the acid chloride is combined with 1,3-cyclohexanedione and triethylamine, then acetone cyanohydrin is added, giving tembotrione. Claim 1 step 3), [0018] and [0025] name on
16. **[patent]** `drawings` on `CN109678767A`
   The IMAGE_EXTRACT of the invention's reaction scheme drops the base drawn as an explicit co-reactant in the second equation.
   > line 152: {"step_id": 2, "reactants": [{"smiles": "COC(=O)c1ccc(S(C)(=O)=O)c(CBr)c1Cl", ...}, {"smiles": "OCC(F)(F)F", ...}], "conditions": [], "products": [...]}
   fix: I opened p05.png. The second equation is drawn as [methyl 2-chloro-3-bromomethyl-4-methylsulfonylbenzoate] + HOCH2CF3 + 碱 -> [ether], with 碱 as a third addend to the left of the arrow, in the same pos
17. **[pathways]** `schema` on `31 of the 39 step projections, across 12 of the 14 pathways`
   Rule 12 defines components as 'the identifiers of that step's reactants plus its product', but components carries reagents, oxidants and bases as well, and the surplus does not follow any single rule.
   > line 188: 将30g  2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯(99.0％、0.0869mol)，18g碳酸钾(99％、0.1289mol)，0.9g三乙烯二胺(99％、0.0079mol)，200ml四氢呋喃，10.5g  2,2,2-三氟乙醇(99％、0.1039mol)加入500ml反应瓶中
   fix: Apply rule 12 mechanically: [c.identifier for c in compounds if c.role == 'reactant'] + [c.identifier for c in compounds if c.is_product]. If the widened definition is intended, state it once and appl
18. **[pathways]** `schema` on `scope=section / Background, 8b8007ba-ee51-5b01-ba9c-4835da7a`
   This step's components lists only the reagent and the product; the compound that actually carries the carbon skeleton into tembotrione has fallen out of the field entirely.
   > line 100: 而且中间态2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸-3-氧代-1-环己烯酯单独分离处理，导致工艺繁琐，收率偏低，只有69％
   fix: components = ['3-oxo-1-cyclohexen-1-yl 2-chloro-3-(2,2,2-trifluoroethoxy)methyl-4-methylsulfonylbenzoate', 'tembotrione']. The compound is present in this step's compounds[] but with role 'intermediat
19. **[pathways]** `vocabulary` on `Background_Step 5 (in 8b8007ba), Claims_Step 1 and Claims_St`
   Rule 11 requires compounds to be copied verbatim from the reaction record, but three step projections carry role values that reactions.json does not hold and that finalise.py itself declares outside the valid set.
   > line 0: N/A. pipeline/finalise.py line 105 VALID_ROLES = {product, reactant, reagent, solvent, catalyst, ligand, base, acid, oxidant, reductant, by_product, additive, d
   fix: Call normalise_role over steps[].compounds in finalise_pathways so the projections match reactions.json: 'intermediate' -> 'reactant', 'wash' -> 'solvent'.
20. **[pathways]** `arithmetic` on `scope=section / Background, 77ebc24a-6046-5af2-bf1f-ae79e5b3`
   Two single-step prior-art fragments carry a route-level overall_yield_pct, and the higher of them is then read downstream as this patent's best route yield, ahead of the invention's own 69.88 percent.
   > line 98: 也是以昂贵NBS为溴化剂，会有大量固废产生，且收率偏低，只有75.2％
   fix: The pathway values are correct under rule 9 and should not be changed. The minimal correction is in finalise.py rollup (line 303): restrict the best-yield search to chains whose product is the patent'
21. **[reactions]** `vocabulary` on `Example 4_Step 1`
   This step is given the name Wohl-Ziegler bromination while Examples 1, 2 and 3 Step 1, Claims_Step 1, Summary_Step 1 and Comparative Example_Step 1 all set named_reaction null, each with an explicit note that Wohl-Ziegler names the N-bromo-reagent bromination and that this hydrobromic acid plus hydrogen peroxide system is not one; Example 4 runs exactly the same HBr/H2O2/AIBN chemistry as Examples 1 and 2.
   > line 272: 1.66g偶氮二异丁腈(99％、0.01mol)，33.75g氢溴酸(48％、0.2mol)加入500ml反应瓶中，在60～65℃滴加22.7g双氧水(30％、0.2mol)
   fix: set named_reaction null on Example 4_Step 1 and drop the named_rxn tag, matching the other five records and the reasoning they state. The Background records that do use the name (Steps 1 and 2) are th
22. **[reactions]** `vocabulary` on `Claims_Step 3`
   The identical final transformation is classified 'other' here but 'acylation' in Summary_Step 3, all four Example Step 3 records, Comparative Example_Step 3 and Scheme Step 4, and the notes on both sides give the SAME reason for the opposite answer, so the gold set carries two contradictory labels for one reaction.
   > line 59: 将1,3-环己二酮、溶剂加入反应瓶，在30℃以下滴加三乙胺，LC跟踪至反应完全；反应完全后，加入丙酮氰醇
   fix: pick one value for this transformation and use it in all eight records. The six-to-one weight of the rest of the artifact favours 'acylation' with transformation:rearrangement carried in tags, which i
23. **[reactions]** `vocabulary` on `Summary of the Invention_Step 2`
   named_reaction is null here but 'Williamson ether synthesis' in Claims_Step 2 and in all four Example Step 2 records, for the same two-transformation step classed as hydrolysis; the stated reason, that naming the other transformation on a record classed as the hydrolysis would misread the field, applies identically to the five records that do it.
   > line 123: [0016] 将2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯、碱1、催化剂、溶剂、2,2,2-三氟乙醇加入反应瓶，在80℃以下进行反应
   fix: one value across the six records, with one line of reasoning; the named_rxn tag must follow it.
24. **[reactions]** `fidelity` on `Example 3_Step 2`
   This record takes its structured temperature from the FIRST transformation (0 to 5 C, the etherification) while Examples 1, 2 and 4 Step 2 take it from the FINAL transformation (70 to 75 C, the alkaline hydrolysis) and state that convention explicitly, so the same field means a different stage in one of four sibling records.
   > line 249: 加入500ml反应瓶中，在0～5℃进行反应，LC跟踪至反应完全 ... 200ml水，在70～75℃进行碱解
   fix: apply one rule to all four Step 2 records. The stated reason for Example 3's choice, that the range sits on the main charge sentence, is equally true of Example 1's 75-80 C and Example 4's 20-25 C, bo
25. **[reactions]** `fidelity` on `Example 1_Step 2`
   The acidification is counted as a third one-pot transformation here, giving three entries, while Claims_Step 2, Summary_Step 2, Comparative Example_Step 2 and Examples 2, 3 and 4 Step 2 all carry two and each states in terms that the acidification is an isolation operation and NOT a third transformation.
   > line 188: 在70～75℃进行碱解，LC跟踪至反应完全，反应完全后滴加盐酸酸化，过滤，洗涤，烘干
   fix: drop the third entry from Example 1_Step 2 and keep the acidification in workup and ph_target_stage, as the other six records do; a consumer counting transformations gets 3 from Example 1 and 2 from E
26. **[reactions]** `recall` on `Summary of the Invention_Step 1`
   The two permitted catalysts and the seven permitted solvents named at lines 131 and 133, inside this record's own section, are carried by no compound entry, although Claims_Step 1 records all nine from claims 3 and 4, which are word-for-word the same recitation, and this record did take the 45-80 C range from line 131.
   > line 133: [0021] 进一步的，步骤1)中，所述反应溶剂为二氯甲烷、1 ,2-二氯乙烷或氯仿；所述结晶溶剂为甲醇、乙醇、异丙醇或正丁醇。
   fix: add azobisisobutyronitrile, m-chloroperoxybenzoic acid, dichloromethane, 1,2-dichloroethane, chloroform, methanol, ethanol, isopropanol and n-butanol alongside the placeholders, as Claims_Step 1 does,
27. **[reactions]** `recall` on `Summary of the Invention_Step 2`
   The ten species enumerated at lines 137 and 142, inside this record's own section, are carried by no compound entry, although Claims_Step 2 records all ten from claims 6 and 7, which recite the same thing.
   > line 137: [0023] 进一步的，步骤2)中，所述碱1为碳酸钾；所述催化剂为三乙烯二胺或2-甲基三乙烯二胺；所述碱2为氢氧化钠、氢氧化钾或氢氧化锂。
   fix: add potassium carbonate, triethylenediamine, 2-methyltriethylenediamine, sodium hydroxide, potassium hydroxide, lithium hydroxide, acetonitrile, N,N-dimethylformamide, acetone and tetrahydrofuran, mat
28. **[reactions]** `recall` on `Summary of the Invention_Step 3`
   The catalyst identified as DMF and the four crystallisation solvents named at line 148, inside this record's own section, are carried by no compound entry, although Claims_Step 3 records all five from claim 10.
   > line 148: [0027] 进一步的，步骤3)中，催化剂为DMF；结晶溶剂为甲醇、乙醇、异丙醇或正丁醇。
   fix: add N,N-dimethylformamide, methanol, ethanol, isopropanol and n-butanol, matching Claims_Step 3. Note the record's own reagent_written_not_drawn flag rests on [0027] identifying the catalyst as DMF, s
29. **[reactions]** `recall` on `Summary of the Invention_Step 1 and Summary of the Invention`
   Wash water is excluded from compounds[] on these two records although the same sentences in Claims_Step 1 and Claims_Step 3 put water in compounds[] with role solvent; the same species, from the same wording, is present in one section's records and absent from the other's. Reported as one finding because it is one convention decision, not two independent omissions.
   > line 127: 反应完全后加入水进行水洗，分层，油层脱尽溶剂，加溶剂进行重结晶，过滤，烘干得米黄色固体环磺酮。
   fix: adopt one rule for whether workup water appears in compounds[] and apply it to both prose recitations of the route.
30. **[reactions]** `precision` on `All 13 Example and Comparative Example records and the 5 Sch`
   The notes carry 218 numeric values that appear nowhere in the patent: molecular weights (262.71, 341.60, 346.70, 440.82, 112.18, 164.21, 118.97, 100.04, 73.09, 85.11), derived mole figures (0.15165, 0.08694, 0.008825, 0.01995), derived theoretical masses and percentages (51.92, 30.13, 34.67, 88.98, 89.2, 17.9, 10.3) and, on the five Scheme records, page pixel coordinates (526-766, 792-1067, 1088-1373, 1389-1712, 1739-2040). A2 rule 32 says notes must introduce no number absent from the text, and the A2 output section says arithmetic_check "is written to output/reactions-provenance.json ... It never enters reactions.json". The same derivations already exist in full in the provenance sidecar.
   > line 181: 在75～80℃滴加20.6g双氧水(30％、0.182mol)，滴加完毕后继续反应
   fix: reduce the notes to the qualitative statement plus the printed numbers and leave the derivation in reactions-provenance.json arithmetic_check, where it already sits verbatim; validation_flags already 
31. **[reactions]** `linkage` on `All sections`
   Each of the three principal intermediates carries two or three different identifiers, split cleanly along section lines, so no cross-section join on identifier is possible: the bromide is 'methyl 2-chloro-3-(bromomethyl)-4-(methanesulfonyl)benzoate' in Claims and Summary, '...(methylsulfonyl)...' in the Examples and the Comparative Example, and 'methyl 2-chloro-3-bromomethyl-4-methylsulfonylbenzoate' in the Background; the benzoic acid splits the same three ways; the starting ester splits two ways.
   > line 49: [claim 1] step 1) title 1)2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的合成
   fix: originates in A1 (compounds.json holds the variants as separate records) and A2 rule 7 forces an exact match, so reactions.json should follow whichever single identifier A1 settles on. Reported here b
32. **[reactions]** `schema` on `Background_Step 5`
   missing_reactant is raised on a record that does have a compound with role 'reactant', so the flag contradicts its own definition in A2 rule 27 and is_complete is false on a record whose flag set should be one shorter.
   > line 100: 中间态2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸-3-氧代-1-环己烯酯单独分离处理，导致工艺繁琐，收率偏低，只有69％
   fix: drop 'missing_reactant'. The other six Background records that carry it (Steps 1, 2, 3, 7, 8, 10) genuinely have no compound with role reactant and are correct. If the intent was that the record's rea
33. **[reactions]** `recall` on `None`
   The abstract recites the whole three-step route with its reagents, its addition order and its workup, in the same quantity-free form as claim 1, yet no record is emitted for it, while claim 1 yields three records.
   > line 40: 1)先加入2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯、溶剂、催化剂、氢溴酸，然后滴加双氧水，反应后水洗、浓缩、重结晶，得到溴代物2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯
   fix: emit three Abstract records, or say in the Claims records why a quantity-free recitation is a procedure in the claims and not in the abstract. The stated reason does not separate them: claim 1 also st
34. **[reactions]** `recall` on `None`
   Paragraphs [0031] to [0033] each name a transformation of the invention's own route with the reagent used, in exactly the 在制备X的时候 construction from which the ten Background records were emitted, yet no record is emitted for any of them.
   > line 160: [0031] 1.在制备2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的时候，以价格便宜的氢溴酸为溴化剂，降低了安全风险，提高了收率，降低了生产成本。
   fix: either emit three Beneficial Effects records or state why the same clause form is a transformation in 背景技术 and not in 有益效果. Originates in A0's contains_procedure decision for that section. What would 

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 58 | 57 | 1 |
| `patent` | 16 | 15 | 4 |
| `pathways` | 15 | 14 | 1 |
| `reactions` | 42 | 36 | 8 |
