# Stage outputs

One folder per pass, holding exactly what that pass produced, before any merging or
post-processing. Nothing here is rewritten by a later stage, so each folder can be
checked on its own.

| Folder | Written by | Contains |
|---|---|---|
| `A0-sections/` | A0 | `00-sections.json`, the section map |
| `A1-compounds/` | A1 | one `<section>.json` per section, plus its provenance sidecar |
| `A2-reactions/` | A2 | one `<section>.json` per section, plus its provenance sidecar |
| `A3-pathways/` | A3 | `pathways.json` as the prompt returned it |
| `A4-patent/` | A4 | `patent-llm.json`, narrative and tags only, before the biblio merge |
| `A5-verify/` | A5 | one report per artifact audited |

The merged, finalised artifacts land one level up in `output/`:
`compounds.json`, `reactions.json`, `pathways.json`, `patent.json`, `structures.json`.
Those, plus the provenance sidecars, the audits and the write-ups, are collected as
the actual deliverable in `../relevant_output/`.

`../../input/vision/pNN.json` is the pass-V output and is the input to all of this.

Reading order for a manual check:
1. `A0-sections/00-sections.json` - are the boundaries and types right
2. `A1-compounds/` - is anything named in the text missing, is anything invented
3. `A2-reactions/` - step count, conditions, and the `validation_flags` on each step
4. `A3-pathways/` - does the chain and its cumulative yield follow from A2
5. `A4-patent/` - narrative and tags
6. `A5-verify/` - what an adversarial read found in all of the above
