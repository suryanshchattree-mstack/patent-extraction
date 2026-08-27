# How a cited Chinese line resolves to its English

A trap, measured. Getting this wrong makes the tool accuse correct extractions of
being wrong, which is the single worst thing it can do.

## The shape of the source

`input/<PATENT_ID>-enriched-numbered.md` is bilingual. Three line kinds:

- `zh`  - Chinese, 103 lines
- `en`  - English, either marked with `> EN:` (90 lines) or plain (35 lines)
- blank - 28 lines

The commonest shape is simple alternation, `zh, en, zh, en`, 53 times. That is why
"the translation of line n is line n+1" looks right and mostly is.

It is not always right, and the exceptions are concentrated exactly where the
chemistry is.

## Where it breaks

    45 | 1) 1)2-氯-6-甲磺酰基甲苯的合成                  <- zh, a heading
    46 | 将2-氯甲苯、催化剂无水三氯化铝和溶剂加入到...      <- zh, the PROCEDURE
    47 |     > EN: 1) Synthesis of 2-chloro-6-...       <- en, the heading
    48 | 2-Chlorotoluene, the catalyst anhydrous...     <- en, the PROCEDURE

Two Chinese lines, then two English lines. So:

- Line 45's translation is line 47, not 46. Naive n+1 lands on another Chinese line
  and returns nothing at all.
- **Line 46's translation is line 48, not 47.** Naive n+1 returns the HEADING.

The second one is the dangerous case. Line 46 is where the masses, the temperatures
and the times live. A reviewer checking "25.3 g of 2-chlorotoluene" against line 46
would be shown "1) Synthesis of 2-chloro-6-methylsulfonyltoluene", a heading with no
number anywhere in it, and would correctly conclude the evidence does not support the
claim. The extraction was right. The pairing was wrong.

## Measured

Over the 288 compound-provenance citations that point at a Chinese line:

    naive n+1 disagrees with block pairing on   54  (19%)
    block pairing supplies a line in all 54 of those

Some of the 54 are cases where naive returns nothing; the rest return a heading in
place of a body. Both fail the reviewer, the second one silently.

## The rule to use instead

Pair by BLOCK, not by offset.

1. Walk the file. Take each maximal run of consecutive `zh` lines, then the maximal
   run of `en` lines that immediately follows it.
2. If the two runs are the same length, pair them positionally: the i-th Chinese line
   pairs with the i-th English line. This is the case that matters and it is exact.
3. If the lengths differ, pair what you can positionally and clamp the overflow to the
   last English line, but MARK those as approximate so a consumer can say so on screen.
4. A line that is already English is its own translation.
5. A line with no English anywhere in its block has no translation. Say that in
   English; never fall back to showing the Chinese.

## Who implements it

The pipeline, once, in `verify.py`, which ships `evidence_en` already resolved inside
each claim. The UI must not pair lines itself for the review queue: it renders what
the contract hands it. That keeps one implementation rather than two that can drift.

`verifier/lib/source.ts` still pairs for the older two-pane screen. Its docstring
records that 373 of 395 citations resolve and 22 do not; those 22 are this bug, and
block pairing closes them. Fix it there too, or retire the screen.
