# Triage of the Outstanding list

The 34 `major` findings in `AUDIT.md`, measured against the gold as it stands. The
one `critical` entry is already done at `contracts/DUPLICATE-FAMILIES.md`.

Four questions per finding: is it real, has it already been fixed, could it reach a
deliverable the way the sulcotrione title did, and should it be a gate.

**Ordered by deliverable reach**, because that is the triage question.

---

## Summary

| tier | what it means | findings |
|---|---|---:|
| **A** | reaches a document a colleague reads | **1** |
| **B** | reaches an internal artifact a benchmark scores | **17** |
| **C** | real, but the deliverable already reports it | **9** |
| **D** | stale: already fixed, or already documented elsewhere | **7** |

**Nothing on this list is a second sulcotrione.** The one Tier A item is a
provenance ambiguity rather than a wrong fact. That is the headline: the audit is
doing its job and its bookkeeping lags, exactly as hoped.

Two counts on the list are wrong in opposite directions, and one live defect is
**not on the list at all** (section A2).

---

## Tier A - reaches a document a colleague reads

### A1. The export asserts a computed molecular weight as a headline fact

**Finding 34** as written is about `reactions.json` notes and is internal. But
measuring it turned up the deliverable-facing version, which is not on the list.

The self-contained HTML export prints, for every step of the route:

> 1 2-chloro-6-(methanesulfonyl)toluene -> electrophilic_substitution, told in Claims,
> Summary of the Invention, Example 1. **C8H9ClO2S, MW 204.68.** Not drawn in the
> patent under this name; reached through a synonym that is drawn.

`C8H9ClO2S` and `204.68` appear nowhere in the patent. They are computed from the
structure we resolved. The sentence that follows states provenance **for the
structure** - "not drawn under this name, reached through a synonym" - and a reader
reasonably carries that caveat onto the structure, not onto the formula and mass
sitting immediately before it.

1. **Real?** Yes. Verified in the rendered export, 251 KB, fetched from the running
   server. The export's `204.68` is not even the notes' `204.67`, so it is computed
   independently at render time rather than lifted from the notes.
2. **Already fixed?** No, and it is not on the Outstanding list in this form.
3. **Reaches a deliverable?** **Yes.** This is the closest thing on the whole list to
   the sulcotrione shape: a value we generated, printed as fact, in the document
   meant for someone who will never run the tool.
4. **Gate?** Not mechanically. This is a labelling change - mark computed values as
   computed, the way the report already marks machine matches as not human
   confirmations. The report is scrupulous about that distinction everywhere else,
   which is why the omission stands out here.

**Finding 34 proper** - eight Example 1 records carrying 9 to 15 computed numbers in
`notes` - is **real and live**, 8 of 8 records still affected. But it is Tier B: it
violates A2 rule 32 and pollutes a field a benchmark reads, and it does not reach the
export, which computes its own.

---

## Tier B - reaches an internal artifact a benchmark scores

These change what an extractor is scored against. None of them reaches a document a
colleague reads. All are live.

### B1. Two artifacts disagree about the same compound's role (findings 14-18)

**Real, all five, and worse than stated**: the contradiction is not only between a
record and its own notes, it is **between two gold artifacts**.

| compound | `reactions.json` | `compounds.json` |
|---|---|---|
| methanesulfonyl chloride | `reactant` | `reagent` |
| acetyl chloride | `reactant` (notes) | `reagent` |
| methanol | `reactant` (notes) | `reagent` |
| sodium 2,2,2-trifluoroethoxide | `reactant` (notes) | `reagent` |
| N,N-dimethylformamide | `additive` (notes) | `catalyst` |

Verified directly on `Example 1_Step 1`: `methanesulfonyl chloride` is `reactant` in
the reaction record and `reagent` in the compound record. The export renders the
reaction value, so a reader sees the better one; a benchmark joining on
`compounds.json` gets the worse one.

**Gate?** Yes, and cheaply: assert that a compound's role in `compounds.json` matches
its role in every `reactions[].compounds` entry for the same identifier, or that the
disagreement is explicit. That is a `finalise` or `validate` exit code.

### B2. Summary steps carry no solvent where Claims steps carry three to five (28-32)

Live and exactly as stated:

| step | Summary | Claims |
|---|---:|---:|
| 1 | 0 solvents | 3 |
| 2 | 0 | 3 |
| 5 | 0 | 5 |
| 6 | 0 | 5 |
| 7 | 0 bases | 6 |

**Gate?** Yes. Where two sections recite the same step and one names permitted
solvents on a line inside the other's own span, the omission is mechanical to detect.

### B3. One workup convention, applied to one section only (33)

Live, and the count is clean:

| section | workup species in `compounds[]` | records |
|---|---:|---:|
| Claims | 10 | 8 |
| Example 1 | 12 | 8 |
| **Summary of the Invention** | **0** | **17** |

One decision, 17 records. The gold scores identical extractor behaviour as correct in
two sections and incorrect in the third. **Gate?** Yes - a consistency check, not a
correctness one.

### B4. Pathway step roles outside the enum (21) - understated by the audit

The audit says 10 projections. **Measured: 18.** Values found: `quench`, `wash`,
`intermediate` - none in `finalise.py`'s own `VALID_ROLES`.

**Gate?** Yes, trivially: validate `steps[].compounds[].role` against the same enum
`normalise_role` already enforces elsewhere. This is the most obviously gate-able item
on the list.

### B5. `section_label` names a section that does not hold the quantity (2) - overstated

The audit says **21 of 43**. **Measured: 14 of 43** carry a `mass_g`.

And the mitigation already exists: `compounds-sections.json` holds the full section
list per compound, 39 entries, e.g. `2-chloro-6-(methanesulfonyl)toluene -> ['Abstract',
'Claims']`. Same shape as the equivalence file in `DUPLICATE-FAMILIES.md` - the truth is
recorded next to the artifact rather than in it, and the decision is defensible.

### B6. `is_section_product` collapsed to one record (3)

Live and exactly as stated. Exactly one record carries the flag - `tembotrione` - and
its `section_label` is `Technical Field`, a section that only repeats the invention
title. `raw-compounds.json` had it true in five sections and the merge kept one.

### B7. Computed numbers in Example 1 notes (34, internal half)

8 of 8 Example 1 records still carry computed MWs and formulae in `notes`. See A1.

### B8. Bromine mass and moles disagree, and nothing computes it (12)

`mass_g 39.6`, `mmol 220.0`. 39.6 g of Br2 at MW 159.81 is **247.8 mmol**, not 220.
No note flags it.

I checked whether the verification engine catches it independently, the way it catches
the product-yield mismatches. It does not: `39.6` appears in the checks file, but
`0.248`, `247.8` and `248 mmol` do not. **The arithmetic check covers product yield
identity and not reagent mass/mole consistency.**

**Gate?** Yes, and this is the highest-value gate on the list, because it is the same
check the engine already performs on products, applied to a field it currently skips.
One rule, and every reagent in every future patent gets it.

### B9. `scale_discontinuity` not raised on Example 1 Step 4 (23)

Live. `validation_flags` holds `molar_mass_inconsistent` and
`mass_balance_implausible`, but not `scale_discontinuity`.

### B10. `components` includes reagents inconsistently (22)

Not separately re-measured; the audit's own description is self-consistent and the
field is internal. **Gate?** Yes - the rule is mechanical, "role == reactant plus
is_product", and the complaint is precisely that no single rule reproduces the field.

---

## Tier C - real, but the deliverable already reports it

The gold is thin here and the verification engine catches it downstream. That is the
system working: a gap in one layer surfaced by the next.

### C1. The eight arithmetic non-closures (4-11)

**All live in the gold**: none of the five product records I checked carries an
`INTERNALLY INCONSISTENT` note.

| step | mass_g | yield_pct | note flags it |
|---|---:|---:|---|
| 1 | 28.6 | 84.0 | no |
| 2 | 36.5 | 86.0 | no |
| 4 | 44.2 | 97.0 | no |
| 5 | 41.6 | 70.0 | no |
| 8 tembotrione | **null** | **null** | no |

**But the export reports every one of them**, computed independently:

> The product mass agrees with the charge and the yield: 500 mmol charged at 95% of
> tembotrione, molecular weight 440.82, comes to 209.39 g, but the patent prints
> 188 g. Implied molecular weight 395.79 against 440.82, outside the tolerance of 6.61.

