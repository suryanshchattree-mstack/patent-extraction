# WO2000021924A1 run notes

Benzoylcyclohexandione herbicides, Aventis CropScience GmbH, priority 1998-10-10.
A 112 page German WO publication. Scanned: 0 characters of text layer on every one
of the 112 pages, so every character in this annotation came from the vision pass.

## Model provenance, and why the agreement here is weaker than it looks

CLAUDE.md asks for this because correlated blindness is invisible to the pipeline.

Every judgement artifact in this run was produced by a subagent of one Claude Code
session running **Claude Opus 5**. Subagents inherit the session model, and no
model override was set on any dispatch. That covers all of it:

| pass | invocations | what it produced |
|---|---:|---|
| V | 112 | one page read each, fresh context, `input/vision/pNNN.json` |
| A0 | 1 | the 38 section map |
| A1 | 38 + 8 re-runs | 583 compound records |
| A2 | 3 | 21 reaction records |
| A3 | 1 | 10 pathways |
| A4 | 1 + 2 corrections | the patent record |
| A5 | 4 | the adversarial audits, fresh context, barred from `output/stages/` |
| step 6 | 10 | the independent substance read, 1724 spans |

**The three independent readings in this pack are not independent in the way the
word implies.** The vision pass, the extraction passes and the step 6 read are the
same model, prompted by the same operator, working from the same page images. Where
the extraction missed something and the step 6 read also missed it, nothing here can
see that, and it reports as clean. Where A5 agrees with A1, that agreement cannot
distinguish "both read it correctly" from "both inherited the same error from the
vision pass". Only the disagreements are strong evidence.

One further caveat: the step 6 readers were barred from `output/` and had never seen
A1, which is real independence of *access*, not of *model*. The A5 audits were
barred from `output/stages/` for the same reason and with the same limit.

One agent self-reported as "Claude Opus 4.5" in its A0 reply. That contradicts the
session model and I could not verify it either way, so it is recorded here rather
than asserted in an artifact.

## The prompts are written for the reference patent, and this one is German

`render_prompts.py` substitutes the patent id and the text-layer facts. It does not
substitute the language or the document shape, so every rendered prompt in this run
described CN104292137A's Chinese 9 page patent. Each pass was given a written
deviation telling it what was actually true, and the deviations are the part of this
run most worth a reviewer's scepticism:

- **V** says "a scanned Chinese patent" and "transcribe verbatim in Chinese". Here
  `zh` holds verbatim GERMAN. That follows the convention the biblio schema already
  states for `abstract_zh`: "the abstract as printed, in the patent's own language
  despite the field name".
- **A0** rules 5 to 8 describe CN inline markers, `CN 104292137 A` headers, and an
  Example 1 with eight numbered steps. None exist here. The generalisable intent
  was kept: an Example is one section however many `Schritt` it has.
- **A1** rule 20's translation hazards name four Chinese compounds from the other
  patent. Replaced with this document's four real discrepancies.
- **A2** rules 5e and 5f describe the other patent's scheme in detail, including a
  prose/scheme step count mismatch that does not exist here.
- **A3** rule 3's KSM example is the other patent's, though its principle held.
- **A5** was told only that the document is German and that the German is
  authoritative. It was told nothing about any defect found earlier in the run,
  deliberately: an auditor handed a list of defects is confirming a list, not
  auditing, and the output looks identical either way.

## Two conventions the prompts did not settle

Agents working in isolation diverged on both, so both were pinned mid-pass and the
affected sections re-run.

1. **Whole-molecule class terms are records.** `Verbindungen der allgemeinen Formel
   (I)`, `Benzoylcyclohexandione` and the like are emitted unresolved. Settled by
   the reference gold's own precedent: it emits `硫醇` (thiols), a bare class term,
   with `resolved: false`. Only an R-group SUBSTITUENT fragment is not a record.
2. **Enumeration table rows: only the characterised ones.** Tabelle 1 to 5 hold
   roughly 542 fully determined compounds; the caption fixes every symbol the row
   does not. Of those, about 26 print a 1H NMR block and were actually made. Those
   26 are records; the rest are prophetic enumeration and are not. This is a
   documented decision by the run owner, not a rule in any prompt, and it is the
   single largest scope judgement in the run. An extractor scored against this gold
   will appear to over-produce by roughly 500 records if it emits every table row.

## Hand-authored structures

