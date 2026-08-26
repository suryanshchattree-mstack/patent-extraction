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
  "record_kind": "compound | reaction | pathway | patent",
  "record_label_en": "2-chlorotoluene",
  "field": "quantity.mass_g",
  "field_label_en": "Mass used",
  "question_en": "Does the patent say 12.6 g of 2-chlorotoluene was used?",
  "claimed_en": "12.6 g",
  "claimed_value": 12.6,
  "claimed_unit": "g",
  "cited_lines": [32, 33],
  "evidence_en": "full English text of the cited lines, already translated",
  "evidence_lines": [ { "n": 32, "text_en": "...", "is_translation": true } ],
  "highlights": [ { "line": 32, "start": 14, "end": 18, "kind": "value" } ],
  "auto": "found | not_found | partial | not_checkable",
  "auto_reason_en": "The number 12.6 appears on line 32 next to the word grams.",
  "needs_human": true,
  "risk": 0.0,
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

`highlights` are offsets into `evidence_lines[i].text_en`, so the UI highlights without
re-deriving anything. `kind` is one of `value`, `unit`, `name`, `condition`, `yield`.

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

`needs_human` is the queue filter. `risk` orders it, descending.

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
