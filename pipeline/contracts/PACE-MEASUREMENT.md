# What the review queue actually costs per claim

REVIEW-PROTOCOL.md sets the whole three-tier design on one number: "a realistic 6
seconds per claim on a good UI". That number was assumed, never measured. This is the
measurement.

Measured 2026-08-27 against the queue at `http://127.0.0.1:3100/CN104292137A/review`,
seed 756563520, on the artifact holding 394 claims: tier 1 census 78, tier 2 census 15,
tier 3 population 301 sampled at 50.

## The headline

**Net median 5.3 s per claim, p90 8.7 s, worst 15.1 s, over 20 claims.**

The census as it is built today fits the budget on the median and busts it on the
pessimistic reading. Demoting `not_checkable` out of the census makes it fit on every
rate measured, and is the difference between a protocol that works if the reviewer is
fast and one that works regardless.

| census | at 5.3 s (median) | at 8.7 s (p90) | at 10.4 s (gross) |
|---|---|---|---|
| as built, 93 claims | 8.3 min, **fits**, 76 of 301 sampled after | 13.4 min, **fits**, 10 sampled after | 16.1 min, **OVER**, 0 sampled |
| minus `not_checkable`, 64 claims | 5.7 min, fits, 105 sampled after | 9.2 min, fits, 39 sampled after | 11.1 min, **fits**, 22 sampled after |

At the pessimistic rate the current census does exactly what the protocol says must
never happen: it eats the whole budget and tier 3 gets zero samples, so the report
loses its confidence bound. At 64 claims that failure mode disappears.

## Read this before you use the number

**This measures an agent, not a person.** I am not a human reviewer and I read faster
than one. What transfers from this measurement is the *structure*: which claim types
are expensive, how much of the census is redundant, and which screens cannot be
answered at all. What does not transfer is the absolute second count. Treat 5.3 s as a
floor for a fast reader, not as a prediction.

**Gross and net are different questions.** Every claim here cost one harness round
trip, measured separately at **5.05 s** (three consecutive empty calls: 4.67, 4.93,
5.54). Net subtracts it and is the reading-and-deciding time. Gross includes it. A
human's equivalent per-claim interaction cost on a keyboard-driven UI with 1/2/3
shortcuts is far below 5 s, so the truth for a human is nearer net plus a keystroke,
with their slower reading pushing the other way. Both columns are given because I
cannot honestly collapse them.

**Method.** The queue advances on client state with no URL for the current question, so
I could not fetch question N directly, and answering through the API would have written
junk verdicts into a shared file. Instead I rendered each claim from the same artifact
the page reads, through the app's own `buildQueues`, restricted to the fields the screen
displays. The reconstruction agrees with the live page exactly: 78 / 15 / 50 and seed
756563520. Timestamps were taken at the instant each claim was put in front of me and at
the instant I moved on, so the gap is real deliberation.

**I judged only from the screen.** Every time I wanted something it did not give me,
that is recorded below as a defect rather than resolved from what I already knew.

## Per claim

| claim | tier | about | kind | gross | net |
|---|---|---|---|---:|---:|
| yield_identity | 1 | patent | quantity | 8.65 | 3.60 |
| product_yield_pct | 1 | patent | quantity | 8.57 | 3.52 |
| validation_flags | 1 | patent | judgement | 10.18 | 5.14 |
| yield_identity | 1 | patent | quantity | 7.48 | 2.43 |
| mass_g | 1 | patent | quantity | 5.22 | 0.17 |
| mmol | 1 | patent | quantity | 10.56 | 5.51 |
| product_yield_pct | 1 | patent | quantity | 5.94 | 0.90 |
| validation_flags | 1 | patent | judgement | 10.88 | 5.83 |
| yield_identity | 1 | patent | quantity | 23.81 | 8.67 |
| mass_g | 1 | patent | quantity | 11.32 | 6.28 |
| mmol | 1 | patent | quantity | 9.97 | 4.92 |
| mass_g partial | 1 | extraction | judgement | 15.80 | 10.75 |
| schema time_h | 2 | schema | schema | 10.84 | 5.80 |
| schema time_h | 2 | schema | schema | 10.95 | 5.90 |
| quote containment | 3 | extraction | quote | 11.58 | 6.53 |
| quote containment | 3 | extraction | quote | 9.56 | 4.52 |
| yield pct | 3 | extraction | quantity | 7.09 | 2.05 |
| molar_ratio_text | 1 | extraction | pointer | 10.60 | 5.55 |
| provenance.quote | 1 | extraction | quote | 9.97 | 4.92 |
| resolved | 1 | extraction | judgement | 20.12 | 15.08 |

