# What is wrong with WO2022024094A1

Produced by annotating the patent by hand, against the scanned pages rather than
against anyone's OCR. Every item below is a defect in the **patent**, not in the
annotation. The annotation records them and changes nothing.

- 24 reactions extracted, of which 21 carry at least one flag
- 43 unique compounds, 16 pathways
- 53 discrepancies raised by the page-vision pass

## Flags raised, by kind

| flag | count | what it means |
|---|---:|---|
| `no_conditions` | 16 | no reaction conditions stated at all |
| `reagent_written_not_drawn` | 10 | a reagent in the procedure appears on no arrow |
| `drawing_text_conflict` | 5 | the drawn scheme and the written procedure disagree |
| `reagent_drawn_not_written` | 3 | a reagent on an arrow appears in no procedure |
| `molar_mass_inconsistent` | 2 | a stated mass/mole pair implies a molecular weight that is not the named compound's |

## The headline findings

No hand-written analysis exists for WO2022024094A1. The generated sections above and below are complete; this section is not, and is omitted rather than filled with another patent's findings.

## Everything the page-vision pass raised

- **[p03.png]** The lower block draws a base and a solvent on the arrow that the prose of [005] never mentions.
  - drawing: (CH3CH2 )3N above the arrow and Solvent below it, for the NMSBC plus cyclohexanedione step
  - text: step (iii) is only 'reacting cyclohexanedione with 2-nitro-4-methylsulphonyl benzoyl chloride (NMSBC) to form an enol ester', with no base and no solvent named
- **[p03.png]** The prose of [005] names two transformations for the top block whose reagents are drawn nowhere.
  - drawing: both top-row arrows are bare, with nothing above or below either of them
  - text: (i) 'oxidation of' NMST to NMSBA and (ii) 'conversion of' NMSBA to the benzoyl chloride NMSBC, so an oxidant and a chlorinating agent are implied by the text and absent from the drawing
- **[p03.png]** The prose of [005] leaves the dione unlocated while the drawing fixes it.
  - drawing: a cyclohexane ring with the two C=O groups on the 1 and 3 vertices, i.e. cyclohexane-1,3-dione
  - text: 'cyclohexanedione', with no positions given
- **[p03.png]** The same moiety is spelt two ways on this one page, in the two paragraphs either side of the scheme.
  - drawing: the drawings carry only the abbreviations NMST, NMSBA, NMSBC, so they do not settle the spelling
  - text: [005] prints 'methylsulphonyl' with a PH in all four of its occurrences, and [006] prints 'methylsulfonyl' with an F in both of its occurrences, for the same compounds NMST and NMSBA
- **[p03.png]** The prose calls the drawn chemistry one scheme, the page lays it out as two blocks.
  - drawing: two spatially separate blocks, the second one redrawing NMSBC from scratch rather than being reached by an arrow from the first
  - text: 'as shown in the following reaction scheme', singular
- **[p04.png]** The scheme for the cited US patent drops the cobalt option that the prose beside it offers.
  - drawing: The second drawing names one catalyst only, Vanadium Pentoxide, above the arrow. No cobalt compound appears anywhere in it.
  - text: [007] says the US5424481 process oxidises 'in the presence of vanadium or cobalt compounds', naming cobalt as an alternative catalyst on equal footing with vanadium.
- **[p04.png]** The scheme for the cited US patent carries a reaction temperature the prose does not state.
  - drawing: 145 followed by a degree ring and a capital C, printed below the arrow shaft.
  - text: [007] gives reagents and catalyst but states no temperature, and no temperature appears anywhere in the prose on this page.
- **[p04.png]** The scheme for the cited Chinese application adds an oxidant the prose does not mention.
  - drawing: The third drawing prints 'Nitric acid/O2' above the arrow, bringing molecular oxygen into the reagent list.
  - text: [008] names only sulphuric acid, nitric acid and vanadium pentoxide as catalyst. Oxygen is not mentioned in [008] or anywhere else on this page.
- **[p04.png]** The scheme for the cited Chinese application carries a temperature range the prose does not state.
  - drawing: 140-150 followed by a degree ring and a capital C, printed below the arrow shaft.
  - text: [008] states no temperature.
