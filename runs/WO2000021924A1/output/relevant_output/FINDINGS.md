# What is wrong with WO2000021924A1

Produced by annotating the patent by hand, against the scanned pages rather than
against anyone's OCR. Every item below is a defect in the **patent**, not in the
annotation. The annotation records them and changes nothing.

- 21 reactions extracted, of which 13 carry at least one flag
- 520 unique compounds, 10 pathways
- 30 discrepancies raised by the page-vision pass

## Flags raised, by kind

| flag | count | what it means |
|---|---:|---|
| `no_conditions` | 9 | no reaction conditions stated at all |
| `cross_reference_unresolved` | 9 |  |
| `molar_mass_inconsistent` | 3 | a stated mass/mole pair implies a molecular weight that is not the named compound's |
| `scale_discontinuity` | 1 | a step charges more material than the previous step produced |
| `a1_missing_compound` | 1 |  |

## The headline findings

No hand-written analysis exists for WO2000021924A1. The generated sections above and below are complete; this section is not, and is omitted rather than filled with another patent's findings.

## Everything the page-vision pass raised

- **[p001.png]** The printed English abstract calls the compounds benzocyclohexandiones, but the drawn formula (I) shows an aroyl group joining the two rings, which is a benzoylcyclohexanedione, and both title fields and the German abstract say Benzoyl.
  - drawing: formula (I) draws a substituted benzene ring joined by a C=O bridge to a cyclohexane-1,3-dione type ring, that is a benzoylcyclohexanedione
  - text: (57) Abstract, English: 'The invention relates to benzocyclohexandiones of general formula (I)'. Against that, (54) Title: 'BENZOYLCYCLOHEXANDIONES', (54) Bezeichnung: 'BENZOYLCYCLOHEXANDIONE', and (57) Zusamme
- **[p001.png]** The abstracts state that Y and Z are a monoatomic bridging element, and the drawing is consistent with this: Y and Z are each drawn as a single labelled ring position. Recorded as an agreement, not a conflict, so that the check is on record.
  - drawing: Y and Z each occupy one ring vertex of the left ring, with the bracket ( )v carrying the variable CH2 count
  - text: 'Y und Z für ein einatomiges Brückenelement' / 'Y and Z are a monoatomic bridging element'
- **[p003.png]** No structural formula, scheme or table is drawn anywhere on this page, so no drawing-versus-prose cross-check is possible here. Every chemical entity on the page is given by class name or by citation only.
  - drawing: no drawing present on p03
  - text: chemical matter named in prose only: Benzoylcyclohexandione, Phenylring 3-Position, substituierter Phenoxymethylrest, Brücke containing Sauerstoff/Schwefel/Stickstoff, Kohlenstoffkette, heterocyclischer Rest
- **[p003.png]** Rule 11 (invention route versus prior art): the chemistry described on this page is entirely prior art. The paragraph beginning "Aus verschiedenen Schriften ist bereits bekannt" and the paragraph beginning "Die Anwendung" both discuss the cited JP-A and WO documents; the only statement about the invention is the object stated in the final paragraph. Nothing on this page describes the invention's own compounds or route.
  - drawing: no drawing present on p03
  - text: "Aus verschiedenen Schriften ist bereits bekannt ..."; "Aufgabe der vorliegenden Erfindung ist die Bereitstellung von ... Verbindungen, die die aus dem Stand der Technik bekannten Nachteile überwinden."
- **[p003.png]** The header carries no centred printed page number, although the run convention expects one (printed page number = PDF page number minus two, so this would be printed page 1). The header is only the two flanking identifiers, and there is no footer at all. Recorded as printed rather than reconstructed.
  - drawing: n/a, header/footer observation
  - text: header reads "WO 00/21924" at the left margin and "PCT/EP99/06627" at the right margin, with blank space between; the foot of the page is empty
- **[p004.png]** The prose names the compounds 'Benzoylcyclohexandione', which specifies a six-membered all-carbon 1,3-dione ring, but the drawn left ring is generic and is not restricted to that.
  - drawing: Left ring drawn with a repeat bracket '( )v' on one vertex, so the ring size is variable, and with two labelled ring-atom placeholders Y and Z, so ring members may be heteroatoms. Neither v nor Y nor Z is defin
  - text: 'speziell substituierte Benzoylcyclohexandione der allgemeinen Formel (I)' - benzoylcyclohexanediones, i.e. a carbocyclic six-membered ring. Not resolved here; must be checked against the definitions of Y, Z, v
- **[p004.png]** The prose says 'dione' but only one ring C=O is drawn.
  - drawing: One exocyclic C=O on the left ring's lower-right vertex, plus a ring C=C between the R6-bearing top vertex and the vertex carrying the aroyl bridge. R6 is defined on this page as OR12, alkylthio, alkylsulfonyl 
  - text: 'Benzoylcyclohexandione' implies two ring ketones. Recorded, not resolved: this is very likely the standard enol/enol-ether depiction of a 2-aroyl-1,3-dione, but that reading is chemical inference and is delibe