Four, at the structures gate. Each was checked twice: atom by atom against its name,
then against the patent's own printed mass/mole pair, which is the only arithmetic
check available since that gate has no OPSIN and no network.

| identifier | formula | MW | patent's printed pair | implied MW |
|---|---|---:|---|---:|
| 2-chloro-3-methyl-4-methylthio-acetophenone | C10H11ClOS | 214.72 | 223.48 g / 1.04 mol | 214.88 |
| 2-chloro-3-methyl-4-methylsulfonyl-acetophenone | C10H11ClO3S | 246.71 | 60.0 g / 0.24 mol | 250.00 |
| sodium tungstate | Na2O4W | 293.82 | 27.47 g / 0.08 mol | 343.38 |
| 3-oxo-1-cyclohexenyl 2-chloro-4-methylsulfonyl-3-phenoxymethyl-benzoic acid | C21H19ClO6S | 434.90 | 0.51 g / 1.17 mmol | 435.90 |

Two of those four carry a disagreement that is recorded in the curated file and NOT
resolved:

- **sodium tungstate**: the structure follows the NAME, the anhydrous salt. The
  patent's own 27.47 g / 0.08 mol implies 343.4, which fits the dihydrate at 329.85
  and no anhydrous reading. The German never states a hydrate, so none is asserted.
- **the last row**: the printed name at line 601 is internally contradictory,
  carrying an ester prefix and a free-acid suffix at once. The structure is the enol
  ester the procedure makes and the arithmetic supports (0.23 percent agreement);
  the free acid at 340.78 is 28 percent away and cannot be what was weighed. The
  compound record keeps `resolved: false` and keeps the printed name.

Four Markush genus labels went to `no_structure_needed` instead of being given a
SMILES: `compound of formula (I)`, `(III)`, `(Ib)`, `(Ic)`. A genus over undefined
R groups has no single structure and any SMILES would have been invented.

## The translations gate did not check what its name suggests

`resolve_translations.py:127` matches Han ideographs only. This document has none,
so the gate's universe was empty and its coverage check passed over zero strings.
`index_curated` at line 714 further refuses any curated key that is not Han, so
German has no escape hatch if it ever reaches an identifier.

That is narrower than it first appears, and the honest statement is: the gate did
verify that all 1344 source lines come out of the substitution in English, because
pass V wrote an `EN:` line under every paragraph. What went unchecked is whether any
individual German string lacks one. Nothing here failed; nothing here was checked
either, and those are different facts.

TARGETS.md flags this hazard only for row 12, `DE10113137A1`. It applies equally to
row 6. The caveat is written as though DE10113137A1 were the only non-Chinese patent
in the twenty, and it is not.

## Defects found in the pipeline, not in the patent

All six were invisible on the reference run and fired here.

1. **`render_pages.py:63` pads page numbers to two digits.** Above 99 pages the
   filenames stop sorting numerically and five stages sort them lexicographically,
   putting p100-p109 between p10 and p11. The enriched document came out with the
   claims split across two disjoint ranges. Worked around by renaming `pages/` and
   `vision/` to three digits; the code is still wrong for the next long patent. The
   fix is to pad to `max(2, len(str(page_count)))`, and the `max(2, ...)` matters:
   a bare width would rename the reference run's p01-p09 to p1-p9.
2. **`run_pipeline.py`'s `merge` stage omits `--patent-id`** where the adjacent
   `finalise` passes it, so it cannot resolve which run to read once `runs/` holds
   more than one directory. Worked around with `ANNOTATION_PATENT_ID`. The guard
   failed safe rather than annotating the wrong patent, which is CLAUDE.md rule 1
   working exactly as intended.
3. **biblio and patent schemas disagree on the assignee vocabulary.** Only
   `government`, `individual` and `university` validate in both; the reference's
   assignee is a university, which is why this never fired. Every company-assigned
   patent failed `validate`. FIXED with a mapping in `finalise.py`, approved by the
   run owner. `company` maps to null rather than to `multinational_corp` or `sme`,
   because the input vocabulary does not record company size and guessing it would
   assert a fact nobody read off the patent; the `assignee_type:company` tag keeps
   the source word. Verified not to alter the reference run.
4. **`make_svgs.py` `wrap()` had no hard break.** A systematic chemical name is one
   unbroken token, 83 characters here, so it rendered past the canvas and failed the
   diagrams stage. FIXED with a hard break plus content-sized boxes, approved by the
   run owner. Verified inert on the reference run, whose target is "tembotrione".
