# What is wrong with CN111440099B

Produced by annotating the patent by hand, against the scanned pages rather than
against anyone's OCR. Every item below is a defect in the **patent**, not in the
annotation. The annotation records them and changes nothing.

- 38 reactions extracted, of which 33 carry at least one flag
- 25 unique compounds, 11 pathways
- 26 discrepancies raised by the page-vision pass

## Flags raised, by kind

| flag | count | what it means |
|---|---:|---|
| `mass_balance_implausible` | 19 | stated product mass cannot be reconciled with the stated input moles and yield |
| `no_conditions` | 8 | no reaction conditions stated at all |
| `drawing_text_conflict` | 5 | the drawn scheme and the written procedure disagree |
| `missing_product` | 5 |  |
| `route_attribution_unclear` | 4 | cannot tell from the page whether the drawn route is the invention's or prior art |
| `reagent_written_not_drawn` | 4 | a reagent in the procedure appears on no arrow |
| `cross_reference_unresolved` | 1 |  |

## The headline findings

No hand-written analysis exists for CN111440099B. The generated sections above and below are complete; this section is not, and is omitted rather than filled with another patent's findings.

## Everything the page-vision pass raised

- **[p01.png]** The substance is tembotrione throughout, but the printed abstract names it two different ways: twice it drops the leading character of the three-character Chinese name and prints a two-character short form instead.
  - drawing: (no drawings on this page - this is a text-internal inconsistency, recorded here so it is not lost)
  - text: The (54) title and the first half of the (57) abstract print the full three-character name; the clause beginning 'the purification method of the present invention' then prints the short form twice, with the lea
- **[p01.png]** The abstract credits an Ames test with producing a cyanide impurity figure in ppm, which is not what an Ames test measures.
  - drawing: (no drawings on this page - this is a text-internal inconsistency, recorded here so it is not lost)
  - text: The closing sentence of the (57) abstract says that by subjecting the product before and after purification to an Ames test, the cyanide impurity content originally at 1327ppm was reduced to below 100ppm. The a
- **[p03.png]** The prose in [0009] names an acyl chloride intermediate that the drawn scheme never draws: the drawing collapses two of the three prose stages onto a single arrow, putting SOCl2 above that arrow and cyclohexane-1,3-dione below it.
  - drawing: one arrow running from 2-chloro-4-(methylsulfonyl)-3-[(2,2,2-trifluoroethoxy)methyl]benzoic acid straight to the enol ester, with reagents SOCl2 above and cyclohexane-1,3-dione below; no acyl chloride structure
  - text: [0009] names three stages, with 2-chloro-3-(2,2,2-trifluoroethoxy)methyl-4-methylsulfonylbenzoyl chloride as a discrete named product of the thionyl chloride step, then reacted with cyclohexanedione to give the
- **[p03.png]** The prose names the dione without a locant while the drawing fixes it. This is the prose being less specific than the drawing, not a contradiction.
  - drawing: the co-reagent below the first arrow is drawn with its two ring ketones separated by one CH2, i.e. unambiguously cyclohexane-1,3-dione
  - text: [0009] writes the reagent as plain cyclohexanedione with no locant, which on its own would also admit the 1,2- and 1,4-diones
- **[p03.png]** The molecular weight printed in [0005] does not match the molecular formula printed in [0004] or the structure drawn at [0008]. Recorded, not corrected.
  - drawing: the structure drawn at [0008] is exactly C17H16ClF3O6S, counted off the drawing as 17 C, 16 H, 1 Cl, 3 F, 6 O, 1 S, whose formula weight is 440.81 on standard atomic weights
  - text: [0005] gives the molecular weight as 440.88, which is 0.07 higher than the formula in [0004] and the drawn structure give
- **[p03.png]** NO DISAGREEMENT, cross-check run and passed: the molecular formula in [0004] and the CAS number in [0003] both agree with the structure drawn at [0008].
  - drawing: atom count off the drawing at [0008] is C17 H16 Cl1 F3 O6 S1, and the connectivity drawn is that of tembotrione, CAS 335104-84-2
  - text: [0004] gives the molecular formula as C17H16ClF3O6S and [0003] gives the CAS number as 335104-84-2
