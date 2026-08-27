# Verification contract

One file, written by the pipeline, read by the verifier UI. Everything the reviewer
sees comes from here. The UI computes no chemistry and no matching of its own.

    output/relevant_output/verification/checks-<PATENT_ID>.json

## Who the reader is

A manual reviewer who does NOT know chemistry. They are answering one question over
and over:

> Is this thing we extracted actually in the patent, and does it say what we say it says?

They have 15 minutes, maybe 30. There are ~114 records and several hundred field
values. They cannot read all of it, and they must not have to. So the machine does the
string matching first and the human only adjudicates what the machine could not settle.

Three consequences bind every producer of this file:

1. Every string that reaches a screen is ENGLISH. No Chinese, ever, anywhere in this
   file, including inside quotes, notes, reasons and labels. Use the translation index
   at `output/translations.json`. If a string cannot be translated, say so in English.
2. Every claim carries the evidence that would settle it, inline. A reviewer must never
   have to go and find the source text.
3. The machine states its own verdict first. The human's job is to agree or overrule,
   not to start from nothing.

## Top level

```json
{
  "patent_id": "CN104292137A",
  "engine_version": 1,
  "generated_at": "ISO 8601",
  "source": { "file": "...", "sha256": "...", "line_count": 256 },
  "summary": { ... },
  "claims": [ ... ],
  "records": [ ... ],
  "source_coverage": { ... },
  "completeness": { ... }
}
```

Written by `verify.py`. On CN104292137A the file is about 3.5 MB, because every
claim carries its evidence inline and that is the point: the reviewer must never
have to go and find the source text.

`generated_at` is the one thing that moves between two runs over unchanged inputs.
Set `SOURCE_DATE_EPOCH` to pin it and the whole file is byte-identical, which is
what makes a diff between two runs meaningful.

### Which lines a record "cites"

Every grounding verdict is relative to this, so it is contract, not implementation.

| source | rule |
|---|---|
| `reactions-provenance.json`, `source_lines` of length 2 | read as `[start, end]`, the whole inclusive range |
| `reactions-provenance.json`, length 3 or more | exact lines |
| `compounds-provenance.json` | exact lines, unioned over every row for that identifier |
| any cited Chinese line | also pulls in the English line it was translated into, by block pairing, per `SOURCE-PAIRING.md`. Never `n + 1` |

## `claims[]` - the review queue. THE most important array.

One atomic, human-answerable question. This is the unit the reviewer works through.
A claim is one field of one record paired with the evidence for it.

```json
{
  "claim_id": "sha256 of (record_id, field) truncated to 16 hex - STABLE across runs",
  "record_id": "CN104292137A_2-chlorotoluene",
  "record_kind": "compound | reaction | pathway | patent | source_line",
  "rec": "cmp:e63b6978-e898-5387-9bda-fde3f362ec1e",
  "rec_field": "quantity.mass_g",
  "record_label_en": "2-chlorotoluene",
  "section_en": "Example 1",
  "about": "extraction | patent | schema",
  "field": "quantity.mass_g",
  "field_label_en": "Mass charged",
  "question_en": "Does the patent say 25.3 g of 2-chlorotoluene?",
  "claimed_en": "25.3 g",
  "claimed_value": 25.3,
  "claimed_unit": "g",
  "basis": "quoted | derived",
  "cited_lines": [182, 183, 184, 185, 186, 187, 188],
  "evidence_en": "full English text of the cited lines, already translated",
  "evidence_lines": [ { "n": 187, "text_en": "...", "is_translation": true,
                        "kind": "prose", "pairing": "exact", "matched": true } ],
  "highlights": [ { "line": 187, "start": 39, "end": 43, "kind": "value" } ],
  "auto": "found | not_found | not_reconciled | partial | not_checkable",
  "work_kind": "judgement | comparison",
  "auto_reason_en": "The number 25.3 appears with its unit grams on the Chinese line 187 and on the English translation on line 188.",
  "needs_human": true,
  "load_bearing": false,
  "risk": 0.05,
  "risk_reasons_en": ["..."],
  "structure_svg_path": "output/relevant_output/structures/xxx.svg or null",
  "tier": 1,
  "stratum": "compound:Example 1"
}
```

`severity` and `severity_action_en` say what the reviewer will FIND when they get
there, which is a different question from which queue it is in. Five things must not
share one badge:

| `severity` | fires on | what the reviewer does |
|---|---|---|
| `critical` | the claimed value is on no line of the document at all | read this first; nobody can source the number |
| `high` | the patent's own numbers disagree with each other | confirm what the page says; the extraction is not at fault |
| `medium` | a judgement, an uncited line, or a field left empty | read the evidence and decide |
| `low` | the fact stands and the pointer or the quote is misplaced, or the schema could not hold it | fix the citation, or file a schema ticket |
| `none` | matched cleanly, or a derivation that checks out | nothing to do |

`critical` is reserved and it fires only on a value found nowhere in the document.
On CN104292137A it fires zero times, and that is the single most useful fact the
file states. A label that means everything means nothing, and this label is what
stands between the team and a fabricated number in a future run.

`tier` is the QUEUE, `risk` is the order within it. See `REVIEW-PROTOCOL.md`.

- `tier: 1` - a human must see it. Anything `not_found` or `partial`, any load-bearing
  `not_checkable` judgement, and any claim on a record with a failed structure,
  quantity or reference check. Small population, worked as a census.
- `tier: 2` - the candidate misses. The recall side, also a census, and it has THREE
  feeders: `__coverage__` claims for a whole line no record cites, `__quantity__`
  claims for one quantity on a cited line that no claim asserts, and `__schema__`
  tickets. Read only the first and you compute the denominator as zero while the
  queue holds work.
- `tier: 3` - the machine matched it cleanly. Sampled, never exhausted. This is the
  ONLY population the residual-defect bound may be drawn from, so nothing the
  machine failed to match may appear in it.
- `tier: 4` - the machine had NO OPINION: every `not_checkable` claim outside the
  recall census. Sampled, and deliberately NOT part of tier 3's bound.

**Why tier 4 exists.** The census was tier 1 plus tier 2, 93 claims, and the queue
has been timed at a 5.3 s median and an 8.7 s p90 over 20 claims. At the pessimistic
rate 93 claims consume the entire 15 minutes, tier 3 is sampled zero times, and the
report carries **no confidence bound at all**. That is the failure, not slowness.
Demoting the 29 `not_checkable` claims and pooling the schema tickets brings the
census to 55, which fits at every rate measured and leaves 48 tier 3 claims
samplable at the p90.

It is also correct rather than merely convenient. "The machine had no opinion" is a
different population with a different prior from "the machine looked and failed";
they should never have shared a census. And they must not join tier 3 either, whose
bound is specifically the residual defect rate among claims the machine MATCHED - a
claim it never matched would silently widen an estimate it carries no evidence about.

Read the 5.3 s with the caveat its author attached: measured by an agent, who reads
faster than a person, so treat it as a floor for a fast reader rather than an
average one. That makes the margin thinner than the median suggests, which is an
argument for the demotion and not against it.

`summary.tier_population` carries each tier's size twice: `claims`, counted off the
queue, and `population`, derived from where the work came from - the verdicts and
failing checks for tier 1, the uncited lines and unaccounted quantities for tier 2 -
with `from_en` saying so in English and `agrees` asserting the two match. A
denominator recovered from the list it measures cannot detect the one failure that
matters, a claim that was never emitted at all, which is exactly how tier 2 came to
hold fifteen claims while both of its old denominators read zero.

`summary.claims_by_severity` is the same idea for severity, and `summary.grounding_failed`
is true when any grounding claim is `not_found`, which is what makes the stage exit
non-zero. A failed DERIVATION does not set it: `quantity.yield_identity` and the
derived-field recomputations are arithmetic about the patent, not grounding, and
stopping the pipeline because the document contradicts itself would be wrong.

`stratum` is `<record_kind>:<section_en>`, so tier 3 can be sampled proportionally
instead of being dominated by whichever section is largest. `summary` must carry the
population size of each tier and the tier 3 breakdown by stratum, because a confidence
bound needs the denominator and it cannot be safely derived from a filtered list.

`rec` and `rec_field` are the verdict key `verifier/lib/verdict.ts` `resolveRec()`
understands: `rx:<reaction_id>`, `cmp:<compound_uuid>`, `pw:<pathway_uuid>`,
`pt:<patent_id>`. Emitted rather than left for the UI to reconstruct, because
reactions key on `reaction_id` and everything else keys on a uuid, and a consumer
that guesses one rule for all four writes verdicts that never load again. A
`__coverage__` claim has no slot in that convention, so it keys on the patent with
the line number in `rec_field`: `pt:CN104292137A` plus `__coverage__.line_48`.