- **[p04.png]** The first drawing on the page has no prose on this page to check it against, and its reagents are unlike those of the other two drawings.
  - drawing: Acetic acid, Sodium acetate and Cobalt (II) acetate tetrahydrate, three lines above the arrow, converting NMST to NMSBA. No mineral acid, no vanadium, no temperature.
  - text: Nothing. The drawing is printed above [007] with no text above it on this page, so the paragraph that introduces it is on p03 and the cross-check of prompt rule 10 cannot be run here. Recorded so a later pass j
- **[p04.png]** The same reagent is spelled with a ph and with an f on this one page, in the drawings and in the prose, and the two prose paragraphs disagree with each other.
  - drawing: Both clean drawings print 'Sulphuric Acid/' with a ph.
  - text: [007] prints 'sulfuric acid' with an f, twice, for the same reagent in the same reaction. [008] prints 'sulphuric acid' with a ph, agreeing with the drawings and not with [007]. Nothing normalised, per brief se
- **[p04.png]** The moiety name takes three different forms inside [007] alone, one of which the brief does not list.
  - drawing: The drawings spell nothing out; they use only the abbreviations NMST and NMSBA and the atom labels CH3, NO2, SO2, H3C, OH, O.
  - text: [007] prints 'methyl sulfonyl benzoic acids' with a space, 'methylsulfonyl toluenes' closed up with an f, and '2-nitro-4-methylsulphonyl toluene' with a ph, then '2-nitro-4-methylsulfonyl benzoic acid' with an 
- **[p05.png]** The drawn arrow carries a reaction temperature that the prose beside it does not mention.
  - drawing: 140-150°C printed below the arrow shaft.
  - text: [009] gives the reagents (nitric acid, vanadium pentoxide as catalyst) but states no temperature anywhere for the oxidation, nor anywhere else on the page.
- **[p05.png]** The prose describes the cited process as making a benzoyl chloride, but the drawn scheme stops one step earlier at the carboxylic acid and draws no chlorination.
  - drawing: A single arrow, NMST to NMSBA. No acid chloride is drawn and no chlorinating agent appears.
  - text: [009] says CN106565561A 'discloses a process for the preparation of 2-nitro-4-methylsulfonylbenzoyl benzoyl chloride', and describes the drawn oxidation as only 'a step' within that process.
- **[p05.png]** The same moiety is spelled a third way on this page, unlike either of the two spellings the brief records.
  - drawing: The drawing spells nothing out; it uses only the abbreviations NMST and NMSBA and the atom labels CH3, NO2, SO2, H3C, OH, O.
  - text: [009] prints 'methylsulfonyl' with an f AND closed up against the next fragment with no space, three times: '2-nitro-4-methylsulfonylbenzoyl', '2-nitro-4-methylsulfonyltoluene', '2-nitro-4-methylsulfonylbenzoic
- **[p06.png]** The scheme in paragraph 15 writes oxidant and catalyst as one slash-separated string above the arrow and does not name the oxidant, while the prose distinguishes the two roles and names the catalyst.
  - drawing: Oxidant / RuO2, written above the arrow as a single label, with nothing below the arrow; the oxidant itself is not named and the label does not say which of the two is the catalyst.
  - text: 'using an oxidant in presence of ruthenium (IV) oxide (RuO2) as a catalyst', which names RuO2 explicitly as the catalyst and leaves the oxidant unnamed as well.
- **[p06.png]** The page spells the same methylsulfonyl moiety two ways within a single sentence of paragraph 15, while the drawings carry no spelling at all and so cannot settle it.
  - drawing: Nothing. The structures are drawn with SO2 and H3C labels only, and the printed captions are the formula numbers Formula IV, Formula III and Formula II, which carry no compound name.
  - text: '2-nitro-4-methylsulphonyl benzoic acid (NMSBA)' with a PH and '2-nitro-4-methylsulfonyl toluene (NMST)' with an F, three lines apart in the same sentence. Paragraph 16 then uses the PH form for both NMSBA and 
