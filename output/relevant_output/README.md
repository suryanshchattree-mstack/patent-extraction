# Gold annotation of CN104292137A

A hand-run reference annotation of one patent, in LiteratureIQ's own JSON schemas,
for scoring the automated extractor against.

Patent: **CN104292137A**, *Synthesis process for the triketone herbicide
tembotrione*, Wuhan Institute of Technology, filed 2014-10-15, DOCDB family
**52312131**. Its Example 1 is a complete eight-step linear route to tembotrione,
the same molecule as the Day 2 discovery golden test.

> Google's English title reads *Process for synthesizing triketone herbicide cyclic sulcotrione*, which glosses 环磺草酮 character by character and names sulcotrione, a real and different herbicide this route does not make. The title here follows the Chinese, and the gold's own translation index,
> which resolve 环磺草酮 to tembotrione.

## What is here

```
gold/          the reference annotation, plus the JSON Schema for each artifact
provenance/    where every record came from, and the arithmetic behind each check
verification/  four independent adversarial audits of the above
structures/    one 2D drawing per unique molecule, monochrome SVG
FINDINGS.md    what is wrong with the patent
AUDIT.md       what the audits found, what was fixed, what is outstanding
svg/           six diagrams, each as SVG and JPG.
               approach.* is the one-page summary of the whole method.
```

| file | records | what it is |
|---|---:|---|
| `gold/compounds.json` | 75 | `CompoundRecord[]`. Identity, role, quantity, characterisation, tags. |
| `gold/reactions.json` | 33 | `ReactionRecord[]`. Steps with conditions, workup, classification, linkage, validation flags. |
| `gold/pathways.json` | 5 | `PathwayRecord[]`. Stitched chains with cumulative yield. |
| `gold/patent.json` | 1 | `PatentRecord`. Bibliographic, narrative, tags, rollup. |
| `gold/structures.json` | 9 drawings | The 18 structures and 9 scheme arrows drawn across the pages, each read substituent by substituent with its ring positions. No production counterpart. |
| `gold/structures-resolved.json` | 75 | One entry per distinct compound identifier: SMILES, RDKit canonical SMILES, molecular formula, molecular weight, the drawing that shows it, and `origin`, which says where the structure came from. 39 of the 75 resolve. |
| `structures/` | 22 drawings | One 320x240 monochrome SVG per unique molecule, written by `../../resolve_structures.py`. The `svg` field of each resolved entry is a path relative to this directory's parent. |

## Using it

Run the production extractor over the same patent and diff artifact against
artifact. The schemas are transcribed from the Java records in
`literatureiq-engine/core/model/persistent/`, and ids and UUIDs are computed by
`../../finalise.py` reproducing `PersistentRecordBuilder` and `PathwaysBuilder`, so
records key-join rather than sitting in a parallel namespace.

**Before joining on `compound_uuid`, read `provenance/compounds-equivalence.json`.**
Eight molecules appear under three English spellings each, because extraction runs
per section with no shared vocabulary. They are deliberately not merged: production
keys on the exact identifier string and fragments them identically, so merging here
would create a diff that has nothing to do with extraction quality. Join on the
equivalence index instead, or the recall numbers will be wrong.

**Do not benchmark enrichment against this.** `smiles`, `inchi_key`,
`molecular_formula`, `atom_mapped_rxn`, the template fields and all six scores are
null on purpose. They are produced by a downstream service, not by extraction, and
no prompt in this pack can produce them honestly. Structures read off the drawings
live in `aliases[]` as SMILES, which is where MolScribe output arrives in
production.

**Structures come from the sidecar, not from the records.** `gold/structures-resolved.json`
maps each of the 75 identifiers onto a structure, and every entry carries an
`origin` saying how strong that claim is. Nothing is merged back into
`compounds.json`, so the records still diff cleanly against a production run.

| `origin` | count | what it means |
|---|---:|---|
| `patent_scheme` | 3 | the identifier string is itself a SMILES, read off the drawn scheme |
| `patent_drawing` | 14 | the molecule is drawn in the patent, joined on RDKit canonical SMILES |
| `derived` | 10 | same molecule as a synonym, propagated along `provenance/compounds-equivalence.json` |
| `curated` | 12 | named in the patent but never drawn, hand-authored in `../../input/structures-curated.json` |
| `none` | 36 | no structure: solvents, workup reagents, and the class terms the gold records `resolved: false` |

The join is on canonical SMILES and never on names. `gold/structures.json` holds 18
SMILES for 11 unique molecules, and 12 of its 16 distinct names match no record
name, because the drawn scheme is read more than once and the reads name things
differently. A name join would report molecules that **are** drawn in the patent as
not drawn. Treat `patent_drawing` as a claim about the patent and `curated` as a
claim about us: only the first is evidence.

All 34 identifiers that carry chemistry, meaning they are a reaction product or
appear in a reaction-compound row with both `mass_g` and `mmol`, resolve to a
structure with a formula. That is enforced, not observed: `resolve_structures.py`
exits non-zero otherwise.

## What this annotation is not

- Not experimentally verified. It is a faithful record of what one document says.
- Not a corrected version of the patent. Where the patent's arithmetic does not
  close, the numbers are recorded as printed and a flag is raised. See `FINDINGS.md`.
- Not clean. 24 of 33 reactions carry at least one validation flag, and that is the
  correct result for this document.

## Provenance

| file | what it gives you |
|---|---|
| `compounds-provenance.json` | source line and verbatim Chinese quote per compound |
| `reactions-provenance.json` | same, plus `arithmetic_check`: the input moles, product mass, stated yield, molecular weight used, and whether it closes |
| `compounds-sections.json` | which sections each compound was found in |
| `compounds-equivalence.json` | which identifiers are the same molecule |

## How it was made

Nine pages, no text layer at all. Pages rendered to PNG and read by vision agents,
one per page, which transcribed the Chinese verbatim and read every drawn structure
substituent by substituent. Their output was assembled into enriched markdown with
inline `[IMAGE_EXTRACT: {...}]` spans, the same format production's Phase 1 produces
via Mistral OCR plus MolScribe/RxnScribe. Then A0 section map, A1 compounds, A2
reactions, A3 pathways, A4 patent record, and A5 four adversarial audits that
re-opened the page images. Last, `resolve_structures.py` attached a 2D structure to
every identifier it could and refused to exit clean until every molecule that
carries chemistry had one.

Full method, per-pass prompts and stage-by-stage outputs are two levels up in
`../../`. See `../../README.md` for the method and `../stages/README.md` for the
unmerged per-pass output.
