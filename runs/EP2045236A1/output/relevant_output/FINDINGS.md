# What is wrong with EP2045236A1

Produced by annotating the patent by hand, against the scanned pages rather than
against anyone's OCR. Every item below is a defect in the **patent**, not in the
annotation. The annotation records them and changes nothing.

- 7 reactions extracted, of which 4 carry at least one flag
- 349 unique compounds, 8 pathways
- 21 discrepancies raised by the page-vision pass

## Flags raised, by kind

| flag | count | what it means |
|---|---:|---|
| `a1_missing_compound` | 2 |  |
| `cross_reference_unresolved` | 2 |  |

## The headline findings

No hand-written analysis exists for EP2045236A1. The generated sections above and below are complete; this section is not, and is omitted rather than filled with another patent's findings.

## Everything the page-vision pass raised

- **[p07.png]** Tabelle 6 on this page, the X-ray powder pattern of crystal modification II, carries values identical to Tabelle 5 on page 6, the pattern of crystal modification I, digit for digit in all 49 cells. Two different polymorphs cannot have identical powder patterns, so one of the two tables is almost certainly wrong in the published patent. Recorded, not resolved: both readings are transcribed as printed and the disagreement is left visible.
  - drawing: Page 7 image, Tabelle 6, caption 'Kristallmodifikation II': 7.3765, 8.0674, 10.7988 ... 36.4372, 36.7974, 13 rows in 4 columns, read off the page image and confirmed against the page 7 text layer.
  - text: Page 6 text layer, Tabelle 5, caption 'Kristallmodifikation I': the same 49 values in the same order, with the last row carried over to page 7 under '(fortgesetzt)'. I have not seen the page 6 image myself, so 
- **[p07.png]** The prose of [0019] names two instruments in a word order that a downstream pass could easily normalise into the wrong thing; recorded so the printed form is recoverable.
  - drawing: No drawing on this page; not applicable.
  - text: The page prints 'mit dem Ultrapyknometer 1000 T der Fa. Quanta-Chrome' (the manufacturer follows the model) and 'SHELXTL NT-Version V5.1' (with 'NT-Version', not a bare 'NT'). Both are transcribed exactly and n
- **[p08.png]** Text-vs-text. The temperature preference ladder in [0024] is internally inconsistent as printed: the most preferred range is wider than the merely particularly preferred one.
  - drawing: n/a - no drawing on this page
  - text: [0024]: 'bevorzugt bei Temperaturen von 0°C bis 80°C, besonders bevorzugt bei Temperaturen von 60°C bis 80°C, ganz besonders bevorzugt bei Temperaturen von 50°C bis 80°C'. A narrowing ladder would put 50-80 bef
- **[p08.png]** Text-vs-text. The upper temperature bound for the conversion is given twice with different values.
  - drawing: n/a - no drawing on this page
  - text: [0021] and [0022] both give the treatment window as '0°C bis 80°C' with no wider bound. [0024] gives the general bound as 'Temperaturen kleiner 100°C' and makes 0°C to 80°C only the preferred range. Not necessa
- **[p08.png]** Unit omission in [0024]. The cooling rate is given in degrees Celsius with no time unit.
  - drawing: n/a - no drawing on this page
  - text: 'mit einer Kühlrate von kleiner 25°C, besonders bevorzugt mit einer Kühlrate von kleiner 20°C'. A rate requires a time denominator (most likely °C per hour) and none is printed anywhere on this page. No unit ha
- **[p08.png]** Grammatical mismatch in the [0021] tail at the top of the page, flagged so a downstream pass does not read it as a transcription error.
  - drawing: n/a - no drawing on this page
  - text: 'in einem geeigneten Lösungsmitteln' - singular article and adjective with a plural noun. Printed that way on the page image; the parallel sentence in [0022] reads simply 'in Lösungsmitteln'.
- **[p13.png]** The number table at the head of the page carries no claim number, so its owner cannot be established from this page alone.
  - drawing: The boxed table prints only the caption (fortgesetzt) above 4 columns of 6 integers (363 to 3075). No claim number, no column heading and no unit appear on page 13.
  - text: Page 12 ends with claim 4 (Raman-Spektrum, Bandenmaxima angegeben in cm-1) followed by two unlabelled 4-column lists; the four columns of this continuation ascend directly out of the four columns of the second 
- **[p13.png]** The task brief anticipated a density claim among the claims on this page; no such claim is printed here.
  - drawing: The claims printed on this page are 5 (X-ray powder diffractometry), 6 (unit cell), 7 (melting point 124,0°C), 8 and 10 (processes), 9 (solvents) and 11 (herbicidal composition). No g/cm3 value and no Dichte ap
  - text: Claim 11 back-refers to Ansprueche 1 bis 7, and claims 1 to 4 are on page 12 (orthorhombic system, space group Pna21, infrared spectrum, Raman spectrum), so claims 1 to 7 are fully accounted for without a densi
- **[p16.png]** The figure sheet and the description use different words for the same figure label.
  - drawing: Fig. 1a
  - text: Abbildung 1a, the infrared spectrum of crystal modification I, per [0018] of the description on an earlier page
- **[p18.png]** The sheets label the figures 'Fig. N' while the description labels them 'Abbildung N'. Same numbering, different word.
  - drawing: Fig. 2a
  - text: [0018] enumerates Abbildung 1, Abbildung 1a, Abbildung 2, Abbildung 2a, Abbildung 3, Abbildung 3a.
