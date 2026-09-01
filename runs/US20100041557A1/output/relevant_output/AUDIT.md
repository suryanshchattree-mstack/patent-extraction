# A5 adversarial audit of US20100041557A1

Four independent audits, each in a fresh context, each re-opening the page images.
None of them produced the artifact it audited.

| artifact | records | critical | major | minor | checks passed |
|---|---:|---:|---:|---:|---:|
| `compounds` | 497 | 0 | 7 | 29 | 12 |
| `patent` | 1 | 0 | 4 | 10 | 14 |
| `pathways` | 58 | 0 | 6 | 4 | 14 |
| `reactions` | 61 | 0 | 5 | 10 | 13 |
| **total** | | **0** | **22** | **53** | **53** |

## Acted on

Nothing recorded for US20100041557A1. Every finding below is outstanding.

## Outstanding, by severity

These are recorded and not yet acted on. They are real and a second pass should
work through them.

### critical


### major

1. **[compounds]** `recall` on `None`
   Rhodopol 23 is named as a rheology modifier in its own right and carries no record, although the coordinate item Xanthan Gum in the same list was emitted.
   > line 585: such as Xanthan Gum® (Kelzan® from Kelco Co.), Rhodopol® 23 (Rhone Poulenc) or Veegum® (R.T. Vanderbilt Co.) should be mentioned
   fix: add a record identifier 'Rhodopol 23', role additive, resolved false, in formulation-surface-active-substances-and-au.json
2. **[compounds]** `recall` on `None`
   Veegum is named as a rheology modifier in its own right and carries no record, although the coordinate item Xanthan Gum in the same list was emitted.
   > line 585: Rhodopol® 23 (Rhone Poulenc) or Veegum® (R.T. Vanderbilt Co.) should be mentioned
   fix: add a record identifier 'Veegum', role additive, resolved false, in formulation-surface-active-substances-and-au.json
3. **[compounds]** `recall` on `None`
   Benzoic acid is printed as the head of a mixing-partner entry and carries no record, even though it is a fully specified single compound and not a class term.
   > line 708: benzoic acid and derivatives thereof
   fix: add a record identifier 'benzoic acid', identifier_type iupac, resolved true, role other
4. **[compounds]** `recall` on `None`
   The roughly fifty chemical-class names of paragraph [0162] are omitted wholesale, while class terms of exactly the same kind are emitted elsewhere in the artifact; 'ureas' is printed in this list and is also emitted as a compound from line 564, so the same string is a compound in one section and not in another.
   > line 708: halogen-carboxylic acids and derivatives thereof, ureas, 3-phenyluracils, imidazoles, imidazolinones, N-phenyl-3,4,5,6-tetra-hydrophthalimides, oxadiazoles, oxi
   fix: either emit the [0162] class terms as unresolved records, as the formulation sections do for 'ureas', 'fatty acids', 'clays' and 'polyacrylates', or state the distinguishing test and apply it to the f
5. **[compounds]** `recall` on `None`
   Emulsifiers are named as an additive class alongside wetting agents and dispersant, both of which the artifact does emit as records, but no emulsifiers record exists anywhere.
   > line 568: in particular those wetting agents, emulsifiers and dispersant (additives) normally used in plant protection agents
   fix: add a record identifier 'emulsifiers', role additive, resolved false, in formulation-composition-carriers-and-additiv.json
6. **[compounds]** `recall` on `None`
   Solid foam suppressants are named as a distinct antifoam type and carry no record, although the neighbouring 'foam suppressants of the aqueous wax dispersion type' was emitted as 'aqueous wax dispersions'.
   > line 587: foam suppressants of the aqueous wax dispersion type, solid foam suppressants (so-called Compounds) and organofluorine compounds
   fix: add a record identifier 'solid foam suppressants', role additive, resolved false
7. **[compounds]** `arithmetic` on `tembotrione crystalline form C`
   The note that records the form C cell-volume unit defect states the wrong conversion factor: cubic nanometres and cubic Angstrom differ by 10 cubed, that is 1000, not by 10 to the 21st.
   > line 256: | volume | 1811.3(4) nm^3 |
   fix: replace '10^21' with '10^3'; 15.89 x 7.10 x 16.14 x sin(95.91 deg) = 1811 cubic Angstrom, which is the printed number with the wrong unit, and the printed density 1.616 Mg/m^3 is consistent with 1811 
