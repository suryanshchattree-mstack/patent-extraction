# CN111440099B run notes

A purification patent, not a synthesis patent. Nineteen numbered experimental
batches, six examples, and a target compound the document only ever purifies.
Read this before reading the gold.

## What produced each artifact

Every judgement pass in this run was **Claude Opus 5 (1M context)**, model id
`claude-opus-5[1m]`. CLAUDE.md asks for this because it is the only handle anyone
has on correlated blindness later, and the answer here is uncomfortable: one model
family produced the transcription, the extraction, the audit and the independent
reading. What differs between them is the CONTEXT, not the model.

| pass | contexts | isolation |
|---|---|---|
| V, page vision | 10, one per page, then 7 resumed for corrections | fresh per page; no page saw another page |
| A0, section map | 1 | the coordinating session, which had read the whole document |
| A1, compounds | 15, one per section | fresh per section; each saw only its own section text |
| A2, reactions | 10, one per section with procedures | fresh per section; given its own A1 output and a registry |
| A3, pathways | 0 | a deterministic script written by the coordinating session, not a model call |
| A4, patent record | 1 | fresh |
| A5, audit | 4, one per artifact | fresh, and never told what the annotation had found |
| reading A, step 6 | 1 | fresh, and forbidden to open `output/` or `input/vision/` |

Two consequences worth stating plainly.

**A5 was kept genuinely blind and it paid.** The four audit contexts were given the
prompt, the artifact, the source and the page images, and nothing else: no summary
of the run, no list of known defects, not even the fact that 环磺酮 is tembotrione.
They returned 55 findings, and 4 of them changed values in the deliverable. The
most valuable was a critical one no other check in this pipeline could see, and it
is described under "The defect the audit caught" below.

**Reading A is independent of the extraction but not of me.** AGENT.md step 6 asks
the person running the session to read the document themselves. By the time this run
reached step 6 I had read every A1 and A2 record, so my own reading would have been
derived from the extraction in all but name. It was given to a fresh context instead,
under an explicit prohibition on opening `output/` or `input/vision/`, and that agent
confirmed it read only the enriched markdown, `CLAUDE.md`, `AGENT.md` and the
reference run's file for its shape. That is more independent than I could be at that
point, and less independent than a second person would be. Where reading A and the
extraction agree, the agreement is weak evidence: one model family read the same
page twice.

Reading B, ChemDataExtractor, is not installed on this machine. `mentions.py` says so
loudly and writes nothing rather than an empty file, so the recall sweep publishes
`readers: ["llm"]` and every finding carries "one reader only".

## The patent in one paragraph

Tembotrione (环磺酮, CAS 335104-84-2, C17H16ClF3O6S) is made by a rearrangement
catalysed by acetone cyanohydrin, which leaves cyanide impurities in the product.
Those impurities give a positive Ames mutagenicity result, and the patent's argument
is that the positive is an artifact of the impurity rather than a property of the
compound. The method: dissolve the crude product in an aqueous organic solvent and
warm it, stir in an adsorbent and hot-filter, then acidify below pH 3 and crystallise.
Cyanide falls from 1327 ppm to below 100 ppm. Six examples vary one parameter each,
and Example 6 runs the synthesis and the purification end to end at 231.9 g scale.

## Where the content actually is, and why the vision pass mattered more here

Every page carries a text layer, 4,254 characters over 10 pages. But five data
tables and three drawings are images with NO text layer behind them, and those five
tables are the entire results set. Pages 5 to 8 have between 57 and 192 characters of
extractable text each. So:

- **Examples 1 to 4 print no prose procedure at all.** Every treatment lives inside
  the 处理方法 cell of a table image. All nineteen batches' procedures, and every
  cyanide number the patent exists to report, came from reading pixels.
- The V prompt's schema has no place for a table: `drawings` takes `structure` or
  `scheme`, and `build_enriched.py` turns a drawing into a molecules/reactions
  IMAGE_EXTRACT span. A table recorded there would have reached the rest of the
  pipeline as an empty span and every number in it would have been lost silently.
  So a table was recorded as the CONTENT OF ITS PARAGRAPH, in `zh` as a markdown
  table with cells verbatim and in `en` translated. In production the OCR stage would
  emit exactly that, so the enriched document keeps its shape.
