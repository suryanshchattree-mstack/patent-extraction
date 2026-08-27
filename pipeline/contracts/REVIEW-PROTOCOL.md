# The 15-minute review protocol

How a reviewer who does not know chemistry spends 900 seconds and comes out with a
defensible statement about hundreds of annotations.

## The constraint, stated honestly

The user's budget: "maybe 30 minutes, and 30 minutes is max, but I'll give it 15
minutes because there could be hundreds of annotations."

CN104292137A produces 114 records and on the order of 500 field-level claims. At a
realistic 6 seconds per claim on a good UI - read the question, glance at the
highlighted evidence, press a key - 900 seconds buys about 150 claims. That is 30% of
the work.

So a UI that simply lists everything and asks the reviewer to grind through it
CANNOT succeed. It runs out of time at 30% with no way to say anything about the
other 70%. This is exactly why the first UI failed. The fix is not a faster reviewer.
It is spending those 150 attention-units where they buy the most information.

## Three tiers, in this order

### Tier 1 - census of the suspicious

Every claim the machine could not confirm: `not_found`, `partial`, plus every failed
structure, quantity or reference check. These are not sampled. Every one is seen by a
human, because this is where errors actually live and the population is small.

Expected size: tens, not hundreds. Budget roughly a third of the time.

`not_found` means the annotation states a value that is NOT in the source lines the
annotation itself cites. That is the hallucination signal and it is the single most
valuable thing on the reviewer's screen.

### Tier 2 - census of the candidate misses

Every source line carrying a chemistry signal - a quantity, a temperature, a duration,
a yield, a named reagent - that NO record cites. This is the recall side, and no
per-record check can see it. Also a census, also small.

Budget roughly a sixth of the time.

### Tier 4 - the machine had no opinion

Every `not_checkable` claim outside the recall census: a role, a reaction class, the
annotation's own validation flags. Sampled, never censused, and **excluded from tier
3's bound**.

This tier was created by a measurement rather than by taste. The census used to be
tier 1 plus tier 2 at 93 claims, and the queue was then timed over 20 claims at a
**5.3 s median, 8.7 s p90, 15.1 s worst**.

    census        @5.3s median   @8.7s p90     @10.4s gross
    93 as built   8.3min FITS    13.4min FITS  16.1min OVER, tier 3 = 0
    55 today      2.9min FITS     8.0min FITS   9.5min FITS, tier 3 = 48

The old census survives on the median and dies on the pessimistic reading, in the
way that matters most: the budget is gone, tier 3 is sampled zero times, and the
report can state **no bound at all**. A protocol that works only if the reviewer is
fast is not a protocol.

Treat the 5.3 s as a floor rather than an average: it was measured by an agent, who
reads faster than a person. That thins the margin and argues for the demotion.

### Tier 3 - stratified random sample of what the machine passed

Whatever time is left goes to a random sample of the claims the machine already
matched. The point is not to find errors; it is to bound the error rate among the
claims nobody would otherwise look at.

Stratify by record kind and by patent section, and sample proportionally, so the
estimate is not dominated by one easy section. Draw with a seed derived from the
patent id so the sample is reproducible and a second reviewer can be given the same
one or a deliberately different one.

## What the reviewer can then honestly claim

This is the output that makes the whole exercise worth doing, and the UI must state
it in these terms:

> All 41 machine-flagged claims were reviewed. 12 were confirmed defects.
> All 14 uncited chemistry lines were reviewed. 3 were genuine misses.
> Of the 447 claims the machine matched, 68 were sampled at random and 1 defect
> was found. The residual defect rate among machine-matched claims is therefore
> at most 6.8% with 95% confidence.

Three separate populations, three separate statements, never merged into one
percentage. A machine string match is not a human confirmation and the report must
never let the two blur.

## Order the census by work, not by subject

`about` describes the record and does not predict cost. `work_kind` does, and the
two kinds differ by a factor of 2.3: **judgement 8.3 s, comparison 3.6 s**. The UI
should order on it and tell the reviewer which they are about to do, because a queue
that mixes them without warning makes the remaining-time estimate wrong in both
directions.

As it now falls out, the census is entirely comparison work and tier 4 is entirely
judgement work, which is what the tier split was for.

## The arithmetic

Use a one-sided 95% upper bound. Compute it exactly; do not approximate in code.

**Zero defects found in the sample.** The exact bound is `1 - alpha^(1/n)`, which for
alpha = 0.05 is very close to the familiar rule of three, `3/n`. Sample 68 and find
nothing, and the honest ceiling is about 4.3%. Note what this does NOT say: it does
not say the extraction is 96% correct. It says that if the true defect rate were
above 4.3%, a clean sample of 68 would have been unlikely.

**Some defects found.** Clopper-Pearson upper bound, `BetaInv(1 - alpha, x + 1, n - x)`
for x defects in n draws. Exact, conservative, and correct at small n where the normal
approximation is not. Do not use a normal-approximation interval; n is small and the
proportion is near zero, which is precisely where it misbehaves.

**Finite population.** Sampling 68 of 447 without replacement makes the true interval
narrower than the binomial one. Ignoring that is conservative, so the simple bound is
safe to report. Say in the report that it is conservative rather than pretending the
correction was applied.

**Stratified estimate.** When strata are sampled proportionally the pooled estimate is
the simple one. If any stratum is deliberately oversampled, weight it back by
population share, and say so.

## What the UI must do with this

1. Show the three tiers as three distinct queues with their own counts and their own
   completion states. "Tier 1 complete" is a real milestone and must feel like one.
2. Show the running time budget and what it is being spent on. The reviewer should
   see that finishing tier 1 unlocked tier 2.
3. Never present tier 3 progress as overall progress. Sampling 68 of 447 is 100% of
   the sample and 15% of the population, and the reviewer must see both framings.
4. On stopping early, still produce a valid statement. A reviewer who does 40 of 68
   sampled claims gets a wider bound, not a broken report. The report must degrade
   gracefully and say what the reviewer's actual effort supports.
5. Make the sample reproducible and say what seed produced it.

## The rule that governs all of it

The report may only claim what the reviewer's actual clicks support. If a tier was not
finished, the report says so, in that tier's own words, and widens its bound.
Optimism here is not a presentation choice, it is a defect.
