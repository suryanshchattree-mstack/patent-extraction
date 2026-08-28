# A5 adversarial audit of WO2000021924A1

Four independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 520 | 0 | 20 | 15 | 12 |
| `patent` | 1 | 1 | 4 | 7 | 8 |
| `pathways` | 10 | 0 | 4 | 5 | 16 |
| `reactions` | 21 | 0 | 6 | 10 | 19 |
| **total** | | **1** | **34** | **37** | **55** |

## Acted on

- **The summary puts Y and Z in the 3-position side chain** - FIXED. A4 rewrote patent_summary. Y and Z are ring members of the cyclohexanedione ring and the 3-position substituent is only -L-R1. The replacement takes the genus definition from claim 1 at lines 933 to 936 rather than from line 334, which is claim 7 narrowing Y and Z to CHR7 or C(R7)2 and is not the genus.
- **R7 is swept into the R2 to R5 definition** - FIXED in the same rewrite. The summary no longer attributes the R2 to R5 list to R6 or R7; both are described as drawn from their own lists.
- **The summary says R6 additionally covers OR12** - FIXED in the same rewrite, for the same reason.
- **The abstract is not verbatim** - FIXED at the input, not the artifact. The umlauts were folded to ASCII when the biblio was hand-authored; abstract_zh is now the (57) Zusammenfassung copied verbatim from line 36, umlauts and eszett intact.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical


### major

1. **[compounds]** `recall` on `None`
   Table 2 enumerates 360 fully specified compounds Nr. 30 to Nr. 389 (caption on line 675 fixes R2, R3, R4, R5, R6, Y, Z, v, w; each row gives R7a, R7b, R12, L and R1) and the artifact carries not one of them, only a single generic header record for the whole table.
   > line 677: 30 | H | H | Bz | CH2 | O-c-Hexyl
   fix: add 360 records for Nr. 30 to Nr. 389 in the same local_label form used for Tabelle 1, Nr. 3 to Nr. 15
2. **[compounds]** `recall` on `None`
   Table 1 rows Nr. 16 to Nr. 29 are absent from the artifact although rows Nr. 3 to Nr. 15 of the same table were extracted; the only difference is that rows 16 to 29 print no Physikalische Daten.
   > line 642: 16 | OCH2CF2CF3 | H | 17 | OCH2CF2CF3 | Me |
   fix: add records 'Tabelle 1, Nr. 16' through 'Tabelle 1, Nr. 29'
3. **[compounds]** `recall` on `None`
   Table 3 rows Nr. 394 to Nr. 400 are absent although rows Nr. 390 to Nr. 393 of the same table were extracted; the difference is only the empty Physikalische Daten cell.
   > line 753: 394 | CH2 | OCH2CH2Br | 395 | CH2 | OCH2CH2F |
   fix: add records for Nr. 394 to Nr. 400
4. **[compounds]** `recall` on `None`
   Table 4 rows Nr. 436 to Nr. 451 are absent; the artifact's only Table 4 record is the generic formula (I) header.
   > line 786: 436 | OCH2CF3 | Me | SO2Me 437 | OCH2CF3 | Me | SO2Et
   fix: add 16 records for Nr. 436 to Nr. 451
5. **[compounds]** `recall` on `None`
   Table 5 rows Nr. 518 to Nr. 530 are absent although Nr. 517 of the same table was extracted.
   > line 830: 518 | OCH2CF3 | Me, Me | 519 | OCH2CF2H | Me, Me |
   fix: add records for Nr. 518 to Nr. 530
6. **[compounds]** `fidelity` on `hydrogen peroxide`
   The oxidant charge of Example 1 Schritt 3 is printed as 203.83 g and the merged record carries no quantity; the record's own notes still refer to 'The 203.83 g', a number that now appears in no field.
   > line 563: 203.83 g einer 30 %igen Wasserstoffperoxidlösung
   fix: set mass_g to 203.83
