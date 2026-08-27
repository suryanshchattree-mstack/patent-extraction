# CN112645853A run notes

Preparation method for 2-chloro-3-alkoxymethyl-4-methylsulfonylbenzoic acid,
Jiangxi Tianyu Chemical Co Ltd, published 2021-04-13. Annotated 2026-08-27/28.

There was no run-notes file in the pack before this one. `CLAUDE.md` requires the
model provenance of everything a model wrote to be recorded in the run notes, and
the reference run has nowhere it did that, so this file starts the convention at
the top of the run directory.

## Which model wrote what, and why that matters here

**Every artifact in this run that a model produced was produced by the same model:
Claude Opus 5 (1M context).** The orchestrating session and every subagent ran on
it; no subagent was given a model override.

That covers all of it: the 20 vision page reads (V), the section map (A0), the 29
compound passes (A1), the 23 reaction passes (A2), the pathways pass (A3), the
patent record (A4), the four adversarial audits (A5), the independent completeness
read of step 6, and the 38 hand-authored quote translations.

`CLAUDE.md` warns that where the extraction missed something and the independent
read also missed it, nothing in the pipeline can see it. State the sharper version:

- **A5's independence here is context-independence, not model independence.** Each
  A5 audit ran in a fresh context that was never shown the annotating passes'
  reasoning or the convention files, and was told not to read the A1/A2 stage
  folders. That is what the pass is specified to be. It is NOT a second opinion
  from a different model, so a blind spot in the model's chemistry or its Chinese
  reading is invisible to the audit by construction.
- **The same is true of step 6.** The completeness read was delegated to a fresh
  context that saw only the numbered source, the English rendering per line and the
  reference run's format file, precisely so it would not be derived from the
  extraction. It was still the same model. Where it agrees with the extraction,
  that agreement is weaker evidence than two readers agreeing would be.
- The one genuinely non-model check in the run is `resolve_names.py`, the
  grammar-based OPSIN pass, and `mentions.py` (reading B, ChemDataExtractor) did
  not run: the artifact publishes `readers: ["llm"]` and every substance finding
  says "one reader only". That is the pack behaving correctly, not a gap I closed.

Two places where the single-model risk actually bit, and was caught:

1. The p08 vision read rendered 呋喃磺草酮 as "fenquinotrione". It is
   **tefuryltrione**, which the patent itself settles: [0002] prints the Chinese
   common name followed by "(Tefuryltrione)" in its own parentheses, and does the
   same for 环磺酮 "(Tembotrione)". Two other page reads (p01, p04) got it right, so
   the pages disagreed with each other, and the step-6 independent read flagged the
   line. Fixed by re-running pass V for page 08 in a fresh context and rebuilding
   the enriched markdown; the corrected read records the disputed name, what it was
   resolved to and the first-party evidence, so the earlier error is still visible.
2. Chinese typed by hand rather than sliced from the source got corrupted in three
   files: 磺 became 確 and 呋 became 呑. Every agent that ran its own substring
   assertion caught its own corruption; the three that reached disk were all
   written by agents killed mid-flight by an API spend limit before they could
   verify. Found by a repo-wide sweep, fixed by re-running those passes with an
   explicit instruction never to type Chinese.

## The chemistry, in one paragraph

Two steps, repeated across twenty examples. Methyl
2-chloro-3-(bromomethyl)-4-(methanesulfonyl)benzoate is cleaved to the alkali metal
carboxylate by a base in a tertiary alcohol (酯解 / 碱解), which the patent's own
[0060] says is the point: doing the ester cleavage FIRST avoids liberating methanol
in the presence of the benzylic bromide, and so avoids the
2-chloro-3-(methoxymethyl) impurity the prior-art order produces. The carboxylate is
then etherified at the benzylic bromide by an alcohol plus base, or by a pre-formed
alkali metal alkoxide, and acidified with concentrated HCl to the free acid. The
alkoxy group is left generic on purpose: with 2,2,2-trifluoroethanol it gives the
tembotrione intermediate, with tetrahydrofurfuryl alcohol the tefuryltrione one.

## What the run holds

| | |
|---|---|
| pages | 20, born digital, 21,576 characters of real text layer |
| sections (A0) | 29, covering all 607 lines contiguously |
| compound records | 280 raw over 29 sections, 43 after identifier merge |
| reaction records | 54 over 23 sections, all `reaction_id`s unique |
| pathways | 32 (31 section scope, 1 patent scope) |
| drawings | 38 recorded, matching 38 embedded scheme images exactly |
| step-6 independent read | 607 lines keyed, 1258 spans, 1258 verified on their line |
| A5 findings | 74 across four artifacts: 0 critical, 35 major, 39 minor |
| hand-authored | 2 SMILES, 7 translation entries, 38 quote translations |

