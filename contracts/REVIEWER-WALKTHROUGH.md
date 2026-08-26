# Reviewer walkthrough

One person, timed, using the tool the way the intended user would. No pipeline
knowledge used: every judgement below was made from what the screen showed.

Session: 2026-08-27, 02:11 to 02:35 IST. Dev server on **port 3100**, not 3500.
Browser: headless Chromium at 1440x950 through Playwright, real keypresses.

---

## The short version

The tool is **mechanically excellent and arithmetically impossible**.

Rendering is instant, the keyboard never dropped a key, the empty states are the
best-designed thing in the project, and the structure comparison already solves the
mirroring problem before the reviewer can fall into it.

But the tier the protocol says to do first and in full is the tier where the UI
offers the reviewer no help at all, and it is roughly **twice the size of the entire
time budget on its own**. And in a 12-claim sample, **every single tier 1 claim was a
false positive** - the machine said it could not find a value that is plainly
rendered a few lines below, under a bold instruction to answer "Wrong".

A reviewer who trusts the screen and moves at the intended pace does not produce a
defensible judgement. They produce a list of manufactured defects.

---

## 1. Getting in: the port is wrong in the brief

`3500` was dead, and so was `3400`. The verifier's dev server was already running on
**3100** and had been for some time. Anyone handed "use 3500" loses their first
minutes to a server that is not there, then risks starting a second one and being
told `Another next dev server is already running`.

Not a product defect, but it is the first thing a new reviewer hits.

---

## 2. What works, and works well

**Speed.** Keypress to the next claim fully rendered: **median 3 ms, max 16 ms**
across 12 claims. A full page navigation is ~1.0 s. The tool never made me wait.

**The keyboard.** `1`, `2`, `3`, `s` and `u` all registered. Nothing was dropped,
nothing double-fired, nothing was ambiguous. Answering with `1` moved the counter
`0/78 -> 1/78` and `143 left -> 142 left` in the same frame.

**Meaning never rides on colour alone.** Every state carries a glyph: `[!!]` high
risk, `[x]` could not find, `[=]` matched here, `[P]` about the patent, `[+]` yes,
`[?]` unsure, `[>]` skip. Printed in greyscale this survives intact.

**The `[P] about the patent` badge is the best idea in the interface.** When the
annotation is reporting a defect it found *in the patent*, the screen says so and
explains what answering no means: "Answering no records that the annotation misread
the document; it does not record a defect in the extraction." That is the single
distinction most likely to be got wrong by a tired reviewer, and it is handled
explicitly, in plain words, at the point of decision.

**The empty states are outstanding and should not be touched.** When the checks file
went unreadable mid-session, all three dependent pages refused to render and said
why, naming the file and the exact failing fields:

> This page derives every number from that one file and computes no chemistry of its
> own, so there is nothing it can show you until the file exists. **It is NOT showing
> you a zero.**

and

> The queue refuses to render a partial parse. Half a file looks exactly like a
> complete one to a reviewer working at six seconds a claim, and a pass over half the
> claims that reports itself as a pass over all of them is worse than no pass at all.

That is a tool that fails safe instead of quietly lying. It is the difference between
this being decision-support and being a liability.

**The structure comparison already defeats the mirroring trap.** The predicted
failure - non-chemist sees a flipped rendering, says "not the same molecule", rejects
a correct extraction - **did not happen to me**, because the sheet pre-empts it in
bold above the question:

> BEFORE YOU ANSWER: these two may be drawn flipped or turned round. That is the same
> molecule, not a different one. Compare WHICH groups are attached to the ring, and to
> which neighbours, not where they sit on the page. 9 of 10 panels are laid out the
> patent's way; the rest are however our drawing tool chose.

It also declares its own weakness unprompted: "HOW THE HALVES WERE PAIRED: **WEAK**",
and scopes itself honestly - "This picture answers one question and no other. It does
not say the chemistry is right, only whether we wrote down the molecule the patent
drew." I compared all ten panels against the patent's scheme by attached groups and
answered yes. It took me around 90 seconds, not 6, but it was genuinely answerable
without knowing chemistry.