## Which claim types are slow

By kind, net median:

| kind | n | median | worst |
|---|---:|---:|---:|
| judgement (`validation_flags`, `resolved`, unit-inference) | 4 | **8.3 s** | 15.1 s |
| schema | 2 | 5.8 s | 5.9 s |
| pointer (`molar_ratio_text`) | 1 | 5.6 s | 5.6 s |
| quote containment | 3 | 4.9 s | 6.5 s |
| quantity (does the patent say N) | 10 | **3.6 s** | 8.7 s |

**The expectation that `about: patent` claims would be much slower is wrong, and the
reason matters.** Patent claims came in at a median of 4.9 s against 5.6 s for
extraction claims. That is not because confirming a judgement is cheap. It is because
56 of the 78 tier-1 claims are labelled `about: patent` but only 8 of them are actually
judgements; the rest are `Does the patent say 34 g?` string matches that happen to sit
on a record carrying a patent-defect flag. The label describes the record, not the work.

The real split is **judgement 8.3 s against quantity 3.6 s, a factor of 2.3**. Sort the
census by that and you have a much better predictor than `about`.

## Where the time actually goes

**Reading the evidence, and reading it twice.**

- **39% of all evidence characters on this screen are exact duplicates.** 984 of 2,494
  evidence lines repeat text already shown on the line above. **376 of 394 claims** show
  at least one duplicated line. Median evidence per claim is **1,781 characters, or 917
  after removing the duplicates.**
- The mechanism is not a mystery: a cited Chinese line and its English partner are both
  resolved to English and both rendered, so line 187 and line 188 print the same
  sentence, both chipped `English translation`. Every claim I saw did this.
- **This is the single largest and cheapest pace win available.** Roughly half the
  reading on the screen is re-reading.

**Not deciding.** Once the evidence for a record has been read, the second and third
question on that record are nearly free: net 0.17 s and 0.90 s on claims 5 and 7. New
record median 5.9 s, repeat record median 4.9 s, and the repeat mean is 3.9 s against
6.9 s for a new one. The queue already groups by record, which is why the median is as
low as it is. Anything that breaks that grouping will make the whole census slower.

**Hunting for what the screen did not give.** Three of the twenty claims could not be
answered from their own screen. Those are the defects below, and they are the most
expensive claims in the set: the two worst times, 15.1 s and 10.8 s, are both this.

## How repetitive the census is

Two question shapes cover **84% of all 394 claims**:

| n | question shape |
|---:|---|
| 176 | Is the text this record quotes actually on the source lines it cites? |
| 156 | Does the patent say N of X? |
| 24 | The annotation says the PATENT is defective here. Was it right? |
| 10 | Line N prints N h, and `conditions.time_h` cannot hold it. Schema change worth it? |
| 8 | The patent's own numbers for this step do not agree. Does the page really print N? |

Tier 1 questions 1 to 40 are eight repetitions of the same five questions against eight
reaction records. That repetition is why the median is 5.3 s and not higher, and it is
also why the census buys less information than its size suggests: 40 claims to confirm
the arithmetic of 8 records.

## The 12 schema claims

**The screen makes it obvious, and it is the best-written screen in the queue.** It says
in as many words: *"Nothing here is wrong and nothing here can be marked wrong. This is
a schema ticket, not a review decision."* I did not sit there trying to judge something
unjudgeable. Net 5.8 s and 5.9 s, and both were spent reading, not deliberating.

Two problems remain, and neither is a UI problem.

1. **They should not be in a census at all.** The screen states that no answer can be
   wrong, and then asks for one. That is 12 of the 93 census claims spent on a decision
   that is not a verification decision. This is the concrete case for the demotion.
2. **Eight of the twelve are the same ticket.** Claims 86 to 93 are all "the patent
   prints a RANGE and `conditions.time_h` is a single number", against eight different
   lines. That is one schema ticket asked eight times. Deduplicating by ticket rather
   than by line would take the schema queue from 12 to about 3.

The question they ask, "Is a schema change worth it?", is also a product judgement, not
a reading of the evidence. A reviewer can answer it without looking at the evidence at
all, which means the evidence pane below it is pure cost.

## Defects: where the screen did not give me what I needed

Ordered by how much they cost.

**1. A claim asks whether quoted text is on the cited lines, and does not show the
text.** (tier 3, record `CSc1ccc(C(C)=O)c(Cl)c1C`) The question is "Is the text this
record quotes actually on the source lines it cites?" and the extracted value renders as
*"an English note rather than a quotation"* rather than as the note. There is nothing to
compare. Unanswerable as displayed. The same screen also says *"The machine found this
where the record says it is. Bulk-acceptable"* while the machine verdict directly above
says `not_checkable`; those two statements contradict each other.

