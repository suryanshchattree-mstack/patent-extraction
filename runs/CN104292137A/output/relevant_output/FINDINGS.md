# What is wrong with CN104292137A

Produced by annotating the patent by hand, against the scanned pages rather than
against anyone's OCR. Every item below is a defect in the **patent**, not in the
annotation. The annotation records them and changes nothing.

- 33 reactions extracted, of which 24 carry at least one flag
- 75 unique compounds, 5 pathways
- 41 discrepancies raised by the page-vision pass

## Flags raised, by kind

| flag | count | what it means |
|---|---:|---|
| `no_conditions` | 9 | no reaction conditions stated at all |
| `route_attribution_unclear` | 9 | cannot tell from the page whether the drawn route is the invention's or prior art |
| `mass_balance_implausible` | 8 | stated product mass cannot be reconciled with the stated input moles and yield |
| `molar_mass_inconsistent` | 7 | a stated mass/mole pair implies a molecular weight that is not the named compound's |
| `drawing_text_conflict` | 7 | the drawn scheme and the written procedure disagree |
| `reagent_written_not_drawn` | 6 | a reagent in the procedure appears on no arrow |
| `scale_discontinuity` | 5 | a step charges more material than the previous step produced |
| `reagent_drawn_not_written` | 2 | a reagent on an arrow appears in no procedure |

## The three that matter

### 1. The molar masses are those of the des-chloro compounds

Across Example 1 the printed mass/mole pairs imply a molecular weight roughly
34.5 lower than the compound the text names and the page draws. That is exactly a
chlorine-for-hydrogen substitution. The reagent charges are all correct; only the
chlorinated aromatic intermediates carry the offset. Steps 5, 7 and 8 carry a
second, different shortfall of about 44.7 that propagates forward.

Working, per step, is in `provenance/reactions-provenance.json` under
`arithmetic_check`.

### 2. The drawn route is not the route the text describes

Page 6 carries the whole synthesis drawn as structures. Its first arrow uses
CH3SNa, which [0031] says the invention **replaced**. It contains a
sulfide-to-sulfone oxidation, which [0031] says the invention **eliminated**,
drawn with no arrow and no reagent. But it also uses Br2, which [0031] claims
**as** the invention's own improvement over NBS. It starts from
2,6-dichlorotoluene where Example 1 starts from 2-chlorotoluene.

So the scheme is neither cleanly the prior art nor cleanly the invention. The
annotation refuses to decide: all nine scheme records carry
`route_attribution_unclear` and both readings are in their notes.

### 3. The final-step catalyst is drawn as one compound and written as another

The last arrow's catalyst is **drawn** as a quaternary carbon bearing CN and OH
with two methyls, i.e. (CH3)2C(CN)OH, acetone cyanohydrin. The text names
cyanoacetone, a different molecule. Acetone cyanohydrin is the reagent normally
used for this enol-ester rearrangement.

Only a pass that looks at the drawing can catch this. It is the single clearest
argument for reading the pages rather than the OCR.

## Everything the page-vision pass raised

- **[p01.png]** Within the abstract itself, step 5 ends at a methyl ester but step 6 names the corresponding free acid, with no hydrolysis step named in between.
  - drawing: (no drawings on this page - this is a text-internal inconsistency, recorded here so it is not lost)
  - text: 5)2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的合成;6)2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸的合成; - '甲酯' is present in step 5 and absent in step 6. Must be resolved against the description pages, not on this page.
- **[p02.png]** Step 6) names its intermediate as the ethyl ester although the substrate is the methyl ester from step 4) and no ethyl source is introduced.
  - drawing: n/a - there are no drawings anywhere on this page
  - text: 浓缩得2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸乙酯 ('...benzoic acid ethyl ester'), from 2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯 ('...methyl ester') plus 2,2,2-三氟乙醇钠 only
- **[p02.png]** Step 5) specifies peroxybenzoic acid as the additive for a benzylic bromination with elemental bromine, where a radical initiator such as benzoyl peroxide would be expected.
  - drawing: n/a - there are no drawings anywhere on this page
  - text: 加入适量的过氧苯甲酸，在回流的条件下，滴加溴素 ('an appropriate amount of peroxybenzoic acid is added; under reflux, bromine is added dropwise')
- **[p02.png]** Step 8) specifies cyanoacetone as the additive with triethylamine, where acetone cyanohydrin is the catalyst normally used for this enol-ester rearrangement.
  - drawing: n/a - there are no drawings anywhere on this page
  - text: 加入...3-氧代-1-环己烯酯、氰基丙酮和三乙胺溶于溶剂中在室温持续搅拌 ('...the 3-oxo-1-cyclohexenyl ester, cyanoacetone and triethylamine, dissolved in solvent, stirred continuously at room temperature')