- Four tables are printed in two or three fragments because a row is cut mid-cell by
  a page break. Batch 13's cell splits inside the word 含水甲醇: line 228 ends "40%含"
  and line 236 begins "水甲醇中". Read as fragments, that batch loses its solvent.

## The defect the audit caught, and what it cost the previous run

`finalise.py:208` merges one compound across sections with
`elif v not in (None, "", [], {}): out[k] = v`. A dict is tested as a CONTAINER, so
an object of all nulls is not empty and overwrites a populated one. Section files
merge in filename order.

Every A1 context in this run was briefed on that and emitted the literal `null` for
`quantity`, `nmr` and `melting_point` where its section had no data, which is the
prompt's own rule 17. That worked: tembotrione's 262.1 g, its 95% content and its 1H
NMR all survive into the deliverable. On the previous patent the same hole deleted
the target compound's 188 g and 95% yield, and the reference run
`runs/CN104292137A/` still has that loss.

**But the same merge has a second mouth, and only the blind audit saw it.** Scalars
are overwritten too, and `synthesis-scheme.json` sorts second-to-last of the fifteen
section files. It carried `appearance: "红棕色固体"`, the RED-BROWN crude from [0029].
Example 6 carried "pale yellow solid", the material the patent actually isolates and
weighs. So the merged record described the crude while carrying the product's mass,
its purity and its NMR, its own notes asserted the opposite, and an untranslated
Chinese string sat in a screen-facing field. Nothing in the pipeline can see that: the
record is schema-valid, every field is populated, and both values are real quotations
from the document.

Fixed at the input: Synthesis Scheme now emits null for all three appearance fields
and records the crude in `notes`, so Example 6's isolated-product description wins.

## What this run did differently, and the one deviation from the prompts

**One canonical identifier table, shared by all fifteen A1 contexts.** A1 has no
`PRIOR_REGISTRY` placeholder, so nothing in the prompt makes two sections spell one
compound the same way, and `build_compound_id` keys on the exact string. The
reference run carries three spellings of one benzoic acid and two of the
cyclohexanedione as five separate compounds. This run was given a fixed table of
identifiers and of the merge-sensitive fields (`role`, `commercially_available`,
`resolved`), with an instruction to use the table AND record what the section's own
reading would have been. Result: **99 records, 24 distinct identifiers, and
`finalise.py` reports "molecules carried under more than one spelling: 0"**.

That is a deviation from the prompt as written, and it is the only one in this run
that adds information the prompt did not ask for. It is recorded here rather than
left implicit, and each overridden section says in its notes that it was overruled.

**A3 was a script, not a model call.** The A3 prompt says its rules are a
deterministic builder's logic written out and that where a rule fully determines the
answer no judgement should be exercised. Implementing it as code makes that literal
and re-runnable. The script is at
`<scratch>/cn111/build/build_a3.py` and it marks its two genuine judgement calls in
comments. The blind pathways audit then re-derived all eleven pathways from the rules
and caught three places where my code departed from them, all three now fixed:
`components` was taking every non-product compound instead of the reactants (rule 12),
rule 16's inheritance covered only the arithmetic flag, and
`scale_discontinuity_in_chain` was never raised.

## Prompt text that describes the previous patent, not this one

The rendered prompts substitute only the patent id, so their patent-specific
paragraphs are about CN104292137A and are simply false here. Every pass was told
this and told to follow the RULES and ignore the claims of fact. Recorded so nobody
later reads a pass's output as having missed something the prompt promised:

- A0 rule 5 and 6: "numbered inline markers `1、<compound name>`", "do not split
  Example 1 into eight sections". This patent has six 实施例 headings and no `N、`
  markers anywhere.
- A1 rule 20's translation hazards: `1,2-二氯甲烷`, `二氯甲烷` as a solvent,
  `环己二酮` at 24.5 g / 0.22 mol, `氰基丙酮`. Only 环己二酮 occurs here, and with no
  mass beside it.
- A2 rule 5b: "one drawing usually precedes each experimental step". No experimental
  section in this patent contains a drawing.