7. **[compounds]** `fidelity` on `oxalyl chloride`
   Oxalyl chloride is charged with mass and mmol twice in the experimental part and the merged record carries no quantity, because the quantity-free mention in Schema 4 overwrote it.
   > line 578: 0.59 g (4.58 mmol) Oxalylchlorid
   fix: set mass_g 0.59 and mmol 4.58 (Example 1) and note the second charge of 0.76 g / 5.9 mmol on line 606
8. **[compounds]** `fidelity` on `methyl 3-bromomethyl-2-chloro-4-methylsulfonyl-benzoate`
   This compound is the isolated product of Example 1 Schritt 6 with a stated 67 % of theory and the record carries no yield.
   > line 574: Ausbeute: 38.82 g (67 % der Theorie), farblose Kristalle, Fp.: 74-75 °C
   fix: set yield_pct to 67.0
9. **[compounds]** `fidelity` on `methyl 3-bromomethyl-2-chloro-4-methylsulfonyl-benzoate`
   mass_g holds 1.0, the amount charged into Example 2 Schritt 1, while the record's melting point, NMR and appearance all come from the Example 1 Schritt 6 isolation of 38.82 g; the isolated mass is lost and the record mixes two steps' numbers.
   > line 574: Ausbeute: 38.82 g (67 % der Theorie), farblose Kristalle, Fp.: 74-75 °C
   fix: set mass_g to 38.82 with role 'product' and record the 1.0 g / 2.93 mmol charge separately
10. **[compounds]** `fidelity` on `hydrochloric acid`
   The concentrated hydrochloric acid charge of Example 1 Schritt 2 is printed as 300 ml and the merged record carries no volume.
   > line 556: 300 ml konz. Salzsäure
   fix: set volume_ml to 300.0
11. **[compounds]** `arithmetic` on `2-chloro-3-methyl-4-methylthio-acetophenone`
   Step to step continuity breaks: Schritt 2 isolates 111.24 g of this compound and Schritt 3 charges 223.48 g (1.04 mol) of it, twice what the preceding step produced; the artifact carries only the 111.24 g, has no field in which the 223.48 g can appear, and the CompoundRecord schema has no validation_flag, so the break is invisible to every structured consumer.
   > line 563: 223.48 g (1.04 mol) 2-Chlor-3-methyl-4-methylthio-acetophenon
   fix: carry the 223.48 g / 1.04 mol charge in a structured field and flag the mass balance break rather than leaving it in notes only
12. **[compounds]** `precision` on `2-[2-chloro-3-(2,2-difluoroethoxymethyl)-4-ethylsulfonyl-ben`
   The identifier is a full IUPAC name that appears nowhere in the patent; it was assembled from the Tabelle 3 caption plus the row substituents, and it is carried with identifier_type 'iupac' and resolved true, while the equivalent rows of Tables 1, 1a, 1b and 5 are carried as local_label with resolved false. Only the notes disclose the construction, so a scored extractor is measured against an invented string for these four records and against a label for the other twenty two.
   > line 753: 390 | CH2 | OCH2CHF2 |
   fix: use the local_label form 'Tabelle 3, Nr. 390' with resolved false and keep the constructed name in aliases
13. **[compounds]** `precision` on `2-[2-chloro-4-ethylsulfonyl-3-(2,2,2-trifluoroethoxymethyl)-`
   The identifier is a full IUPAC name that appears nowhere in the patent; it was assembled from the Tabelle 3 caption plus the row substituents, and it is carried with identifier_type 'iupac' and resolved true, while the equivalent rows of Tables 1, 1a, 1b and 5 are carried as local_label with resolved false. Only the notes disclose the construction, so a scored extractor is measured against an invented string for these four records and against a label for the other twenty two.
   > line 753: 390 | CH2 | OCH2CHF2 |
   fix: use the local_label form 'Tabelle 3, Nr. 391' with resolved false and keep the constructed name in aliases