`record_id` is the gold `id` wherever that is ASCII. Five of the 75 compound
identifiers in this gold are Chinese; those records get
`<patent_id>_zh-<10 hex of sha256(identifier)>` instead. The readable name is
`label_en`, the join key is `uuid`. The id is deliberately NOT derived from the
translation table: `claim_id` hashes it, this contract promises `claim_id` is stable,
and a hand-edited translation improving would otherwise orphan every verdict already
recorded against that record.

`about` is which question the claim asks, and it is not decoration:

- `extraction` - the annotation says X and the patent says Y. **We** are wrong.
- `patent` - the annotation says the patent contradicts itself. The annotation is
  **right** and the document is defective.
- `schema` - the annotation read the document correctly and the field it had to put
  the answer in could not hold it. Nobody is wrong and re-running the extraction
  fixes nothing. This one needs a schema change, which is a different fix from the
  other two, which is the whole reason it is a separate value.

Blurring them asks a reviewer to mark a correct annotation as wrong. `FINDINGS.md` is
explicit that its items are defects in the patent and that the annotation records them
and changes nothing; that posture survives into `question_en`, which is worded from
`about`. `summary.claims_by_subject` counts both.

`basis` says whether a numeric field is one this patent QUOTES or one the annotator
DERIVED, inferred per patent from the data rather than hardcoded: a field where no
value at all appears on any cited line is derived. A derived field is never scored as
ungrounded - it is recomputed instead, and `auto` reports whether the arithmetic
holds. `summary.field_basis` shows the inference and its evidence. On CN104292137A
every numeric field turns out to be quoted, `mmol` included, because the patent prints
molar amounts in mol and the matcher is unit-aware.

`highlights` are offsets into `evidence_lines[i].text_en`, so the UI highlights without
re-deriving anything. `kind` is one of `value`, `unit`, `name`, `condition`, `yield`.

`evidence_lines[].pairing` is `exact` where the Chinese line and its English paired one
for one, `approximate` where the block lengths differed and the English had to be
clamped, `none` where the block has no English at all, `self` where the line is its own
translation. `matched` marks the lines that carried the match. `is_translation` is true
when what is shown came out of a translator - the machine translation of a Chinese
line, or a `> EN:` line, which is that translation written into the file - and false
for a line whose own characters are already English: the NMR shifts, the drawn-
structure spans, the page markers. The Chinese is the authoritative text in this
document, so a reviewer weighing evidence has to know which of the two they are
reading.

An `[IMAGE_EXTRACT]` line is rendered as a sentence, not as its JSON: "Drawn on the
page: 1 structure. C8H9ClO2S (Cc1c(Cl)cccc1S(C)(=O)=O)." The drawn scheme is the only
evidence a Scheme Step record has, and handing a reviewer 4 kB of raw span and asking
them to find the chemistry in it is not evidence.

`auto`:
- `found` - the machine located the claimed value in the cited evidence. Low risk. The
  reviewer can bulk-accept these.
- `partial` - located some of it. Needs a human. Also where a value is printed without
  its unit, where it is in the translation but not in the authoritative Chinese, and
  where a quote is split across cited and uncited lines.
- `not_found` - the machine could not confirm the value: it is not in the cited
  evidence, or, for a `derived` field, the derivation does not reproduce it. HIGHEST
  risk. This is the hallucination signal and it goes to the top of the queue.
- `not_checkable` - the claim is a judgement (a role, a reaction class, a flag the
  annotation raised about the patent) that no string match can settle. Needs a human,
  but is not evidence of a defect. `load_bearing` separates the ones a human must
  actually see from the ones that are merely unmatchable.

`not_found` and `not_reconciled` are separate verdicts and must stay separate.

- `not_found` - the claimed value is NOT on the lines this claim cites. This is the
  hallucination signal and the most load-bearing label in the file. A consumer
  filtering `auto` to answer "how many possible fabrications" reads this and nothing
  else, so it must never carry anything but that meaning.
- `not_reconciled` - the value IS where the record says it is, and the patent's own
  numbers do not multiply out. `quantity.yield_identity` and a failed derived-field
  recomputation both land here. It is not about citation at all, it is never the
  annotation's fault, it carries `about: "patent"`, and it does NOT trip the
  grounding gate.