**2. The record is identified by a raw SMILES.** Same claim: the record label is
`CSc1ccc(C(C)=O)c(Cl)c1C`. The entire premise of this protocol is a reviewer who does not
know chemistry, and that reader cannot tell what molecule this is. Every other record on
screen has an English name.

**3. A judgement claim does not carry the arithmetic that justifies it.** (`validation_flags`,
24 claims) The question is "The annotation says the PATENT is defective here. Was it right
to say so?" and the claimed defect renders as *"the masses printed for this step do not
balance"* with no numbers. I could only confirm it because I had read the arithmetic two
questions earlier on a different claim. A reviewer landing here first, or returning after
a break, cannot answer it. The numbers exist: they are on the `yield_identity` claim for
the same record.

**4. A cross-step claim shows only one step's evidence.** The same `validation_flags`
claim on Example 1 Step 2 bundles three flags, one of which is *"the amount carried into
this step does not match the amount the previous step produced"*. Confirming that needs
step 1's output, 28.6 g, which is not on this screen. Worse, three separate flags share
one yes/no answer, so a reviewer who agrees with two and doubts the third has no way to
say so.

**5. Two claims on one record give contradictory remedies.** On `Summary of the Invention
Step 1`, the `molar_ratio_text` claim says *"The fact is right and the pointer is wrong.
Move the citation to 77-78, 154-155"*, and the `provenance.quote` claim says *"The
citation stands and the quoted text does not come from it. Fix the quote rather than the
pointer."* Same record, same line-154 mismatch, opposite instructions.

**6. The question asks something different from the field.** (`resolved`, 5 claims, my
slowest at 15.1 s) The question is *"Is 'cyclohexanedione' really a compound the patent
names?"*, which is trivially yes, the patent prints it. The field is *"Whether this is a
definite molecule"*, which is the hard question: cyclohexanedione carries no locant and
1,2-, 1,3- and 1,4- are different compounds. Answering the field needs chemistry the
screen does not supply and the intended reviewer does not have. I marked it unsure.

**7. "Does the patent say 200 mmol?" when the patent prints "0.2 mol".** The machine
reports `found` with the note "The number 200 appears with its unit millimoles". The
evidence line reads `(0.2 mol)`. A reviewer answering the question as literally worded
marks this wrong. Normalised units are right, but the question should not claim the
document prints a string it does not print.

**8. Unit inference has no way to be recorded.** (`partial`, thionyl chloride) The patent
prints `thionyl chloride 71.4 (0.6 mol)` with no unit and the annotation records `71.4 g`.
Grams is certainly what was meant. But the only answers are correct, wrong and unsure,
and none of them says "value right, unit inferred". I marked unsure, which understates
what I actually concluded.

## What I would change, in order of pace bought per unit of work

1. **Deduplicate the evidence lines.** Frees roughly half the reading on every claim in
   the queue. Nothing else on this list comes close.
2. **Demote `not_checkable` out of the census**, 93 to 64. Turns a protocol that busts
   the budget at the pessimistic rate into one that fits at every rate measured.
3. **Put the arithmetic on the `validation_flags` claim** that is currently only on the
   `yield_identity` claim for the same record. Turns 24 unanswerable claims into
   answerable ones.
4. **Collapse the eight identical range-versus-float schema claims into one ticket.**
5. **Show the quoted text on quote-containment claims**, or drop the claim when there is
   no text to show. 176 claims ask this question.
6. **Name records in English, never by SMILES.**

## Reproducing this

The claim bodies were rendered through the app's own `buildQueues` from
`output/relevant_output/verification/checks-CN104292137A.json` with seed text
`CN104292137A`, and agree with the live page on all three queue sizes and the seed. The
timing method was one claim per round trip with a timestamp taken as the claim appeared;
the harness baseline was measured with three consecutive empty calls in the same session.
No verdicts were written and no source was edited.

## The census on a fourth patent, and two engine defects that inflated it

Measured 2026-08-28 on US20100041557A1, a BASF polymorph application: 786 source lines,
49 sections, 306 compound records, 61 reactions, 58 pathways.

The number above buys a capacity, not a target. At the 8.7 s p90 a 15 minute budget
admits **103 census claims** and nothing more. Every figure below is that same engine
run against the same gold, changing only the engine.

