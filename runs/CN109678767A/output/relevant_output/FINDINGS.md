# What is wrong with CN109678767A

Produced by annotating the patent by hand, against the scanned pages rather than
against anyone's OCR. Every item below is a defect in the **patent**, not in the
annotation. The annotation records them and changes nothing.

- 36 reactions extracted, of which 23 carry at least one flag
- 66 unique compounds, 14 pathways
- 63 discrepancies raised by the page-vision pass

## Flags raised, by kind

| flag | count | what it means |
|---|---:|---|
| `no_conditions` | 15 | no reaction conditions stated at all |
| `missing_reactant` | 7 |  |
| `scale_discontinuity` | 5 | a step charges more material than the previous step produced |
| `reagent_written_not_drawn` | 4 | a reagent in the procedure appears on no arrow |
| `molar_mass_inconsistent` | 3 | a stated mass/mole pair implies a molecular weight that is not the named compound's |
| `mass_balance_implausible` | 1 | stated product mass cannot be reconciled with the stated input moles and yield |

## The headline findings

No hand-written analysis exists for CN109678767A. The generated sections above and below are complete; this section is not, and is omitted rather than filled with another patent's findings.

## Everything the page-vision pass raised

- **[p01.png]** The embedded text layer's reading order does not match the printed layout: the values for the (10) publication number and the (43) publication date are emitted at the very end of the extraction rather than beside their labels.
  - drawing: The image shows '(10)申请公布号 CN 109678767 A' and '(43)申请公布日 2019.04.26' as two complete lines in the top-right block, above the first horizontal rule. Layout is read from the image, which is authoritative for lay
  - text: The extraction emits '(10)申请公布号 ' as line 3 and '(43)申请公布日 ' as line 4, each with a trailing space and no value, then emits 'CN 109678767 A' as line 39 and '2019.04.26' as line 40, after the page-count line. La
- **[p01.png]** The rendered glyph widths disagree with the encoded character widths, in both directions, so glyph width on this page carries no information.
  - drawing: The page renders the brackets around 特殊普通合伙 as wide full-width brackets, and renders the abstract's CJK commas, semicolons and colon at a compressed advance width that reads as half-width. Verified at high magn
  - text: The text layer encodes the 特殊普通合伙 brackets as half-width ASCII '(' ')', and encodes every abstract prose mark as full-width '，' '；' '：' '、' '。'. Per the born-digital rule the text layer wins for characters, so 
- **[p01.png]** The abstract names a catalyst in all three steps and two distinct bases, but identifies none of them. Recorded so the gap is visible rather than being silently filled later.
  - drawing: (no drawings on this page - this is a text-internal omission, recorded here so it is not lost)
  - text: Step 1 lists 催化剂 with no identity; step 2 lists 碱1 and 催化剂 and later 碱2; step 3 lists 催化剂. The abstract also gives no yield, no temperature, no reaction time and no molar ratio anywhere. All of these must come 
- **[p02.png]** There are NO drawings on this page, so every entry below is text-vs-text or image-vs-text-layer. Chemistry-plausibility flag: the step-1 catalyst is offered as either a radical initiator or a peracid oxidant, which are different kinds of reagent playing the same declared role.
  - drawing: n/a - no drawing anywhere on this page. The whole page is prose; an ink-band scan of the rendered image finds exactly 40 marked bands: the header line, the rule beneath it, 37 body text lines and the footer pag
  - text: Claim 3 reads '所述催化剂为偶氮二异丁腈或间氯过氧苯甲酸' = said catalyst is AIBN or mCPBA. AIBN is a radical initiator, appropriate to the benzylic bromination of claim 1 step 1); mCPBA is a peracid oxidant. Both are printed as al
- **[p02.png]** Omission in the prose: claim 1 step 1) never names a brominating species, yet its product is the bromomethyl compound.
  - drawing: n/a - no drawing on this page, so there is no scheme to supply the missing reagent.
  - text: Claim 1 step 1) charges only '溶剂、催化剂、氢溴酸' and then adds '双氧水' dropwise, and claim 2 gives a molar ratio for exactly those four components. Neither 溴素 nor Br2 nor any other bromine reagent is written anywhere on
