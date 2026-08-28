# WO2022024094A1 run notes

"Process for preparation of mesotrione and its intermediates", a WO publication in
English. 23 rendered pages. Born digital, not a scan: the PDF carries a text layer,
so the prose in this annotation comes from the text layer and the vision pass was
run for the drawn structures, which no text layer contains.

## Model provenance, and why the agreement here is weaker than it looks

CLAUDE.md asks for this because correlated blindness is invisible to the pipeline.

Every judgement artifact in this run was produced by Claude Opus 5, across two
Claude Code sessions. The first session ran the seven passes and the step 6 read;
the second resumed the deterministic half from the structures gate onward. The
`what_this_is_en` field of `input/substances-observed.json` carries the same
attribution, written at the time that file was produced.

| pass | invocations | what it produced |
|---|---:|---|
| V | 23 | one page read each, `input/vision/pNN.json` |
| A0 | 1 | the 15 section map |
| A1 | 15 | 109 compound records across sections, 43 unique after merge |
| A2 | 11 | 24 reaction records |
| A3 | 1 | 16 pathways |
| A4 | 1 | the patent record |
| A5 | 4 | the adversarial audits, fresh context, one per artifact |
| step 6 | 1 | the independent substance read, 758 spans over 406 lines |

**The three readings in this pack are not independent in the way the word implies.**
The vision pass, the extraction passes and the step 6 read are the same model working
from the same pages. Where the extraction missed something and the step 6 read also
missed it, nothing here can see that, and it reports as clean. Only the
disagreements are strong evidence.

Reading B is the one genuinely non-model reader: ChemDataExtractor, a grammar and a
CRF tagger, over the same lines. Where it and the LLM read agree, that agreement is
worth more than any agreement between two of the passes above.

## Three input defects this run found and fixed

None of these were fixed in `output/`. Each was fixed in the input that produced it
and the pipeline re-run, per CLAUDE.md rule 3.

1. **`family_id` was an integer.** `biblio.schema.json` permits `["string","integer"]`
   but `patent.schema.json` requires `["string","null"]`, so a biblio that validates
   produced a `patent.json` that does not. Every other run in this repo happens to
   author the field as a string, so the integer branch had never been exercised.
   Fixed by quoting it in the biblio. **The schema disagreement is still there** and
   the next person to type an unquoted family id will hit it again.

2. **The step 6 read quoted reagent labels out of the `IMAGE_EXTRACT` JSON.**
   34 spans over 15 drawing lines. That JSON is machine-readable structure, not text:
   the English rendering of a drawing line is "Drawn on the page: N structures" plus
   each drawn structure's formula and SMILES, and it carries no condition labels at
   all. `verify.py` checks spans against that rendering and stopped the run,
   correctly. The 34 spans are removed and the removal is recorded in
   `drawn_only_reagents_not_carried_en` inside the file rather than done silently,
   because two of them are named nowhere else in the document.

3. **The vision pass wrote `null` in `between_markers`.** 8 drawings over 6 pages.
   The convention the reference run and the V prompt both use is a pair of strings,
   with parenthesised prose where no marker is visible. `null` crashed
   `make_visual_evidence.py` on `m.strip()`. Replaced with the prose form.

## What the removal in defect 2 costs

Two substances are now recorded nowhere:

- **Sodium acetate**, drawn at line 75. The prose at line 70 says "acetic acid and
  acetate ion", which is not the same claim.
- **O2**, drawn at line 83 as the condition "Nitric acid/O2". The prose at line 81
  recites sulphuric acid, nitric acid and vanadium pentoxide, and no oxygen.

Both are conditions on background-art schemes reciting US 5,591,890 and
CN 105669504 A, so neither touches the invention's own route. Recorded because a
loss that happens to be harmless is still a loss.

`(CH3CH2 )3N` and `V2O5` were also removed, but those substances survive under
their other spellings: triethylamine in the prose at lines 245, 246, 329 and 330,
and vanadium pentoxide at 77, 78, 81, 82, 88 and 89. Only the formula spellings
are gone.

## The gates

Both coverage gates passed with no curated entries.

- **structures**: 43 compounds resolved and 34 drawings produced with
  `input/structures-curated.json` empty. Nothing was hand-authored, so the warning
  in CLAUDE.md rule 5 about checking SMILES atom by atom did not arise on this run.
  Every structure here came from a resolver tier that can be re-derived.
- **translations**: `output/translations.json` is `{}`. The document is English
  throughout and nothing Chinese can reach a screen.

