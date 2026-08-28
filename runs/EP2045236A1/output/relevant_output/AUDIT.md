# A5 adversarial audit of EP2045236A1

Four independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 413 | 0 | 4 | 12 | 19 |
| `patent` | 1 | 2 | 5 | 10 | 14 |
| `pathways` | 6 | 3 | 2 | 4 | 16 |
| `reactions` | 7 | 0 | 2 | 6 | 25 |
| **total** | | **5** | **13** | **32** | **74** |

## Acted on

Nothing recorded for EP2045236A1. Every finding below is outstanding.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical

1. **[patent]** `precision` on `EP2045236A1`
   The summary asserts that the only preparative operations in the document are conversions of the metastable forms into the stable one, but two of the three worked examples prepare the metastable forms II and III and convert nothing.
   > line 670: Herstellung der metastabilen Kristallmodifikation III
   fix: Drop the word only, or say that the document also gives two preparations of the metastable forms themselves ([0056] from ethanol at line 668, [0057] from toluene at line 672, both under headings that 
2. **[patent]** `precision` on `EP2045236A1`
   The claim that the 2 g charged in the three examples is the only quantity in the document is false; the description and the claims carry many quantities, including ones the same field quotes two sentences earlier.
   > line 644: [0050] Die angewandte Wirkstoffmenge kann in einem größeren Bereich schwanken. Sie hängt im wesentlichen von der Art des gewünschten Effektes ab. Im allgemeinen
   fix: Narrow the claim to what is actually true: no product mass, yield or assay of purity is reported for any preparation. Delete the assertion that the 2 g is the only quantity in the document; applicatio
3. **[pathways]** `precision` on `scope=section, section_label=Preparation - General Process, `
   The key starting material is recorded as bare tembotrione, which is not a reactant of the step the pathway cites; the step consumes crystal modifications II and III.
   > line 578: dass man die nach WO 00/21924 erhältliche Kristallmodifikation II und III von Tembotrione beziehungsweise Gemische davon in einem geeigneten Lösungsmitteln susp
   fix: ksm.identifier = "tembotrione crystal modification II" (the first-listed reactant of the earliest step, per A3 rule 3), keeping the existing recited_inputs_are_alternatives_not_a_single_ksm flag to ca
4. **[pathways]** `precision` on `scope=section, section_label=Preparation - General Process, `
   Same defect on the grinding route: the ksm is recorded as tembotrione while the step's only reactants are crystal modifications II and III.
   > line 588: Die stabile Kristallmodifikation I kann auch durch Mahlen unter hohem Druck aus den Kristallmodifikationen II und III beziehungsweise Gemischen davon erhalten w
   fix: ksm.identifier = "tembotrione crystal modification II".
5. **[pathways]** `precision` on `scope=patent, section_label=null, steps=[Preparation - Gener`
   The patent-scope pathway asserts the route tembotrione to crystal modification I, which the patent never discloses; the disclosed and claimed process starts from a metastable modification, not from tembotrione at large.
   > line 802: a) eine metastabile Kristallmodifikation oder ein Gemisch der metastabilen Kristallmodifikationen von Tembotrione in Lösungsmitteln suspendiert und/oder löst un
   fix: ksm.identifier = "tembotrione crystal modification II". As written, finalise.py will bind compound_uuid to the bulk tembotrione record and the one distinction the whole patent turns on is lost silentl

### major

1. **[compounds]** `recall` on `None`
   The Formulation Types section names Tembotrione but emits no tembotrione record, although fourteen other sections emit one on exactly this construction.
   > line 615: [0037] Die erfindungsgemäße Kristallmodifikation I von Tembotrione kann, wie bereits oben ausgeführt, in die üblichen Formulierungen übergeführt werden
   fix: Add one tembotrione record to formulation-types-carriers-and-surfactants.json, matching the tembotrione record that mixtures-with-known-herbicides-and-safeners.json emits from the identical wording at
2. **[compounds]** `recall` on `None`
   The Application Forms and Rates section names Tembotrione twice but emits no tembotrione record.
   > line 640: [0048] Die erfindungsgemäße Kristallmodifikation I von Tembotrione kann als solche, in Form ihrer Formulierungen oder den daraus durch weiteres Verdünnen bereit
   fix: Add one tembotrione record to application-forms-and-rates.json.
3. **[compounds]** `recall` on `None`
   The Table 5 caption names Tembotrione but the section emits no tembotrione record.
   > line 472: [0018] Tabelle 5: Röntgen-Pulver-Diffraktometrie Muster der Kristallmodifikation I von Tembotrione [2θ]
   fix: Add one tembotrione record to table-5-xrpd-pattern-modification-i.json, or drop the tembotrione records the other sections emit from the same construction, so that one rule is applied throughout.
4. **[compounds]** `recall` on `None`
   The Table 6 caption names Tembotrione but the section emits no tembotrione record.
   > line 513: Tabelle 6 Tabelle 6: Röntgen-Pulver-Diffraktometrie Muster der Kristallmodifikation II von Tembotrione [2θ]
   fix: Add one tembotrione record to table-6-xrpd-pattern-modification-ii.json.