- **[p06.png]** The prose of paragraph 16 names an intermediate that the scheme beside it does not draw.
  - drawing: Two reactants and one product only: the benzoic acid, 1,3-cyclohexanedione, and the enol ester. No acid chloride appears anywhere in the drawing.
  - text: 'it does not require the additional step of converting NMSBA to an intermediate of 2-nitro-4-methylsulphonyl benzoyl chloride (NMSBC)'. The absence from the drawing is consistent with the claim being made, and 
- **[p07.png]** Step (i) names the catalyst and the oxidant class in prose, and the drawing labels the same arrow the same way, but neither names the oxidant itself; the oxidant is written but never identified on this page.
  - drawing: the arrow of the first scheme carries only 'Oxidant / RuO2' above it
  - text: 'with an oxidant in presence of ruthenium (IV) oxide (RuO2) as a catalyst', which also leaves the oxidant unnamed
- **[p07.png]** Step (ii) prose names the second reactant, but the second scheme draws that reactant without any label, and draws no reagent, solvent or condition on its arrow.
  - drawing: the second scheme's arrow carries no text above or below it, and its middle structure carries no printed label
  - text: 'reacting NMSBA of formula (III) with 1, 3-cyclohexanedione to produce an enol ester of formula (II)'
- **[p07.png]** Step (iii) prose says the enol ester is converted to mesotrione but names no reagent or condition, and the third scheme's arrow is likewise bare, so nothing on this page says how the rearrangement is effected.
  - drawing: the third scheme's arrow carries no text above or below it
  - text: 'converting the enol ester of formula (II) to mesotrione of formula (I)'
- **[p10.png]** The arrow names the oxidant only generically while the prose names specific oxidants.
  - drawing: Oxidant / RuO2 above the arrow, with no named oxidising agent.
  - text: [0032]: 'Examples of oxidizing agent include alkali metal hypochlorite and peroxide such as hydrogen peroxide.' and [0033] names hypochlorite specifically.
- **[p10.png]** The arrow gives no indication which of the two species on it is the catalyst; the prose does.
  - drawing: 'Oxidant / RuO2' with the two separated by a slash and neither marked as catalytic.
  - text: [0031]: the oxidation is carried out 'with an oxidant in presence of ruthenium (IV) oxide (RuO2) as a catalyst', so RuO2 is the catalyst and not a stoichiometric reagent.
- **[p10.png]** The prose spells the same methylsulfonyl moiety two ways within one paragraph.
  - drawing: The drawings carry no word for it, only H3C-SO2- as a structural fragment, so the drawings cannot arbitrate.
  - text: [0031]: 'methylsulphonyl benzoic acid (NMSBA)' with a ph and 'methylsulfonyl toluene (NMST)' with an f. Both transcribed as printed; neither normalised.
- **[p12.png]** The second scheme draws Formula III plus 1,3-cyclohexanedione going to Formula II over a completely bare arrow, while paragraph [0037] on the same page names a coupling agent and a solvent for that same conversion. Both readings are recorded; neither is treated as correcting the other.
  - drawing: arrow from Formula III plus 1,3-cyclohexanedione to Formula II with nothing written above or below it
  - text: [0037]: 'the enol ester of formula (II) can be prepared by reacting NMSBA of formula(III)with 1, 3-cyclohexanedionein presence of N,N'-dicyclohexylcarbodiimide and a solvent', preferably dichloromethane; and su
- **[p12.png]** In the first scheme the oxidant and the ruthenium species are printed above the arrow as one slash-separated label that does not say which is reagent and which is catalyst, whereas the prose distinguishes them. No specific oxidant is named anywhere on this page, by drawing or by prose.
  - drawing: Oxidant / RuO2 above the arrow
  - text: sub-step (i) of [0038]: 'oxidation ... with an oxidant in presence of ruthenium (IV) oxide as a catalyst'
- **[p12.png]** The page contradicts itself on the spelling of one moiety inside a single sentence, and both spellings are transcribed as printed rather than unified.
  - drawing: the drawings spell nothing out; both structures carry the group drawn as H3C-SO2- with no name printed
  - text: sub-step (i) of [0038] reads '2-nitro-4-methylsulfonyl toluene (NMST)' with an f and '2-nitro-4-methylsulphonyl benzoic acid (NMSBA)' with a ph, one clause apart in the same sentence
