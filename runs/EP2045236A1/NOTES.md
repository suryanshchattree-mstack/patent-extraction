# EP2045236A1 run notes

Bayer CropScience, `Thermodynamisch stabile Kristallmodifikation von
2-({2-Chlor-4-(methylsulfonyl)-3-[(2,2,2-trifluorethoxy)methyl]phenyl}carbonyl)cyclohexan-1,3-dion`.
Filed 24.08.2007, published 08.04.2009, **Withdrawn**. Family 38984191.

## What this patent is, and why it is unlike the other three

**It discloses no synthesis. Not one bond is formed or broken anywhere in it.**

It is a polymorph patent. One molecule, tembotrione, in three crystal
modifications, distinguished by Raman and infrared band maxima, X-ray powder
diffraction, DSC melting point, density and, for two of the three, a
single-crystal structure. The three worked examples dissolve 2 g of tembotrione
at the boil in acetone, ethanol or toluene and cool it slowly; the same substance
comes out in a different lattice. The invention's own process runs the other way,
converting modifications II and III into I in a solvent at 0 to 80 degrees C, or
by grinding at 5 bar or more with no solvent at all.

So every reaction record here is a physical transformation with the same
substance on both sides, `reaction_class: recrystallisation` (or `other` for the
grinding route, which no enum value covers). There is no route, no intermediate,
and no reagent, catalyst, base or acid in the entire document. The solvents are
the chemistry: which solvent, at which temperature, is what decides the form.

It is also the first non-Chinese patent in this set, and the first where the
results are not a yield table. **No yield, no isolated product mass and no
chemical assay purity is stated for any preparation.** The only mass in the
document is the 2 g charged in each example.

## Model provenance

| artifact | produced by |
|---|---|
| `input/vision/p01..p23.json` | Claude Opus 5, one fresh context per page, 23 in parallel |
| `output/stages/A0-sections/` | Claude Opus 5, one context |
| `output/stages/A1-compounds/` | Claude Opus 5, ten contexts over 35 sections |
| `output/stages/A2-reactions/` | Claude Opus 5, one context over the 5 procedure sections |
| `output/stages/A3-pathways/` | Claude Opus 5, one context |
| `output/stages/A4-patent/` | Claude Opus 5, one context |
| `output/stages/A5-verify/` | Claude Opus 5, four fresh contexts, one per artifact |
| `input/substances-observed.json` | Claude Opus 5, one fresh context, launched before A1 finished |
| `input/structures-curated.json` | one entry, hand-authored, confirmed with the run owner |
| `input/EP2045236A1-biblio.json` | hand-authored |

**The correlated blindness caveat.** Every artifact above is the same model. The
independent read in step 6 is one language model checking another language
model's reading of the same page, and it says so in its own `what_this_is_en`.
Where it and the extraction agree, that agreement is weaker evidence than it
looks, and nothing in this pipeline can see a substance both of them missed. The
A5 audits were given no access to the reasoning they audit, which is the only
structural defence here, and they did find things the passes had not.

## The two findings worth a reader's time

### 1. Tabelle 5 and Tabelle 6 are the same table, and claim 5 recites it

Tabelle 5 is captioned the X-ray powder pattern of crystal modification I and
Tabelle 6 that of modification II. **They print the same 49 values of 2 theta in
the same order, 7.3765 through 36.7974.** Claim 5 recites the same 49 values.

Verified four ways: deterministically from the PDF text layer independent of any
vision read; by the A1 pass off the page images; by the A4 pass; and by the A5
audit reading Tabelle 5 on page 6 and Tabelle 6 on page 7 value by value. It is
not a transcription artifact.

Two readings were originally recorded and neither resolved. The adversarial audit
then showed that **the patent's own Tabelle 7 excludes one of them**: modification
I is orthorhombic, space group Pna21, cell volume 1788,91; modification II is
monoclinic, P2(1)/n, 1814,21. Two different lattices cannot produce one powder
pattern, so a mislabelled caption cannot explain two tables printing the same
numbers.

What remains is a duplication in the published patent **whose direction the
document does not reveal**. Nothing in it says which table holds the real
measurement. So the powder pattern of crystal modification II is not disclosed
anywhere in this document, while claim 5 recites a pattern as though it defined
the claimed form. Nothing in this annotation decides which table is the misprint,
corrects either, or drops either; each record keeps the attribution its own
caption gives.

Recording that an alternative is ruled out by evidence is not the same as
resolving a disagreement by preference. The first is what the data supports; the
second is what CLAUDE.md rule 8 forbids.