---

## 3. The finding that matters: tier 1 is full of false positives

I stepped through the first 12 claims of queue 1 and, for each, checked whether the
value the annotation is accused of inventing actually appears in the source lines the
claim itself cites.

| outcome | count | what it means |
|---|---:|---|
| exact string present in cited lines | **7** | the machine simply missed it |
| present in different units | **2** | extraction says `200 mmol`, patent prints `0.2 mol` |
| claim is prose, never string-matchable | **3** | "the masses printed for this step do not balance" |
| genuinely absent | **0** | |

**Zero of twelve were real.**

### The worked example

Claim 1 of 78 asks:

> The patent's own numbers for this step do not agree with each other. Does the page
> really print 28.6 g of 2-chloro-6-(methylsulfonyl)toluene from 200 mmol at 84%?

Banner: `[x] Machine could NOT find this in the cited lines`. Orange callout:

> The machine read every line above and did not find this value. **If you cannot find
> it either, answer Wrong**: that is the signal this pass exists to collect.

Cited lines are 182-188. Line 187, rendered on the same screen, ends:

> ...the organic phases were combined and concentrated to give a pale yellow solid
> **28.6 g, yield 84%.**

The value is right there. The correct answer is `1`, and I answered `1`. But the
element telling the reviewer to answer `2` is bold, orange, and above the fold, while
the evidence contradicting it is **1,081 px down a scroll pane** whose visible window
is 710 px. The loudest thing on the screen is wrong, and the thing that refutes it
requires scrolling.

### The unit case is worse, because it is invisible

The annotation records `200 mmol`. The patent prints `0.2 mol`. Identical quantity.
The grounding check does a literal string comparison, fails, and reports `not_found`.

A non-chemist is then told to search for "200 mmol", scans the line, sees "0.2 mol",
and has no way to know those are the same thing. **They answer Wrong and record a
false defect against a correct extraction.** This is exactly the predicted
mirrored-structure failure, arriving on units instead of pictures, and unlike the
structure comparison there is no warning box protecting them from it.

---

## 4. Pace: the budget does not close

Measured per tier-1 claim, across 12 claims:

| | |
|---|---|
| evidence text | median **4,331 characters** (min 4,081, max 5,499) |
| scroll pane | median **1,771 px** inside a **710 px** window |
| screenfuls to scan | median **2.5** |
| render after keypress | median **3 ms** |

The mechanical cost is nil. The whole cost is reading.

**And in tier 1 there is nothing to aim at.** The affordance that makes a claim fast
is the `[=] the yield matched here` marker, which puts the reviewer's eye straight on
the right line. That marker exists *only for claims that matched*. Tier 1 is by
definition the claims that did not match, so the reviewer performs an unaided visual
search over 2.5 screens of dense procedure text, for every one of 78 claims.

A full careful read of 4,331 characters of technical prose is about 260 seconds. Real
reviewers do not read, they scan - but an unaided scan of 2.5 screens for one number
is realistically 20 to 45 seconds, not 6.

The arithmetic that follows:

- Total budget: **900 s**
- Protocol allots tier 1 roughly a third: **300 s** for **78 claims = 3.8 s each**
- Observed floor with no highlight to aim at: **~20 s each = 1,560 s**

**Tier 1 alone is about 1.7x the entire fifteen-minute budget**, and the protocol
expects it to consume one third. The three-tier structure does not rescue this,
because tier 1 is a census and censuses cannot be sampled down.

The queues as the tool actually presents them: **78 could-not-confirm, 15 uncited
chemistry, 50 machine-matched (drawn from 301, 17%), 11 annotator's open questions -
143 total.** The brief said 62 / 15 / 309; the counts have moved.

### The design inversion