- **[p02.png]** Image versus embedded text layer: the extracted text stream emits the footer page number twice, while the page prints it once.
  - drawing: n/a - no drawing on this page. Layout evidence is from the rendered image: the header carries 'CN 109678767 A' at the left, '权　利　要　求　书' centred and '1/1 页' at the right, above a full-width horizontal rule; the 
  - text: The text layer for this page ends with the five items '权　利　要　求　书', '1/1 页', '2', 'CN 109678767 A', '2' in that order. The publication number belongs to the header, not the footer, and the page number '2' appear
- **[p02.png]** Naming form: the trifluoroethoxymethyl substituent is printed without the outer bracket that strict IUPAC nomenclature requires.
  - drawing: n/a - no drawing on this page. There is no structural formula anywhere in CN109678767A's claims, so every structure on this page exists only as a name.
  - text: The page prints '2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸' at all four occurrences, i.e. 3-(2,2,2-trifluoroethoxy)methyl, where the strict form is 3-[(2,2,2-trifluoroethoxy)methyl]. This is a bracketing convention only 
- **[p02.png]** Typographic inconsistency that downstream passes must not read as meaningful.
  - drawing: n/a - no drawing on this page.
  - text: Claim 7 prints '步骤2)中所述溶剂' with no comma after 中, where claims 2, 3, 4, 5, 6, 8, 9 and 10 all print '中，'. Reproduced as printed. Otherwise the page is punctuation-consistent: prose commas are full-width U+FF0C,
- **[p03.png]** Text-vs-text (there are NO drawings on this page). Mesotrione is named two different ways within the same page.
  - drawing: n/a - no drawing anywhere on this page
  - text: [0002] prints '其活性高于硝磺酮(硝磺草酮、甲基磺草酮)', using the three-character form 硝磺酮 as the head term and glossing it with 硝磺草酮 and 甲基磺草酮. [0003] prints 硝磺草酮 twice as the head term. 硝磺草酮 and 甲基磺草酮 are both standard Chinese
- **[p03.png]** Text-vs-text. [0006] is printed as a run-on where the parallel sentences [0005] and [0007] carry a comma.
  - drawing: n/a - no drawing anywhere on this page
  - text: [0006] reads '...为起始原料合成环磺酮的工艺在制备2-氯-3-溴甲基...的时候' with no comma after 工艺, whereas [0005] reads '...合成环磺酮的工艺，在制备...' and [0007] reads '...合成环磺酮的工艺，在制备...'. Confirmed in both the text layer and the ink. Almost ce
- **[p03.png]** Text-layer-vs-image. The embedded text layer emits the running head and the footer AFTER the body and emits the page number twice; the image shows the head at the top and one page number at the bottom.
  - drawing: The image shows, in reading order: running head 'CN 109678767 A' left / '说　明　书' centre / '1/9 页' right, under a full-width rule; then the title; then the body; then a single centred '3' at the foot. Nothing els
  - text: The text layer ends with the sequence '说　明　书', '1/9 页', '3', 'CN 109678767 A', '3' - the head and footer components appended after the body, and '3' appearing twice where the ink shows it once. Layout was taken
- **[p03.png]** Naming-form variation that a downstream name parser must not read as a structural difference.
  - drawing: n/a - no drawing anywhere on this page
  - text: [0007] prints the enol-ester intermediate as '...苯甲酸-3-氧代-1-环己烯酯' WITH a hyphen joining 苯甲酸 to 3-氧代, while the patent it is describing, CN104292137A, prints '...苯甲酸3-氧代-1-环己烯酯' without it. Same compound; the hy
- **[p04.png]** Text-vs-text (there are NO drawings on this page). Step 3) describes two separate reaction flasks but never states that the contents of the first are combined with the contents of the second, so the actual coupling operation is missing from the written procedure.
  - drawing: n/a - no drawing on this page; both statements below are prose
  - text: [0018] reads '…加入反应瓶，升温回流反应，反应完毕后脱尽溶剂；将1,3-环己二酮、溶剂加入反应瓶，在 30℃以下滴加三乙胺…'. The acid chloride is formed and the solvent stripped in flask one; 1,3-cyclohexanedione, solvent and triethylamine are charged to flask tw