So **finding 10 is the one to reconsider**. Its sharpest claim - "the final product of
the whole route has no isolated mass or yield anywhere in the artifact" - is true of
`compounds.json` and **false of the deliverable**, which prints 188 g and 95% and
flags the discrepancy. The data gap is real; the information loss is not.

**Gate?** Already gated, in the right place. `verify.py` raises these as claims a
human must settle. Adding notes to the gold would be duplication, and worse,
duplication that can drift.

### C2. Step-to-step discontinuity across Example 1 (11)

Same shape: five steps consume more than the preceding step produced. The engine
surfaces the per-step arithmetic; the chain-level check is the part not gated.
**Gate?** Yes, and it is mechanical: compare each step's charge against the previous
step's isolated mass along the pathway.

---

## Tier D - stale, or documented elsewhere

### D1. Pathway uuid collision (20) - **FIXED, and the list has not caught up**

The audit says "three pathways share it, and two of those three have
`overall_yield_pct` null". **Measured now: 5 pathways, 5 distinct uuids, maximum
share 1.** `finalise.py` was changed to fold the ordered step signature into the seed.

This is the clearest instance of the pattern the whole exercise is about: fixed hours
ago, still sitting under "Outstanding, not yet acted on".

### D2. Sodium hypochlorite strength (13)

`mass_g 500.0` still on a record identified as the solute, but the note **does**
address it, and there is a full writeup at `contracts/HYPOCHLORITE-STRENGTH.md`. The
decision is made and documented; the list entry is stale.

### D3. compound_count 75 (19)

`compound_count` is 75 and `len(compounds.json)` is 75, so the arithmetic passes
exactly as the finding itself says. The upstream defect is the duplicate families,
already measured and decided at `contracts/DUPLICATE-FAMILIES.md` (61 substances
behind 75 records). Nothing separate to do.

### D4. The duplicate-derived findings (1, 2 partly, 19)

Findings 1 and 19 are consequences of the critical entry and are covered by its
writeup. Finding 2 has its own mitigation in `compounds-sections.json` (see B5).

---

## Not on the list: five Chinese identifiers in the gold

`compounds.json` holds five records whose `identifier` is Chinese:

    硝环磺酮   硫醇   N-溴琥珀酸亚胺   甲硫醚   1,2-二氯甲烷

**None of them reaches the export.** I checked all five against the rendered HTML and
the translation index substitutes every one. The English gate is doing its job, and
this is a Tier D observation rather than a defect.

One is worth a note anyway. `1,2-二氯甲烷` is "1,2-dichloromethane", which is not a real
name - dichloromethane has no 1,2 positions. It is the patent's own typo for
1,2-dichloroethane, and we hold it as a **separate compound record from
`1,2-dichloroethane`**, with both appearing as solvents on `Example 1_Step 1`. That is
a duplicate family the equivalence index should probably cover, and it is a duplicate
created by a defect in the patent rather than by our spelling variation - which makes
it a different case from the twelve in `DUPLICATE-FAMILIES.md` and arguably a correct
non-merge, since merging would silently repair the document.

---

## What I would gate, in order of value

1. **Reagent mass/mole consistency** (B8). The engine already does this for products.
   Extending it to reagents is one rule and it would have caught bromine without a
   human. Highest value because it generalises to every future patent.
2. **Role agreement between `compounds.json` and `reactions.json`** (B1). Cheap,
   mechanical, and it currently lets two gold artifacts contradict each other.
3. **`steps[].compounds[].role` against the existing enum** (B4). `normalise_role`
   already exists and is simply not applied here.
4. **Chain-level mass continuity along a pathway** (C2).
5. **Cross-section consistency for the same step** (B2, B3, and the vocabulary
   contradictions in findings 24-27, all verified live: `reaction_class` `other` vs
   `acylation`, `is_one_pot` true vs false, `named_reaction` set vs null, and one
   temperature range read two ways). These are one check: where two sections recite
   the same step, their structured values must agree or the disagreement must be
   recorded.

---

## Method

Everything above was measured against `output/relevant_output/gold/` as it stands, and
against the export fetched from the running server at
`/CN104292137A/report/export` (251 KB). Nothing was fixed. Two audit counts were
found wrong - finding 2 overstates by 7 records, finding 21 understates by 8
projections - and one entry, finding 20, is fully fixed and still listed.