5. **[patent]** `precision` on `EP2045236A1`
   The summary says the document characterises the three forms by single-crystal bond lengths and angles, X-ray powder diffractometry and unit-cell data, but every one of those three techniques is reported for modifications I and II only; modification III has a melting point, a Raman list and an infrared list and nothing else.
   > line 94: [0017] Weitere kristallographische Daten der Kristallmodifikationen I und II von Tembotrione sind in Tabelle 7 angegeben.
   fix: Attribute the single-crystal data (Tabellen 3 and 4), the powder data (Tabellen 5 and 6) and the cell data (Tabelle 7) to modifications I and II only, and the melting point, Raman and infrared data to
6. **[patent]** `precision` on `EP2045236A1`
   The blanket statement that no purity is stated for any preparation anywhere in the document is contradicted by [0027], which specifies a graded polymorphic purity for the active substance quality obtained.
   > line 590: Bevorzugt wird eine Wirkstoffqualität mit mehr als 20 Gew.-% der Kristallmodifikation I von Tembotrione, besonders bevorzugt mit mehr als 90 Gew.-%, ganz besond
   fix: Say that no measured purity is reported for any worked example, and note that [0027] (590) and claim 12 (816) do specify polymorphic purity levels as preferences.
7. **[patent]** `recall` on `EP2045236A1`
   The record recites claim 7's melting point of 124.0 degrees C as a distinguishing feature without noting that the patent gives metastable modification II a melting point of 123.9 degrees C, 0.1 K away, so the melting point separates I from II no better than the powder pattern the record does flag.
   > line 79: [0011] Die eine metastabile Modifikation hat einen Schmelzpunkt von 123,9°C, ein charakteristisches Raman-Spektrum (Abb. 2) und ein charakteristisches Infrarot-
   fix: Add one clause recording that modification I melts at 124.0 ([0010], 77) and modification II at 123.9 ([0011], 79), a separation of 0.1 K on a DSC run at 10 K per minute, so claim 7's limitation does 
8. **[patent]** `precision` on `EP2045236A1`
   One of the two readings the record offers for the identical Tabellen 5 and 6 is excluded by the patent's own Tabelle 7: a mislabelled caption would not make two tables carry the same 49 numbers, and the two forms are reported in different crystal systems, which cannot give one powder pattern.
   > line 548: | Symmetrietyp | orthorhombisch | monoklin |
   fix: Keep the duplication reading and drop the wrong-caption reading, or say why it survives: Tabelle 7 (545 to 553) gives modification I as orthorhombic Pna21 with a cell volume of 1788,91 cubic Angstrom 
9. **[patent]** `recall` on `EP2045236A1`
   A second internal inconsistency in the document is not recorded anywhere in this artifact: the preference cascade for the conversion temperature in [0024] makes the most preferred range broader than the merely particularly preferred one.
   > line 584: [0024] Die Umwandlung in die thermodynamisch stabile Kristallmodifikation I erfolgt bei Temperaturen kleiner 100°C, bevorzugt bei Temperaturen von 0°C bis 80°C,
   fix: Record the inconsistency, in the same manner as the Tabelle 5 and 6 duplication is recorded, without resolving it: 60 to 80 is besonders bevorzugt and 50 to 80, which contains it, is ganz besonders be
10. **[pathways]** `recall` on `None`
   No pathway was emitted for the Claims section although A2 carries two terminal steps for it, Claims_Step 1 and Claims_Step 2.
   > line 801: Verfahren zur Herstellung der thermodynamisch stabilen Kristallmodifikation gemäß Anspruch 1, dadurch gekennzeichnet, dass man
   fix: Emit the section pathways for Claims_Step 1 and Claims_Step 2 as A3 rule 7 requires. Rule 8 already establishes that a duplicate step set is emitted rather than suppressed, and both reference runs (CN
11. **[pathways]** `precision` on `scope=section, section_label=Example - Crystal Modification `
   The flag asserts the acetone example is not the invention's process, which the source does not support and [0024] argues against: the example is exactly the dissolve-warm-then-cooling-crystallisation variant the invention describes, and it sits under the heading Preparation of the thermodynamically stable crystal modification I.
   > line 584: Im Allgemeinen kann die Umwandlung zur Kristallmodifikation I bei vollständiger Auflösung der Kristalle der Kristallmodifikationen II und III beziehungsweise Ge
   fix: Replace with a flag that states only what is true and unstated, e.g. example_charge_modification_unstated: [0055] charges 2 g Tembotrione without saying which modification, and [0020] says such materi
12. **[reactions]** `precision` on `Claims_Step 1`
   Claim 8 recites a generic metastable modification and never names modification II or modification III, but the record asserts both as the reactants, narrowing the claim's scope.
   > line 802: a) eine metastabile Kristallmodifikation oder ein Gemisch der metastabilen Kristallmodifikationen von Tembotrione in Lösungsmitteln suspendiert und/oder löst un
   fix: Either carry a single generic reactant identifier for the metastable modification, or keep the two A1 identifiers and raise the narrowing in validation_flags. [0008] at line 73 says Tembotrione occurs
13. **[reactions]** `precision` on `Claims_Step 2`
   Claim 10 recites the same generic metastable modification and names neither II nor III, but the record asserts both as reactants.
   > line 809: Verfahren zur Herstellung der thermodynamisch stabilen Kristallmodifikation gemäß Anspruch 1, dadurch gekennzeichnet, dass man eine metastabile Kristallmodifika
   fix: Same minimal correction as Claims_Step 1: record the claim's generic material, or flag that the two specific identifiers narrow what the claim recites.

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 417 | 413 | 4 |
| `patent` | 15 | 9 | 6 |
| `pathways` | 8 | 6 | 2 |
| `reactions` | 7 | 7 | 4 |