8. **[patent]** `precision` on `US20100041557A1`
   The record pairs the +/-0.2 degree tolerance with claim 16's three-of-nine threshold to imply the claim cannot exclude the excluded form B, but on the printed tables form B satisfies only two of claim 16's nine reflections and therefore falls outside the claim.
   > line 714: displays at least 3 of the following reflections, quoted as 2θ values: 5.6±0.2°, 8.9±0.2°, 11.1±0.2°, 14.0±0.2°, 18.9±0.2°, 23.4±0.2°, 26.7±0.2°, 28.9±0.2° and 
   fix: State the count. Taking the form B table at lines 335 to 353 (5.6, 9.2, 11.2, 12.7, 15.4, 18.5, 22.6, 25.5) against claim 16's nine windows, only 5.6 (exact) and 11.2 (inside 11.1±0.2) match; 9.2 miss
9. **[patent]** `recall` on `US20100041557A1`
   The record's central distinction between the two processes, slow crystallization for form A against rapid cooling for form C, is contradicted by the document's own cooling-rate numbers, and that inconsistency is nowhere recorded.
   > line 201: [0031] If the crystallization of form A is effected by cooling, the cooling rate is preferably less than 10 K/min.
   fix: Record that the two stated windows overlap completely: [0031] line 201 puts form A at less than 10 K/min, that is less than 600 K/hr, while [0056] line 311 puts rapid cooling for form C at "a cooling 
10. **[patent]** `precision` on `US20100041557A1`
   The record asserts as its sharpest evidence that the process and not the solvent controls the form, but the example tables show the solvent changing the form with the cooling regime held fixed.
   > line 374: [0073] 150 mg of tembotrione were dissolved in 0.15 ml of boiling methanol in a test vessel. The test vessel was sealed and placed in an ice-water bath and left
   fix: Weaken or drop the generalisation. Under one identical regime, boiling solution, sealed vessel, ice-water bath, about 40 mins, methanol gives form A (Example 1, line 374), 2,2-dimethylpropanol gives f
