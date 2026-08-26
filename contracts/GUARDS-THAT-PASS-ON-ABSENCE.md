# The failure every guard in this project had

Four instances in one night, all the same shape, all found by accident or by an
independent grader rather than by the guard itself.

## The pattern

**A check that a string is ABSENT cannot tell "translated" from "destroyed".**

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