On CN104292137A the split is 5 and 8. Folded together the file would report 13
possible fabrications when the answer is 5, and nothing in the value would say
otherwise. `severity` draws the same distinction one layer up, but a consumer that
filters on `auto` never reaches `severity`, which is why the split has to exist at
both layers rather than only at the one a careful reader of this contract would find.

`work_kind` is what the reviewer DOES with the row, which is not what `about` says.
56 of this patent's original tier-1 claims were labelled `about: patent` and only 8
were judgements; the rest were "does the patent say 34 g" comparisons that happened
to sit on a record carrying a patent-defect flag. `about` describes the record;
`work_kind` describes the work, and the measured cost differs by a factor of 2.3:

| `work_kind` | measured median | what the reviewer does |
|---|---|---|
| `judgement` | 8.3 s | read the evidence and form an opinion; nothing is highlighted because the machine had nothing to locate |
| `comparison` | 3.6 s | look at the highlighted span and agree or overrule |

The test is whether the machine has a located thing to put on screen, NOT whether
there is a number. A quote it located and highlighted is a comparison even though it
carries no `claimed_value`. Keying on the value instead classified all 176 quote
claims as judgements and put 163 of them in tier 3, which would have told a UI that
sampling tier 3 costs twice what it does.

`summary.claims_by_work_kind` and `summary.work_seconds_measured` carry the counts
and the timings, so a UI can show a real budget rather than a flat per-claim guess.

`needs_human` is the queue filter. `risk` orders it, descending. It is normally
`auto != "found"`; a claim promoted into tier 1 because a check on its own row failed
also gets `needs_human: true` while keeping `auto: "found"`, because the number is
printed where the record says it is AND the row does not add up, and both are true at
once.

## `records[]` - the per-record roll-up

```json
{
  "record_id": "...", "record_kind": "...", "uuid": "...",
  "label_en": "...",
  "claim_ids": ["..."],
  "checks": [ { "id": "structure.formula", "family": "structure",
                "status": "pass|fail|warn|skip", "title_en": "...",
                "detail_en": "...", "needs_human": false } ],
  "risk": 0.0, "risk_band": "high|medium|low"
}
```

Check families, and what each one catches:

| family | catches |
|---|---|
| `grounding` | a quote or a number that is not in the source it cites. Hallucination. |
| `reference` | a reaction naming a compound that does not exist, a pathway step with no reaction. Orphans. |
| `structure` | SMILES that will not parse, a formula that disagrees with the drawn structure. |
| `quantity` | mass and mmol that disagree with the molecular weight, and the yield identity below. |
| `consistency` | the same molecule given two different structures, or two records for one thing. |
| `drawing` | the structure read off the page image against the gold's structure for the same named molecule. Two independent readings disagreeing is a hard defect. |
| `completeness` | something the patent states that no record holds. |
| `schema_loss` | the patent states it, the annotation read it right, and the field that would hold it is too small. |

Each check also carries `about_fields`: the claim-field prefixes it concerns, or
empty for a check about the whole record. This is what keeps tier 1 readable.
Promoting every claim on a record with one failing check puts about a hundred
cleanly-matched numbers in front of a reviewer who has time for fifty items, purely
because one row of the same reaction failed a mass balance.

`records[]` also carries `uuid`, `rec`, `section_en`, `stratum`, `cited_lines` and
`annotation_flags_en`, the last being the annotation's own `validation_flags` said in
English, so a check that rediscovers one can say the annotation flagged it too rather
than presenting it as new.

## Quantity coverage - the stronger recall test

Line coverage answers "did any record look at this line". It cannot answer "did any
record take what was on it": a line can be cited by one record while carrying three
facts with two of them dropped, and `uncited_with_chemistry` still reads zero.

So every cited line is tokenised into (value, unit) pairs and each one is matched
against what a claim on a record citing that line **structurally asserts** -
`claimed_value` and `claimed_unit`, never the prose of a quotation. Matching against
quoted text is the trap that makes this check meaningless: a "16" occurring anywhere
inside any quotation would count as coverage of a sixteen-hour reaction, and the
sweep returns a clean zero that means nothing.

Rules that make the number trustworthy, each of which removed a false alarm when it
was added:

- Only tokens carrying a unit count. A bare number is a locant, an index or an NMR
  proton count, and sweeping those reports the whole of Example 1 as dropped.
- Matching is unit-aware. 0.22 mol on the page answers 220 mmol in the record.
- A Chinese line and the English it was translated into are one block, so one
  printed quantity is not counted twice.