## The verify gate is red, and 13 of its 20 failures are a bug in verify.py

`verify.py` cannot see a volume written with the unit jammed on in capital-L form,
`120mL`. `UNIT_ALTERNATION` at verify.py:218 lists `ml` case-sensitively, and its
`[gLl]` branch matches a standalone `L` but never the `m` of `mL`. With no unit
matched, `BARE_BOUNDARY` then disqualifies the bare number too, because the next
character is a letter. The number becomes invisible.

Measured, not argued:

```
'hydrochloric acid(120mL, 1.23mol)'  -> [('1.23', 'mol')]      120 not seen
'water (160mL)'                      -> []                     nothing seen
'acid (5.4mL, 0.054mol)'             -> [('5', None), ...]     5.4 MISREAD as 5
'hypochlorite (500ml, 0.745mol)'     -> [('500', 'ml')]        lowercase, fine
'water (60 mL)'                      -> [('60', None)]         spaced, degrades to bare
```

This is why `volume_ml` scores 6/19 in the numeric field table while every other
numeric field scores N/N, and it is 13 of the 20 claims in the grounding gate. Each
of those 13 is reported as "the fabrication signal", and each of the values is
plainly printed on a line the record cites: `120mL` on line 264, `54mL` on line 285,
`160mL` on line 300, `5.4mL` on line 329.

**The annotation is right and the checker is wrong.** No number was invented and no
citation points at the wrong line. Per CLAUDE.md rule 4 that verdict was reached by
re-measuring rather than by preferring the annotation.

`verify_selfcheck.py` cannot catch this. Its check J, "does `not_found` mean what it
says", re-reads the cited lines with the same tokeniser, so it confirms the absence
its own scanner manufactured and reports `[PASS] every not_found value really is
absent from its cited lines: 13 checked`. A self-check that shares a scanner with
the thing it checks cannot see a scanner bug. That belongs in
`contracts/GUARDS-THAT-PASS-ON-ABSENCE.md` as the mirror case: a guard that fails on
presence.

**Not fixed here.** The fix is one token in a regex in the shared verification
engine, and it changes the verification output of every run that writes volumes that
way. Counted across the pack: CN112645853A 114 occurrences, WO2022024094A1 30,
CN109678767A 5, and every other run 0. **The reference run CN104292137A has none, so
its pinned numbers would not move.** That is the fact anyone deciding this should
have, and it is measured rather than assumed.

## The other 7 grounding failures are real

They are `__substance__` claims: the patent names a substance on a line a record
cites and no record holds it as an identifier. `acetate ion` at line 70, `NMSBA` and
`NMST` at 350 and 359, `ruthenium` at 185, `HPPD` at 55 and others. The A5 compounds
audit independently reached the same conclusion about `acetate ion`, calling it the
only compound-level recall gap it found. These are what the tier 1 and tier 2 census
is for and they are left in the queue for a reviewer.

## Reading B could not run

ChemDataExtractor installs but its current API is incompatible with `mentions.py`:
`legacy_pos_tag is not a supported tag type`. `mentions.py` refused to write an empty
`substances-cde.json`, which is correct, because an empty file reads on every screen
as "ChemDataExtractor found nothing" and that is a different claim from "it could not
run". The sweep therefore publishes `readers: ["llm"]` and every finding says so.

So the caveat above stands at full strength: there is no non-model reader in this
run, and every agreement in it is agreement between one model and itself.

## What I am least sure of

Recorded here rather than resolved, per CLAUDE.md rule 8.

- **The A5 compounds audit found a real merge defect and it is still open.** The
  merged `mesotrione` record carries Example 7's melting point, appearance and
  purity but an all-null `quantity`, and is labelled "Summary of the Invention".
  Example 7 prints "Yield: 17g (85%)" and the raw record holds `mass_g 17.0,
  yield_pct 85.0`. The cross-section merge kept the empty quantity of an
  alphabetically later section. This is the patent's target compound losing its
  mass and its yield. The fix belongs in `finalise.py`, not in the artifact, and it
  would change every run in this repo, so it is not made here.
- **The verify gate is red on 13 false positives.** See above. A reviewer opening
  this run will meet 12 claims marked `critical`, "a value on no line of the
  patent", and most of them are values plainly on the page. That is the single most
  misleading thing in this deliverable and it is not fixed.
- **45 A5 findings in total, 14 of them major**, across the four artifacts. They are
  published in the deliverable rather than acted on, which is what the audit is for.
- The step 6 read and the extraction are the same model. See above.
