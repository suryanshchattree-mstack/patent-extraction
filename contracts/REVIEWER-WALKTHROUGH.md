# Reviewer walkthrough

One person, timed, using the tool the way the intended user would. No pipeline
knowledge used: every judgement below was made from what the screen showed.

Session: 2026-08-27, 02:11 to 02:55 IST. Real keypresses through a headless Chromium
at 1440x950. Four verdicts written to the real log, listed in section 9.

---

## The short version

The tool is **mechanically excellent, honest to a fault in its reporting, and not
yet usable for the job it was built for.**

Three things are genuinely first-rate and should not be touched: the empty states,
the completeness report's separation of populations, and the structure comparison,
which already defeats the mirroring trap before a reviewer can fall into it.

Against that:

- **Every tier-1 claim in a 12-claim sample was a false positive**, under a bold
  instruction to record it as a defect.
- **Bulk accept does nothing.** No network call, no write, from either the shortcut
  or the button.
- **`3` is bound to two different actions on the same screen** and wrote a verdict on
  a claim I never read.
- **Undo does not reach disk.** The retracted verdict survives a reload and is
  counted in the completeness report.
- **Tier 1 is roughly twice the entire fifteen-minute budget on its own.**

---

## 1. Getting in

`3500` was dead, and so was `3400`. The verifier was already running on **3100**.
Anyone handed "use 3500" loses their first minutes, then risks starting a second
server and being told `Another next dev server is already running`.

---

## 2. What works, and works well

**Speed.** Keypress to next claim fully rendered: **median 3 ms, max 16 ms** over 12
claims. Page navigation ~1.0 s. The tool never made me wait.

**Meaning never rides on colour alone.** Every state carries a glyph: `[!!]` high
risk, `[x]` could not find, `[=]` matched here, `[P]` about the patent, `[E]` about
our extraction, `[+]`, `[?]`, `[>]`. This survives greyscale printing intact.

**The `[P] / [E]` distinction is the best idea in the interface.** When the annotation
is reporting a defect it found *in the patent*, the screen says so and spells out
what answering no means: "Answering no records that the annotation misread the
document; it does not record a defect in the extraction." That is the distinction
most likely to be got wrong by a tired reviewer, handled explicitly at the point of
decision.

**The empty states are outstanding.** When the checks file went unreadable mid-session
every dependent page refused to render and said why, naming the file and the exact
failing fields:

> This page derives every number from that one file and computes no chemistry of its
> own, so there is nothing it can show you until the file exists. **It is NOT showing
> you a zero.**

> The queue refuses to render a partial parse. Half a file looks exactly like a
> complete one to a reviewer working at six seconds a claim, and a pass over half the
> claims that reports itself as a pass over all of them is worse than no pass at all.

That is a tool that fails safe instead of quietly lying.

**The completeness report is the most honest document in the project.** It separates
three populations and never merges them, states "A machine string match is not a
human confirmation", flags `CENSUS INCOMPLETE` with the unseen count, and refuses to
let a small sample flatter itself:

> At most 78 in 100 of the 264 nobody read are likely to be wrong. This does NOT say
> the extraction is 22% correct.

**The coverage page audits its own arithmetic in public.** It reports 208 cited + 20
uncited = 228 non-blank lines, notices that the engine's own summary says 222, and
explains the discrepancy rather than hiding it: "counting it in the numerator while
dropping it from the denominator is how a coverage figure flatters itself."

**The structure comparison already defeats the mirroring trap.** The predicted failure
- non-chemist sees a flipped rendering, says "not the same molecule", rejects a
correct extraction - **did not happen to me**, because the sheet pre-empts it in bold
above the question:

> BEFORE YOU ANSWER: these two may be drawn flipped or turned round. That is the same
> molecule, not a different one. Compare WHICH groups are attached to the ring, and to
> which neighbours, not where they sit on the page.

It also volunteers its own weakness - "HOW THE HALVES WERE PAIRED: **WEAK**" - and
scopes itself: "This picture answers one question and no other. It does not say the
chemistry is right, only whether we wrote down the molecule the patent drew." I
compared all ten panels by attached groups and answered yes. It took ~90 seconds, not
6, but it was genuinely answerable without knowing chemistry.

---

## 3. Tier 1 is full of false positives

I stepped through the first 12 claims of queue 1 and checked, for each, whether the
value the annotation is accused of inventing actually appears in the lines the claim
itself cites.

| outcome | count |
|---|---:|
| exact string present in the cited lines | **7** |
| present in different units (`200 mmol` vs `0.2 mol`) | **2** |
| claim is prose, never string-matchable | **3** |
| genuinely absent | **0** |