### 2. The three forms are not evenly characterised, and the melting points barely separate them

Tabellen 3, 4, 5, 6 and 7 cover modifications I and II only. **Modification III
has a melting point and its Raman and infrared band lists and nothing else**: no
single-crystal structure, no powder pattern, no unit cell, no density.

And the melting points are 124,0 / 123,9 / 121,6 degrees C, measured by DSC at
10 K/min per [0019]. Modification I and modification II are **0.1 K apart** on a
10 K/min ramp. Taken with the duplicated powder tables, only one of the three
forms has a diffraction pattern that is both present and unambiguous.

## Eight more defects in the published patent, recorded and not repaired

1. **[0024]'s preference ladder does not nest.** "ganz besonders bevorzugt 50 to
   80 degrees C" is *wider* than the "besonders bevorzugt 60 to 80" it should
   narrow.
2. **[0024] gives cooling rates with no time unit**, "kleiner 25°C" and "kleiner
   20°C", where the examples print "20°C/h". The annotation records the general
   passage without the unit and the examples with it; no unit was borrowed.
3. **[0027] prints "mit mehr als als 98 Gew.-%"**, with "als" doubled. Verified on
   the page image, kept verbatim.
4. **Tabelle 7 prints modification II's a-axis as `a = 15,8491 (5) (18) Å`**, two
   uncertainty brackets, which cannot both be the standard uncertainty.
5. **Tabelle 7 prints its b-axis as `b =7,1164(2) Å`**, no space after the equals.
6. **Tabelle 4's caption omits the `[°]`** that Tabelle 3's caption carries.
7. **[0053] prints `Emährungswert`** where [0052] spells the same word correctly.
   The Cry gene names print a lower-case l where a capital I is meant.
8. **[0045] prints `lodosulfuron`** with a lower-case L for iodosulfuron, and
   prints `Flumetsulam` twice. `Phosphinotricin` is missing its h.

## The prosecution context

The European Search Report cites **two X-category documents against all 16 claims**,
WO 03/047340 and WO 2007/006415, both Bayer CropScience's own. An X citation means
the examiner considered the document to destroy novelty or inventive step on its
own. The application is Withdrawn. The same family was granted elsewhere as
US8722582B2, which `TARGETS.md` lists as do-not-also-annotate.

This is recorded as prosecution context in the A1 provenance for the search
report section, not as a claim about the chemistry.

## Deviations and decisions

- **Tables ride inside paragraph `zh`/`en` as markdown.** `build_enriched.py`
  emits `[IMAGE_EXTRACT: ...]` spans only from `drawings[]`, so a table has no
  representation of its own anywhere downstream. This convention was carried over
  from CN111440099B. It is also what triggered the blocking bug below.
- **Aliases are scoped to the section that prints them.** An alias is a spelling
  the source actually uses, so a record carries one only if it appears in that
  section's own lines. `finalise.py` unions aliases across sections, so the
  complete set still assembles.
- **All three crystal modifications share one SMILES.** Confirmed with the run
  owner before authoring. See the structures gate section below.
- **The 246 herbicides and 23 safeners of [0045] and [0046] are all extracted.**
  A1 rule 1 says extract every compound named whatever its role, and a recall
  benchmark over a long list is only meaningful if the gold holds the whole list.
- **`compound_class` is one value per compound run-wide**, `active_ingredient` for
  the tembotrione family, including where a section uses a modification as
  feedstock. Role carries that; the tag describes the substance.
- **The claims recite an unnumbered metastable form.** Claims 8 and 10 say "eine
  metastabile Kristallmodifikation", and [0008] says tembotrione occurs in
  "mindestens zwei" metastable modifications, so the claim reads on forms this
  document never characterises. A separate identifier, `tembotrione metastable
  crystal modification`, carries that rather than narrowing the claim to II and III.

## What the A5 audits found

Four fresh contexts, one per artifact, none shown the reasoning it audited.
Across them: **2 critical, 11 major, 32 minor**. None was in the numerical
fidelity, the quote anchoring or the drawing read, all of which were independently
re-verified off the page images.

The two critical findings were both in the A4 patent summary and both traced to
instructions from the run owner: it said the only preparative operations convert
metastable forms into the stable one, when two of the three examples do the
opposite; and it said the only quantity in the document is the 2 g, while
contradicting itself two sentences earlier.

A third, on A3, was a key starting material of bare `tembotrione` on three
pathways whose steps actually charge modifications II and III. That would have
bound `compound_uuid` to the wrong compound silently. Also from a run-owner
instruction, this one overcorrecting against a failure seen on an earlier patent
where a solvent became the KSM.