## The most valuable finding: the patent's yields use the wrong molecular weight

Six examples (2, 3, 4, 6, 8, 9) print a two-step yield that does not reproduce from
their own printed mass and assay. All six are the trifluoroethoxy product. Computed
against that product's own MW of 346.710 they overshoot the printed figure by +0.41
to +0.58 points; computed against **348.804**, which is the MW of the OTHER product
of the same patent, the tetrahydrofurfuryl acid, all six land within -0.12 to +0.03.

The A5 reactions audit found this and it was then verified independently with RDKit.
The two acids differ by about 2 mass units, which is why it is invisible by eye. So
the discrepancy is an error in the patent's own arithmetic, not in this annotation,
and it is recorded rather than corrected.

Consequence that a reviewer must settle: `mass_balance_implausible` is raised on
only two of those six steps (Examples 2 and 6). Two A5 audits and one A2 pass all
flagged the inconsistency independently. It was deliberately NOT normalised by
feeding the audit's conclusion back into A2, because an A5 whose findings are
folded into the pass it audits stops being an audit. Flagging all six and none of
the other fourteen is the resolution both audits propose.

## Other disagreements recorded and not resolved

- **Sodium versus potassium, drawings against prose.** Five reaction records carry
  `drawing_text_conflict`. This was checked against the page pixels at 400 dpi
  before being believed: the mixed counter-ions really are printed that way. In
  Example 14 the scheme draws the sodium carboxylate with CF3CH2OK over the arrow
  while the prose calls the substrate the potassium salt; Example 10 draws the
  potassium carboxylate with NaOH over the arrow. Prose kept in the structured
  fields per the pass rules, both readings in the notes.
- **Potassium hydroxide made up as an aqueous sodium hydroxide solution**, printed
  twice, around lines 199/200 and 218/219. Both compounds extracted, conflict noted.
- **Solid hydrides and 85 or 96 percent solid hydroxides described as added 滴入**,
  dropwise. Transcribed as printed.
- **(RS) named in the prose where no stereo bond is drawn.** No stereodescriptor was
  added to any SMILES.
- **Examples 13 to 20 give step (1) only as "the same procedure as Example 1"**, so
  those records carry `cross_reference_unresolved` and `conditions_unresolved`.
- **The [0069] and [0077] schemes are chemically identical** although the examples
  differ in the prose. The vision pass suspected they were the same graphic; they
  are two distinct embedded images differing by 2 percent of pixels, i.e.
  re-rasterisation noise, so the finding stands as a real property of the document.

## Hand-authored, with the reasoning

**Two SMILES** at the structures gate, both confirmed with the operator before
commit, and both corroborated against the patent's own charges:
`sodium metal` = `[Na]` (formula Na, MW 22.990; printed charges imply 22.63 to
23.10) and `potassium metal` = `[K]` (formula K, MW 39.098; imply 38.66 to 38.89).
Those figures rule out the hydrides, which the patent charges separately.

**Two identifiers were exempted instead of drawn**, via `no_structure_needed`:
`2-chloro-3-(alkoxymethyl)-4-(methanesulfonyl)benzoic acid` and `the methyl ester of
the target compound`. Neither denotes one molecule. Drawing either would have
resolved a class the patent deliberately leaves open, which is the principle the
reference run states for its own `cyclohexanedione`.

**Seven translation entries**, including `浓盐酸` to "concentrated hydrochloric
acid" with `override: true`, because the gold's own alias resolved it to the
unqualified acid and the name-fidelity gate was right to object: the qualifier is a
fact about what was charged.

**38 quote translations** in `output/relevant_output/visual/quote-translations.json`,
a hand-authored input the visual stage reads from inside the deliverable. Without it
the index substitutes compound names inside Chinese prose and produces hybrids like
"苯甲酸盐在basic substance存在下与醇反应", which is how the English-only rule fails in
practice.

## Three latent pipeline bugs, none of which the reference run can expose

All three are in shared code and were fixed only with the operator's explicit
approval. Each is invisible on CN104292137A and fires on the second patent.

1. **`run_pipeline.py:220` invokes `merge_stages.py` with no `--patent-id`.** It is
   the only stage that does. `pipeline_context` refuses to guess between two runs,
   so the stage failed the moment a second run directory existed. Worked around
   with `ANNOTATION_PATENT_ID`, which the module documents; NOT patched, because the
   fix is one argument and belongs to whoever owns the runner.
2. **`biblio.schema.json` and `patent.schema.json` disagreed about assignee type.**
   biblio accepted `company`; patent requires one of
   `multinational_corp | sme | university | government | individual | consortium`;
   `finalise.py` copies the value across with no mapping. The two enums intersected
   only at university, government and individual, so **no company-assigned patent
   could ever validate**, and the pack did not know because its one worked run is
   assigned to a university. Fixed by moving biblio's enum to production's
   vocabulary; this patent's assignee is `sme`. The reference still validates.