- **[p03.png]** NO DISAGREEMENT, cross-check run and passed: every reagent drawn on the scheme is also written in the prose, and every reagent written in the prose is also drawn. The only reagent-level gap between the two is the missing acyl chloride intermediate reported above, which is a structure rather than a reagent.
  - drawing: reagents drawn: SOCl2 above arrow 1, cyclohexane-1,3-dione below arrow 1, acetone cyanohydrin above arrow 2; nothing else is drawn on either arrow
  - text: [0009] names thionyl chloride, cyclohexanedione and acetone cyanohydrin, and names no other reagent, no base, no solvent and no temperature
- **[p03.png]** The structure drawn at [0008] and the final structure of the scheme at [0010] are drawn identically. This is consistent, and is recorded so that a downstream pass does not read them as two different compounds.
  - drawing: Formula 1 and the row-2 product of Formula 2 have identical cores, identical substituent positions and identical condensed labels
  - text: [0007] introduces Formula 1 as the structural formula of tembotrione; [0009] says the route of Formula 2 finally gives tembotrione
- **[p05.png]** The text names the starting material as the acyl chloride, but the drawing starts from the free carboxylic acid.
  - drawing: The first structure is drawn with HO-C(=O) on the ring, i.e. 2-chloro-3-[(2,2,2-trifluoroethoxy)methyl]-4-(methanesulfonyl)benzoic acid, and SOCl2 is written above the first arrow.
  - text: [0029] on p04 charges the flask with 2-chloro-3-(2,2,2-trifluoroethoxy)methyl-4-methanesulfonylbenzoyl chloride and only then adds thionyl chloride; [0032] on this page likewise calls the species that reacts wi
- **[p05.png]** The acid chloride intermediate the prose describes as isolated is drawn nowhere: one arrow collapses two written stages.
  - drawing: A single arrow carries the benzoic acid straight to the enol ester, with SOCl2 above it and cyclohexane-1,3-dione below it, so no acid chloride structure appears on the page.
  - text: [0029] on p04 describes two separate stages: reaction with thionyl chloride at 15℃ then 75℃ for 3h, distillation of the solvent and the excess thionyl chloride off at 85℃ under reduced pressure, and only then a
- **[p05.png]** Every solvent, base and condition written in the prose is absent from the drawing.
  - drawing: Nothing appears above or below either arrow except SOCl2 and the two drawn reagent molecules: no solvent, no base, no temperature, no time.
  - text: [0029] on p04 specifies 1,2-dichloroethane, triethylamine, 15℃, 0.5h at room temperature, 75℃ for 3h, -0.098mP, 85℃ and 40℃ for 6h; [0032] on this page adds that a suitable base such as triethylamine may be add
- **[p05.png]** The dione is written without a locant on this page while the drawing fixes the isomer.
  - drawing: The reagent below the first arrow is drawn as cyclohexane-1,3-dione, its two carbonyls one carbon apart.
  - text: [0032] on this page writes only cyclohexanedione, with no isomer locant; [0029] on p04 does write the 1,3-isomer, so the drawing agrees with p04 and is merely more specific than [0032].
- **[p05.png]** Acetone cyanohydrin is drawn but never written on this page, and its place in the sequence differs between drawing and prose.
  - drawing: An unlabelled (CH3)2C(OH)CN structure sits above the second arrow, i.e. as the reagent that converts the enol ester into the product, in a step of its own.
  - text: [0029] on p04 names acetone cyanohydrin but charges it together with 1,3-cyclohexanedione into a single 40℃ 6h step; nothing on this page names it at all.
- **[p05.png]** The final drawn structure is never named in the prose, so the drawing is the only record of the product's connectivity.
  - drawing: The product is drawn as 2-{2-chloro-3-[(2,2,2-trifluoroethoxy)methyl]-4-(methanesulfonyl)benzoyl}cyclohexane-1,3-dione.
  - text: [0029] on p04 calls the product only a red-brown solid; [0032] on this page calls it the tembotrione product. Neither gives a systematic name for the drawing to be checked against.