- A2 rule 5f: "Summary of the Invention ends with a drawn multi-arrow scheme" and
  "the prose gives eight steps and the scheme draws nine". This patent's Summary has
  no drawing at all; the A2 context checked and said so.
- A2 rule 29: "at least three steps in this document have arithmetic that does not
  close". The arithmetic that does not close here is a percentage column, not a mass
  balance, and it fails in 18 of 19 batches.
- The closed `validation_flags` list has no value for a percentage that disagrees
  with the numbers beside it. All ten A2 contexts independently reached for
  `mass_balance_implausible` and each said in its notes that it is being used for a
  percentage and not a mass. That is why the deliverable shows 19
  `mass_balance_implausible` flags on a patent that states no mass in eighteen of
  those records.

## The patent's own defects

Everything here is a defect in the document. The annotation records them and changes
nothing.

1. **The results column does not follow from the results.** All five tables head
   their fifth column 氰化物杂质含量降低% (percentage reduction in cyanide impurity
   content), and in 18 of the 19 batches the printed percentage does not follow from
   the two ppm columns printed beside it. Batch 7 is the only one that closes
   (1125 to 32 is 97.16%, printed 97). The worst is batch 3: 1327 to 92 is a 93.07%
   reduction, printed as 74%. And the column is not even monotonic against the
   residual it is computed from: batch 3 leaves MORE cyanide than batch 4, 92 ppm
   against 88, yet states a much lower reduction, 74% against 89%. Every printed
   figure and its computed counterpart is in `provenance/reactions-provenance.json`
   under `arithmetic_check`.
2. **Example 6's masses fit the acid, not the compound it names.** [0053] charges
   231.9 g of a material it calls the benzoyl CHLORIDE, then adds 237.9 g of thionyl
   chloride and later strips off "the excess". 237.9 g of thionyl chloride is
   1.9997 mol, a round 2.000 mol. Against the named acid chloride (MW 365.15) that is
   3.149 equivalents; against the corresponding benzoic acid (MW 346.70) it is 2.990,
   three equivalents to three figures. And chlorinating an acid chloride is not a
   reaction. So either the material charged is the acid, or the thionyl chloride stage
   is redundant. [0009] says the acid is what reacts with thionyl chloride, and the
   drawn scheme at [0031] starts from the free acid. The annotation keeps the printed
   name in every structured field, flags it, and records both readings.
3. **The one worked example falls outside its own claim.** Claim 3 and [0025] specify
   a stirring speed of 150 转 to 200 转. Example 6 at [0053] uses 280 转/h. Neither
   figure carries a per-minute base, and the two are not in the same unit.
4. **pH 2 buys nothing over pH 3, by the patent's own data.** Example 5's batches 18
   and 19 print the same residual (25 ppm) and the same reduction (99%) at pH 3 and
   at pH 2, while [0016] and claim 1 both specify below 3 and Examples 1 to 4 all run
   at pH 2.
5. **Example 5 lists its pH values in two different orders.** [0050] enumerates
   2、3、4、5 ascending; the table lists 5, 4, 3, 2 descending. Same set, same count.
   A reader who numbered the batches from the prose would pair every batch with the
   wrong pH.
6. **Example 4 does not isolate the variable it says it isolates.** [0047] presents
   it as a comparison 在不同吸附剂中, in different adsorbents. Batch 14 is activated
   carbon in 20% aqueous methanol; batch 15 is diatomaceous earth in 20% aqueous
   ETHANOL. Solvent and adsorbent move together, so nothing in the section attributes
   the difference to the adsorbent.
7. **Example 3's batch 11 is not a clean member of its own comparison.** The example
   varies water content, 20 / 30 / 40 percent. Batch 11 alone strips the methanol off
   and adds 10 g of fresh water before the acid, so it acidifies and crystallises from
   water rather than from aqueous methanol.
8. **The Ames test is credited with a measurement it does not make.** The abstract and
   [0026] both attribute the 1327 ppm to below 100 ppm figures to Ames testing. An
   Ames assay reports mutagenicity, not a cyanide concentration. No analytical method
   for the ppm figures is named anywhere in the patent.