- **[p04.png]** Text-vs-text. The radical initiator for the step-1 benzylic bromination is called a 'catalyst' and one of the two options given is m-chloroperoxybenzoic acid, an oxidant not normally used as a radical initiator.
  - drawing: n/a - no drawing on this page
  - text: [0020] reads '所述催化剂为偶氮二异丁腈或间氯过氧苯甲酸' = 'said catalyst is azobisisobutyronitrile or m-chloroperoxybenzoic acid'. Verified in the image character by character: the second reagent carries the 间 (meta) prefix and re
- **[p04.png]** Text-vs-text. Reagent slots used in the procedure paragraphs are left undefined on this page: the step-2 solvent, and both the catalyst and the two solvents of step 3).
  - drawing: n/a - no drawing on this page
  - text: [0016] charges a '溶剂' and [0018] charges a '催化剂' plus two '溶剂', but the definition paragraphs on this page stop at [0023], which covers only step 2)'s bases and catalyst. [0021] defines solvents for step 1) alo
- **[p04.png]** Printing / text-layer artifact that downstream passes must not read as meaningful. One locant string carries an embedded space.
  - drawing: n/a - no drawing on this page
  - text: [0021] is encoded as '二氯甲烷、1 ,2-二氯乙烷或氯仿' with a literal U+0020 between '1' and ','. The image shows CNIPA justification air on both sides of that comma ('1 , 2-'). Reproduced verbatim in zh per the no-normalisa
- **[p04.png]** Text-layer-vs-image. The footer page number appears twice in the extracted text layer but only once on the rendered page.
  - drawing: n/a - no drawing on this page
  - text: The text layer emits, after the body, the sequence '说　明　书' / '2/9 页' / '4' / 'CN 109678767 A' / '4'. The image shows exactly one '4', centred at the foot of the page, and the header band 'CN 109678767 A' left, 
- **[p04.png]** Text-vs-text. A character in the prior-art criticism is printed as 再 ('again') where the sentence requires its homophone 在 ('during').
  - drawing: n/a - no drawing on this page
  - text: [0009] reads '因极易挥发，再生产过程中容易造成慢性中毒事故。' Verified in the image at high magnification as 再, not 在. Almost certainly a typing error for '在生产过程中' ('in the production process'). Transcribed and translated as printed 
- **[p05.png]** The scheme draws the acid chloride formation AFTER the reaction that consumes the acid chloride, so the drawn order is not the chemical order.
  - drawing: Reaction row 4 (page y 1389-1712) shows cyclohexane-1,3-dione plus the benzoyl chloride reacting to the final triketone. Reaction row 5, printed BELOW it at page y 1739-2040, shows the benzoic acid plus 氯化亚砜 gi
  - text: [0025] lists the step 3) components in the order acid, catalyst, thionyl chloride, 1,3-cyclohexanedione, triethylamine, acetone cyanohydrin, which is the chemically sensible order and the reverse of the drawn o
- **[p05.png]** The catalyst named in the prose is drawn nowhere on the scheme.
  - drawing: No DMF and no 催化剂 label appears at any position in any of the five reaction rows. Row 5, where the acid chloride is formed, carries an entirely bare arrow.
  - text: [0025] gives a 催化剂 (catalyst) at 0.01-0.1 equivalents in step 3) and [0027] identifies it as DMF. A reagent written but not drawn.
- **[p05.png]** The prose collapses into one numbered step what the drawing splits into two reactions.
  - drawing: Step 3) chemistry is drawn as two separate arrows: acid to acid chloride (row 5), then acid chloride plus cyclohexane-1,3-dione to product (row 4).
  - text: [0025], [0026] and [0027] treat step 3) as a single step with one combined molar ratio covering all six components. Neither representation is wrong, but a downstream pass that counts steps will get 3 from the p
- **[p05.png]** The scheme shows five transformations while the prose on this page numbers only three steps, and this page alone does not determine the mapping.
  - drawing: Five arrows: bromination, etherification, ester hydrolysis, acylation, acid chloride formation.
  - text: [0024] constrains step 2), [0025] to [0027] constrain step 3), and no paragraph on this page mentions step 1) or the ester hydrolysis of row 3. Rows 1 and 2 map plausibly onto steps 1) and 2) and rows 4 and 5 o