- **[p06.png]** The stated percentage reduction in column 5 does not follow from the two ppm columns beside it in any row on this page, and it is not monotonic against the residual it is supposedly computed from.
  - drawing: As printed on this page: batch 3 reads 1327, 92, 74%; batch 4 reads 1327, 88, 89%; batch 5 reads 1327, 72, 91%; batch 6 reads 1327, 45, 98%. Computed from the two printed ppm columns, the reduction would be 93.
  - text: Nothing on this page. The header row and the Table 1 caption are printed on p05; per that header, supplied by the coordinator, column 3 is the original cyanide impurity content in ppm, column 4 is the cyanide i
- **[p07.png]** The fifth column of Table 2 is the percentage reduction in cyanide impurity content, so it should follow arithmetically from the two ppm columns printed beside it. On three of this page's four batches it does not.
  - drawing: Printed on this page, then the value that follows from the same row's two ppm cells. Batch 7: printed 1125 and 32, printed reduction 97, computed 97.16%, agrees. Batch 8: printed 1125 and 67, printed reduction 
  - text: No prose on this page states any reduction percentage, so nothing in the text either confirms or contradicts the printed column; the disagreement is internal to the patent's results. The coordinating pass repor
- **[p07.png]** The reduction column is punctuated inconsistently inside the table image: batch 7's cell prints a bare number with no percent sign while batches 8, 9 and 10 all print one.
  - drawing: 97 for batch 7, against 91%, 88% and 81% for batches 8, 9 and 10.
  - text: The column header itself translates as "Reduction in cyanide impurity content %", so the header carries the percent sign for every row. Cells are kept exactly as printed rather than normalised.
- **[p08.png]** The printed reduction column of this table disagrees with the two cyanide-content columns printed beside it, in all three batches on this page. The disagreement is arithmetic and internal to the table image; it is not a disagreement with any prose on this page. Confirmed by the coordinator to run through all five tables in this patent, not only this one. Every printed cell is left exactly as printed.
  - drawing: Printed cells, batch 11: original 1257 ppm, after treatment 31 ppm, reduction 96%. Batch 12: 1257 ppm, 37 ppm, 95%. Batch 13: 1257 ppm, 12 ppm, 98%.
  - text: Computed from the two printed content columns, not printed anywhere on the page: batch 11 is a 97.53% reduction against the printed 96%, batch 12 is 97.06% against the printed 95%, and batch 13 is 99.05% agains
- **[p08.png]** Reading disagreement on the first character of the first column header, recorded rather than resolved. The coordinator reads that character, from the copy of this header printed on p05, as the one meaning actual or experiment, giving 'experiment batch'. On p08 it is the character meaning test or trial: checked twice at 7x zoom, the glyph carries the three-stroke speech radical on the left and the phonetic for 'style' on the right, with no roof radical above, so on this page the header reads 'test batch'. The zh cell is left as printed on this page. Whether p05 genuinely prints a different character or the two readings simply differ is not decidable from p08 alone, and is left open.
  - drawing: p08 header row, first column: the character for test or trial plus batch, that is 'test batch'.
  - text: Coordinator reading of the same header printed on p05: the character for actual or experiment plus batch, that is 'experiment batch'.
- **[p09.png]** The fifth column of both tables on this page is the percentage reduction in cyanide impurity content, so it should follow from the two ppm columns printed in the same row. In every row on this page it does not. The printed cells are recorded unchanged; the percentages below marked computed were derived here from the printed ppm pairs purely to state the size of the disagreement, and no printed cell was recomputed, corrected or replaced. The column header is not on this page for the first table in the series; it was supplied by the coordinating read of p05, where the first table of the series prints it.
  - drawing: Table Four at paragraph 0048: row 14 goes from 1029 ppm to 38 ppm, which is 96.31 percent computed against 97 printed with no percent sign; row 15 goes from 1029 ppm to 46 ppm, which is 95.53 percent computed a
  - text: The prose on this page, paragraphs 0050 and 0053, states no reduction percentage at all, so nothing on this page settles which figure is intended. The fifth column header, printed on both tables on this page an
