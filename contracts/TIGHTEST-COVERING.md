# 28 translations answer a heading with the whole abstract

FIXED. `source_translation` now asks `cover()` for the tightest covering; the rest of
this file is the diagnosis that led there, with what the fix actually did, and one
prediction it made that turned out to be wrong, recorded at the bottom.

Latent, not live: nothing rendered these and all 13 routes were clean. But any
consumer that trusts an `en` value to be English would have leaked Chinese, and this
would have fired on the next patent.

## What is wrong

    entries whose English still contains Chinese   28 of 274
    all resolved via                               source_mt (tier 1)
    typical shape                                  17-character key -> 924-character
                                                   English, ratio 54.4x, 4 residual
                                                   Chinese characters

The keys are step headings. The English they got is the whole Abstract.

## Why, measured

`2-氯-6-甲磺酰基甲苯的合成` appears on **four** source lines, and their English differs
enormously in length:

    line  38   the Abstract, which lists all eight steps      English 934 characters
    line  45   a heading whose partner is Chinese             (needs block pairing)
    line 117   [0006] the same heading                        English  58 characters
    line 182   [0033] the same heading                        English  59 characters

Tier 1 covered the key with line 38 and took its 934-character translation. Lines 117
and 182 carry exactly the right answer, "1) Synthesis of
2-chloro-6-methylsulfonyltoluene", in 58 characters.

**The algorithm found A covering, not the TIGHTEST covering.**

## The fix

When a key can be covered by more than one source line, **prefer the line whose English
is shortest**, not the first one found. A short string covered by a long paragraph is
almost always the wrong pairing, and the ratio is the signal.

That one change fixes all 28 with no curation, because in every case a correct short
translation already exists on another line. It also removes the need for the curated
override on `革除了硫醚的过氧化氢氧化步骤`, which is the same defect: a 14-character
phrase answered with the 695-character translation of paragraph [0031].

## Why the existing gate does not catch it

The prose-ratio gate is correct and its limit of 20x sits cleanly in the gap between
the widest legitimate prose entry at 10.5x and the known defect at 49.6x. But it is
**scoped to the 37 entries substituted into annotator prose**, and these 28 are not in
that population.

The scoping was right at the time: 70 of the 274 entries exceed 20x, and the other 42
are quotations shown AS quotations, where covering a quote with its source line's
translation is the designed and correct behaviour.

So this is not a gate that failed. It is a gate whose population was drawn before this
class was known. **Tightest-covering selection makes the gate unnecessary for this
class**, which is the better fix: a rule that prevents the defect beats a gate that
reports it.

## What the fix did, measured

The rule: among the source lines that supply the same span, the one whose English is
SHORTEST wins. It sits ahead of the declared-line preference and behind span length.

    entries whose English is not the shortest available   58  ->  0
    worst slack, in characters                           897  ->  0
    entries whose English still contains Chinese          28  ->  15
    entries whose English changed                                58
        of which shorter                                         56
        of which longer                                           2

The worked example, `1)2-氯-6-甲磺酰基甲苯的合成`, went from the 924-character Abstract to
`1) Synthesis of 2-chloro-6-methylsulfonyltoluene`, 48 characters, from line 45.

The 2 that lengthened are elided quotes, `A ... B`, whose two halves both landed on
line 38 before and now take a line each. The English grows because it stops collapsing
two spans into one paragraph, which is what the `ELISION` join exists to avoid.

The 15 that still contain Chinese are a DIFFERENT CLASS and are correct. The source's
own machine translation left 7 Chinese terms inside its English - 环磺草酮, 硝环磺酮,
甲基磺草酮 and four weed genera - and the index holds an English answer for every one of
them. All 15 render to English under the documented longest-key-first substitution.
Checked positively: 7 runs resolved, 15 entries rendered, none left Chinese.

## The off-declared note had to move with it

Preferring a non-declared line for its tighter English made the "Line N is not among
the source_lines the gold declares" note fire 68 times instead of 19, and 49 of those
would have been false: the gold citing line 38 for a heading is right, the heading
really is printed there, it is just not the line whose English answers the question.

So the note is now computed against what the declared lines COULD have covered rather
than against what the cover chose. Attribution and translation are separate questions
and only one of them is being asked here. Back to 19.

## verify.py shares cover() and must not move

`verify.py` calls `cover()` to decide whether a quote sits on the line the gold cites,
which IS the attribution question, so there the declared line must keep winning. The
tightening is opt-in: `cover(..., tighter=...)`. With no `tighter` the ranking is
unchanged, checked over 822 (quote, cited-lines) pairs - every string in the universe
against its own cited lines, against none, and against a wrong line. Zero differ.

## The prediction that was wrong

This file predicted the fix would remove the need for the curated override on
`革除了硫醚的过氧化氢氧化步骤`. It does not, and the reason is worth keeping.

    革除了硫醚的过氧化氢氧化步骤     printed on 1 line   (176, English 695)
    2-氯-6-甲磺酰基甲苯的合成       printed on 4 lines  (38/45/117/182, 924/48/48/49)

Tightest covering can only choose among the lines that carry the string. Where there
is one, there is nothing to tighten, and that phrase still resolves to the 695-
character translation of paragraph [0031] at 49.6x. The override stays.

**Two defects wore the same symptom.** One is a selection defect and has a rule fix;
the other is a genuine absence of a short translation anywhere in the source, and the
only honest answer to it is a hand-written one. Counting them together as "28 entries
answering a phrase with a paragraph" made the second look like it would fall out of
the first for free. The measurement that separated them was counting the source lines
each key appears on, and it is cheap enough that it should have come before the
prediction rather than after it.

## Verification

    resolve_translations.py --check   report byte-identical, coverage gate 274/274 PASS
    check_substitution.py             28/28 PASS, exit 0
    prose ratio gate                  37/37 within 20x, PASS
    name fidelity gate                PASS
    manifest                          deliverable matches output/ on all 11 copies