- **[p19.png]** The sheet labels the figure with the English abbreviation while the German description names the same series differently.
  - drawing: Fig. 3
  - text: [0018] lists the six figures as Abbildung 1, 1a, 2, 2a, 3, 3a
- **[p20.png]** The sheet labels the figure with the English abbreviation while the German description calls the same thing an Abbildung.
  - drawing: Fig. 3a
  - text: [0018] of the description names the six figures Abbildung 1, Abbildung 1a, Abbildung 2, Abbildung 2a, Abbildung 3 and Abbildung 3a. The word Abbildung is not printed on this sheet.
- **[p21.png]** The task briefing states that pages 15 to 22 are the eight figure sheets carrying the six Abbildungen, and that p21 is a spectrum sheet with no text. The page is not a figure sheet and carries no spectrum.
  - drawing: p21 is the EPO search report sheet, EPO FORM 1503, headed EUROPÄISCHER RECHERCHENBERICHT for application EP 07 01 6606. It is dense with text: a four-row citation table, the IPC boxes, the place, date and exami
  - text: VISION-BRIEF.md, section 'What this patent is, so you are not surprised': 'Pages 15 to 22 carry no text at all beyond the running header, and they are the six Abbildungen of [0018]'. The task prompt likewise as
- **[p21.png]** The premise behind the briefing's page range is nonetheless half right, and the half that is right explains the other half. p21 genuinely has a 19-character text layer, but the reason is that the search report is appended to the A1 publication as a scanned image, not that the sheet is blank.
  - drawing: Every character on p21 is pixels. The citation table, the legend and the examiner's name are all image, which is why the extractor found only the running header 'EP 2 045 236 A1' and the page number '21'.
  - text: VISION-BRIEF.md correction 2: 'This patent is born digital, not scanned. It has a clean text layer of 47,791 characters.' That holds for pages 1 to 14 and not for pages 15 to 22, and an absent text layer was re
- **[p21.png]** The figure sheets are p15 to p20, six sheets for six Abbildungen, one to one, and not eight sheets for six as the briefing states. This was checked against the neighbouring pages rather than assumed.
  - drawing: p20 prints the label 'Fig. 3a' and plots an infrared spectrum, absorbance 0.0 to about 0.4 on the ordinate against 'Wellenzahl cm-1' running from about 3500 down to below 1000 on the abscissa, the sheet rotated
  - text: VISION-BRIEF.md: 'There are eight figure sheets for six Abbildungen, so the mapping from sheet to Abbildung is NOT one to one'. On the evidence of p20 and p22 the mapping is one to one over p15 to p20, and p21 
- **[p21.png]** The page prints no figure label, because it is not a figure. The task asked for the label verbatim if one is printed and for an explicit statement if none is.
  - drawing: No 'Abbildung' and no 'Fig.' appears anywhere on p21. The only large-type headings are 'EUROPÄISCHER RECHERCHENBERICHT' and 'EINSCHLÄGIGE DOKUMENTE'.
  - text: The task asked which Abbildung this sheet is. It is none of them, and no Abbildung number can be assigned to it.
- **[p21.png]** 'drawings' is empty, and the empty array is a finding rather than an omission. The task asked that this be stated on the grounds that the sheet carries a spectrum and no chemical structure; the true grounds are stronger, because the sheet carries neither.
  - drawing: p21 carries no chemical structure, no reaction scheme and no plotted spectrum. Its whole content is a printed EPO form: ruled boxes, a four-row citation table, two IPC boxes, an examiner row and a category lege
  - text: The task prompt required drawings to be [] with a note that the sheet carries a spectrum. It is [] for a different reason, and recording the stated reason would have put a false statement into the artifact.
- **[p22.png]** The V-pass briefing states that pages 15 to 22 are the eight figure sheets carrying the six Abbildungen, and that p22 is the last figure sheet. p22 is not a figure sheet at all.
  - drawing: p22 carries no plot, no axes and no figure label. It is the ANHANG ZUM EUROPÄISCHEN RECHERCHENBERICHT for application EP 07 01 6606, dated 06-02-2008: a four column patent family table. p21, checked to place p2
  - text: The briefing infers 'figure sheet' from the 19 character text layer. The inference does not hold: p21 and p22 also have no usable text layer because the EPO search report and its annex are inserted into the A1 
- **[p23.png]** The WO publication number is printed in the EPO's compressed form on this page and in slashed form in the description's prose. Both denote the same document; neither has been normalised.
  - drawing: This page (EPO cited-documents appendix) prints: WO 0021924 A
  - text: The description's prose at [0004], [0020] and [0021] prints: WO 00/21924
- **[p23.png]** The EP publication number is printed without digit-group spacing on this page and with digit-group spacing in the description's prose. Both denote the same document; neither has been normalised.
  - drawing: This page (EPO cited-documents appendix) prints: EP 1314724 A1
  - text: The description's prose at [0003] prints: EP 1 314 724 A1
- **[p23.png]** The non-patent literature reference is formatted differently on this page than in the description's prose: caps and semicolons and an explicit 'vol.' here, mixed case and commas and no 'vol.' there. Same paper, same year, same volume, same page range.
  - drawing: This page prints: J. BERNSTEIN ; R.J. DAVEY ; J.O. HENCK. Angew. Chem. Int. Ed., 1999, vol. 38, 3440-3461
  - text: The description at [0003] prints: J. Bernstein, R.J. Davey, J.O. Henck, Angew. Chem. Int. Ed., 1999, 38, 3440-3461