- A range is one fact. Its endpoints merge before anything is queued, so "1-10 h"
  is one row and not two.
- A volume printed immediately before the word for a flask is glassware, not a
  charge. Counted, never queued.
- A percentage is a yield or a concentration by the words beside it, never by which
  field happens to be free. 36% HCl read as a yield because `product_yield_pct` was
  occupied is a false second stage.
- Quantities are said back in the unit the page prints. "50 min" rendered as "50 h"
  is the matcher lying about the document.

An unaccounted quantity becomes a tier-2 claim with `field: "__quantity__[<line>:
<value><unit>]"` and a `quantity_verdict`, which is the finding:

| `quantity_verdict` | `about` | what it means and what fixes it |
|---|---|---|
| `schema_loss_range` | `schema` | the patent prints a range, the field is one number. Widen the schema. |
| `schema_loss_second` | `schema` | the step has two stages and the field has one slot. Make the field a list. |
| `gap` | `extraction` | the field exists and is empty. Re-extract. |
| `unmapped` | `extraction` | no field of that kind exists on any record citing the line. Design question. |

`summary.quantity_coverage` carries the tally and every finding.

**Schema losses are pooled into tickets, one per (limitation, field).** Eight of this
patent's twelve schema losses are the SAME question - a range against a single-float
`conditions.time_h` - asked against eight different lines. A reviewer answering one
question eight times is the clearest waste the queue can contain, so the twelve
instances become three claims with `field: "__schema__[<kind>:<path>]"`, each
carrying every instance in `schema_instances` and in its reason text. Every affected
record still carries its own failing check, so nothing is hidden; only the question
is asked once. `quantity_coverage.schema_loss` counts INSTANCES and the tier 2
population counts TICKETS, which is why they differ.

## The recall sweep for substances - "is this all", for names

`uncited_with_chemistry` reported **0** for as long as it existed, and that was never
evidence that nothing was missed. Coverage is decided per LINE and a line counts as
covered the moment any record cites it: 222 of 256 lines are covered, and a
730-character line carrying eight facts reads exactly as covered when three were
captured.

One sub-line sweep existed and it covered numbers only. Of the seven signal kinds the
engine tags on a line, five had a sweep behind them and the two largest did not:

    signal        lines   swept before?
    reagent         146   NO      <- the most common thing in the document
    duration         32   yes  __quantity__
    temperature      24   yes
    ratio            20   yes
    quantity         16   yes
    yield            16   yes
    structure         9   NO

So the pack could say *every number the patent prints is in a record or reported as a
gap* and could say nothing whatever about the substances it names.

`substance_coverage` is the same sweep with a different tokeniser and a different key.
Both run through `line_sweep`, which owns the walk, the ZH/EN block dedup, the
accounted/excused/missed taxonomy and the pooling into tickets.

**`asserted` is built from what a record IS, never from what it QUOTES.** This is the
same trap the quantity sweep documents and it is worse here: a procedure quotes the
name of every substance it uses whether or not any field holds it, so matching on
quoted prose reports a clean zero that means nothing. The index is built from each
record's own `identifier` and `aliases` fields.

**The join is on canonical SMILES first, on the normalised name only when no structure
can be had, and which one fired is on the finding.** `gold/structures.json` holds 18
SMILES for 11 molecules because the drawn scheme is read more than once and the reads
name things differently, and 12 of the 16 drawn names match no record name. A name
join alone would report molecules the patent DRAWS as missing.

Three outcomes:

| outcome | claim | what it means |
|---|---|---|
| `accounted` | none | some record citing this line names this molecule |
| `unaccounted` | yes, `not_found` | nothing does. Pooled by record into one ticket carrying every instance. |
| `named_not_identifiable` | none | the span refers to a substance without naming one |

**The third bucket is not a stoplist and that distinction matters.** 92 mentions on
this patent name no molecule: "the mixture", "the organic layer", "an inorganic base".
Queued they would be 92 rows a reviewer learns to skip, which is worse than no sweep.
Deleted by a stoplist they would take `the catalyst` with them, which appears twelve
times and is sometimes an anaphor pointing two lines up and sometimes the finding -
the patent says "a catalytic amount of aluminium trichloride" and no record kind has a
catalyst slot. So they are counted, shown on the section screen, and never queued.

**Tickets are pooled by record**, exactly as schema losses are. Four substances missing
from one record is one question about one record with four things listed on it. The
census has limited headroom before it stops fitting a fifteen-minute budget, and a
queue nobody finishes is indistinguishable on every screen from a clean one.

