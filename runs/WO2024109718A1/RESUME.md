# WO2024109718A1: where this run stopped

Stopped deliberately at a checkpoint, mid pass A5. Everything below is on disk and
committed. Nothing is half written: the two A5 audits that were still running were
killed before they wrote, so their outputs are simply absent rather than partial.

## Done

| pass | state |
|---|---|
| PDF, biblio, page renders | done. 45 pages, no text layer at all, so every character comes from pass V |
| V, page vision | done, 45 of 45 pages |
| A0, section map | done, 22 sections, 1121 lines, no gaps or overlaps |
| A1, compounds | done, 16 sections, 284 raw records, 137 after merge |
| A2, reactions | done, 15 sections, 71 steps |
| A3, pathways | done, 27 pathways |
| A4, patent record | done |
| step 6, independent read | done, 1014 specific and 198 generic mentions over 147 distinct names |
| A5, adversarial audit | **2 of 4**: patent.json and pathways.json written, compounds and reactions NOT run |

## The exact next command

```
python3 pipeline/run_pipeline.py --patent-id WO2024109718A1
```

It will ask for A5. Two audits are owed, each in a FRESH context, each re-opening the
page images:

- `output/stages/A5-verify/compounds.json`, over `output/compounds.json` (137 records)
- `output/stages/A5-verify/reactions.json`, over `output/reactions.json` (71 records)

The compounds audit has now failed twice, once to a machine sleep and once to this
stop. Tell whoever runs it to write its output as soon as the findings settle rather
than at the end of a long analysis.

After A5 the run reaches the two gates, structures and translations, which are the
next things that will need a human. Neither has been touched yet.

## What the two completed audits found, unfixed

`patent.json`: 10 findings, 1 major. The major one is that
`extraction_rollup.scale_distribution` calls Examples 2 and 3 `pilot` while Example 1,
which charges more, is `lab`. The fix is in `reactions.json`, not in the rollup.

`pathways.json`: 15 findings, 1 critical. The critical one is that the Claims pathway
through step (vi) collapses four drawn arrows into one, so the benzoic acid, the
benzoyl chloride and the enol ester are missing from its intermediates and its chain
length is wrong. Two further systematic findings: `steps[].components` carries
reagents and byproducts where rule 12 says it should not, on 40 of 71 steps, and
`compounds[].role` was re-classified rather than copied verbatim on 12 reactions.

None of these has been acted on. Read the audit files before deciding.

## Two things a reviewer should know about how this run was produced

**The vision pass rendered 环磺酮 four different ways**, and one of them named a
different herbicide. Four paragraphs on pages 21 and 23 read `sulcotrione`, which is
磺草酮, not 环磺酮; eight more on pages 7, 8 and 13 read `cyclic sulfone ketone`, a
character gloss. All twelve were corrected to `tembotrione` in `input/vision/*.json`,
each with a note on the paragraph recording what the pass originally wrote. The Chinese
is untouched and authoritative. The patent's own printed English title, CYCLOSULFONONE,
is left as printed on page 1, because that is what the document says.

**The parallel vision agents shared one scratch directory and clobbered each other.**
Four of them reported reading back a crop of a different page than the one they had
written, and two said they nearly transcribed another page's chemistry before catching
it. Later agents were given per page subdirectories. A cross page sweep afterwards found
paragraph markers 0001 to 0146 exactly once each, in order, with no gaps, which is the
evidence that no contamination reached the transcripts. Anyone running V in parallel
should give each page its own scratch directory from the start.

**Provenance of the model work.** The vision pass, all five extraction passes, the two
completed A5 audits and the step 6 independent read were all produced by Claude Opus 4.5
through Claude Code, in separate contexts. They are not independent in the way the word
usually implies. Where the extraction missed something and the step 6 read missed it
too, nothing here can see that.
