# The one failure that was not a detection failure

Everything else recorded tonight was a check that could not see the thing it was
written to see. This one is the opposite, and it is worth keeping separate because the
fix is completely different.

## What happened

The exported completeness report went out with the wrong molecule on line two:

    Process for synthesizing triketone herbicide cyclic sulcotrione

against a body that says **tembotrione** twenty-three times. Sulcotrione is a real and
different triketone herbicide, so the first line a colleague reads named a compound the
route does not make.

It reached `gold/patent.json`, the completeness report, and the self-contained export.

## The part that matters

**The pipeline had already found it.** `AUDIT.md`, produced by the A5 adversarial pass,
finding 19, written hours before anyone looked at the export:

> "The title names a different herbicide from the one the document is about: 'cyclic
> sulcotrione' is Google's character-by-character gloss of 环磺草酮 (环 = cyclic,
> 磺草酮 = sulcotrione) and is not a compound, while sulcotrione itself is a real and
> different triketone.
> **fix:** Follow the Chinese. [0002] gives the chemical name and attributes it to
> Bayer in 2007, which is tembotrione"

Correct diagnosis, correct mechanism, correct fix, and the exact reasoning two people
later reproduced independently while believing they had found something new.

It sat under the heading **"Outstanding, by severity"** and everything downstream
shipped anyway.

## So this was never a detection failure

The adversarial pass did its job perfectly. What failed is that a finding it produced
had no consequence. Nothing downstream of `AUDIT.md` reads `AUDIT.md`. An "Outstanding"
list is a document, and documents do not stop pipelines.

Compare the checks that DO stop things: `resolve_structures.py` exits non-zero when a
molecule carrying chemistry has no structure, `resolve_translations.py` exits non-zero
when a string cannot be rendered in English, `verify.py` exits non-zero on a grounding
failure. Every one of those is a gate. None of them can be shipped past.

**A finding on a list and a finding on a gate are different objects.** The audit
produced the first when only the second changes behaviour.

## What was actually done

- The title is fixed at source, in the one hand-authored input that feeds it, so it
  survives a rerun.
- `title_en_note` records why it is deliberately not the machine title, so nobody
  restores it from Google Patents later.
- The finding moved from "Outstanding" to "Acted on" automatically, by being added to
  the bookkeeping the report generates from.
- Every remaining occurrence of the word in the deliverable is now ABOUT the
  discrepancy rather than asserting it.

## The general rule

**A check whose output is a list needs someone whose job is reading the list. A check
whose output is an exit code does not.** Prefer the second wherever the finding is
mechanical enough to express that way.

Where it genuinely cannot be - and much of the A5 audit is judgement that no gate could
express - then the list needs an owner and a review step, and "Outstanding" needs to
mean something to somebody. Otherwise the most careful adversarial pass in the project
produces a document nobody reads and a wrong molecule ships on line two.