9. **Two headings for one column.** Example 1's table heads its first column
   实验批次; the tables in Examples 2 to 5 head the same column 试验批次. Verified at
   900 dpi on both p05 and p07 after two page contexts disagreed with a third. The
   two are translated differently on purpose, "experiment batch" and "test batch", so
   the inconsistency survives into English rather than being flattened.
10. **Smaller things, all recorded and none corrected.** [0024] repeats the operative
    clause of [0023] almost word for word. [0021] is missing a verb before 入含水溶液,
    so the step cannot be read with confidence. The abstract and [0026] print 磺酮,
    dropping the leading character of 环磺酮. [0005] gives the molecular weight as
    440.88 where the formula printed two lines above comes to 440.8. The reduced
    pressure is printed `mP` where MPa is meant. Two reduction cells print a bare
    number with no percent sign where the rest of the column carries one. Example 5's
    table has no caption, and heads its fourth column 析晶后 where the other four
    head it 处理后. pH is printed capital `PH` everywhere except the claims.

## Corrections made during the run, and who caught what

Recorded because a run that only reports its final state hides how it got there.

- **Six of the ten page contexts translated 环磺酮 as "sulcotrione"**, and one
  transliterated it. Sulcotrione is 磺草酮, a different herbicide. The identity is
  pinned on p03 by CAS 335104-84-2, C17H16ClF3O6S, 440.88 and the drawn structure,
  and no other page carries any of that. This is the exact failure AGENT.md warns
  about for `title_en`, appearing instead in a per-page pass whose isolation is what
  made it possible. Each page was sent the evidence and corrected its own file.
- **p10 reported the 1H NMR as inconsistent with the product.** It was, under
  "sulcotrione": 16 protons where sulcotrione has 13. Under tembotrione every peak
  is accounted for. The finding is kept in the artifact marked FIRST READING
  WITHDRAWN / SECOND READING ADOPTED rather than deleted.
- **I sent two page contexts a wrong codepoint** (U+2010 where the text layer uses
  U+2011 NON-BREAKING HYPHEN). p03 checked and corrected me.
- **I told three A1 contexts that batches 1 to 15 all charge 1 g of activated
  carbon.** Two of them refused: batch 15 charges diatomaceous earth. One of those
  two then over-corrected and claimed batches 3 to 6 state no mass at all, which was
  its own regex requiring 加入1g with no space where the page prints 加入 1g. Both
  are now right: activated carbon at 1 g in batches 1 to 14, diatomaceous earth at
  1 g in batch 15 and in Example 5.
- **Example 1's A1 context put a 10 g mixture mass on methanol.** The 10 g is 10 g of
  20% aqueous methanol, and the patent never states the split. Now `quantity: null`
  with the figure in notes, since no field holds the mass of a mixture.
- **Seven A2 records had the solvent composition inverted**, reading 20%含水甲醇 as
  20% methanol. [0018] says the figure is the water content. Examples 2 to 5 had it
  right; Example 1 and Example 6 did not.
- **The Summary section annotated pH 至3以下 as `ph_value: 3.0`** where Claims
  annotated the identical wording as null. The audit rated it the most serious finding
  in the reactions artifact and it is right: a consumer reads the field, not the note.
- **The Summary section used a different substrate/product convention** from the other
  nine, one dual-flagged compound entry instead of two. That emptied A3's reactant set
  and resolved the Summary pathway's KSM to **acetonitrile**, a solvent, in the
  deliverable. Two sections disagreeing about a convention put a wrong value in the
  gold.
- **A4's narrative cited paragraph markers and example numbers** its declared inputs
  do not contain, because I handed it the A0 section map, which is outside the
  prompt's contract. The audit caught it. The narrative was rewritten to what the
  title, abstract, claims and rollup support, and the assertions dropped for want of a
  declared input are listed in that pass's own report. The sharpest of them, the pH 2
  against pH 3 finding, now lives only in the A0 notes and here.

## Recorded disagreements that are NOT resolved

1. **Is the drawn route prior art or the invention's own?** The same route is drawn
   twice, at [0010] under 背景技术 and at [0031] inside 具体实施方式. The p03 context
   read [0010] as prior art; the p05 context read [0031] as the invention's route.
   Neither page decides it, and the invention is a purification, so the synthesis is
   neither claimed nor criticised. All four scheme records carry
   `route_attribution_unclear` and both readings.