The tier that must be done **first and in full** is the **slow** one. The tier that is
**fast**, because it has match highlights, is the one that is **sampled**. If the
highlight machinery could point at *near* misses - the line containing `0.2 mol` when
looking for `200 mmol` - tier 1 would collapse to something close to tier 3's pace.
That is the single highest-leverage change available.

---

## 5. The schema claims

12 claims carry `about: "schema"` with `quantity_verdict: "schema_loss_second"` and
`needs_human: true`. Example:

> Line 187 prints 10 degrees C, and the field that would hold this number already
> holds 5 degrees C from an earlier stage.

Nothing is wrong. The step has two stages, the patent prints a temperature for each,
and the record has one slot. The data carries everything needed to say so - the
`about` discriminator and a written `auto_reason_en`.

**Whether the screen makes that obvious, I could not test**: the queue went down
before I reached one. Given the `[P] about the patent` badge exists and is well
executed, an analogous badge for `about: schema` is the obvious shape, but I am not
going to claim I saw it when I did not.

---

## 6. What the outage blocked

At **02:20**, mid-session, `verify.py` regenerated the checks file and introduced a
new `auto` value, **`not_reconciled`** (8 claims). The UI's contract accepts only
`found | not_found | partial | not_checkable`. Three of the four pages went down and
stayed down:

| page | state |
|---|---|
| `/CN104292137A` route spine | works (reads the gold, not the checks file) |
| `/CN104292137A/review` | **down** |
| `/CN104292137A/coverage` | **down** |
| `/CN104292137A/report` | **down** |

`not_reconciled` is very likely the right change - it is a far more honest label for
the arithmetic claims than `not_found`, and it addresses the false-positive class
above. The defect is that producer and consumer share no enforced contract, so a
one-word addition on the Python side takes the reviewer UI to zero with no warning,
mid-review.

**Therefore untested, and honestly unknown:**

- **Bulk accept**, including whether `attention: "batch"` is recorded and whether
  bulk-accepted claims are distinguishable from individually confirmed ones on disk.
  This was an explicit question and it does not have an answer yet.
- `u` undo and `j`/`k` navigation inside the review queue. (`1`, `2`, `3`, `s` were
  all exercised and all worked.)
- The coverage map and the completeness report, and whether they answer "can I trust
  this extraction" for someone who was not in the room.
- The on-screen presentation of the 12 schema claims.

One verdict was written during the session, by pressing `1` on claim 1. It landed
correctly, with `attention: "record"`, `verdict: "correct"`, and a content hash:

```json
{"rec":"rx:Example 1_Step 1","field":"yield_identity","artifact_says":"28.6 g",
 "verdict":"correct","attention":"record","by":"yash.singh","schema":1}
```

So the individual write path is sound. Only the batch path is unverified.

---

## 7. What I would change, in order

1. **Make the grounding check unit-aware, or stop calling the result `not_found`.**
   `200 mmol` vs `0.2 mol` is not a hallucination and must not be presented to a
   non-chemist as one. `not_reconciled` looks like the start of this.
2. **Soften the instruction, or move the evidence.** "If you cannot find it either,
   answer Wrong" is a confident instruction sitting above evidence that frequently
   refutes it. Either the check earns that confidence or the sentence should not be
   that loud.
3. **Give tier 1 something to aim at.** Highlight near misses and numerically-equal
   values in other units. This is what turns 20 seconds into 6, and it is the only
   change that makes the budget close.
4. **Version the checks contract** so a producer change fails loudly at write time
   rather than silently at read time, mid-review.
5. **Re-check the tier 1 population after 1 and 3.** If the false-positive rate in my
   sample holds across the census, tier 1 is far smaller than 78 and the whole budget
   problem may evaporate on its own.

---

## 8. One thing I got wrong

I first read the evidence pane as truncating at line 187 and silently dropping cited
line 188, and nearly reported it. It does not. All seven cited lines render; my own
text extraction had truncated them. Recorded here because a walkthrough that only
lists confirmed hits is not showing its work.