**`readers` is published beside the tally.** One reader and two readers agreeing
produce the same finding count and mean completely different things, so every ticket
carries the set of readers that saw it and says "one reader only" when there was one.
A reader that cannot run writes nothing rather than an empty file: an empty
`substances-cde.json` reads on every screen as "ChemDataExtractor found nothing wrong".

**Per line, five states**, written onto `source_coverage.lines`, and `unread` is the
one worth having. A line nobody read and a line read with nothing on it are the same
absence in any file that records only hits, and on a screen where green means "nothing
here is unaccounted for" they would both be green.

    unaccounted  something printed here is in no record. THE FINDING.
    accounted    substances printed here, all of them in some record
    none         a reader looked and no substance is named here
    named_only   only generic references
    unread       NO reader has looked at this line

On CN104292137A: **376 distinct mentions on cited lines, 277 accounted, 92 naming no
molecule, 7 unaccounted**, pooled into 7 tickets, all joined on structure. Six are
`CDCl3` and `DMSO` - every Example step reports an NMR and names the solvent it was run
in, and no record holds it. The seventh is `water` on line 127, where six records cite
the line and none is a water record, while the Claims and Example tellings of the SAME
step both record it.

## The second reader - the only check here that is not this pack reading itself

Every other check in this file compares the annotation against the patent, or the
annotation against itself. Both are one reader. `structure.second_reader` compares
the structure this pack assigned against what OPSIN makes of the compound's NAME:
English chemical nomenclature parsed by grammar, with no sight of this patent and no
failure mode shared with the vision pass that read the drawing.

It fires on every compound record and it is worth reading when it PASSES. On
CN104292137A it agrees with 36 of the 37 structures that had one to compare, which
is the closest thing this pack has to corroboration of its own chemistry: two
unrelated routes to the same molecule.

Three outcomes reach a reviewer, and a claim carries `second_reader`:

| outcome | claim | `auto` | what it means |
|---|---|---|---|
| `agree` | none | - | two readings, one molecule. The check row records it. |
| `disagree` | yes | `not_reconciled` | two readings, two molecules. Both drawings are on the card and exactly one is what the patent used. |
| `ambiguous` | yes | `not_checkable` | OPSIN parsed the name and warned it does not pin one molecule down. |
| `is_the_source` | none | - | the structure IS the parse. Nothing independent has looked at it, and the check says so rather than counting itself as agreement. |
| `no_parse` | none | - | a trade name, an abbreviation, a SMILES used as an identifier, or not English. Not a defect. |

**`ambiguous` is the outcome nothing else here can produce.** `cyclohexanedione`
names three molecules that share the formula C6H8O2 and the mass 112.13, so every
formula check, every mass balance and the yield identity pass on all three. A name
parser is the only reader in this pack that can tell them apart, which is why an
OPSIN WARNING is recorded and is never promoted to a structure.

## The yield identity - the arithmetic `mass_check` structurally cannot see

`quantity.mass_mmol` needs a mass AND a mole count on the SAME row. Every example
step in this patent writes its product as a mass with no mole count, so the check
built to find the des-chloro defect cannot see it at the one step where it matters
most. The annotation flagged Example 1 Step 1; this stage passed it; that single
disagreement was the whole of `agreement_with_annotation.annotation_only`.

`quantity.yield_identity` asks the question those rows CAN answer:

    limiting reactant mmol  x  yield  x  MW(product)  =  the product mass printed

It applies to 8 of the 33 reactions - the rest lack a product mass, a reactant molar
charge, a yield or a resolved structure, and are `skip` rather than `pass`. All 8
disagree. Steps 1, 2 and 4 land within half a unit of the chlorine-for-hydrogen
shift by a path completely independent of mass-over-moles, which is corroboration of
the des-chloro finding rather than the same measurement twice. The rest cluster near
-44.7 and are deliberately left unexplained: naming a cause this stage cannot support
would be the machine guessing in front of a reviewer who cannot check it.

The three numbers are the PATENT's own, so a disagreement is the document
contradicting itself and never an extraction error. The claim carries
`about: "patent"`, `basis: "derived"` and `severity: "high"`, and it does NOT trip
the grounding gate.