- **[p02.png]** The compound name used throughout the claims does not match any standard Chinese common name, and the route as claimed builds tembotrione rather than sulcotrione.
  - drawing: n/a - there are no drawings anywhere on this page
  - text: 三酮类除草剂环磺草酮 - 环磺草酮 is neither 环磺酮 (tembotrione) nor 磺草酮 (sulcotrione); the claimed intermediates carry the 3-[(2,2,2-trifluoroethoxy)methyl] group that distinguishes tembotrione
- **[p02.png]** The cyclohexanedione reagent in step 7) is named without ring locants, so the claim does not itself state that the 1,3-isomer is used.
  - drawing: n/a - there are no drawings anywhere on this page
  - text: 加入环己二酮和碱的混合物 ('a mixture of cyclohexanedione and base is added'), while the product is named ...苯甲酸3-氧代-1-环己烯酯
- **[p03.png]** No chemical structures are drawn anywhere on this page; every molecule is given by Chinese name only, so no drawing-versus-prose cross-check is possible for this page.
  - drawing: no drawing present on p03
  - text: all species named in prose: 2-氯-6-甲磺酰基甲苯, 2-氯-4-甲磺酰基-3-甲基苯甲酸甲酯, 2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯, 2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸, 环己二酮
- **[p03.png]** Ring numbering of the step-2 substrate and the step-5 substrate differs between claims: the mesyl group is at position 6 in claim 3 but at position 4 in claim 4. Both names are read as printed and neither has been altered. This cannot be resolved from this page because the intervening steps 3) and 4) are described on pages this pass does not see.
  - drawing: no drawing present on p03
  - text: claim 3: 2-氯-6-甲磺酰基甲苯 (mesyl at 6); claim 4: 2-氯-4-甲磺酰基-3-甲基苯甲酸甲酯 (mesyl at 4)
- **[p03.png]** The dependent claims on this page cover only steps 2), 5), 6) and 7). Steps 3) and 4) have no dependent claim on this page. If they are claimed at all it must be on the previous claims page.
  - drawing: no drawing present on p03
  - text: claim 3 → 步骤2), claim 4 → 步骤5), claim 5 → 步骤6), claim 6 → 步骤7)
- **[p03.png]** Trifluoroethyl locants are printed inconsistently between claims: claim 5 writes 三氟乙醇钠 with no locants while claim 6 writes (2,2,2-三氟乙氧基). Preserved as printed rather than normalised.
  - drawing: no drawing present on p03
  - text: claim 5: 三氟乙醇钠; claim 6: (2,2,2-三氟乙氧基)甲基
- **[p03.png]** Solvent and reagent lists are separated inconsistently: claim 3 and claim 6 use the Chinese enumeration mark 、 while claims 4, 5 and 7 use commas. Both marks are unambiguously distinguishable on this page, so this is an inconsistency in the printed original and has been preserved.
  - drawing: no drawing present on p03
  - text: claim 3: 二氯甲烷、氯仿或1,2-二氯乙烷; claim 4: 四氯化碳，氯仿，二氯甲烷或1,2-二氯乙烷
- **[p04.png]** There is not a single drawing on this page - no structural formula, no reaction scheme, no table. Every molecule, including the target compound and all four intermediates, is given by Chinese chemical name in running prose only. No drawing-versus-prose cross-check is therefore possible for p04, and no structure has been drawn or inferred.
  - drawing: no drawing present on p04
  - text: all species named in prose: 2-(2-氯4-甲磺酰基-3-[(2,2,2-三氟乙氧基)甲基]苯甲酰基)环己烷-1,3-二酮 (target, [0002]); 2-氯甲苯; 2-氯-6-甲磺酰基甲苯; 2-氯-3-乙酰基-6-甲磺酰基甲苯; 2-氯-3-甲基-4-甲磺酰基苯甲酸; 2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯
- **[p04.png]** The prior-art reagent list is split between two paragraphs, so reading either alone gives an incomplete picture of what the invention claims to eliminate. [0003] names sodium methanethiolate and NBS; the highly toxic cyanoacetone appears only in [0004].
  - drawing: no drawing present on p04
  - text: [0003] prior-art drawbacks: 甲硫醇钠, N-溴琥珀酸亚胺. [0004] eliminated by the invention: 甲硫醇钠 and 剧毒氰基丙酮