- **[p006.png]** The prose fixes R6 as hydroxy for this drawing, but no R6 label appears anywhere in the four drawn tautomers; the hydroxy is drawn out as an explicit OH (or as the corresponding C=O in the keto forms) instead.
  - drawing: Four structures labelled only with L, R1, R2, R3, R4, R5, (R7)w, Y, Z, v, w and explicit O / OH atoms. No R6 anywhere.
  - text: 'Für den Fall, daß R6 für Hydroxy steht, sind folgende tautomeren Strukturen möglich:'
- **[p006.png]** The four structures drawn are said in the caption to be the tautomers 'possible' for R6 = hydroxy, but the top-left structure as drawn carries no hydroxy group at all: it is the fully keto triketone form. Recording the discrepancy rather than deciding which reading is intended.
  - drawing: Top-left structure has three C=O groups (two ring, one exocyclic aroyl) and a CH at ring C2; no OH.
  - text: The set is introduced as the tautomeric structures for the case that R6 stands for hydroxy.
- **[p010.png]** Text-vs-text. The final sentence lists benzo-fused 6-membered heteroaryl EXAMPLES as parent ring names rather than as attached yl radicals, unlike every other example on the page, so the attachment position of those four is not stated.
  - drawing: n/a - there is no drawing on this page
  - text: 'Beispiele fuer benzokondensierte 6-gliedriges Heteroaryl sind Chinolin, Isochinolin, Chinazolin und Chinoxalin.' All the other examples in the same paragraph carry an explicit locant and yl suffix (2-Pyridinyl
- **[p010.png]** Grammatical inconsistency in the printed German, recorded as printed and not corrected.
  - drawing: n/a - there is no drawing on this page
  - text: 'benzokondensierte 6-gliedriges Heteroaryl' mixes a plural or weak-declension adjective with a neuter singular noun phrase; the parallel earlier phrase reads 'anneliertes 5-gliedriges Heteroaryl'. Transcribed v
- **[p010.png]** Typography that downstream passes must not read as meaningful.
  - drawing: n/a - there is no drawing on this page
  - text: Two different quotation-mark styles appear on one page: raised curled marks around 'partiell oder vollstaendig halogeniert' in the second paragraph, and straight ASCII-style double quotes around Y and Z in the 
- **[p030.png]** Formula (III) is drawn twice on this page and the two drawings label the benzene ring differently, so the same formula number carries two different substituent sets.
  - drawing: Schema 1, structure (III): going round the ring from the acyl carbon C1 in the direction of R2, the labels are R2 at C2, L-R1 at C3, R3 at C4, R4 at C5, R5 at C6.
  - text: Schema 2, structure (III) (and the (IV) it comes from): the same traversal gives R2 at C2, L-R1 at C3 (L-Hal in (IV)), R4 at C4, R5 at C5, R6 at C6. R3 appears in the first drawing and not the second; R6 appear
- **[p030.png]** R6 appears on the product of Schema 1 but on nothing in its starting materials, and the scheme shows no reagent that could introduce it.
  - drawing: Structure (I) carries R6 bonded directly to the upper-left ring carbon. Structure (II), the ring that becomes it, carries a C=O at that position and no R6 anywhere. The arrow between them is bare.
  - text: The prose on this page says nothing about R6. It discusses only where the starting materials (II) and (III) come from.
- **[p030.png]** The prose paragraph on the preparation of (III) names formula (III) as both product and starting material.
  - drawing: Schema 1 draws (III) as a single structure with a single bare R on its acyl group; nothing on the page draws two distinct members of formula (III).
  - text: 'Verbindungen oben genannter Formel (III) können gemäß bekannten Methoden aus Verbindungen der Formel (III), in der R für Hydroxy oder Alkoxy steht, hergestellt werden.' Whether the first (III) is a misprint fo
- **[p031.png]** The prose calls the Scheme 3 reaction base-catalysed, but no base and no conditions of any kind are written on the arrow.
  - drawing: The arrow carries only 'R1-Z2' above it and nothing below it.
  - text: 'basenkatalysierte Umsetzung einer  Verbindung der Formel (V) ... mit ... Verbindungen der Formel R1-Z2' (base-catalysed reaction of a compound of the formula (V) with compounds of the formula R1-Z2).
- **[p031.png]** The prose restricts Z1 to five specific meanings, and the drawing shows Z1 only as an unlabelled variable on L.
  - drawing: L-Z1 at C3 of the starting material, with Z1 left as a bare symbol.
  - text: 'in der Z1 für OH, SH, NH-Alkyl, NH-Aryl oder NH-Heteroaryl steht' (in which Z1 is OH, SH, NH-alkyl, NH-aryl or NH-heteroaryl).
- **[p031.png]** The ring is labelled R2, R4, R5, R6 with no R3, and the acyl substituent is a plain unnumbered R; this differs from the aryl labelling of formula (I) used elsewhere in the patent. The text on this page does not name the ring substituents, so nothing on this page resolves it.
  - drawing: Going round the ring from the acyl vertex towards R2: acyl (plain R on the carbonyl), R2, L, R4, R5, R6.
  - text: Nothing. The three prose paragraphs on this page mention only R1, Z1 and Z2 and never the ring substituents.
- **[p033.png]** The scheme and the prose on this page describe different things, so no cross-check between them is possible on this page alone.
  - drawing: Ia converts to Ib, and Ib converts to Ic, with no reagents or conditions written on either arrow.
  - text: The only prose on the page is about the herbicidal activity of the formula (I) compounds against mono- and dicotyledonous weeds. It says nothing about Schema 4 or about any of Ia, Ib and Ic. Any text describing
- **[p050.png]** The scaffold draws two separate substituents on one ring carbon and labels both R7, while the table offers only a single R7 column with one value per row.
  - drawing: two plain bonds from the same left-ring carbon, one going left and one going down, each labelled R7
  - text: a single column headed R7, giving H for each of rows 3 to 8
- **[p050.png]** The caption fixes Y, Z, v and w, but none of those four symbols appears anywhere on the drawn scaffold.
  - drawing: the left ring is drawn out explicitly as a six-membered carbocycle with no Y, Z, v or w labels on it
  - text: Y = CH2, Z = CH2, v = 1, w = 2
- **[p053.png]** The table has an R7 column, filled with H in all four rows, but no R7 label appears anywhere on the drawn scaffold above it.
  - drawing: The benzene ring carries COOH, Cl, CH2R1 and SO2CH3 on four consecutive carbons and two unlabelled plain ring vertices; there is no R7 label and no bond drawn to any R7.
  - text: The table header row reads Nr. | R1 | R7 | Physikalische Daten, and rows 3b, 4b, 5b and 9b each carry H in the R7 column.
- **[p054.png]** The caption block defines Z = CH2, but one carbon of the drawn left ring carries two substituents R7a and R7b rather than two hydrogens.
  - drawing: the lower-left vertex of the six-membered left ring bears R7a as a bold wedge to the left and R7b as a plain line downward, so that carbon has no drawn hydrogens
  - text: Z = CH2, with w = 2, in the caption block directly above the drawing
- **[p068.png]** The fixed substituent block defines nine symbols, but only R2, R3 and R6 can be matched to a label or a drawn group on the scaffold; R4, R5, Y, Z, v and w appear nowhere on the drawing.
  - drawing: The benzene ring carries Cl and SO2Et as drawn text, the cyclohexenone carries a drawn OH, and the remaining ring vertices are plain unlabelled vertices with no R4, R5, Y, Z, v or w label anywhere on the page.
  - text: R2 = Cl, R3 = SO2Et, R4 = H, R5 = H, R6 = OH, Y = CH2, Z = CH2, v = 1, w = 0.
- **[p068.png]** Row 392 gives a two proton integral for an aromatic doublet where the other four data rows give a one proton doublet at the same position.
  - drawing: The scaffold has exactly two unlabelled benzene CH vertices, so the aromatic region can carry at most two aromatic protons in total, which rows 390, 391 and 393 report as two separate one proton doublets.
  - text: Row 392: '... 7.32 (d,2H), 8.1 (d,1H), 16.7 (s,1H)'.
- **[p075.png]** The drawn scaffold carries a methylsulfonyl group where the fixed substituent block above it defines an ethylsulfonyl group.
  - drawing: SO2Me, drawn as a bond from the benzene ring at the position para to the ketone bridge and ortho to the CH2-R1 arm, labelled SO2Me.
  - text: R3  =  SO2Et in the fixed substituent block printed directly above the drawing.
- **[p075.png]** The only physical data on the page, the 1H NMR of Nr. 517, contains a three proton singlet and no ethyl pattern in the region where the fixed substituent block's SO2Et would put a triplet and a quartet.
  - drawing: SO2Me on the benzene ring, a group that accounts for a single three proton singlet.
  - text: R3  =  SO2Et in the fixed substituent block, and the row 517 data cell '3.3 (s,3H)' with no triplet near 1.3 and no quartet near 3.9 anywhere in the list.
- **[p075.png]** The fixed substituent block defines nine symbols, but only R2, R3 and R6 can be matched to a label or a drawn group on the scaffold; R4, R5, Y, Z, v and w appear nowhere on the drawing.
  - drawing: The benzene ring carries Cl and SO2Me as drawn text, the cyclohexenone carries a drawn OH, the linker to R1 is an unlabelled CH2 apex, and the remaining ring vertices are plain unlabelled vertices with no R4, R
  - text: R2 = Cl, R3 = SO2Et, R4 = H, R5 = H, R6 = OH, Y = CH2, Z = CH2, v = 1, w = 0.
- **[p075.png]** Compound numbers 518 and 523 are printed with identical values in every column the table records.
  - drawing: The scaffold is the same single drawing for every row, so nothing outside the R1 and R7a/R7b columns can distinguish the two rows.
  - text: Row 518: 'OCH2CF3 | Me, Me'. Row 523: 'OCH2CF3 | Me, Me'.
- **[p106.png]** The heading line and the body paragraph give different claim ranges for the same objection.
  - drawing: no drawing on this page; the heading line reads 'Claims Nos. 1-13 in part'
  - text: the paragraph immediately below reads 'Claims Nos. 1-12  relate to a disproportionately large number of possible compounds'