**Zero of twelve were real.**

### The worked example

> The patent's own numbers for this step do not agree with each other. Does the page
> really print 28.6 g of 2-chloro-6-(methylsulfonyl)toluene from 200 mmol at 84%?

Banner: `[x] Machine could NOT find this in the cited lines`. Orange callout: "The
machine read every line above and did not find this value. **If you cannot find it
either, answer Wrong.**"

Line 187, one of the seven cited lines, on the same screen, ends:

> ...concentrated to give a pale yellow solid **28.6 g, yield 84%.**

The loudest element on the screen instructs the reviewer to record a defect against a
correct extraction. The evidence refuting it sits **1,081 px down a scroll pane whose
window is 710 px**.

### The unit case is worse, because it is invisible

The annotation records `200 mmol`; the patent prints `0.2 mol`. Identical quantity.
The check does a literal string comparison, fails, reports `not_found`. A non-chemist
searches for "200 mmol", sees "0.2 mol", and has no way to know they are the same.
**They record a false defect.** This is the predicted mirrored-structure failure
arriving on units instead of pictures, and unlike the structure comparison there is
no warning box protecting them.

`not_reconciled`, which verify.py introduced mid-session, looks like the right fix for
the arithmetic subset.

---

## 4. Pace: the budget does not close

Per tier-1 claim, over 12 claims:

| | |
|---|---|
| evidence text | median **4,331 characters** (4,081-5,499) |
| scroll pane | median **1,771 px** in a **710 px** window |
| screenfuls to scan | median **2.5** |
| render after keypress | median **3 ms** |

The mechanical cost is nil. The whole cost is reading.

**And in tier 1 there is nothing to aim at.** The affordance that makes a claim fast
is the `[=] the yield matched here` marker. It exists *only for claims that matched*.
Tier 1 is by definition the claims that did not, so the reviewer performs an unaided
visual search over 2.5 screens of dense procedure text, 87 times.

- Budget: **900 s**. Protocol allots tier 1 about a third: **300 s for 87 claims =
  3.4 s each.**
- Observed floor for an unaided scan of 2.5 screens: **~20 s each = 1,740 s.**

**Tier 1 alone is roughly twice the entire budget**, and it is a census, so it cannot
be sampled down.

### The design inversion

The tier that must be done **first and in full** is the **slow** one. The tier that is
**fast**, because it has match highlights, is the one that is **sampled**. If the
highlighter could point at *near* misses - the line containing `0.2 mol` when looking
for `200 mmol` - tier 1 would collapse toward tier 3's pace. That is the single
highest-leverage change available.

---

## 5. The keyboard: one collision, and it writes data

`1`, `2`, `3`, `s`, `u` all registered. Nothing was dropped and nothing double-fired.
Timing was never ambiguous.

**But `3` is bound to two different things on the same screen.** The queue tabs
advertise `1`, `2`, `3`, `*` as their shortcuts. The answer bar advertises `1`
Correct, `2` Wrong, `3` Unsure. I pressed `3` intending to switch to queue 3. It
recorded **Unsure** on a claim I had never read:

```json
{"rec":"rx:Summary of the Invention_Step 1","field":"molar_ratio_text[0]",
 "verdict":"unsure","attention":"record"}
```

The queue counter moved `1/87 -> 2/87` and the shortlist counter `0/11 -> 1/11`.
Switching queues requires clicking the tab.

This is a data-integrity bug, not a cosmetic one: the collision silently writes a
verdict, and the digits are the natural thing to reach for because the tabs
themselves display them as shortcuts.

---

## 6. Undo does not reach disk

Pressing `u` after that mistake updated the UI correctly: `2/87 -> 1/87`, `1/11 ->
0/11`. But:

- the `unsure` line **is still in the JSONL**, with no retraction appended
- **reloading the page brings the count back to `2/87`**
- the **completeness report counts it**: "2 of the 78 machine-flagged claims have been
  reviewed... **1 the reviewer could not settle**"

So undo is a session-local illusion. A reviewer who mis-keys, undoes, and finishes
ships a report containing verdicts they explicitly retracted. Given the `3` collision
above, mis-keying is not hypothetical.

---

## 7. Bulk accept does nothing

Queue 3 shows `b | Accept 2 machine-verified`. The button is present, **visible,
enabled, and has a real bounding box**.

| action | result |
|---|---|
| press `b` | no network request, no write, counter stays `0/50` |
| click the button | no network request, no write |
| force-click the button | no network request, no write |