14. **[compounds]** `precision` on `2-[2-chloro-3-(2-chloroethoxymethyl)-4-ethylsulfonyl-benzoyl`
   The identifier is a full IUPAC name that appears nowhere in the patent; it was assembled from the Tabelle 3 caption plus the row substituents, and it is carried with identifier_type 'iupac' and resolved true, while the equivalent rows of Tables 1, 1a, 1b and 5 are carried as local_label with resolved false. Only the notes disclose the construction, so a scored extractor is measured against an invented string for these four records and against a label for the other twenty two.
   > line 753: 390 | CH2 | OCH2CHF2 |
   fix: use the local_label form 'Tabelle 3, Nr. 392' with resolved false and keep the constructed name in aliases
15. **[compounds]** `precision` on `2-[2-chloro-4-ethylsulfonyl-3-(2,2,2-trifluoroethylthiomethy`
   The identifier is a full IUPAC name that appears nowhere in the patent; it was assembled from the Tabelle 3 caption plus the row substituents, and it is carried with identifier_type 'iupac' and resolved true, while the equivalent rows of Tables 1, 1a, 1b and 5 are carried as local_label with resolved false. Only the notes disclose the construction, so a scored extractor is measured against an invented string for these four records and against a label for the other twenty two.
   > line 753: 390 | CH2 | OCH2CHF2 |
   fix: use the local_label form 'Tabelle 3, Nr. 393' with resolved false and keep the constructed name in aliases
16. **[compounds]** `drawings` on `Tabelle 1, Nr. 5`
   The IMAGE_EXTRACT span that machine reads this row's drawn R1 cell carries the SMILES *OCC1CCCCO1, and page image p050 confirms the drawing is O-CH2 bonded to the 2-position of an oxane ring, but the SMILES is in no record's aliases; A1 rule 4b requires it there. No SMILES from any of the six populated spans in this document reaches any record.
   > line 635: [IMAGE_EXTRACT: {"molecules": [{"smiles": "*OCC1CCCCO1", "molecular_formula": "C6H11*O2", "inchi_key": ""}]}]
   fix: add '*OCC1CCCCO1' to aliases
17. **[compounds]** `drawings` on `Tabelle 1, Nr. 13`
   The row's alias points at 'drawings[0]', but the only IMAGE_EXTRACT span on that page returns an empty molecules array, so no structure was read. Page image p051 shows the cell drawn as O-CH2 bonded to the 2-position of a tetrahydrofuran ring, and the record carries that structure in no field. This is a guard passing on absence: an empty molecules array was accepted as if the page held no drawing.
   > line 640: [IMAGE_EXTRACT: {"molecules": []}]
   fix: record R1 as (tetrahydrofuran-2-yl)methoxy, read off page image p051, and note that the vision pass returned nothing for it
18. **[compounds]** `drawings` on `None`
   Page image p069 (printed page 67) is a full Table 3 page carrying rows Nr. 401 to Nr. 422, four of which (412, 413, 421, 422) have drawn R1 cells. The enriched markdown for that page holds four IMAGE_EXTRACT spans with empty molecules arrays and no row text at all, so 22 compounds and their four drawn substituents are absent from the source text and therefore from the artifact.
   > line 758: [IMAGE_EXTRACT: {"molecules": []}]
   fix: re-read page p069 so the row text and the four drawn R1 groups enter the source, then extract the 22 compounds
19. **[compounds]** `drawings` on `None`
   Page image p072 (printed page 70) is a full Table 4 page carrying rows Nr. 452 to Nr. 475, four of which have drawn R1 cells. The markdown for that page holds only the four structure spans and no row text, so 24 compounds are absent from the source and from the artifact. The four SMILES that were read, *OCC1CCCO1, match the drawing as (tetrahydrofuran-2-yl)methoxy.
   > line 793: [IMAGE_EXTRACT: {"molecules": [{"smiles": "*OCC1CCCO1", "molecular_formula": "C5H9*O2", "inchi_key": ""}]}]
   fix: re-read page p072 so the row text enters the source, then extract the 24 compounds