5. **`make_svgs.py:22` writes patent-specific diagrams to a SHARED directory**,
   `pipeline/svg/`, not into the run. Generating this run's diagrams silently
   overwrote the reference run's committed `m2-route.svg`, `m1-pass-map.svg`,
   `m5-ocr-comparison.svg` and `approach.svg` in place, replacing tembotrione's
   route with this patent's. Caught at `git status` and restored with
   `git checkout HEAD -- pipeline/svg/`; this run's own copies live in
   `output/relevant_output/svg/` and were never at risk. NOT FIXED in code. This is
   the same hazard CLAUDE.md rule 1 was written about, one directory over: anyone
   who runs two patents in one checkout overwrites the first one's diagrams and
   only notices if they read `git status` before committing.
6. **`finalise.py:208` treats an all-null `quantity` object as populated**, so a
   cross-section merge overwrites a measured quantity with an empty one. NOT FIXED.
   `hydrogen peroxide` loses its 203.83 g, `oxalyl chloride` its 0.59 g / 4.58 mmol.
   **This is present in the reference gold too**: tembotrione loses its quantity the
   same way. It is silent data loss in shared deterministic code and the reference's
   own numbers depend on the current behaviour, so it was left for a maintainer.

## selfcheck: 33 pass, 3 warn, 2 fail

The run reaches the end. It does not meet AGENT.md's "0 fail" bar, and the reason is
not a defect in this gold.

Both failures are one fact: the review census is tier 1 plus tier 2 = 281 claims,
which at the pinned 8.7s P90 rate is 40.7 minutes against a 15 minute budget. The
consequence, in the check's own words, is that tier 3 is sampled zero times, so the
verification report ships with **no statistical bound** on its 776 tier 3 claims.

The budget is a pinned number and CLAUDE.md rule 4 forbids changing one to make a
check pass, so it was left failing. The census is not inflated: 220 of the 281 are
`not_checkable` judgement claims, and per compound this run produces FEWER census
claims than the reference (0.54 against 1.08). The 15 minute budget was calibrated
on a 9 page patent with 75 compounds; this is a 112 page patent with 520. A reviewer
should expect to spend about 40 minutes, or the budget should be made a function of
the gold's size. That is a decision for a maintainer, not for this run.

The three warnings are described in the selfcheck output and are acceptable per
AGENT.md.

## One A5 finding checked and rejected

The compounds audit reported that pages p069, p072 and p076 were never read into the
source and hold only empty IMAGE_EXTRACT spans. That is false: the rows are present,
p069's at line 766, and the vision files for all three carry full row text. The
finding is left in `compounds-report.json` rather than deleted, per CLAUDE.md rule
"never delete a finding because you disagree with it". This note is the recorded
disagreement.

## Also worth a reviewer's eye

- **`cyclohexanedione`** appears as a bare identifier with no locants. OPSIN's
  second reading guesses the 1,2-dione; the patent means the 1,3-dione. Example 1
  resolves it correctly from the printed 0.19 g / 1.68 mmol, but the bare-name
  record elsewhere is genuinely ambiguous and is deliberately left unresolved,
  exactly as the reference run left its own.
- **Example 1 Step 3 charges 223.48 g of a compound Step 2 made 111.24 g of**, a
  factor of 2.009. The charge is internally consistent (223.48/1.04 = 214.9 against
  C10H11ClOS at 214.71), so the discontinuity is between steps, not within one.
- **Example 1 Step 1 prints `88.2 g (0.5 mol) Jodmethan`.** CH3I is 141.94, so 88.2 g
  is 0.62 mol and 0.5 mol is 71.0 g. Flagged `molar_mass_inconsistent`, uncorrected.
- **Tabelle 5's caption fixes R3 = SO2Et while the scaffold drawn beneath it shows
  SO2Me.** The drawing is not machine-readable in this input, so the conflict is
  recorded from the caption side only and no reading is preferred.
- **Every reaction scheme in the patent is unreadable here.** Schema 1, 2 and 4
  returned empty `reactants`/`conditions`/`products`, and Schema 3 produced no span
  at all. The nine general-method reaction records therefore rest on prose alone,
  and no drawing-versus-text comparison was possible anywhere in this run. Those
  comparison flags were deliberately NOT raised, because raising them would assert a
  check that never ran.