- **[p05.png]** Reagents drawn on the scheme that no paragraph on this page mentions.
  - drawing: Row 1 uses HBr plus H2O2 with a catalyst labelled 'cat'. Row 2 uses HOCH2CF3 plus an unspecified 碱 (base). Row 3 uses 碱/酸 (base then acid).
  - text: None of HBr, H2O2, 'cat', HOCH2CF3, 碱 or 碱/酸 appears anywhere in [0024] to [0029]. They are drawn but not written on this page. The prose for those steps is on earlier pages and was not available to this pass, 
- **[p05.png]** Two reagent names that DO appear in both places agree exactly, recorded here as a positive check rather than a conflict.
  - drawing: Row 4's arrow label reads 三乙胺/丙酮氰醇 and row 5's co-reactant reads 氯化亚砜. Row 4's left-hand structure is drawn as cyclohexane-1,3-dione (two C=O separated by one CH2).
  - text: [0025] names 氯化亚砜, 1,3-环己二酮, 三乙胺 and 丙酮氰醇. Drawing and prose agree on all four, including the 1,3 substitution pattern of the dione, which is read off the drawing independently.
- **[p05.png]** The embedded text layer carries a character-spacing pattern the printed page does not, and omits a mark the printed page does carry.
  - drawing: The printed page shows no spaces inside '(2,2,2-三氟乙氧基)' in [0025], and it does show a small '。' at page x 317-323, y 2082-2088 below the last reaction row.
  - text: The text layer encodes '(2 ,2 ,2-三氟乙氧基)' with a space before each comma while encoding '1,3-环己二酮' in the same sentence with none, and it contains no character at all for the small '。', which is part of the sche