20. **[compounds]** `drawings` on `None`
   Page image p076 (printed page 74) is a Table 5 page carrying rows Nr. 531 to Nr. 544, one of which (538) has a drawn R1 cell. The markdown for that page holds only the one structure span and no row text, so 14 compounds are absent from the source and from the artifact.
   > line 837: [IMAGE_EXTRACT: {"molecules": [{"smiles": "OCC1CCOC1", "molecular_formula": "C5H10O2", "inchi_key": "PCPUMGYALMOCHF-UHFFFAOYSA-N"}]}]
   fix: re-read page p076 so the row text enters the source, then extract the 14 compounds
21. **[patent]** `drawings` on `None`
   The IMAGE_EXTRACT spans covering the three drawings of formula (I) (p001, p004, p081) encode no molecule at all, so nothing in the enriched markdown records the structure the patent_summary describes and the Y and Z placement could only have been inferred.
   > line 67: [IMAGE_EXTRACT: {"molecules": []}]
   fix: the vision pass must encode formula (I) as drawn on p004: a 2-aroyl-1,3-dione ring bearing R6, (CH2)v, Z, Y and (R7)w, joined by a carbonyl to a benzene ring carrying R2, L-R1, R3, R4 and R5 at positi
22. **[pathways]** `recall` on `None`
   The base salt formation of the compounds of formula (I) is described as a transformation of the invention and no pathway (and no step in any pathway) carries it.
   > line 113: Je nach Art der Substituenten enthalten die Verbindungen der allgemeinen Formel (I) ein acides Proton, das durch Umsetzung mit einer Base entfernt werden kann. 
   fix: One further section pathway, ksm 'compound of formula (I)', product its base salt, one step of reaction_class salt_formation with the named base classes as reagents. The section 'Preparation Schemes 1