11. **[patent]** `precision` on `US20100041557A1`
   The claim that the cooling regime is the only variable between Example 14 and Comparative Example 16 is unsupported, because the charge, the concentration and the standing time differ too.
   > line 426: [0076] 150 mg of tembotrione were dissolved in 0.50 ml of boiling 2,2-dimethylpropanol in a test vessel. The test vessel was sealed and placed in an ice-water b
   fix: Drop the word alone. Example 14 is a defined charge of 150 mg in 0.50 ml, about 300 g/l, held 40 mins; Comparative Example 16 is one row of "A saturated solution of about 50 mg of tembotrione" (line 4
12. **[pathways]** `fidelity` on `Comparative Examples 3-10_Step 1`
   All 23 comparative-example recrystallisation steps carry non_synthetic false while the 15 chemically identical inventive-example recrystallisation steps carry true, and every pathway's own flag asserts that no bond is formed or broken in any step.
   > line 453: [0080] A saturated solution of about 50 mg of tembotrione in the solvents stated in Table 3 was prepared in a test vessel at the boiling point of the solvent. T
   fix: non_synthetic: true on all 23 comparative-example steps, matching the 15 inventive recrystallisation steps in this same run and the convention in runs/CN111440099B and runs/EP2045236A1 where every rea
13. **[pathways]** `precision` on `Preparation of Form B (Not According to the Invention)`
   The flag form_b_is_explicitly_not_according_to_the_invention_stated_at_line_356_line_362_and_line_439 cites two lines that do not state anything of the kind, and omits the two lines that state it in words.
   > line 356: [0066] The production of the modification B is effected analogously to the production of the modification A, using n-pentanol instead of 2,2-dimethylpropanol as
   fix: Cite line 181 ('the form B also described here, not according to the invention'), line 307 (the same clause repeated in [0054]) and line 439 (the section heading '(not According to Invention)'). Line 
14. **[pathways]** `precision` on `patent-scope pathway to tembotrione crystalline form A`
   The flag asserts the generic process block is the only two-step telling in the patent, which is false, and is contradicted by the artifact's own two-step Claims 16-33 pathways.
   > line 745: 19 19. A process for the production of the crystalline form A of claim 16, comprising: i) preparing a solution of 2-[2-chloro-4-methylsulfonyl-3-(2,2,2-trifluor
   fix: Drop the clause 'and is the only two step telling', or replace it with 'and is preferred over the equivalent two step recitations in claim 19 at line 745 and claim 23 at line 759 because it is the des
15. **[pathways]** `precision` on `all 58 records`
   The flag claims no assay purity is stated anywhere in the patent, but the patent states the tembotrione content of the product of both inventive crystallizations and recites a content in the claims.
   > line 218: [0039] By means of the crystallization according to the invention, the form A is obtained with a tembotrione content of as a rule at least 90 wt. %, often 94 wt
   fix: Narrow to 'no yield and no product mass stated anywhere in this patent; the only purities stated are the generic product content ranges at line 218 for form A and line 323 for form C and the at least 
16. **[pathways]** `recall` on `all 58 records`
   The pathway tag union omits chemical_family:triketone on 54 of 58 records and chemical_family:aryl_sulfone on 30 of 58, because the endpoint tags were taken from the per-section A1 files rather than the merged compounds.json that A3 rule 14 and the A3 input spec name.
   > line 72: [0002] Tembotrione is the herbicidal active substance of the formula I or the tautomers I' and I" and mixtures thereof.
   fix: Add chemical_family:triketone to the 54 records that lack it and chemical_family:aryl_sulfone to the 30 that lack it. compounds.json carries all nine tags for tembotrione and for forms A, B and C; the
17. **[pathways]** `fidelity` on `Example 15_Step 1`
   The pathway step gives the form C seed crystals role seed_crystal while the shipped reactions.json gives the same compound on the same reaction role other, so a field A3 rule 11 requires to be a verbatim copy diverges between the two artifacts.
   > line 437: The solution was cooled on an oil bath to 101° C. and then some seed crystals of the form C (tip of a spatula) were added without stirring.
   fix: Make the two agree. seed_crystal is the better reading of line 437 and is what A2's own stages/A2-reactions/example-15.json and raw-reactions.json both emit, so the divergence is introduced by finalis
18. **[reactions]** `precision` on `Comparative Example 1_Step 1`
   Twenty-three records carry non_synthetic false while their own notes state that no bond is made or broken, the exact reason the other thirty-eight records give for setting it true.
   > line 443: 150 mg of tembotrione were dissolved in 0.20 ml of boiling n-pentanol in a test vessel. The test vessel was sealed and placed in an ice-water bath and left ther
   fix: non_synthetic: true on all 23 records of comparative-example-1, comparative-example-2, comparative-examples-3-10 (8), comparative-examples-11-20 (10) and comparative-examples-21-to-22 (3). The same fi
19. **[reactions]** `fidelity` on `Example 15_Step 1`
   The temperature is typed as a range spanning 6 to 110 C, a range the source never states; it is the span of an ordered cooling programme whose printed values are four discrete points.
   > line 437: The solution was cooled on an oil bath to 101° C. and then some seed crystals of the form C (tip of a spatula) were added without stirring. The turbid solution 
   fix: Record the temperature of the transformation the step is classified from, per the A2 rule that a multi-operation step takes its temperature from the final transformation: either {"type":"exact","value
20. **[reactions]** `recall` on `None`
   Stability Studies Step 2 collapses two separate experiments, pure form A and pure form C held for 8 days, into one record, while its own addition_profile calls each one 'its own experiment'.
   > line 529: [0085] After 8 days under these conditions, the pure modifications A and C were unchanged.
   fix: Two records, one for pure form A and one for pure form C, each with a single reactant and a single unchanged product; the section then holds four experiments (mixture A+B+C, pure A, pure C, pure B) ra
21. **[reactions]** `recall` on `None`
   The generic production process for solid plant protection agents at [0129] has no record anywhere in the artifact, although the equally generic crystallisation processes of [0013] to [0040] and [0045] to [0062] each got two.
   > line 637: Such formulations can be produced by mixing or simultaneous grinding of the forms A or C of tembotrione with a solid carrier and if necessary other additives, i
   fix: One record with reaction_class formulation for the generic solid-formulation route, which the same line goes on to extend with spray drying, extrusion, fluidized bed granulation and spray granulation,
22. **[reactions]** `schema` on `Formulation Examples I to X_Step 1`
   On 31 of 61 records product_name is coined prose that matches no A1 identifier and no is_product entry in the record's own compounds[], so the flattened field does not join the compound artifact.
   > line 647: In this manner, a water-dispersible powder which contains the form A or C is obtained.
   fix: product_name must be one of the record's compounds[] product identifiers, per A2 rule 8 that these fields are a flattening of compounds[]. Put the composition-level description in notes. Affects all 1

## Recall estimates

| artifact | items found in text | present in artifact | missing |
|---|---:|---:|---:|
| `compounds` | 376 | 305 | 22 |
| `patent` | 26 | 20 | 6 |
| `pathways` | 56 | 56 | 0 |
| `reactions` | 63 | 61 | 2 |
