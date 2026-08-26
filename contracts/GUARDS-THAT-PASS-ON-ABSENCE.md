# The two failures every guard in this project had

Four instances in one night, all the same shape, all found by accident or by an
independent grader rather than by the guard itself.

## The pattern, in two halves

**A check that a string is ABSENT cannot tell "translated" from "destroyed".**

**A check that a value is PRESENT cannot tell "confirmed" from "coincidence".**

Every guard here was written to assert that something bad is not present. None of them
asserted that the corresponding good thing IS present. So each one certified an output
that had been emptied rather than fixed.

## The four

**1. Source line 76.** 307 characters of readable English procedure, rendered to the
reviewer as "[This source line is Chinese and the pipeline carries no English pairing
for it. Ask a Chinese reader.]" because one Han term inside it sent the whole line down
the give-up path. It reached 11 claims and it is the line that makes the product.
**Deleting the line entirely would also have passed the zero-Chinese gate.**

**2. The scrubber, and this is the big one.** `scrub()` looked up each run of Chinese
rather than the longest key, so ASCII locants split a chemical name into fragments the
index does not hold and every lookup missed:

    2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯   rendered as   2-[untranslated]-3-[untranslated]-4-[untranslated]

while the index held `methyl 2-chloro-3-methyl-4-(methylsulfonyl)benzoate` all along.

    strings mangled          250 of 325  ->  0
    [untranslated] markers          1442  ->  0
    index entries resolvable   74 of 274  ->  274 of 274

**The shipped artifact reported 0 markers before the fix.** It was latent. Everything
looked clean because the strings were being destroyed rather than translated, and it
would have fired on the second patent with nobody able to say why.

**3. The empty 200.** Against a stub server answering every route with zero bytes, the
English guard printed 13 PASS lines and "No Chinese on any of the 13 routes checked".
`/report/export` returning 0 bytes was the live symptom. A related hole: route handlers
were skipped on any status, so a broken handler read the same as one that only accepts
POST.

**4. My own quantity sweep.** I harvested numbers out of quoted text as well as
structured fields, so a "16" appearing anywhere in any quote counted as coverage of a
16-hour reaction time. It reported zero misses. Redone strictly it reported ten, and
reading all ten left one real finding.

## The fix, generally

**Assert the presence of the thing that should be there, not only the absence of the
thing that should not.**

- For the scrubber: for every entry the index HAS an English answer for, assert the
  scrubber produces it. No threshold, and it cannot be gamed by deletion.
- For the routes: a PASS requires a 200, a body over a measured size floor, a minimum
  of visible text for a page, AND no Chinese. Four conditions, so absence is never
  mistaken for cleanliness.
- For the quantity sweep: compare against structured values only, then read every
  failure by hand before reporting the count.

## The habit that actually caught these

None of the four was caught by the guard that should have caught it. What caught them:

- an independent grader that drives the engine and asks different questions
- testing against deliberately broken stubs rather than reasoning about behaviour
- reading every failure by hand before reporting a number
- one agent measuring another's claim rather than relaying it

A number nobody has read the failures behind is not evidence. That rule caught my own
error twice tonight, and both times the correction came from someone re-measuring
rather than from the check going red.


---

## The second half: present is not confirmed

Found by hand-checking wide-citation `found` verdicts. Verified here against the
source.

A compound record's citation is the union of every provenance row for that identifier,
so `water` cites 34 lines because water is quoted in seventeen places. Against 34 lines,
"the claimed number appears on a line this record cites" is close to unfalsifiable.

The example that makes the whole argument, and both verdicts are correct:

| claim | genuine evidence | coincidence |
|---|---|---|
| `dichloromethane` 100 ml | line 244, "100 ml dichloromethane" | line 237, where the 100 ml is **THF** |
| `water` 100 ml | line 206, "100 ml of water was added" | line 237, the same THF |

**One printed quantity, belonging to a third substance, counted as confirming evidence
for two different compounds.** A reviewer glancing at the highlighted 100 ml on line
237 is looking at THF while being told it confirms dichloromethane.

### The cheap fix does not work, and this is why it matters

The obvious repair is "require the cited line to also name the compound". It fails.
Line 237 DOES name dichloromethane, later in the same sentence, as the extraction
solvent:

    ... and 100 ml THF solvent; stirred at room temperature for 16 h ...
    ... then extracted with dichloromethane, washed with water ...

So no cheap machine test separates these. **Attachment is genuinely the reviewer's
job**, and that is the strongest argument yet for why this tool exists rather than a
script.

### What was done about it

Not a downgrade to `partial`: the match usually IS genuine, so calling it partial
would be its own kind of lie, and it would move 43 claims into tier 1, taking it from
78 to 121 and costing a third of the review budget re-confirming numbers that are
mostly right.

Instead every claim carries `evidence_width` and `evidence_class`, and the tier 3
denominator splits: **266 narrow, 35 wide**. The bound is reported separately for each,
so a match against 46 lines is never averaged with a match against one and silently
presented as equal evidence.

    1-3 cited lines    110
    4-10 cited lines   236
    11-30 cited lines   45
    31+ cited lines      3      widest 46

43 of 316 `found` claims, 13.6%, are wide.