23. **[pathways]** `drawings` on `None`
   The IMAGE_EXTRACT span on line 105 types the drawing on page image p006 as ten reactions, but p006 draws a four corner tautomeric equilibrium (four structures joined by double headed equilibrium arrows, including a diagonal cross), which is not ten reactions and is not a synthesis at all; all four drawn structures were also missed.
   > line 105: [IMAGE_EXTRACT: {"reactions": [{"step_id": 1, "reactants": [], "conditions": [], "products": []}, {"step_id": 2, "reactants": [], "conditions": [], "products": 
   fix: The span should be typed as a tautomer equilibrium and not as ten reactions, so that a re-run cannot mistake ten arrowheads for ten synthetic steps. Verified by opening input/pages/p006.png; the text 
24. **[pathways]** `precision` on `22726d0a-f4d4-540b-9600-bdd956a1522d`
   This pathway's ksm and product are the same CompoundRef, identifier 'compound of formula (III)' with compound_uuid a57e897c-e575-5cfd-a172-4f74dbb71ea0 on both sides, so the record asserts a compound is made from itself; the source distinguishes the two sides by the meaning of R and the pathway carries no honest_uncertainty_flag saying the identity is a labelling artifact.
   > line 355: Verbindungen oben genannter Formel (III) können gemäß bekannten Methoden aus Verbindungen der Formel (III), in der R für Hydroxy oder Alkoxy steht, hergestellt 
   fix: Minimal correction: add an honest_uncertainty_flag such as 'ksm_equals_product_labelling_artifact' to this record. The step's own notes field already states 'that identity is a labelling artifact and 
25. **[pathways]** `precision` on `a4aeb75a-0b1e-5200-aae1-39ba56ae6c8c`
   The terminal product 'compound of formula (Ic)' is the same CompoundRef, compound_uuid e7a177dc-e48d-5dd8-a650-7deb6aad8918, as intermediates[1], so the three step chain ends on a compound it already listed as a mid chain intermediate; the source separates the two by the meaning of R6 and the pathway carries no flag for the collapse.
   > line 381: zu weiteren erfindungsgemäßen Verbindungen der Formel (Ic), in der R6 für Alkylthio, Halogenalkylthio, Alkenylthio, Halogenalkenylthio, Alkinylthio, Halogenalki
   fix: Minimal correction: add an honest_uncertainty_flag such as 'ksm_equals_product_labelling_artifact' (or 'product_equals_intermediate_labelling_artifact') to this record. Step 8 makes (Ic) with R6 alkyl
26. **[reactions]** `precision` on `Example 1_Step 1`
   The notes carry computed molecular formulae and molecular weights that appear nowhere in the source, which A2 rule 32 forbids (notes must introduce no number absent from the text) and which A5 check 2 lists among the things this annotation is not permitted to contain.
   > line 548: Man ließ abkühlen, fügte 88.2 g (0.5 mol) Jodmethan hinzu und ließ 0,5 h bei Raumtemperatur nachrühren.
   fix: Strip the derived molecular weights and molecular formulae from notes and leave them only in reactions-provenance.json arithmetic_check, which is where A2 says they live. The same defect is present in
27. **[reactions]** `drawings` on `Preparation Schemes 1 to 4_Step 7`
   Page p033 draws Schema 4 as Ia to Ib to Ic with two completely bare arrows carrying no reagent text, while the prose names Oxalylchlorid and Oxalylbromid, so reagent_written_not_drawn applies and is not raised.
   > line 376: Die  in Schema 4 angegebene Umsetzung einer Verbindung der Formel (Ia) mit einem Halogenierungsreagenz, wie Oxalylchlorid oder Oxalylbromid, führt zu erfindungs
   fix: Add "reagent_written_not_drawn" to validation_flags. The drawing does exist on page p033; only the vision read of it is empty, and declining the flag on the ground that no comparison was possible turn
28. **[reactions]** `drawings` on `Preparation Schemes 1 to 4_Step 1`
   Page p030 draws Schema 1 as (II) plus (III) over a bare arrow to (I), with nothing written above or below the arrow, while the prose names DCC and a cyanide source as reagents of two of the three variants, so reagent_written_not_drawn applies and is not raised.
   > line 344: Dazu wird die Verbindung der Formel (II) im Fall von R = Hydroxy in Gegenwart wasserentziehender Mittel, wie DCC, oder im Fall von R = Chlor oder Brom basenkata
   fix: Add "reagent_written_not_drawn" to validation_flags for this record.
29. **[reactions]** `drawings` on `None`
   The vision read of every scheme drawing in this document is empty, so nine records rest on prose alone and no drawing check anywhere in the artifact could be performed; the pages themselves carry complete structures.
   > line 351: [IMAGE_EXTRACT: {"reactions": [{"step_id": 1, "reactants": [], "conditions": [], "products": []}]}]
   fix: Re-run the vision pass over pages p030, p031 and p033 and populate the spans. Page p030 draws (II) plus (III) to (I) for Schema 1 and (IV) to (III) for Schema 2; page p031 draws (V) to (III) for Schem
30. **[reactions]** `recall` on `None`
   The five formulation examples on pages p077 and p078 state quantified compositions and named unit operations and carry no record, although reaction_class has a formulation value and the schema carries a non_synthetic flag for exactly this case.
   > line 848: Ein Stäubemittel wird erhalten, indem man 10 Gew.-Teile einer Verbindung der allgemeinen Formel (I) und 90 Gew.-Teile Talkum als Inertstoff mischt und in einer 
   fix: Emit one record per formulation example (lines 848, 852, 856, 860 and 864 to 871) with reaction_class formulation, non_synthetic true and scale not_specified, or state on the record set that formulati
31. **[reactions]** `recall` on `None`
   The four biological examples on pages p078 to p080 state dosed application procedures with rates and assessment intervals and carry no record, although reaction_class has a biological_assay value.
   > line 877: Die in Form von benetzbaren Pulvern oder Emulsionskonzentraten formulierten erfindungsgemäßen Verbindungen werden dann als wäßrige Suspension bzw. Emulsion mit 
   fix: Emit one record per biological example (lines 877, 884, 888 and 897) with reaction_class biological_assay and non_synthetic true, or state that assays are deliberately out of scope for this artifact. 

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 930 | 520 | 6 |
| `patent` | 20 | 14 | 6 |
| `pathways` | 22 | 21 | 1 |
| `reactions` | 31 | 21 | 10 |