- **[p13.png]** Within one sentence of [0039] item (i) the methylsulfonyl moiety is spelled two ways, while the two drawings beside it draw one and the same group.
  - drawing: Formula IV and Formula III both draw an identical H3C-SO2 group on ring carbon C4; the drawings give no basis for two different moieties.
  - text: Item (i) prints '2-nitro-4-methylsulfonyl toluene (NMST)' with an f and, two lines later, '2-nitro-4-methylsulphonyl benzoic acid (NMSBA)' with a ph. Both spellings are transcribed as printed and neither has be
- **[p13.png]** Steps (ii) and (iii) are drawn with completely bare arrows, and the prose for those two steps names no reagent or condition either, so the page as a whole specifies no way to carry either step out.
  - drawing: The arrow in the step (ii) scheme and the arrow in the step (iii) scheme each carry nothing above and nothing below. Only the step (i) arrow is labelled, with 'Oxidant / RuO2'.
  - text: Item (ii) says only 'reaction of NMSBA of formula (III) with 1,3-cyclohexanedione to produce enol ester of formula (II)' and item (iii) says only 'conversion of the enol ester of formula (II) to mesotrione of f
- **[p15.png]** The scheme names the oxidant only generically while the prose names a specific one.
  - drawing: 'Oxidant / RuO2' above the arrow; the actual oxidant is left unnamed and only the ruthenium catalyst is spelled out.
  - text: [0047] charges 'sodium hypochlorite (500ml, 0.745mol)' as the oxidant together with 'ruthenium oxide (1.5g, 0.011mol)'.
- **[p15.png]** The acidification step of the written procedure has no counterpart on the drawing.
  - drawing: A single arrow from Formula IV to Formula III carrying only 'Oxidant / RuO2'; no acid, no reflux, no temperature and no work-up is drawn.
  - text: [0047] additionally requires reflux for 6-8hours, cooling to 25-30°C, filtration, cooling to 5-10°C and acidification to pH <3 with concentrated hydrochloric acid(120mL, 1.23mol) before NMSBA precipitates.
- **[p15.png]** Example 1 and Example 2 are given identical titles and identical chemistry, differing only in scale.
  - drawing: One scheme is drawn, under Example 1 only; Example 2 has no scheme of its own on this page.
  - text: The Example 2 title line is character-for-character identical to the Example 1 title line, and [0048] repeats the same three charges (NMST, sodium hypochlorite, ruthenium oxide) at roughly one twelfth the scale
- **[p16.png]** The scheme's arrow carries no reagents or conditions at all, while the prose paragraph directly beneath it names the solvent, the coupling agent and the temperature.
  - drawing: Nothing above or below the arrow. Only the two reactant structures, a '+', a bare arrow, the product, and the labels 'Formula III' and 'Formula II'.
  - text: dichloromethane (160mL) as solvent, N,N’-dicyclohexylcarbodiimide (DCC) (24g, 0.12mol) as the coupling agent, 25-30°C, about2 hours.
- **[p16.png]** The second reactant is drawn but never named beside the drawing; the prose names it only in the paragraph after the drawing, and with a different style of name.
  - drawing: An unlabelled cyclohexane ring with two ketones 1,3 to each other.
  - text: '1,3-cyclohexanedione(12g, 0.11mol)' in the paragraph below the scheme.
- **[p16.png]** The same moiety is spelled two ways within one sentence of the Example 3 title line, exactly as already seen on p15.
  - drawing: The drawing labels carry no spelling at all, only 'Formula III' and 'Formula II'.
  - text: '2-nitro-4-methylsulphonyl benzoic acid' with a ph and '2-nitro-4-methylsulfonyl toluene' with an f, one line apart.