**What this does NOT establish.** Matching is by VALUE, not by attachment. It shows
no quantity was ignored. It does not show each quantity was attached to the right
compound: "25.3 g" being present somewhere in the annotation is not evidence that it
was attached to 2-chlorotoluene. That is precisely what the human reviewer is for.

## Evidence width - why `found` is not one thing

`evidence_width` is how many lines the claim cites and `evidence_class` is `wide`
above ten, `narrow` at or below. Every claim carries both, and they are always
consistent with `cited_lines`.

A `found` verdict means the claimed value is on SOME line the record cites. Against
one cited line that is strong. Against 34 it is close to unfalsifiable: a compound
record's citation is the union over every provenance row for that identifier, so
`water` cites 34 lines because water is quoted in seventeen places, and almost any
two-digit number appears somewhere in 34 lines of a chemistry patent.

Measured on this patent: **43 of 316 `found` claims, 13.6%, rest on more than ten
cited lines, and the widest cites 46.** Two hand-checked examples, both verdicts
CORRECT and half the cited evidence coincidence:

| claim | genuine | coincidence |
|---|---|---|
| `dichloromethane` 100 ml | line 243, "100 ml dichloromethane" | line 236, where the 100 ml is THF |
| `water` 100 ml | line 206, "100 ml of water was added" | line 236, the same THF |

One printed quantity, belonging to a third substance, counted as confirmation for
two different compounds. Note what would NOT have caught it: line 236 does name
dichloromethane, elsewhere in the same sentence, so a "the cited line names the
compound" test passes it too. Matching is by VALUE and never by attachment, here as
in the quantity sweep, and attachment is exactly what the human reviewer is for.

**So the tier 3 bound must be reported as two bounds.**
`summary.tier3_population_by_width` gives the denominators, `{"narrow": 266,
"wide": 35}` on this patent. Averaging them into one residual-defect rate borrows
the credibility of the narrow matches to cover the wide ones, which is the kind of
optimism `REVIEW-PROTOCOL.md` calls a defect rather than a presentation choice.

A wide `found` also says so on its own row, in `risk_reasons_en`, so a reviewer who
meets one knows to check the attachment rather than the number. The verdict is NOT
downgraded to `partial`: the match usually is genuine, and moving 43 claims into
tier 1 would cost the reviewer a third of their budget to re-confirm numbers that
are mostly right.

## `source_coverage` - "what did we MISS"

The other half of the job, and the half no per-record check can answer.

```json
{
  "lines": [ { "n": 32, "kind": "prose|translation|heading|claim|image_extract|blank",
               "has_english": true, "text_en": "...",
               "section_en": "Example 1",
               "cited_by": ["record_id", "..."],
               "signals": ["quantity", "temperature", "duration", "yield",
                           "ratio", "structure", "reagent"],
               "status": "covered | uncited_with_chemistry | uncited_plain" } ],
  "summary": { "total": 262, "covered": 180, "uncited_with_chemistry": 12, "uncited_plain": 70 }
}
```

`uncited_with_chemistry` is the actionable list: a line that carries a number, a unit, a
temperature or a yield and that NO record cites. Each one is a candidate miss and gets
its own claim with `field: "__coverage__"` so it enters the same review queue.

## `completeness` - the report

```json
{
  "score": { "grounded_pct": 0.0, "covered_pct": 0.0, "structure_pct": 0.0 },
  "verdict_en": "one paragraph a manager can read",
  "blocking_en": ["..."],
  "by_section": [ { "section_en": "Example 1", "records": 12, "claims": 40,
                    "found": 30, "not_found": 2, "uncited_chemistry_lines": 1 } ]
}
```

## Hard rules

- Deterministic. Same input, same bytes out, so a diff between two runs is meaningful.
- No network. No API keys. Runs offline.
- Never mutates a gold file. Writes only into `verification/`.
- Exits non-zero when any `grounding` check fails, so the pipeline stops on a
  hallucination rather than shipping one.
- Every human-facing string ends in `_en` and is English. Keys are ASCII too: the
  file is grepped for Han characters as the last gate before it is written, and the
  run aborts rather than shipping one.
- `summary` carries the denominators a sampler needs and cannot safely derive from a
  filtered list: `claims_by_tier`, `tier3_population_by_stratum`, `claims_by_family`,
  `claims_by_subject`, `field_basis` (the quoted-versus-derived inference, with its
  evidence), `agreement_with_annotation` (this engine's arithmetic findings against
  the annotation's own flags, in three buckets), `checks_by_family` and
  `source_coverage`.