- **[p06.png]** Both drawings on this page show only the PRODUCT of their step. Every reagent, solvent, catalyst, temperature and workup for those steps is written in the prose and drawn nowhere, and neither starting material is drawn.
  - drawing: Drawing 1 ([0039]) is the bare structure of methyl 2-chloro-3-(bromomethyl)-4-(methanesulfonyl)benzoate with no arrow and no annotation. Drawing 2 ([0042]) is the bare structure of 2-chloro-4-(methanesulfonyl)-
  - text: [0040] supplies the whole of step 1 (substrate methyl 2-chloro-3-methyl-4-methylsulfonylbenzoate, dichloroethane, AIBN, HBr 48%, H2O2 30%, 75 to 80 C, isopropanol recrystallisation, 46.67 g, 99.0% purity, 89% y
- **[p06.png]** No conflict, recorded as a positive cross-check: each drawing agrees exactly with the compound name in its own step heading.
  - drawing: Drawing 1 reads 2-Cl / 3-CH2Br / 4-SO2CH3 on a benzoate whose ester oxygen bears a methyl. Drawing 2 reads 2-Cl / 3-CH2OCH2CF3 / 4-SO2CH3 on a free benzoic acid.
  - text: [0038] names methyl 2-chloro-3-bromomethyl-4-methylsulfonylbenzoate and [0041] names 2-chloro-3-(2,2,2-trifluoroethoxy)methyl-4-methylsulfonylbenzoic acid. Both match their drawings substituent for substituent 
- **[p06.png]** Text-vs-text. The boilerplate sentence introducing the examples says 'this aspect' where the standard phrasing is 'the present invention', twice in one sentence.
  - drawing: n/a - the discrepancy is between prose and convention, not with any drawing
  - text: [0035] reads '下面结合实施例对本方面做进一步详细的说明，但是此说明不会构成对本方面的限制。' The characters 本方面 are what the embedded text layer contains, so this is not a reading error on this pass; compare [0030] on the same page, which uses the n
- **[p06.png]** Text-vs-text. The chlorinated solvent in step 1 is named without a locant.
  - drawing: n/a - solvent does not appear in any drawing
  - text: [0040] says only '200ml二氯乙烷' (dichloroethane), never '1,2-二氯乙烷'. 1,2-dichloroethane is the solvent this would conventionally be, but the isomer is not stated anywhere on the page and has NOT been inferred into 
- **[p06.png]** Naming variation between this publication and the target's Chinese common name as it appears elsewhere in the same family of documents. Recorded so a downstream name-matching pass does not treat the two spellings as two compounds.
  - drawing: n/a
  - text: [0033] and [0037] both name the target 环磺酮 (three characters). The sister publication CN104292137A uses 环磺草酮 (four characters, with 草). Both denote tembotrione. The form on this page is verified from the embedd
- **[p06.png]** PDF text-layer artifact that is NOT visible on the page and must not be transcribed as content.
  - drawing: The rendered page image shows exactly one footer, the page number '6' centred at the bottom, and one header line: 'CN 109678767 A' at the left, '说 明 书' centred, '4/9 页' at the right.
  - text: The extracted text layer emits the header and footer OUT OF READING ORDER, after the body text, and emits the page number '6' TWICE: the tail of the file reads '说　明　书', '4/9 页', '6', 'CN 109678767 A', '6'. The 
- **[p07.png]** Text layer versus image, on characters. The embedded text layer inserts a space before the '.' or ',' inside three numeric tokens on one line of [0046]; the printed page has no space there.
  - drawing: n/a, this is a text layer versus page-image disagreement and not a drawing
  - text: The raw text layer line reads '将27 .4g  2-氯-3-(2 ,2 ,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸(99 .7％、'. Re-read at high magnification the page prints 27.4g, (2,2,2-三氟乙氧基) and (99.7％ with no internal spaces, and the same tokens are
- **[p07.png]** Reagents written but not drawn. All three drawings on this page are lone product structures; none of the reagents named in the prose appears in any drawing, and no arrow is drawn anywhere on the page.
  - drawing: drawings[0] shows only tembotrione; drawings[1] shows only the bromomethyl methyl ester; drawings[2] shows only the trifluoroethoxymethyl benzoic acid. No arrows, no reagents above or below anything, no startin
  - text: [0046] names 氯化亚砜 (thionyl chloride), DMF, 1,3-环己二酮, 三乙胺 and 丙酮氰醇, and [0051] names 偶氮二异丁腈, 氢溴酸 and 双氧水. None of these is drawn. This is the patent's convention of captioning each numbered step with its product
- **[p07.png]** Intermediate described in neither prose nor drawing. The [0046] sequence implies an enol ester that is never named and never drawn.
  - drawing: n/a, drawings[0] shows the final product only
  - text: [0046] goes from the acid plus 氯化亚砜 straight to adding 1,3-环己二酮 and 三乙胺, then adds 丙酮氰醇, then works up to the product. The acid chloride and the enol ester that acetone cyanohydrin rearranges are implied by the
- **[p07.png]** A solvent is named without its locant.
  - drawing: n/a, no drawing on this page names a solvent
  - text: [0046] says only 二氯乙烷 (dichloroethane), twice, never 1,2-二氯乙烷. The 1,2-isomer is the usual reading but the isomer is not stated on the page and has not been supplied in the transcription or the translation.
- **[p07.png]** Punctuation width in the image is not a reliable guide on this page and downstream passes must take the text layer's widths, not the picture's.
  - drawing: n/a
  - text: CNIPA's fixed-width setting renders half-width '(' ')' as visually wide glyphs and compresses the full-width '，' toward a Western comma, so the two cannot be told apart by eye on the rendered page. Per the born
- **[p08.png]** The final step's prose describes a three-stage reagent sequence but only the finished product is drawn; the acid chloride and the enol ester it passes through appear in the text and nowhere in the picture.
  - drawing: drawings[0] shows only the completed 2-aroylcyclohexane-1,3-dione. There is no acid chloride, no enol ester, no arrow and no reagent label anywhere in or beside the drawing.
  - text: [0057] charges thionyl chloride with catalytic DMF (acid chloride formation), then 1,3-cyclohexanedione with triethylamine (O-acylation to the enol ester), then acetone cyanohydrin (cyanide-catalysed rearrangem
- **[p08.png]** The target is drawn as the keto (2-acyl-1,3-dione) tautomer, while the name in the text carries no tautomer information at all.
  - drawing: drawings[0] is drawn saturated, with two ring C=O, no ring double bond, no enol OH, and an implicit H on the attachment carbon.
  - text: [0055] and [0059] name the product only as 环磺酮 (tembotrione), which fixes the constitution but says nothing about tautomer. Not a conflict, but recorded so a downstream pass generating a canonical structure doe
- **[p08.png]** Text-vs-text. The Chinese common name for the target is written one character short of the usual form.
  - drawing: drawings[0] read off the picture is the tembotrione skeleton: 2-chloro-4-methanesulfonyl-3-[(2,2,2-trifluoroethoxy)methyl]benzoyl on C2 of cyclohexane-1,3-dione.
  - text: [0055] and [0059] both write 环磺酮. The usual CNIPA form is 环磺草酮. Both denote tembotrione. Recorded as printed and not corrected.
- **[p08.png]** Text-vs-text. The same chemical fragment and the same style of purity figure are printed with and without justification spaces on this one page.
  - drawing: n/a - the disagreement is between two prose passages, not with a drawing.
  - text: [0057] prints 3- (2 ,2 ,2-三氟乙氧基) and (99 .8％, with spaces inside the locant string and inside the number; [0063] prints the same fragment tight as (2,2,2-三氟乙氧基), and [0054] prints 99.8％ tight. Reproduced verbat
- **[p08.png]** Text-vs-text. A charging sentence in the second-step procedure has no verb.
  - drawing: n/a - prose only.
  - text: [0054] reads 往剩余物里4.53g氢氧化钠(99％、0.112mol)，200ml水，在70～75℃进行碱解, literally 'into the residue 4.53 g sodium hydroxide, 200 ml water'. The 加入 (add) the construction requires is absent from the publication. The Engli
- **[p09.png]** The PDF's embedded text layer inserts spaces inside four numeric tokens in [0068]; the rendered page shows no such spaces. This is the one thing on the page that can silently corrupt a mass balance.
  - drawing: n/a - this is a text-layer versus image disagreement, not a drawing disagreement
  - text: Text layer: '将34 .75g', '(2 ,2 ,2-三氟乙氧基)', '(99 .7％', '将11 .3g', '1 ,3-环己二酮'. Rendered image, verified at 2x magnification: '将34.75g', '(2,2,2-三氟乙氧基)', '(99.7％', '将11.3g', '1,3-环己二酮'. The zh field reproduces th
- **[p09.png]** Paragraph [0065] never names the compound it produces, so the identity of its product rests on the adjacent drawing and on the next example step rather than on the paragraph itself.
  - drawing: The drawing at [0064] is 2-chloro-3-[(2,2,2-trifluoroethoxy)methyl]-4-(methylsulfonyl)benzoic acid.
  - text: [0065] ends '烘干得31.58g白色粉末，纯度99.3％，收率90.5％。' - '31.58 g of a white powder', with no compound name. [0068] then charges '2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸' as its starting material, which is the same compound as t
- **[p09.png]** The chlorinated solvent in [0068] is named without a locant.
  - drawing: n/a - the solvent is not drawn anywhere on the page
  - text: [0068] says only '二氯乙烷' (dichloroethane) in both places it appears, never '1,2-二氯乙烷'. The 1,2-isomer is the conventional reading but is nowhere stated on this page, and has not been inferred into the transcript
- **[p09.png]** The drawing at [0072] depicts the PRODUCT of the step titled at [0071], while the prose at [0073] opens with the step's SUBSTRATE. A downstream pass must not read the drawing as the starting material.
  - drawing: Drawing at [0072] is methyl 2-chloro-3-(bromomethyl)-4-(methylsulfonyl)benzoate, i.e. the bromomethyl compound.
  - text: [0071] titles the step '1、2-氯-3-溴甲基-4-甲磺酰基苯甲酸甲酯的合成' (synthesis of the bromomethyl ester) and [0073] begins '将26.43g 2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯...' - the 3-METHYL ester, the substrate. Same convention holds for the dr
- **[p09.png]** A verb is missing from the printed Chinese in [0065].
  - drawing: n/a - prose only
  - text: '往剩余物里4.04g氢氧化钠(99％、0.1mol)，200ml水，在70～75℃进行碱解' has no 加入 or equivalent between 往剩余物里 and the reagent list. Transcribed as printed; the English supplies the verb in square brackets so the gap stays visible.
- **[p09.png]** Parenthesis width cannot be settled from the two sources together, and downstream passes should not rely on it for this page.
  - drawing: n/a - typography, prose only
  - text: The embedded text layer holds half-width ASCII '(' and ')' everywhere on this page. The printed glyphs are visually wide, occupying a full CJK em, as CNIPA typesetting renders them. The text layer is taken as a
- **[p10.png]** Text-vs-text, chemically significant. In [0076] the mass printed for triethylenediamine (DABCO) does not correspond to the molar amount printed beside it.
  - drawing: n/a - not a drawing issue; drawings[0] on this page depicts only the product of [0076] and says nothing about reagent charges
  - text: [0076] prints '2.26g三乙烯二胺(99％、0.01mol)'. Triethylenediamine (DABCO) MW 112.17, so 0.01 mol at 99% purity is 1.13 g, not 2.26 g; 2.26 g corresponds to 0.02 mol. Transcribed exactly as printed and NOT corrected. 
- **[p10.png]** Text-vs-text, chemically significant. In [0076] the mass printed for 2,2,2-trifluoroethanol is roughly 18-fold below the molar amount printed beside it, and it is the limiting-reagent line of the step.
  - drawing: n/a - not a drawing issue
  - text: [0076] prints '1.13g2,2,2-三氟乙醇(99％、0.2mol)'. 2,2,2-Trifluoroethanol MW 100.04, so 0.2 mol at 99% purity is 20.2 g, not 1.13 g; 1.13 g corresponds to about 0.011 mol, i.e. only 0.11 equivalent against the 0.1 mo
- **[p10.png]** Text-layer-vs-image, whitespace only, no character affected. The PDF text layer inserts a space before the decimal point or before a locant comma in twelve numeric literals that the printed page shows unbroken.
  - drawing: The rendered page (each token inspected on a crop enlarged 2x to 3x) prints, without any gap: 30.66g / 1.13g / 31.1g / 34.72g / (99.8％ / 0.1mol / 0.74g / 0.01mol / 0.2mol / 22.6g / (2,2,2- / 1,3-
  - text: The embedded text layer emits: '30 .66g' / '1 .13g' / '31 .1g' / '34 .72g' / '(99 .8％' / '0 .1mol' / '0 .74g' / '0 .01mol' / '0 .2mol' / '22 .6g' / '(2 ,2 ,2-' / '1 ,3-'. These are kerning artifacts of the extr
- **[p10.png]** Text-layer-vs-image, running heads. The extracted text layer duplicates the footer page number and emits the header and footer out of visual order.
  - drawing: The rendered page shows the header as three separated fields on one ruled line (CN 109678767 A at the left, 说　明　书 centred, 8/9 页 at the right) and a single centred footer '10' at the very bottom, with nothing e
  - text: The text layer ends with the sequence '说　明　书' / '8/9 页' / '10' / 'CN 109678767 A' / '10', i.e. the page number 10 appears twice and the publication number follows rather than precedes the centred title. The ima
- **[p10.png]** Grammatical omission in the source prose, preserved rather than repaired.
  - drawing: n/a - not a drawing issue
  - text: [0076] reads '往剩余物里8.1g氢氧化钠(99％、0.2mol)，200ml水，在70～75℃进行碱解' - the 往...里 construction has no governing verb (no 加入 'add' or equivalent). Transcribed as printed and translated with the same ellipsis rather than s
- **[p10.png]** Gap in the source, noted so a downstream route-extraction pass does not read it as a one-step transformation.
  - drawing: drawings[1] shows only the final triketone product of step 3. No intermediate is drawn and there is no arrow.
  - text: [0079] describes three distinct chemical operations (acid chloride formation with SOCl2/DMF; reaction with 1,3-cyclohexanedione and triethylamine; then addition of acetone cyanohydrin). The enol-ester intermedi
- **[p10.png]** Naming variation between this patent and the reference patent, recorded so the two datasets can be reconciled. Not an internal inconsistency on this page.
  - drawing: drawings[1] on this page draws the tembotrione skeleton.
  - text: [0077] names the target 环磺酮 (three characters). The reference patent CN104292137A names the same target 环磺草酮 (four characters). Both denote tembotrione. Transcribed as printed here; no normalisation applied.
- **[p11.png]** Whole-page attribution. Every structure and every step on this page belongs to the Comparative Example, not to the invention. Downstream passes that pick up the drawings without this context will read the patent's counter-example as its route.
  - drawing: Three product structures are drawn with no caption or label of any kind identifying which route they belong to. Nothing inside any drawing distinguishes them from the invention's own intermediates, which are th
  - text: The heading 对比实施例 (Comparative Example) is printed as [0080] on PAGE 10, one page earlier, and the step-1 heading as [0081]. Neither is repeated on this page. [0090] on this page confirms the attribution from t
- **[p11.png]** The drawing shows a benzylic bromination product, but the prose for that step names no radical initiator and no light source.
  - drawing: [0082] shows CH2Br on the ring carbon that carried CH3 in the substrate, i.e. benzylic substitution rather than ring bromination.
  - text: [0083] gives only 溴素 (Br2), 四氯化碳 (CCl4) and 升温回流 (heat to reflux). No AIBN, no benzoyl peroxide, no peroxide of any kind and no irradiation is mentioned. The invention's own corresponding step [0073] on page 10
- **[p11.png]** Printed typo carried through verbatim: 整出 where 蒸出 (distil off) is meant.
  - drawing: n/a - text-vs-text, no drawing involved
  - text: [0089] reads 然后整出溶剂和过量的氯化亚砜. 整 (zheng, 'to arrange') makes no sense with 溶剂; 蒸出 ('distil off') is plainly intended, and the very same paragraph set uses 蒸出 correctly twice in [0086] (蒸出DMF, 蒸出乙醇). Both the embe
- **[p11.png]** Printed word-order error carried through verbatim: the locative 中 is misplaced in the solvent phrase.
  - drawing: n/a - text-vs-text, no drawing involved
  - text: [0089] reads 溶于200ml中二氯甲烷, literally 'dissolved in 200 ml, in dichloromethane'. Standard order would be 溶于200ml二氯甲烷中. The meaning is not in doubt - 200 ml of dichloromethane - but the characters are reproduced 
- **[p11.png]** Printed capitalisation error carried through verbatim: HCL for HCl.
  - drawing: n/a - text-vs-text, no drawing involved
  - text: [0086] reads 用HCL调至酸性 with a capital L. Elsewhere the description writes 盐酸 in Chinese ([0089]) rather than a formula, so there is no competing spelling on this page. Reproduced as printed.
- **[p11.png]** The prose for step 2 identifies its product neither by name nor by mass; only the drawing supplies the identity, and no mass balance is possible for that step.
  - drawing: [0085] draws the product as 2-chloro-3-[(2,2,2-trifluoroethoxy)methyl]-4-(methylsulfonyl)benzoic acid, the free acid.
  - text: [0086] ends 黄色固体析出，收率为83.2％ - 'a yellow solid precipitated, the yield was 83.2％'. No product name, no product mass, no substrate quantity and no trifluoroethanol quantity are given anywhere in the paragraph, so
- **[p11.png]** The final coupling step names no base, unlike the corresponding step of the invention's Example.
  - drawing: [0088] draws the C-acylated 2-aroylcyclohexane-1,3-dione, the product of the acylation plus rearrangement sequence.
  - text: [0089] charges only the acid chloride solution, 150 ml acetonitrile, 13.44 g 1,3-cyclohexanedione and 4 drops of acetone cyanohydrin. No triethylamine and no other base appears, where the Example's correspondin
- **[p11.png]** The catalyst in the final step is quantified as a drop count, which cannot be converted to moles.
  - drawing: n/a - text-vs-text, no drawing involved
  - text: [0089] reads 4滴丙酮氰醇 - '4 drops of acetone cyanohydrin'. Every other reagent in that paragraph carries both a mass and a molar figure. A downstream mass-balance pass must treat this loading as unquantified rathe
- **[p11.png]** Unit and name-form inconsistencies within the page that downstream passes should not read as meaningful.
  - drawing: n/a - text-vs-text, no drawing involved
  - text: Volume units are printed 'mL' in [0083] and [0086] but 'ml' in [0089]. [0089] prints 'PH＝2' with a full-width '＝' and an upper-case P-H rather than 'pH'. This patent writes the target as 环磺酮 throughout, whereas