- **[p16.png]** The two analytical data lines on this page report the same product, NMSBA, from the same starting material, but disagree on purity, yield and melting point, and the Example 3 figures are identical to the Example 1 figures on p15.
  - drawing: Not shown in any drawing.
  - text: Example 2 tail: 'HPLC purity > 92%; Yield: 67%; and Melting point: 207-210°C.' Example 3: 'HPLC purity >95%; Yield: 68%; and Melting point: 210-214°C.'
- **[p18.png]** The drawn arrow names no reagent, solvent, temperature or work-up, while the prose beside it specifies all four.
  - drawing: A bare arrow from Formula II to Formula I with nothing written above it and nothing below it.
  - text: The paragraph numbered 53 charges dichloromethane (60mL) as solvent, sodium cyanide (1.2g, 0.025mol) and triethylamine (6.6g, 0.065mol), holds the mixture at 10-15°C for about 2 hours, then quenches with water 
- **[p18.png]** The scheme and the prose name the same two compounds in two different naming systems that are never connected on this page.
  - drawing: The starting material is labelled 'Formula II' and the product 'Formula I'.
  - text: The paragraph numbered 53 calls the starting material only 'enol ester' and the product only 'mesotrione'. Neither 'Formula I' nor 'Formula II' appears anywhere in the text on this page, so the identification o
- **[p18.png]** The prose gives the product a melting point but nothing on the page ties it to the drawn structure.
  - drawing: Formula I is drawn as the 1,3-diketone tautomer with a plain CH at the 2-position.
  - text: 'Melting point of the solid was 155-157°C' and the product is described as a 'yellow to tan colour solid'. The page states no tautomer and gives no spectroscopic evidence, so which tautomer the isolated solid i
- **[p19.png]** The oxidant is named on the page but not on the scheme that depicts the oxidation.
  - drawing: The step (i) arrow carries the single label 'Oxidant / RuO2' above it and nothing below it, naming no specific oxidant and joining the oxidant and the ruthenium oxide with a slash as though they were one reagen
  - text: Claim 1 (i) distinguishes them, 'using an oxidant in presence of ruthenium oxide as a catalyst', and claim 2 on the same page names the oxidant as sodium hypochlorite. Recorded rather than resolved: claim 1 is 
- **[p19.png]** The claimed route has three steps and no benzoyl chloride, which is one step fewer than the route the vision brief describes.
  - drawing: The three schemes on this page run Formula IV to Formula III to Formula II to Formula I, that is NMST to NMSBA to the enol ester to mesotrione. No acid chloride is drawn anywhere on the page.
  - text: Claim 1 matches the drawings: NMSBA of formula (III) reacts directly with 1,3-cyclohexanedione. Brief section 8 states the route runs NMST to NMSBA to NMSBC to mesotrione, with NMSBC being the benzoyl chloride.
- **[p20.png]** The scheme under claim 5 names the oxidant only generically while claim 6, printed immediately below the same scheme, names a specific one. This is the same disagreement the brief records on p15, recurring in the claims.
  - drawing: 'Oxidant / RuO2' above the arrow, the only text on it. The actual oxidant is left unnamed, and the reagent and the catalyst are run together on one line separated by a slash so the drawing does not distinguish 
  - text: Claim 5 asks for 'an oxidant in presence of ruthenium oxide as a catalyst'; claim 6 then fixes 'the oxidant is sodium hypochlorite', which appears nowhere on the drawing.
- **[p20.png]** The scheme under claim 7 draws the coupling with a bare arrow, while both claim 3 and claim 8 make a coupling agent and a solvent essential to it.
  - drawing: Nothing above the arrow and nothing below it: no coupling agent, no solvent, no temperature, no time. Only the two reactants, the '+' and the product are drawn.
  - text: Claim 3 and claim 8 both require the reaction to be 'carried out in presence of N, N′-dicyclohexylcarbodiimide and a solvent'.
- **[p20.png]** The page contradicts itself on the spelling of the methylsulfonyl moiety, twice within claim 5's single sentence and then consistently one way afterwards. Recorded, not resolved.
  - drawing: The drawings carry no spelled-out name at all, only 'Formula IV', 'Formula III', 'Formula II' and the graphical SO2 / S-O2 labels, so they cannot arbitrate the spelling.
  - text: Claim 5 prints '2-nitro-4-methylsulphonyl benzoic acid' with a ph and '2-nitro-4-methylsulfonyl toluene' with an f, on consecutive lines of one sentence. Claims 6 and 7 then use the ph form only. Both forms are