All were corrected, and the corrections are in the stage files rather than in the
audit reports, which stand as written.

## Four pipeline defects this patent surfaced

Each was found because this patent's data is shaped unlike the reference's. Three
were fixed in `pipeline/` with the run owner's authorisation; the fourth needed no
code change.

### 1. `resolve_translations.py` aborted, blocking `verify.py` for the whole run

`english_by_line()` builds its `body` list with `if t.strip()`, dropping blank
lines, but splits each vision paragraph **without** dropping them. Any paragraph
carrying an interior blank line desynchronised the walk, and it aborts by design
rather than guessing which English belongs to which line. The table-in-paragraph
convention put blank lines inside 27 paragraphs across 13 vision files.

**Found by the step 6 independent read**, which is not what that step is for. A
completeness read turning up a blocking bug in the deterministic half is worth
knowing can happen.

Fixed on the **input** side, at the run owner's direction, with no code change: 91
whitespace-only lines removed from the vision files and the document rebuilt,
1169 to 1078 lines. Both versions hold exactly 1030 non-blank lines in the same
order with zero content mismatches. Every line number in the section map, all 70
A1 files and the 1030 keys of the independent read was remapped and re-verified
against the rebuilt text.

That rework paid for itself. Because every pass had to re-assert its citations
against a *changed* document, checks that had been passing began failing
honestly, and the passes found: seven quote fragments silently welded across page
or claim boundaries into strings printed nowhere; a reconstructed `125.30` where
the source prints `125.3`; a unit cell welded across three table rows; a
non-idempotent remap script applying the map twice; and, twice, a guard that
excluded nothing because it tested a line including its `NNN | ` prefix, so an
English alias passed by matching the machine translation.

### 2. `verify.py` gave two different quantities the same claim id

Line 644 prints "zwischen 1 g und 1 kg". The claim tag was built from the raw
printed value paired with the **canonical** unit, and kg canonicalises to g, so
`1 g` and `1 kg` both became `644:1g` and collided. A reviewer's verdict on one
would have silently answered the other. `quantity_key` already dedupes on
`canonical()`; the tag now uses it too.

### 3. `verify.py` counted the machine translation as uncited source

The coverage sweep flagged every `> EN:` line as a source line carrying uncited
chemistry, though the German original directly above is cited by a record. **53 of
108 census claims were duplicates**, and they pushed the reviewer budget from 7.5
to 15.7 minutes and over the limit. `label_kind` already returns `translation` for
those lines and `verify.py` uses that idiom elsewhere; the sweep now skips them.

On a German patent this is most of the census, because every paragraph has such a
partner. It would do the same to row 12, `DE10113137A1`.

### 4. `finalise.py:merge_compound` destroyed the only quantity in the patent

This one needed no code change, and it is the one that had actually damaged the
deliverable.

`merge_compound`'s last branch is `elif v not in (None, "", [], {})`. An all-null
quantity object is **not equal to `{}`**, so it passes that test and overwrites
whatever an earlier section recorded. `tembotrione` appears in 19 sections; three
of them, the examples, carry the real `mass_g: 2.0`; the rest carried an all-null
object and sort later alphabetically.

**The merged deliverable held zero compound records with a mass**, though the
patent charges 2 g three times.

A1 rule 17 already prescribes the fix, "an empty object is not the same as null;
use null", and this run is the reason the rule exists. Converting the all-null
containers to `null` across 21 files repaired it with no code change. Verified by
importing the real `merge_compound` and merging all 25 section files for
tembotrione: the 2.0 now survives.

Worth being precise about the blast radius: `analytics` and `aliases` are in
`_UNION`, whose branch reads `existing.get(k) or []`, so for those keys `None` and
`[]` are equivalent and neither could overwrite anything. **The damage was
`quantity` alone**, which is a plain dict outside `_UNION`.

`runs/CN104292137A` and `runs/CN109678767A` are very likely to carry the same loss
and have not been checked.

## The gates

- **structures** passes with **one curated entry**. The three crystal
  modifications carry chemistry as reaction products, so the gate asks for a
  structure for each; they are one molecule, so the answer is one entry with the
  other two as aliases. The gate refuses two curated keys for one molecule, and it
  is right to: three entries would write one drawing and orphan two slugs.
  **SMILES cannot express a crystal lattice**, so the structures artifact cannot
  distinguish the very thing this patent exists to distinguish. That is a limit of
  the notation and is recorded on the entry.
  The structure was not authored fresh: it is the molecule drawn at [0002],
  read off the drawing geometry, canonicalising byte for byte to an independent
  derivation from the printed German IUPAC name, byte-identical to what both
  existing runs carry, and re-checked atom by atom against page 2 by two A5 audits.