- **[p04.png]** The target compound's chemical name in [0002] is missing the hyphen between the chloro and the 4-methylsulfonyl locant, unlike every other locant on the page.
  - drawing: no drawing present on p04
  - text: [0002] prints 2-(2-氯4-甲磺酰基-3-[...] , i.e. 2-氯4- with no dash, verified at 4x
- **[p04.png]** [0002] names a comparator herbicide 硝环磺酮 that is not a standard Chinese herbicide name, alongside 甲基磺草酮 which is itself a common Chinese name for mesotrione. Characters verified individually at 6x; not corrected.
  - drawing: no drawing present on p04
  - text: [0002]: 其活性高于目前市场上的硝环磺酮和甲基磺草酮
- **[p04.png]** [0003] prints the brominating agent as N-溴琥珀酸亚胺, which is not the standard Chinese form of NBS (N-溴代琥珀酰亚胺 / N-溴代丁二酰亚胺): 酸 appears where the standard has 酰, and 代 is absent. Verified at 5x; recorded as printed.
  - drawing: no drawing present on p04
  - text: [0003]: (3)采用N-溴琥珀酸亚胺作溴化剂，该溴化剂昂贵。
- **[p05.png]** Text-vs-text (there are NO drawings on this page). The step-6 substitution product is named as the ethyl ester although the substrate is the methyl ester and no transesterification is described.
  - drawing: n/a - no drawing on this page; both statements below are prose
  - text: [0017] reads '将2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯溶于溶剂中…浓缩得2-氯-3-(2,2,2-三氟乙氧基）甲基-4-甲磺酰基苯甲酸乙酯' - substrate 甲酯 (methyl), product 乙酯 (ethyl). Character verified at high magnification as 乙. Almost certainly a printing typo for 甲
- **[p05.png]** Text-vs-text. The radical bromination initiator is named as perbenzoic acid rather than the benzoyl peroxide conventionally used.
  - drawing: n/a - no drawing on this page
  - text: [0015] reads '加入适量的过氧苯甲酸' = peroxybenzoic (perbenzoic) acid. Verified character-by-character; it is NOT 过氧化苯甲酰 (benzoyl peroxide). Recorded as printed; a downstream chemistry pass should treat the initiator ide
- **[p05.png]** Text-vs-text. The cyclisation reagent in the final step is named cyanoacetone, where the standard reagent for this enol-ester Fries rearrangement is acetone cyanohydrin.
  - drawing: n/a - no drawing on this page
  - text: [0021] reads '氰基丙酮和三乙胺' = cyanoacetone and triethylamine. Verified character-by-character; it is NOT 丙酮氰醇 (acetone cyanohydrin). Recorded as printed and flagged, not corrected.
- **[p05.png]** Text-vs-text. The same step-5 substrate is named with two different locant orderings in two places.
  - drawing: n/a - no drawing on this page
  - text: [0014]/[0015] say '2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯'; [0024] says '2-氯-4-甲磺酰基-3-甲基苯甲酸甲酯'. Same 2-Cl / 3-CH3 / 4-SO2CH3 pattern, so this is a naming-order variation only, not a structural conflict.
- **[p05.png]** Text omission. The diketone coupling partner is named without a locant in both places it appears.
  - drawing: n/a - no drawing on this page
  - text: [0019] and [0026] both say only '环己二酮' (cyclohexanedione), never '1,3-环己二酮'. The 1,3-isomer is implied by the product name '3-氧代-1-环己烯酯' but is nowhere stated; the isomer has NOT been inferred into the transcri
- **[p05.png]** Printing inconsistency in punctuation that downstream passes should not read as meaningful.
  - drawing: n/a - no drawing on this page
  - text: Step numbers use a narrow half-width ')' in [0014]/[0016]/[0018]/[0022]-[0026] but a wide full-width '）' in [0020]. The trifluoroethoxy parentheses are asymmetric throughout: narrow '(' opening, wide '）' closin
- **[p06.png]** The first step of the drawn scheme is exactly the transformation that [0031] says the invention does away with.
  - drawing: 2,6-dichlorotoluene + CH3SNa gives the aryl methyl sulfide 2-chloro-6-(methylsulfanyl)toluene.
  - text: [0031]: 该工艺采用甲磺酰氯替代甲硫醚的氯取代反应 - the process uses methanesulfonyl chloride in place of the chloro-substitution reaction of the methyl sulfide.
- **[p06.png]** The scheme contains a sulfide-to-sulfone oxidation, which [0031] says the invention eliminates, and it is drawn with no arrow and no reagent at all.
  - drawing: SCH3 at C4 in the 3rd structure silently becomes SO2CH3 at C4 in the 4th structure across the row 1 / row 2 line wrap. No arrow, no oxidant.
  - text: [0031]: 革除了硫醚的过氧化氢氧化步骤 - did away with the hydrogen-peroxide oxidation step of the thioether.
- **[p06.png]** The compound and the step that Example 1 actually performs appear nowhere in the drawn scheme.
  - drawing: The scheme never contains 2-chloro-6-(methanesulfonyl)toluene and never contains a CH3SO2Cl/AlCl3 step; its starting material is 2,6-dichlorotoluene.
  - text: [0033]-[0035]: Example 1 step 1 makes 2-chloro-6-methanesulfonyltoluene from 2-chlorotoluene (25.3 g, 0.2 mol), AlCl3 (40.5 g, 0.3 mol) and methanesulfonyl chloride (25.25 g, 0.22 mol) in 1,2-dichloroethane, 84
- **[p06.png]** One point where the drawing agrees with the invention rather than with the prior art, which is why the attribution cannot be settled cleanly.
  - drawing: Benzylic bromination of the C3 methyl uses Br2.
  - text: [0031]: 使用溴素代替昂贵的NBS进行侧链甲基的溴化 - bromine is used in place of expensive NBS for the side-chain methyl bromination, presented as an improvement of the invention over the prior art.
- **[p06.png]** A single drawn arrow performs two transformations but only one reagent is written on it.
  - drawing: CF3CH2ONa over the arrow converts the methyl ester bearing a benzylic bromide into the free carboxylic acid bearing CH2OCH2CF3. The ester hydrolysis has no reagent above or below the arrow.
  - text: Nothing on this page describes this step; no hydrolysis reagent is named in the page text.
- **[p06.png]** The enol-ester formation is present in the scheme but has no arrow and no reagent.
  - drawing: The free benzoic acid at the end of row 3 appears at the start of row 4 as its 3-oxocyclohex-1-en-1-yl enol ester. No arrow, no cyclohexane-1,3-dione, no coupling agent drawn.
  - text: Nothing on this page describes this step.
- **[p06.png]** Apparent typographical error inside [0035], transcribed verbatim and not corrected.
  - drawing: n/a - text-only discrepancy.
  - text: [0035] charges 1,2-二氯乙烷 (1,2-dichloroethane) as solvent but names the extraction solvent 1,2-二氯甲烷 ('1,2-dichloromethane'), which is not a real compound.
- **[p07.png]** Every aromatic mass/mole pair in the prose corresponds to the DES-CHLORO analogue of the structure actually drawn, i.e. the arithmetic behaves as if the ring chlorine were a hydrogen. The offset is the same in all three steps and equals the Cl-for-H substitution (34.4 g/mol).
  - drawing: All three drawn structures carry Cl on the ring. Chlorinated molar masses: 2-chloro-6-(methylsulfonyl)toluene C8H9ClO2S = 204.7; 2-chloro-3-acetyl-6-(methylsulfonyl)toluene C10H11ClO3S = 246.7; 2-chloro-3-methy
  - text: [0038] 34.0g = 0.2mol implies 170.0. [0042] 50.88g = 0.24mol implies 212.0. [0046] 42.8g = 0.2mol implies 214.0. The des-chloro molar masses are 170.2, 212.3 and 214.2 respectively - exact matches. The stated y
- **[p07.png]** In step 3 the isolated product mass cannot be reconciled with the yield printed in the same sentence, on either candidate molar mass. This is separate from and larger than the des-chloro issue above.
  - drawing: Product drawn is 2-chloro-3-methyl-4-(methylsulfonyl)benzoic acid, M = 248.7 (des-chloro analogue M = 214.2).
  - text: [0042]: 0.24 mol of substrate, 干燥得白色固体82g, 收率72％. 0.24 x 0.72 = 0.1728 mol, so 82 g would require M = 474 g/mol. A 72％ yield corresponds to 43.0 g on the chlorinated basis or 37.0 g on the des-chloro basis. The
- **[p07.png]** The parent hydride used for numbering changes between steps, so the same drawn skeleton carries different locants in different paragraphs. This is a nomenclature change and NOT a structural contradiction - flagged so downstream passes do not treat it as one.
  - drawing: Drawings 1, 2 and 3 have identical ring skeletons and identical substitution patterns; only the group at the upper-left vertex changes (acetyl -> COOH -> COOCH3).
  - text: [0036]/[0038] number the ring as a TOLUENE (CH3 = C1, Cl = C2, acetyl = C3, SO2CH3 = C6), while [0040] onward number it as a BENZOIC ACID (COOH = C1, Cl = C2, CH3 = C3, SO2CH3 = C4). Both descriptions map onto 
- **[p07.png]** The NMR list in [0039] contains two printing defects.
  - drawing: The drawn structure has three distinct CH3 environments (acetyl CH3, ring CH3, SO2CH3) plus two adjacent aromatic H, matching three singlets and two doublets.
  - text: [0039] prints '2.64(s,3H,)' with an empty assignment field after the second comma, and '8.10(d,H)' with the proton count missing before H where every other entry prints '1H'. Both transcribed verbatim.
- **[p07.png]** The deuterated-solvent label is typeset two different ways on the same page.
  - drawing: n/a - no drawing involved.
  - text: [0039] prints CDC1 with a SUBSCRIPT 3; [0043] prints CDC13 with the 3 INLINE. Both read as CDCl3. The 'l' is rendered in a glyph indistinguishable from the digit 1 throughout this typeface, which also affects 5
- **[p08.png]** [0054] names the coupling product as an ethyl ester although the substrate charged is the methyl ester and no ethylating agent is present.
  - drawing: The structure between [0053] and [0054] is the free carboxylic acid (HO-C(=O)- drawn), which is the product after the NaOH hydrolysis at the end of the paragraph.
  - text: 浓缩得2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸乙酯 (ethyl ester), whereas the charged substrate is 2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯 (methyl ester).
- **[p08.png]** [0057] gives the thionyl chloride charge without a mass unit.
  - drawing: n/a - no reagent labels are drawn; all three drawings on this page are bare structures with no arrows.
  - text: 滴加氯化亚砜71.4(0.6mol) - the figure 71.4 has no g, while 60.4g, 0.05g, 24.5g and 22.2g on the same paragraph all carry units.
- **[p08.png]** [0057] names the dione without locants while the drawing fixes it as the 1,3-dione enol ester.
  - drawing: 3-oxocyclohex-1-en-1-yl ester, i.e. derived from cyclohexane-1,3-dione.
  - text: 环己二酮 (cyclohexanedione, no locants given).
- **[p08.png]** Two printed mass/mole pairs do not reconcile with standard formula weights (cross-check computed by this pass, not printed in the document).
  - drawing: n/a
  - text: [0050] 39.6g(0.22mol) 溴素 implies FW 180 vs Br2 159.8; [0057] 60.4g(0.2mol) of the benzoic acid implies FW 302 vs 346.7. On the same page 71.4(0.6mol) SOCl2, 24.5g(0.22mol) cyclohexanedione and 22.2g(0.22mol) Et
- **[p09.png]** The masses and moles in [0060] are arithmetically inconsistent with the molecular weight of the structure drawn at [0059]. Both the substrate charge and the product yield imply a molecular weight of about 396, whereas the drawn structure is 440.82.
  - drawing: Drawn product is C17H16ClF3O6S, MW 440.82. The substrate named in the text is its enol-ester isomer, so it has the same MW. 0.5 mol of substrate would be 220.4 g, and a 95% yield of product from 0.5 mol would b
  - text: '198g(0.5mol)' of substrate, which implies MW 396. '浓缩得米黄色固体188g，收率95％' from 0.5 mol, which implies MW 395.8 (188 / (0.5 x 0.95)). Against the drawn MW of 440.82 the true yield from 198 g would be about 85%, an
- **[p09.png]** The proton count reported in [0061] fits the enol tautomer, while [0059] draws the diketo tautomer. Recorded as an observation only; the drawing has not been reinterpreted.
  - drawing: Diketo form: C2 of the cyclohexane-1,3-dione bears one implicit H, and the three remaining ring carbons are CH2 (6H), which would give 16 reported protons in total including the C2-H.
  - text: [0061] reports 15 protons with three 2H multiplets at 2.05, 2.45 and 2.8 (three CH2) and no separate 1H signal for a C2-H; the missing proton is consistent with an exchangeable enol OH that was not reported.
- **[p09.png]** Cyanoacetone is written in the text but no catalyst, reagent or condition appears anywhere in the drawing.
  - drawing: Nothing. The drawing is a lone product structure with no arrow, no reagents above or below, and no conditions.
  - text: 0.2 g 氰基丙酮 (cyanoacetone) as catalyst, triethylamine 60.6 (0.6 mol) as base, 500 ml acetonitrile as solvent, room temperature, 24 h.