**Control, in the identical setup, seconds apart:** pressing `1` on queue 1 fires
`POST /api/verdict` -> `200` and appends to the log. So the write path is healthy and
the bulk handler specifically is inert. This is not an artifact of my instrumentation.

Consequences for the questions that were asked:

- **`attention: "batch"` is never recorded, because nothing is recorded.**
- **Bulk-accepted claims are not indistinguishable from confirmed ones** - there are
  no bulk-accepted claims at all.
- **The completeness report is therefore not over-claiming from bulk accepts today.**
  That risk is real but not yet live. It becomes live the moment the handler is wired,
  so `attention: "batch"` needs to be verified end to end before that ships.

---

## 8. Counts the tool does not agree with itself on

For tier 2, in one session, three different numbers:

| where | number |
|---|---:|
| engine `source_coverage.summary.uncited_with_chemistry` | **0** |
| coverage page headline "UNCITED, CARRIES CHEMISTRY" | **0** |
| coverage page section header "Candidate misses" | **15** |
| review queue tab "Uncited chemistry" | **6** (it read 15 earlier in the session) |

Tier 2 is a census. A census whose size the tool reports as 0, 6 and 15 on the same
data cannot be completed, and a reviewer cannot tell when they are done. The engine
file was regenerated several times during the session, so some of this is churn -
worth re-checking on a settled file before treating the whole gap as a defect.

Tier 1 also moved, 78 -> 87, and tier 3's population 301 -> 292, during the session.

---

## 9. What I wrote to the log

Four verdicts, all as `yash.singh`:

| record | field | verdict | intended? |
|---|---|---|---|
| `rx:Example 1_Step 1` | `yield_identity` | correct | yes |
| `rx:Summary of the Invention_Step 1` | `molar_ratio_text[0]` | unsure | **no - the `3` collision** |
| `rx:Summary of the Invention_Step 1` | `provenance.quote` | correct | control test |
| (one pre-existing line predates this session) | | | |

The unintended `unsure` is still on disk. I have left it there rather than editing
the log by hand, because it is the evidence for sections 5 and 6.

---

## 10. What I would change, in order

1. **Unbind the digits from the queue tabs**, or move the answer keys. A shortcut that
   silently writes a verdict when the user meant to navigate is the most damaging
   class of bug in a tool whose entire output is verdicts.
2. **Make undo append a retraction** so the report stops counting retracted verdicts.
3. **Wire bulk accept, and verify `attention: "batch"` reaches disk before it ships.**
4. **Make the grounding check unit-aware, or stop calling the result `not_found`.**
   `200 mmol` vs `0.2 mol` is not a hallucination and must not be shown to a
   non-chemist as one.
5. **Soften "answer Wrong", or move the evidence above the fold.** A confident
   instruction sitting above evidence that routinely refutes it trains the reviewer to
   distrust the screen.
6. **Give tier 1 something to aim at.** Highlight near misses and numerically-equal
   values in other units. This is the change that makes the budget close.
7. **Reconcile the tier-2 count** across engine, coverage page and queue.
8. **Version the checks contract** so a producer change fails at write time, not at
   read time mid-review.
9. **Re-measure tier 1 after 4 and 6.** If the false-positive rate in my sample holds,
   the census is far smaller than 87 and the budget problem may solve itself.

---

## 11. Two things I got wrong, recorded so the method is visible

**The evidence pane does not truncate.** I first read it as stopping at line 187 and
silently dropping cited line 188. All seven cited lines render; my own text extraction
had truncated them.

**The app builds fine.** A cold `next dev` on a copy failed with a CSS parse error at
`globals.css:1736`, and I briefly believed the app could not be started or built. It
can: `next build` completes and emits every route. The failure was a Turbopack dev
cache flake - the server log even records "Turbopack's filesystem cache has been
deleted because we previously detected an internal error". Not a product defect.

---

## Appendix: how this was run

The checks file became unreadable mid-session when `verify.py` introduced a new `auto`
value, `not_reconciled`, that the UI's contract rejects. To finish, sections 5 to 8
were run against a **production build of a copy of the app**, with `ANNOTATIONS_ROOT`
pointed at the real annotations tree and `CHECKS_FILE` pointed at a copy of the checks
file in which the 8 `not_reconciled` values were rewritten to `not_found`. No file in
`manual_annotations/` or `verifier/` was edited. Verdicts were written to the real log,
which was the point.

The control in section 7 exists precisely because that setup could otherwise be blamed
for the bulk-accept result.