- **translations** passes on **0 strings**, and that is the finding.
  `resolve_translations.py` gates on CJK codepoints only (`CJK` at line 127), so
  `has_chinese()` is always false on a Latin-script document. The gate reports a
  clean pass having checked nothing. `TARGETS.md` carries this caveat on row 12
  and did not carry it on row 4. English was supplied by hand throughout instead
  of relying on it: identifiers resolve to English with the German as an alias, and
  notes are English-only with German confined to `aliases` and `quote_zh`.
- **visual** passes.
- **verify** is **red**, on 13 of 536 claims, and the cause is one thing.

## Why verify is red, in one sentence

`verify.py`'s tokeniser cannot read the German decimal comma, so
`Schmelzpunkt von 124,0°C` parses as the number 124 with no unit plus a separate
temperature of **zero** degrees, `1,637 Mg/m3` becomes the three numbers 1, 637
and 3, and `98 Gew.-%` yields 98 with no unit at all, which leaves nine claims
about the melting points, densities and polymorphic purity of the crystal
modifications unable to match the values printed beside them.

The other four are `__substance__` claims where the independent read saw a name on
a line that the record for that line does not hold: `kaolins` and `silica`,
`alizarin`, `Fenchlorazol` and `lodosulfuron`, and `systemin`. Three are inside
long lists where the record covers the list and the engine matches per line; the
fourth, `systemin`, is correctly excluded as a peptide named in transgenic-plant
boilerplate rather than a compound of the invention.

None of the 13 is a value the annotation invented. A red verify gate is what
`AGENT.md` describes as red on purpose on the reference patent, and it is why a
red gate does not by itself stop a row being `done`.

Fixing the tokeniser would be the honest fix for the nine, and it is in
`verify.py`, not in the gold. It will matter again for `DE10113137A1`.

## Final state

```
run_pipeline.py    reached the end, all 18 stages
selfcheck          37 pass, 1 warn, 0 fail
census             52 claims, 7.5 min of the 15 minute budget
validate.py        clean on all five artifacts, 364 records
manifest           135 artifacts, deliverable matches output/ on all 11 copied
grounded           96.8 percent, 13 of 536 claims not grounded
```

| artifact | records |
|---|---|
| compounds | 349 |
| reactions | 7 |
| pathways | 8 |
| patent | 1 |
| verification claims | 536 |
| structures resolved | 25 of 349 |
| independent read | 949 mentions over 115 lines, 0 span failures |

**Hand-authored at the gates: one SMILES entry, zero translations.**

## The one selfcheck warning

`reading B is not available on this machine`. ChemDataExtractor does not run, so
the substance sweep publishes `readers: ["llm"]` and every finding says "one
reader only". Unchanged from the previous runs and not specific to this patent.

## Things left undone, and open questions

- **`verify.py` cannot read German numerals.** Nine claims are ungrounded for that
  reason alone. Not fixed; the gold is not what is wrong.
- **`resolve_translations.py` is blind to German.** The gate passes on absence and
  will do the same on `DE10113137A1`. Not fixed.
- **The `merge_compound` container test is still there.** This run avoids it by
  writing `null`, but the next run that writes an all-null object will hit it, and
  the two earlier runs have not been checked for the same loss.
- **`quantity` and `analytics` encoding.** All 21 affected files now write `null`.
  Ten records keep `aliases: []`, deliberately: `aliases` is in `_UNION` where
  `[]` and `None` are equivalent, so it was never part of the loss.
- **`chemical_family` differs across sections** for the tembotrione family,
  `triketone` in most and `cyclohexanedione` in `preparation-general-process`.
  Harmless, because `finalise.py` unions tags and both existing runs carry the
  pair, but the per-section files read as though they disagree.
- **`MCPA`, `EPTC`, `2,4-D` and `2,4-DB` are typed `trivial_name`** where the enum
  offers `abbreviation`. Flagged by the audit, not changed.
- **`FINDINGS.md` says no hand-written analysis exists for this patent.** True of
  the file, not of the run: the headline-findings branch of
  `make_relevant_output.py` is hardcoded for CN104292137A with no input a run can
  supply its own through. This patent's findings are in this file.
- **The shared scratchpad caused one cross-agent clobber.** Two agents wrote
  generic script names to one path, one executed the other's generator, and six
  output files were rewritten by the wrong agent. Detected, repaired and verified,
  but the pattern will recur while the scratchpad is shared.