2. **Should a mixture name be an alias of one of its components?** The A5 compounds
   audit says no and would delete `20%含水甲醇` from the methanol record. The
   translations gate's name-fidelity check says the substance is right and only the
   strength is missing, and the reference run's own `无水三氯化铝` entry closes exactly
   that gap with an `override` translation. The alias is kept and qualified. Both
   positions are in `input/translations-curated.json`.
3. **Is `smiles` supposed to be present-and-null or absent?** A1 rule 4c says leave it
   null, which reads as present. The reference run omits the key entirely, in both its
   stage files and its finished `compounds.json`. This run follows the reference. The
   audit called the absence a defect on the strength of the rule.
4. **`experimental_intermediate` for the Synthesis Scheme section.** The compound it
   prepares is a final active ingredient, not an intermediate; it is this patent's
   substrate. The alternative reading (`experimental_example`, with the purifications
   as its workup) is defensible and is recorded in the section map's notes.
5. **One pathway per section, where a section has several terminal steps.** A3 rule 7
   says one per section; Example 1 has six terminal batches. Nineteen near-identical
   purification pathways would differ only in conditions, so one is emitted per
   section and every such pathway carries
   `multiple_terminal_steps_in_section`. `reactions.json` keeps all nineteen.
6. **`cyclohexanedione` cannot be pinned by name.** OPSIN, reading the name with no
   sight of the patent, guesses the 1,2-dione. The document itself fixes the 1,3
   isomer at [0029] and [0053] and draws it at [0010] and [0031], so the identifier is
   `cyclohexane-1,3-dione` and the locant-free form is an alias. `names-opsin.json`
   records the disagreement.

## Defects in the repo, not in this patent

None of these is fixable from a run directory, and none was worked around quietly.

1. **FIXED. `run_pipeline.py` could not complete on a checkout holding more than one
   patent.** It invoked `merge_stages.py` (line 220) and `schemas/validate.py`
   (line 240) with no `--patent-id`, and both fell back to discovery, which refuses
   when `runs/` holds more than one run, so the run stopped at `merge`, stage 4 of 18.
   Every other stage already passed the id. It was invisible on a reference-only
   checkout and it blocked three patents. Both calls now pass the id, and this run
   reaches the end of all 18 stages.
2. **FIXED. No assignee `type` satisfied both schemas.** `biblio.schema.json`
   describes the field as a legal form and accepts company / institute / hospital /
   foundation / university / government / individual; `patent.schema.json` describes
   it as a size and scope and accepts multinational_corp / sme / consortium /
   university / government / individual / null. Only three values are in both and
   none fits a chemical company, and `new_run.py:61` seeds `"company"` into every new
   run directory. `finalise.py` now passes the three shared values through and maps
   every other legal form to `null`, which the production enum accepts. It is NOT
   mapped to `sme`: that would have the gold assert a company size neither patent
   evidences. Nothing is lost, because the `assignee_type:` tag is built from the
   biblio record rather than from the mapped field, so this run publishes
   `type: null` alongside the tag `assignee_type:company`. Reasoning is in
   `pipeline/contracts/SCHEMA-LOSS.md`.
3. **`finalise.py:merge_compound` tests a container, not its contents.** Described
   above under "The defect the audit caught". The reference run still carries the data
   loss it causes.
4. **`FINDINGS.md` can only carry hand-written findings for one patent.** The headline
   findings section of `make_relevant_output.py` is a hardcoded `if` for
   CN104292137A, with an honest `else` for everything else that says no hand-written
   analysis exists. There is no input file a run can supply its own through, so this
   patent's findings reach the deliverable only as the generated flag tables and the
   vision pass's discrepancy list. The ten findings above live here instead. The
   `else` branch is the right call (better an admitted gap than another patent's
   findings) but the gap is real.