- **[p20.png]** Claim 3 and claim 7 claim the same transformation at different dependencies, which a later pass must not collapse.
  - drawing: Only one drawing of this coupling is printed, under claim 7.
  - text: Claim 3 conditions the NMSBA plus 1,3-cyclohexanedione reaction as a dependent of claim 1, while claim 7 claims the same reaction as a standalone independent claim and claim 8 then adds the identical N, N′-dicy
- **[p21.png]** Step (ii) of claim 10 is drawn with a completely bare arrow, no solvent and no condensing agent, while claim 9 on the same page speaks of 'the solvent' used in the enol ester process of claim 8.
  - drawing: Formula III plus 1,3-cyclohexanedione, arrow with nothing written above or below it, Formula II
  - text: step (ii) names only the two reactants and the product, and claim 9 on the same page lists dichloromethane, 1,2-dichloroethane, dichloropropanes, dichlorobutanes and dichloropentanes as the solvent for the proc
- **[p21.png]** Claim 10 spells the same methylsulfonyl moiety two ways within one claim, transcribed exactly as printed and not unified.
  - drawing: the drawings carry no spelt-out name at all, only the labels Formula IV, Formula III and Formula II
  - text: '2-nitro-4-methylsulfonyl toluene (NMST)' with an f in the opening clause and again in step (i), and '2-nitro-4-methylsulphonyl benzoic acid (NMSBA)' with a ph in step (i), a line apart
- **[p21.png]** The formula numbers are printed with parentheses in the claim prose and without parentheses in the labels under the drawings.
  - drawing: Formula IV, Formula III, Formula II
  - text: formula (IV), formula (III), formula (II)
- **[p22.png]** The task brief calls p22 'the first sheet of the International Search Report', but the page's own form footer identifies it as the second sheet.
  - drawing: no drawing on this page; the printed footer reads 'Form PCT/ISA/210 (second sheet) (July 2019)'
  - text: the brief for this page states p22 is the first sheet of the International Search Report
- **[p22.png]** The vision brief section 6 says every page prints 'WO 2022/024094' top left, 'PCT/IB2021/057013' top right and a centred printed page number below them. This page carries none of that furniture.
  - drawing: the page prints the form title 'INTERNATIONAL SEARCH REPORT' centred at the top and a boxed 'International application No. PCT/IB2021/057013' at the top right, with no WO number and no centred printed page numb
  - text: brief section 6: header 'WO 2022/024094' top left, 'PCT/IB2021/057013' top right, centred printed page number below
- **[p23.png]** Brief section 6 says p22 and p23 print a form line at the foot 'such as Form PCT/ISA/210 (second sheet) (July 2019)'. This page's form line names no sheet number at all.
  - drawing: no drawing on this page; the printed form line at the foot reads 'Form PCT/ISA/210 (patent family annex) (July 2019)'
  - text: brief section 6, which gives '(second sheet)' as the example form line, and brief section 7, which warns not to assume a sheet number for p23
- **[p23.png]** Brief section 6 describes a running header 'WO 2022/024094' top left with 'PCT/IB2021/057013' top right and a centred printed page number below it. This page carries none of that, and prints no page number anywhere.
  - drawing: the page prints the form title 'INTERNATIONAL SEARCH REPORT' centred with the subtitle 'Information on patent family members' under it, and a boxed 'International application No. PCT/IB2021/057013' at the top r
  - text: brief section 6: header 'WO 2022/024094' top left, 'PCT/IB2021/057013' top right, centred printed page number below
- **[p23.png]** page_label has no printed number to hold on this page. The form line at the foot is used instead, to match what the p23 sibling page p22 already recorded, and because the prompt's own example for page_label is a section label rather than a bare number.
  - drawing: no printed page number exists anywhere on the page
  - text: brief section 6: page_label = the centred printed number, as a string