3. **`make_svgs.py` m2-route could not fit a target name longer than one line.**
   `Canvas.text` reserves `size*1.08` of height while `Canvas.wrap` spaced lines at
   `lh=15`, so at size 14 any two-line product name overlapped itself, and the "the
   target" caption sat at a fixed offset the second line overran. The reference
   escapes because its target is called tembotrione. Fixed by sizing the box and the
   caption from the actual line count and adding a shared `wrap_lines` helper.

Also worth an owner's attention, not fixed:

- **`merge_stages.py` computes `target_compounds` from `is_section_product` on
  REACTION records**, a field neither the A2 prompt nor the reaction schema defines.
  It is therefore always `[]`, in this run and in the reference, and A4 is fed an
  empty target list on every patent.
- **Several rendered prompts describe the reference patent as "this document".**
  `render_prompts.py` substitutes the patent id but not the patent-specific prose,
  so A1 rule 20, A2 rules 1, 5, 5e, 5f, 27 and 29, and A3 rule 3 all assert things
  about CN104292137A: step markers of the form `N、`, a scheme the vision pass marked
  `unclear`, eight prose steps against nine drawn ones, "at least three steps whose
  arithmetic does not close", a sulfonylating agent. None is true here. Correction
  files were written for A1, A2 and A3 and the passes were told the corrections win.
  A future run on a third patent needs the same treatment, and the passes will
  otherwise hunt for chemistry that is not there.
- **`pipeline/svg/` is a shared tracked directory**, so each run's diagrams
  overwrite the previous run's. It has been restored to the reference's diagrams
  here; the per-run copies live in each run's `relevant_output/svg/`.

## One deliberate normalisation of a stage artifact

A1 wrote `quantity: {mass_g: null, ...}` where the reference writes
`quantity: null`. Because `merge_compound` replaces a populated value wholesale and
a null-filled object is not empty, the last-sorting section erased every mass in the
merged gold: **0 of 43 compound records carried a mass**, against 22 of 75 in the
reference. `summary-of-the-invention` sorts after every example and states only
ranges, which is what did most of the damage.

With the operator's approval this was normalised deterministically across 120
sub-objects in 27 section files: where every member of `quantity`, `nmr` or
`melting_point` was already null, the object was set to null. No extracted value
changed, which is why the four A5 audits already completed against these artifacts
were not invalidated. 12 of 43 records now carry a mass and selfcheck's sensitivity
check passes. The underlying cause was my own convention file, which never stated
the rule; A1's rule 17 does state it, for characterisation fields.

## Where the run stops, and why it is not `done`

All 18 stages run. The manifest is clean and the deliverable matches `output/` on
all 11 copied artifacts. Both coverage gates pass. The `visual` gate passes. The
`verify` gate fails, and so does it on the reference run, on the same check: it
objects that 46 claims quote numbers that are not on the lines their own record
cites (the reference has 12 of these). Proportionally that is 5.0 percent of claims
against the reference's 3.0 percent.

`selfcheck` reports **35 pass, 1 warn, 2 fail**, and both failures are one fact:

    census (tier 1 + 2)   322 claims
    at the measured medians  25.9 min
    at a flat 8.7s p90       46.7 min   budget 15.0

`contracts/REVIEW-PROTOCOL.md` sets the budget from what the user said they would
give ("15 minutes because there could be hundreds of annotations"), which buys about
103 claims at the pessimistic rate. It also says tier 1 should be "tens, not
hundreds"; here it is 227.

This is a property of the document, not a defect that can be annotated away. The
patent has twenty examples where the reference has one, so the same facts recur:
water volume 18 times, the methyl ester mass 12 times, `yield_identity` 19 times.
Tier 1 is 26 percent of claims against the reference's 19 percent, so grounding
quality is comparable rather than collapsed, and even eliminating every one of the
217 tier-1 grounding failures would leave about 105 census claims, still over. It
was measured, not assumed: widening reaction provenance to the lines its own
`procedure_text` covers grounds zero additional quantity numbers.

So the budget cannot be met for this patent by any change to this annotation that
does not delete true records, and the pinned 15.0 must not be edited, because it is
a measurement of what a human agreed to spend. The real fix is pooling claims that
repeat across structurally identical examples: the engine already pools substance
tickets 28 instances into 17, and the protocol's own stated aim is spending the
reviewer's attention "where they buy the most information". That is a change to the
verification engine and is not this run's to make.

Status in `TARGETS.md` is therefore `blocked`, not `done`, with the census as the
reason. Everything a reviewer needs is on disk and current.