5. **`parties.examiners` and `bibliographic.patent_type` can never be populated.**
   `finalise.py` hardcodes both to None, so no biblio can fill them. This patent
   prints 审查员 靳贝贝 on its front page and 发明专利 in field (12), and both are lost.
   The reference run has the same two nulls. This is the
   `GUARDS-THAT-PASS-ON-ABSENCE.md` shape with a field rather than a guard: a null
   that means "the code cannot carry this" is indistinguishable from one that means
   "the document does not say".
6. **A4 rule 4 promises a `legal_status` tag that `finalise.py` does not union in.**
   The reference run's `patent.json` has no `legal_status:` tag either, so the prompt
   and the code have diverged and both runs are affected.
7. **`verify.py` checks reading A's spans against the English rendering of a line**
   (line 3029), which is right and is well argued in its own comment, but nothing
   says so anywhere a reader of AGENT.md step 6 would find it. The first build of
   this run's `substances-observed.json` filed Chinese spans on Chinese lines,
   verified them against the raw line, passed its own 418 assertions, and was
   rejected outright by the engine. The reference file's spans are all English, which
   is the only available evidence of the convention.
8. **The diagram stages write into the shared `pipeline/svg/`.** `make_svgs.py` and
   `make_approach.py` overwrite the working copies for whichever patent ran last, so
   running them for patent three left `pipeline/svg/` holding this patent's diagrams
   under git as eight modified files. The per-run deliverable at
   `output/relevant_output/svg/` is correct and carries this patent's id in every
   file; the shared directory was restored to HEAD afterwards. Same handling as the
   previous run.
9. **Scratchpad script names collide between passes.** Two contexts working on the
   same section, one for A1 and one for A2, wrote generic filenames into a shared
   scratchpad and one overwrote the other's builder. One page context also had a crop
   file overwritten mid-read by a sibling and briefly read a different page's table.
   Neither reached an artifact, both were caught by the contexts themselves, and both
   would have been silent failures with slightly worse luck.

## Known cosmetic artifact in the deliverable

The `cyanide` record carries two analytics entries for the 1327 ppm figure and two
for the below-100 ppm bound. That is not a duplication bug: the patent prints its
closing sentence twice, once in the abstract and once verbatim at [0026], so two
sections each recorded the mention they saw. `finalise.py` unions `analytics` keyed on
the whole entry, and the two entries differ in their `conditions` commentary, so both
survive. One of the two 1327 values is typed as an integer and the other as a float,
which is a real inconsistency between two sections and has no effect beyond making
the pair look less obviously like one measurement seen twice.

## What the completeness evidence cannot see

Reading A found one genuine miss and one hole in its own machinery. The hole is the
more important of the two.

**The miss.** The patent names CDCl3 once, at [0054], as the NMR solvent. Every
correctness check passed over it: it was recorded as `nmr.solvent` on tembotrione, so
the datum was not lost, but no compound record held it. Both existing runs carry the
NMR solvent as a compound under the identifier `chloroform`, so this was a real
recall failure against the pack's own convention, and step 6 is the only thing in the
pipeline that could have found it. It is now a record, identifier `chloroform` to
join the other two runs, alias `CDCl3`, with a note saying that the identifier drops
the deuteration and why it is used anyway.

**The hole, and it is a `GUARDS-THAT-PASS-ON-ABSENCE.md` shape.** `verify.py` checks
reading A's spans against the ENGLISH rendering of each line, and for an
`[IMAGE_EXTRACT]` line that rendering is `describe_drawing(raw)`, which emits the
formula and the SMILES of each drawn structure and DISCARDS the reagent names from the
vision pass's `conditions` text. Lines 97 and 153 of this document name SOCl2,
cyclohexane-1,3-dione and acetone cyanohydrin as drawn labels. Reading A cannot file
any of them, because no span naming a reagent is a substring of the English it is
checked against, so those two line keys are necessarily empty.

The three reagents survive in the file only because the same three are also named in
prose elsewhere. **A reagent that appeared ONLY as a label on a drawn arrow would be
invisible to reading A, and the recall sweep would report clean.** That is precisely
the failure mode this repo's own contract file describes, and it means the sweep's
verdict on drawn-only reagents is not evidence either way. Reading A verified this
itself by importing `verify.Source` and dumping `text_en` for all 285 lines rather
than reimplementing the mapping, and it also established that no line's `text_en`
contains a single Han character, so there is no line in this document where a Chinese
span would have been correct.