- **[p09.png]** The last cell of row 14 of Table Four is printed as a bare number with no percent sign, while every other cell in that column on this page carries one.
  - drawing: Row 14 of the table at paragraph 0048 prints 97; row 15 of the same table prints 94 percent.
  - text: The column header of that table reads cyanide impurity content reduction percent, so a percentage is what the column holds; the prose says nothing about it.
- **[p09.png]** The prose of Example 5 and the table of Example 5 results list the four PH values in opposite order. The number of data rows does match the number of PH values named in the prose, four; only the order differs. Recorded, not reconciled.
  - drawing: The table at paragraph 0051 lists PH 5 for batch 16, then 4 for batch 17, then 3 for batch 18, then 2 for batch 19, descending.
  - text: Paragraph 0050 states that the dilute hydrochloric acid was added to adjust the PH to 2, 3, 4 and 5 respectively, ascending.
- **[p09.png]** The table at paragraph 0051 carries no printed caption, unlike the other tables in this document, so its identity rests on its position immediately after the prose of Example 5 rather than on any table number.
  - drawing: The table image printed at paragraph 0051 has no caption above, below or beside it.
  - text: Paragraph 0050 ends by announcing that the following data were obtained, which introduces a table but does not number or name it.
- **[p09.png]** Example 6 charges thionyl chloride onto a material named as an acid chloride, and strips excess thionyl chloride afterwards, which is the operation one performs on the corresponding acid. Recorded, not corrected, because the same wording appears in Example 1 on p04 and so is the patent's own.
  - drawing: There is no drawing on this page; the comparison is between the prose of paragraph 0053 on this page and the route as described in the body text on p03.
  - text: Paragraph 0053 charges 231.9 g of the 2-chloro-3-(2,2,2-trifluoroethoxy)methyl-4-methylsulfonylbenzoyl chloride and then adds 237.9 g of thionyl chloride, while p03 describes the preparation as the correspondin
- **[p10.png]** FIRST READING WITHDRAWN / SECOND READING ADOPTED. First reading: the 1H NMR list at [0054] and [0055] appeared inconsistent with the product as named, because its peaks sum to 16 protons, only two aromatic doublets are printed, and it carries a 2H quartet at 4.01 and a 2H singlet at 5.21. That reading rested entirely on taking the product name to mean sulcotrione (C14H13ClO5S, MW 328.77, 13 hydrogens, three aromatic protons, no OCH2CF3), which is the wrong compound: sulcotrione is a different herbicide with a different Chinese name. Second reading: the product is tembotrione, C17H16ClF3O6S, which has exactly 16 hydrogens, and every feature called impossible under the first reading is a feature tembotrione has - 4.01 (q, 2H) the OCH2CF3 methylene with its three-bond H-F coupling, 5.21 (s, 2H) the benzylic ArCH2O methylene, and only two aromatic protons because the ring already bears Cl, SO2CH3 and CH2OCH2CF3. The pattern identified in the first reading as 'a trifluoroethoxymethyl analogue' is the compound this patent is about. Outcome: the peak list IS consistent with the named product and there is no discrepancy here. Entry kept, not deleted, so the misreading and its correction stay on the record.
  - drawing: No drawing on this page, and no structural formula anywhere on p10, so p10 alone cannot fix the identity of the product. The identifiers that do fix it are printed on p03, which this pass could not see: [0003] 
  - text: The prose names the target product by its Chinese common name, in the yield line of [0053] and again in [0054], and gives 1H NMR (CDCl3): 2.12 (m, 2H), 2.47 (t, 2H), 2.81 (t, 2H), 3.25 (S, 3H), 4.01 (q, 2H), 5.
- **[p10.png]** The pH of the acid adjustment is printed with capital letters as PH in the tail of [0053] on this page, while the claims print it lower case as pH.
  - drawing: No drawing on this page.
  - text: The [0053] tail reads 'adjust the PH to 2' with capital P capital H, in the clause about dropwise addition of 10% aqueous hydrochloric acid under temperature control.