| state | census | at 8.7 s p90 | at the per-kind medians |
|---|---|---|---|
| as first built | 298 | 43.2 min | 24.6 min |
| after three annotation defects fixed | 197 | 28.6 min | 17.6 min |
| after the two engine defects below | 112 | 16.2 min | 11.7 min |
| after one under-citation fixed | 104 | 15.1 min | 10.5 min |

For scale, EP2045236A1 is the same subject matter with **more** source lines, 1078, and
a census of 32. The gap was never size.

**Defect 1, `build_coverage` asked about the machine's own English.** The sweep tested
`kind == "translation"`, and only the FIRST line of a translation carries the
`    > EN: ` mark. Every continuation line looks exactly like a line of the patent. Every
table in this patent is printed twice, once as source and once inside its own English
rendering, so 40 of 64 coverage claims were the English copy of a table row a record
already cites in the original. `is_en_output` and `en_hint` already existed for this and
the sweep did not consult them. A regex was tried first and is not sufficient: it reads
claim 16's own 2theta table as English, because a claim number does not close a run the
way a paragraph marker does.

**Defect 2, one fieldless failing check promoted an entire record.** `promoted_fields`
appended `""` for a check naming no field, and `""` is a prefix of every field name. Two
`completeness.unmapped` checks on the tembotrione record pulled all 33 of its claims into
the census. The two numbers behind them are "at least 95 wt. % consists of the
crystalline form A": a limit on what the patent claims, which no field on a compound
record can hold, and which recording as `purity_pct` would misreport as an assay.

## The 104 that remain, and why they are not a defect list

This run does not fit the budget and cannot be made to without recording something
untrue. What is left:

- **23 `conditions.time_h`.** The A2 prompt mandates hours (`50min -> 0.83`). The patent
  prints "about 40 mins" and the annotation records 0.67. The engine grounds a claim by
  finding its number on the cited line, so a mandated unit conversion is unfindable by
  construction. EP2045236A1 never met this: it records no `time_h` at all.
- **22 `__substance__` tickets.** Step 6's independent read, which is a census by design.
  These are NOT alias gaps: the systematic name is already an alias on the tembotrione
  record. The sweep requires the alias to sit on a record CITING that line, and the
  merged record's provenance does not cite the claims. That is a third join defect, left
  unfixed and recorded here rather than acted on.
- **5 `__coverage__` on unit cell angle rows.** `signals()` tokenises `90` as a
  temperature, so the three orthorhombic angles of form A and two of form C read as
  uncited chemistry. Citing the table would trade 5 tier 2 claims for tier 1
  `completeness.unmapped` findings, because the compounds schema has no field for a cell
  axis, a volume, Z, a density or an R factor. The A1 pass recorded that judgement and it
  stands.
- **6 `structure.second_reader`.** OPSIN disagreements, which CLAUDE.md rule 8 says to
  record and never resolve.

The honest reading is that 8.7 s is a p90 from 20 claims of one patent, and that at the
per-kind medians this run costs 10.5 min and fits. The budget was not changed to make it
pass, and the annotation was not thinned to make it pass either.

## The same two fixes, across every run on the branch

Re-measured 2026-08-28 after merging, so all six are one engine against unchanged gold.
`runs/CN104292137A/` is deliberately absent: rule 2 makes it read only, and regenerating
the file every other run is compared against is a maintainer's call.

| run | census before | census after | at 8.7 s p90 | selfcheck |
|---|--:|--:|--:|---|
| CN109678767A | | 85 | 12.3 min | 37 pass, 1 warn, 0 fail |
| CN111440099B | 95 | 53 | 7.7 min | 35 pass, 3 warn, 0 fail |
| CN112645853A | 321 | 316 | 45.8 min | 35 pass, 1 warn, 2 fail |
| EP2045236A1 | 52 | 32 | 4.6 min | 37 pass, 1 warn, 0 fail |
| US20100041557A1 | 197 | 104 | 15.1 min | 33 pass, 3 warn, 2 fail |
| WO2000021924A1 | 178 | 168 | 24.4 min | 33 pass, 3 warn, 2 fail |

How much a run moves is how much of it is a **paired** translation, and how many of its
paired blocks run past one line. The two Chinese runs whose enriched lines are mostly
substitutions barely move. CN111440099B nearly halves. The two rows that were blocked on
the budget are still blocked, and both overruns are now real rather than an artefact of
reading the machine's own English back as source.

The earlier fix this pair extends was measured the same way and is written up in the row 4
and row 6 notes of TARGETS.md. Between the two pairs, WO2000021924A1 went from 281 census
claims to 168, and none of that was ever a fact about the chemistry.
