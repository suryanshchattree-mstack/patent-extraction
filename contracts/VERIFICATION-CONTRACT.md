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
  "about": "extraction | patent",
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
  "auto": "found | not_found | partial | not_checkable",
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

`tier` is the QUEUE, `risk` is the order within it. See `REVIEW-PROTOCOL.md`.

- `tier: 1` - a human must see it. Anything `not_found` or `partial`, any load-bearing
  `not_checkable` judgement, and any claim on a record with a failed structure,
  quantity or reference check. Small population, worked as a census.
- `tier: 2` - the `__coverage__` candidate-miss claims. The recall side. Also a census.
- `tier: 3` - the machine matched it cleanly. Sampled, never exhausted.

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
| `quantity` | mass and mmol that disagree with the molecular weight. |
| `consistency` | the same molecule given two different structures, or two records for one thing. |
| `drawing` | the structure read off the page image against the gold's structure for the same named molecule. Two independent readings disagreeing is a hard defect. |
| `completeness` | a record missing a field its own section clearly states. |

Each check also carries `about_fields`: the claim-field prefixes it concerns, or
empty for a check about the whole record. This is what keeps tier 1 readable.
Promoting every claim on a record with one failing check puts about a hundred
cleanly-matched numbers in front of a reviewer who has time for fifty items, purely
because one row of the same reaction failed a mass balance.

`records[]` also carries `uuid`, `rec`, `section_en`, `stratum`, `cited_lines` and
`annotation_flags_en`, the last being the annotation's own `validation_flags` said in
English, so a check that rediscovers one can say the annotation flagged it too rather
than presenting it as new.

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