Two smaller things reading A established that are worth a reviewer's time:

- **The paragraph clamp makes the engine's own substring test too weak.** `_pair_blocks`
  marks lines 44 and 45 and lines 50 to 56 `approximate`, and every line in such a
  block receives the WHOLE paragraph's English. All seven Chinese lines of claim 1
  therefore share one 810-character string containing every solvent, both adsorbents
  and the acid, so line 52, which reads only 加入吸附剂, would accept a span saying
  "diatomaceous earth", and line 41, which is just the field label (54) 发明名称,
  receives English containing "tembotrione". The engine's check cannot detect that.
  Reading A added its own guard for it: a span filed on a Chinese line must also have
  its Chinese counterpart on that same line. That guard caught three false positives
  in its own first build.
- **Casing and spelling split one substance into several spans.** 32 distinct spans
  cover 20 substances. "Tembotrione" capitalised at the start of a sentence is a
  different string from "tembotrione"; the acyl chloride's English is spelled
  "methylsulfonylbenzoyl chloride" on three line pairs and
  "methanesulfonylbenzoyl chloride" on a fourth, for one Chinese name.

## The verify gate is red, and this is what it is objecting to

19 grounding claims are not on the lines their own record cites. All 19 are
explicable and none is a fabricated value. Two more were real and are fixed:

- **16 are `conditions.time_h = 1`.** The source prints the hold time as 保温一小时,
  one hour in the Chinese numeral, and the English pairing says "one hour". The gate
  looks for the digit and finds it only on lines the record does not cite. Converting
  一小时 to 1.0 is the same class of operation as mol to mmol, which A1 rule 12
  expressly allows, and the schema field is a number, so there is no representation of
  this condition that the gate can ground. Batches 2 and 6 do ground, because the
  patent prints their hold times as 0.2小时 and 2小时 with digits, which is clean
  evidence that the numeral is the whole cause.
- **2 are the substance `cyclohexanedione`**, filed by reading A from lines 95 and 155
  where the patent prints the name with no locant. The gold's identifier is
  `cyclohexane-1,3-dione` and carries the locant-free form as an alias, so the molecule
  IS recorded; the gate matches identifiers rather than aliases and cannot see that.
- **`water` on line 219 and `CDCl3` on line 280 were the two the gate was right
  about, and both are fixed.** CDCl3 was a missing compound record; water was a
  missing provenance line on a record that did hold it. Reading A found both.
- **1 is a provenance quote on tembotrione.** The abstract's first sentence and claim
  1's first sentence are the SAME Chinese sentence, printed twice. The gate resolves
  the quote to English and finds it on the abstract's English line rather than on the
  claims lines the record cites, because the two English renderings of one sentence
  differ slightly. The citation is correct; the collision is between two identical
  Chinese sentences with two different translations.

AGENT.md says a failing verify gate is not automatically a defect in the work, and
that on the reference patent it is red on purpose. This is that case: the gate is
reporting the limits of what it can match, not values the annotation invented.

## Gate and check results

| gate | result |
|---|---|
| structures | **PASS with zero curated entries.** 3 identifiers carry chemistry, all 3 resolve. 5 of 5 drawn molecules resolved. |
| translations, coverage | PASS. 227 distinct Chinese strings, all resolve, and all 285 source lines come out of the substitution in English. |
| translations, name fidelity | PASS. |
| translations, prose ratio | PASS. All 25 entries used in prose are within the 20x limit. |
| visual | PASS. 76 markers over 10 pages, 3 comparisons, 30 drawing claims, no Chinese in any curated value. |
| verify, grounding | FAIL, 19 claims, all explained above. Grounded 87.5%. |
| verify, line census | 234 of 285 lines cited; 5 uncited lines carry chemistry, each raised as a tier 2 claim. |
| `schemas/validate.py` | PASS, all five artifacts, after the assignee mapping fix. |
| verify, reviewer budget | PASS. 95 census claims, 13.8 min of the 15.0 minute budget at the 8.7 s p90 rate, 7.2 min at the measured medians. |
| `verify_selfcheck.py` | **35 pass, 3 warn, 0 fail.** |

