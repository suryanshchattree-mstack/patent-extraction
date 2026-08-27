# 28 translations answer a heading with the whole abstract

Latent, not live: nothing renders these today and all 13 routes are clean. But any
consumer that trusts an `en` value to be English will leak Chinese, and this would
have fired on the next patent.

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

## Not fixed here, deliberately

`resolve_translations.py` is a 36 KB file with careful tier logic and three gates, and
its author is unavailable. The defect is latent, so the risk of changing selection
logic unsupervised exceeds the benefit of closing a leak nothing currently renders.

The verification is cheap when someone does it: after the change, all 28 should resolve
to their `[0006]`-style heading translations, `check_substitution.py` should stay at
28/28, and the coverage gate should stay at 274/274.