The three selfcheck warnings are all the same fact seen three ways: 19 records carry
`mass_balance_implausible` and the engine's quantity checks find nothing wrong with
them, because the flag is standing in for a percentage that disagrees with the
numbers beside it and there is no mass in those records at all. The closed flag list
has no value for that, which is defect 6 in the list above.

## Six things a reviewer should look at first

1. **Example 6's thionyl chloride charge, and whether the material is the acid.**
   237.9 g is 2.000 mol, three equivalents against the acid to three figures and
   3.149 against the acid chloride the paragraph names. This is the only quantitative
   evidence in the document about which compound is really being charged, and the
   annotation deliberately keeps the printed name.
2. **The reduction column of all five tables.** 18 of 19 printed percentages do not
   follow from the two ppm columns beside them, and the column is not monotonic.
   Printed and computed values are side by side in
   `provenance/reactions-provenance.json`.
3. **Whether the drawn route is prior art or the invention's.** Two page contexts read
   the same route two ways. Nothing in the document settles it and the annotation
   does not.
4. **The nineteen batches' hold times.** Sixteen of them read 一小时 rather than a
   digit, and are the whole of the grounding gate's failure.
5. **`cyclohexanedione` without a locant.** OPSIN, given the name alone, returns the
   1,2-dione. The document fixes the 1,3 isomer, but only at [0029] and [0053] and in
   the drawings, not at [0009] or [0032] where the name is printed bare.
6. **Example 4's confound.** It says it compares adsorbents and it changes the solvent
   at the same time.

## Final counts

| | |
|---|---:|
| pages | 10 |
| enriched document | 285 lines, 84 paragraphs, 3 IMAGE_EXTRACT spans |
| A1 records, before merge | 100 across 15 sections |
| compounds, after merge | 25, and 0 molecules carried under more than one spelling |
| reactions | 38, matching the section map's estimate of 38 exactly |
| pathways | 11, ten section-scope and one patent-scope |
| structures resolved | 3 of 3 that carry chemistry; 19 of 25 identifiers overall; 5 of 5 drawn molecules |
| translations | 228 strings, all resolved; 24 hand-authored, of which 8 are overrides |
| hand-authored SMILES | **0** |
| reading A | 261 line keys, 361 mentions, 283 specific and 78 generic, 32 distinct spans |
| A5 findings | 55 over four artifacts: 4 critical, 14 major, 37 minor, with 71 checks recorded as passed |
| manifest | 131 artifacts over 17 stages, 21,658,244 bytes; deliverable matches output/ on all 11 copied artifacts |

Of the 55 audit findings, 12 changed the artifacts: the critical appearance merge, the
pathway `components` rule, rule 16's flag inheritance, the missing
`scale_discontinuity_in_chain`, the pH bound written as a value, the inverted solvent
composition on seven records, three `reactant_names` sets carrying non-reactants, four
null quantity objects, two `compound_class` tag collisions, two mis-roled
solubility-only solvents, and the missing NMR solvent found by reading A. The rest are
recorded as disagreements or as accepted limitations above.

## Postscript: the two repo defects were fixed after the run

The run above was completed with `run_pipeline.py` stopping at `merge` and
`validate.py` reporting one violation, and both were reported rather than worked
around. They were then authorised as code changes and fixed, and this run was
re-executed end to end against the fixed pipeline:

- `run_pipeline.py` now passes `--patent-id` to `merge_stages.py` and to
  `schemas/validate.py`, so the runner **reaches the end of all 18 stages** on a
  three-run checkout rather than stage 4.
- `finalise.py` now maps the assignee's legal form into production's vocabulary, so
  `validate.py` is clean on all five artifacts.

Nothing in the annotation changed. The only artifact fields that moved are
`parties.assignees[0].type`, from `"company"` to `null`, and the hashes and byte
counts that follow from it. `selfcheck` is unchanged at 35 pass, 3 warn, 0 fail, and
`verify`'s grounding gate is still red on the same 19 claims for the same reasons.
Every stage of the run was produced by the runner in its own order this time, rather
than driven by hand, which is worth more than the two lines it took.
