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

---

## The third form: a test that passes by checking nothing

The same failure reaches the tests written to catch it.

Section J of the grader re-derives each verdict from the evidence its claim carries,
rather than trusting the label, because counting labels proves nothing: a producer
could emit them at random and the totals would still look plausible.

**Its first version reported "0 checked" and passed.**

All five `not_found` claims are `molar_ratio_text`, which carry `claimed_value: null`.
The numeric path had nothing to look at, found no violations, and reported green. It
was vacuously true and indistinguishable, from the outside, from a genuine pass.

That is the same defect as a gate that passes by deletion, one level up. The fix is the
same: **assert the positive.** A test must report how many things it examined, and a
count of zero must fail rather than pass.

    [PASS] every not_found value really is absent from its cited lines: 5 checked
    [PASS] every not_reconciled value really is present on its cited lines: 8 checked

The "N checked" is not decoration. It is the part that cannot be satisfied by an empty
set.

## The whole pattern, in one place

    a guard   that a string is ABSENT   cannot tell   translated  from  destroyed
    a guard   that a value is PRESENT   cannot tell   confirmed   from  coincidence
    a test    that finds no violations  cannot tell   correct     from  vacuous

Six instances tonight, in five different files, written by five different authors. None
was caught by the check that should have caught it. Every one was caught by something
that asked the positive question instead, and in three cases by the author re-examining
their own green result rather than by anything going red.

The habit worth keeping is not any of these fixes. It is: **when a check passes, ask
what it would take for it to pass while being wrong.** That question found all six.

---

## A fourth form, and the one I caused twice: a strict enum on someone else's vocabulary

Not a guard that passes wrongly. A guard that FAILS wrongly, and takes everything with
it.

Twice tonight a producer added a value to a vocabulary it owns, and a consumer parsing
that vocabulary with a strict enum rejected the entire artifact:

    about gained "schema"            -> three pages down
    auto gained "not_reconciled"     -> 8 of 394 claims carried it,
                                        and the enum took the other 386 down too

Both were consequences of a ruling I made without requiring the consumer to change in
the same step. The rulings were right. The sequencing was mine and it was wrong.

**The structural fix, which two agents arrived at independently:** read an
engine-owned vocabulary as a string and narrow it in the transform. Never as an enum.

    auto: z.string()          then narrow, with the raw word kept as auto_raw
    unknown value             -> partial

`partial` is the right landing place for an unrecognised value because it routes the
claim to a human and keeps it out of the sampled tier, so the confidence bound never
speaks for a claim nobody understood. **Degrade toward more human attention, never
less.**

Two rules fall out:

1. **A strict enum is only safe on a vocabulary you own.** If another process writes
   the value, its next commit is your next outage.
2. **Keep the raw value.** A card that fell back should be able to say which word it
   fell back from, otherwise the fallback is itself a silent data loss.

The general shape, which is the same as everything above it in this document: **the
failure is always in what the check does with the case it did not anticipate.** Passing
silently, failing totally, or checking nothing at all are three ways of not having
thought about it.

---

## A fifth form: a currency check that does not know what it depends on

The `assemble` stage COPIES `output/translations.json` into the deliverable, and did
not DECLARE it as an input.

So a fix landing at stage 9 changed a file the stage reads and does not know it reads.
`is_current()` checked the inputs it had been told about, found nothing moved, called
the stage current, and skipped it. **The runner reported the stage current while the
screen showed the old English.** Six of the eleven copied files were undeclared.

This is worse than "the copy had not run yet". The copy would never have run on a
translation change, ever, and the manifest would have said `current` every time.

It is the third time tonight the manifest asserted the one thing it exists to attest
and was wrong:

    the frozen plan       a stage judged current before its dependency was rebuilt
    write_manifest()      a non-running stage's row rewritten from a tree it had
                          just failed to update, laundering staleness into the record
    undeclared inputs     a stage that reads a file it never declared

All three make `current` mean nothing. **A manifest that cannot tell whether the assets
are current for the gold is worse than no manifest**, because a reader who has no
manifest goes and checks, and a reader who has a lying one does not.

### The fix, which is the positive assertion again

Declaring the missing inputs closes the instance. What closes the CLASS is the manifest
verifying the outcome rather than the bookkeeping: it now hashes every copied pair and
fails the run when any diverge, with the remedy printed.

    FAIL  1 artifact(s) in the deliverable do not match their source in output/.
      gold/translations.json does not match output/translations.json
      Run: python3 run_pipeline.py --patent-id CN104292137A --from publish-gold

Proved by planting the exact stale value that was found in the wild: exit 1, correct
message, correct remedy, then exit 0 after restoring.

**A dependency declaration is a promise a human makes and can forget. A hash comparison
is a fact.** Where a check can compare the outcome instead of trusting the bookkeeping,
it should.

---

## A sixth form: a check scoped by SHAPE rather than by content

The English gate on `quote-translations.json` walked two named sections and tested
`isinstance(val, str)`. Every value of any other shape was skipped, in silence, and
the gate reported clean.

    values inspected   41 of 43     the two top-level _about_en / _origin_en strings
                                    sat outside both named sections
    shapes inspected   str only     a value written {"en": ..., "note": ...}, which is
                                    the form the rest of this pipeline uses, was never
                                    opened

Nothing in the file is dict-shaped today, so the gate was green and had been green
since it was written. It could not tell "these values are English" from "I did not
look at these values", and the first entry written in the pipeline's own house style
would have carried Chinese to the screen through a passing gate.

Fixed by walking every value at every depth, keys exempt because the keys are the raw
Chinese the lookup is done by, and by printing the count so a pass that inspected
nothing fails instead. Proved in both directions rather than by the absence of a
finding: Chinese planted in a dict-shaped `en` field, old gate passes and new gate
fails naming `entries[p03#4.what][en]`; an empty document, old gate passes and new
gate fails; the shipping file, both pass.

**A gate scoped to a shape is a gate scoped to today's data.** The population it does
not cover is invisible from its own output, which is what makes this the same defect
as the prose-ratio gate scoped to the 37 prose entries: both were right about what
they looked at and silent about what they did not.

## The mirror of the fifth form: a declaration nothing reads

The fifth form above was a stage that READS a file it never declared, so `is_current()`
called it current forever. The visual stage had the inverse: `visual_text.py` declared
as an input and imported by nothing, and `glossary.json` declared as an output and
written by nothing.

Both belonged to `make_visual.py`, which imported the scrubber and emitted the
glossary and was deleted in 10fd893 when `make_visual_evidence.py` took the stage
over. `make_visual_evidence.py` has never imported `visual_text` in any commit.

    undeclared input      stage reports `current` when it is stale
    declared non-input    stage reports `stale` when it is current

The second is not the harmless direction. It rebuilt the most expensive stage in the
pipeline on any edit to a module the stage does not read, and a `stale` that fires for
no reason trains the reader to ignore the manifest exactly as reliably as a `current`
that lies. Removed rather than wired in: wiring the scrubber into a stage that already
resolves its Chinese through the hand-authored `quote-translations.json` would be a
second source of truth for the same screen text, which is a feature and not a repair.

---

# Form nine: the producer writes a field the consumer never declared

Found twice in one morning, both times by walking a path rather than by any check.

    the pipeline writes            the consumer's schema declares      result
    pages[].image_path             pages[].src                         safeParse fails,
                                                                       whole index empty
    claim.related_records          nothing at all                      zod strips the key,
                                                                       silently, no error

**Both killed a feature outright and neither produced an error anywhere.**

The first cost every claim its page: `loadVisual` caught the parse failure, fell back to
`EMPTY_PAGE_INDEX`, and the screen printed a banner blaming the data. 0 of 387 claims could
open a scan for the entire life of the feature. The banner was honest and pointed at the
wrong thing.

The second cost the reviewer the drawings on exactly the claims where a drawing is the only
usable answer. `related_records` carries `structure_svg_path` and appeared 28 times in the
artifact and 0 times on the served page.

## Why nothing caught either

    tsc                 passes. Neither side is wrong about its own types.
    the unit suite       558 tests, all green. Nothing asserts producer and consumer
                         agree about field NAMES.
    the pipeline tests   pass. The pipeline writes what it means to write.
    the consumer tests   pass. The consumer parses what it declares.

Each half is correct in isolation. The defect lives in the gap, and the gap is not a file
anyone owns. This is the same shape as the inverted schema labels, where `ReviewAnswers`
and `coverage.ts` were each defensible alone and composed into an inversion.

## What zod does here, and why it is the wrong default for this seam

`z.object` strips unknown keys silently. That is the right default for untrusted input and
the wrong one for reading a sibling process's artifact, where an unknown key means one of
two things and both matter:

    the producer added a field    -> we are discarding new information
    the producer renamed a field  -> we are discarding existing information

Silence is the one response that is wrong in both cases.

## The guard

Neither a stricter schema nor a looser one fixes this. Strict fails totally on the
producer's next commit, which this project has already been bitten by twice. Loose keeps
discarding silently.

What works is a test that does not need to know what any field means:

    read the artifact on disk
    collect the top-level keys the producer actually writes
    fail when one of them is absent from the consumer's schema

with an explicit allowlist of keys we deliberately drop. Then dropping a field is a
decision someone wrote down, rather than a default nobody chose.

**The general form.** Every one of the eight forms above is a check that cannot see
something. This one is different: it is two correct checks either side of a boundary that
neither of them looks at. When you own both ends of a serialisation, test the seam, not the
ends.

## A tenth form, twice in one afternoon: the guard's SUBJECT went away

Both of these are mine, both were introduced by a change made to strengthen something
else, and both left a guard printing PASS about a thing it was no longer looking at.

**One: the watched file stopped existing.** `check-writes.mjs` proves it never writes
to the real deliverable by fingerprinting the real verdict log before and after:

    const realLog = verdictsIn(REAL_ROOT);
    const fingerprint = () => { try { ... } catch { return "absent"; } };

Splitting the runs meant `REAL_ROOT` had to widen from `manual_annotations/run_26_aug`
to `manual_annotations`, so that no run could be mistaken for a sandbox. That widening
was correct and it moved `realLog` to a path that does not exist and never will:

    manual_annotations/output/relevant_output/verification/verdicts-CN104292137A.jsonl
                       \___ no run directory, so nothing is ever written here ___/

`fingerprint()` answered `"absent"` before and `"absent"` after. The comparison held.
The closing line reported a file nobody could have touched as untouched, and the
guard would have gone on saying so for as long as the pack existed.

**Two: the selector had never heard of the new case.** The same script asserts that
every structure question shows two pictures rather than two SMILES strings, and it
picks the claims to check by field name:

    const STRUCTURE_FIELDS = new Set(["drawing.same_molecule", "drawing.smiles"]);

A new check family, `structure.second_reader`, produced exactly the kind of claim this
guard exists for, and the set had never heard of it. PASS, on nothing. Adding the field
turned the guard red immediately, on a real defect I had shipped an hour earlier: the
bromine card showed one drawing and the string `[Br]`, which is unanswerable by the
reader the card is written for. The guard found that; reading the code did not.

**What separates this form from the nine above.** Those are checks that could not see
something from the day they were written. This one is a check that COULD see it, and
then something moved. The nine are design faults. This one is drift, and drift is worse
because the guard has a track record of passing correctly, which is exactly what makes
its later PASS believable.

**The fix, both times, is the same shape and it is the positive assertion again:**

    if (realLogs.length === 0) refuse to run
    if (wanted.length === 0)   say SKIP, out loud, not PASS

A guard whose subject is empty must say so. `PASS` and `there was nothing to check`
have to be different words on the screen, because the reader of that screen is deciding
whether to ship.

**And the enumeration, rather than the name.** `realLog` named one run. It now walks
the pack and fingerprints every verdict log it finds, so the run somebody adds next
month is protected the day it appears rather than the day somebody remembers this file.
Naming a thing is a promise to update the name.


## The tenth form again, same week: a hand-written list of what to check

Three Playwright guards drive the same dev server. One of them walks `app/` and
discovers its routes. Two carried an array:

    const ROUTES = [`/${P}`, `/${P}/review`, `/${P}/coverage`, `/${P}/report`];

A new page went in at `/[patentId]/sections`. check-english found it that same run and
reported 142 KB scanned. check-layout and check-overflow reported PASS across five
viewport widths without ever loading it.

Nothing was broken. That is the point: the guards were green, the page was unchecked,
and no output anywhere said the second thing. A guard whose subject list is typed by
hand covers whatever the codebase looked like when somebody last remembered to update
it, and the gap is invisible precisely because the guard passes.

**The fix is not always "discover it".** Route discovery moved into
`scripts/lib/routes.mjs` and check-overflow now takes its list from there. check-layout
could not: it has two lists, and which one a page belongs in is a judgement nothing can
derive, the difference between "this must never scroll at all" and "this is a document
and may scroll down but never sideways". So the lists stay hand-written and the
COMPLETENESS of them is asserted instead:

    a page route in neither FIXED nor DOCUMENTS fails the guard

Where the content of a list is a judgement, assert that the list is exhaustive rather
than trying to generate it. Mutation tested by removing the new route: the guard goes
red and names it.

## The translations gate on a Latin-script patent

Found by measurement on `EP2045236A1`, a German EP application, not by inference.

`resolve_translations.py` defines its subject as `CJK = re.compile(...)` covering CJK
Extension A, Unified Ideographs and Compatibility Ideographs, and `has_chinese(s)` is
the only test any of its three gates applies. German is Latin script, so `has_chinese`
is false on every string in the document.

The gate did not skip, warn or report a limitation. It printed:

    coverage gate: every one of the 0 strings above must have an English form,
      so that substituting the index leaves no Chinese anywhere
    all 0 strings resolve, and all 1078 source lines come out of the
      substitution in English. PASS

That second clause is the dangerous one. It says the source comes out in English, and
what it verified is that no Chinese remains. On this patent every line was German both
before and after. A consumer reading the gate's output learns that the deliverable is
safe to put in front of an English-speaking reviewer, and the gate has no basis for
saying so.

`TARGETS.md` already carried this as a caveat on row 12, `DE10113137A1`, reasoned from
the code. It did not carry it on row 4, because nobody had noticed that `EP2045236A1`
is published in German. So the guard's blind spot was known, written down, and still
walked into on the next patent that hit it, because the note was attached to one row
rather than to the gate.

The run supplied English by hand regardless: identifiers resolve to English with the
source spelling kept as an alias, and notes are English-only with German confined to
`aliases` and `quote_zh`. That is a discipline, not a check, and nothing in the
pipeline enforces it.

The general shape: **a guard whose subject is narrower than the risk it is read as
covering.** The check is correct about Chinese. The sentence it prints, and the gate
name, are about English.

## A twelfth: the manifest recorded a hash it did not compute

Found 2026-08-28 on US20100041557A1, and this one is in the artifact whose whole job is
integrity.

`runs/US20100041557A1/input/US20100041557A1-biblio.json` was edited, the run was resumed
with `--from finalise`, and the commit that resulted disagreed with itself: the committed
biblio hashed to `19c2cd..` at 9441 bytes and the committed manifest recorded `92ba69..`
at 9430 for that same path. Nothing failed. `validate.py` was clean, the deliverable
matched `output/` on all 11 copied artifacts, and the manifest was internally consistent.

`write_manifest` deliberately carries a skipped stage's row forward rather than writing
today's disk state under a stage that did not run, and the comment there explains why:
re-reading disk for a skipped stage is how the frozen-plan bug survived a second run. The
defect is that the carry-forward does not stay inside that row. `entry()` memoises by
path, the skipped branch seeds the same table with `hashes.setdefault(e["path"], e)`, and
stages are walked in pipeline order. `prompts` was skipped and declares the biblio as an
input, so its stale entry landed first, and `finalise` and `diagrams`, both of which RAN
and both of which read that file after it changed, were handed the cached stale hash:

    prompts    status=not selected   92ba692fcf05  9430   <- carried forward, intended
    finalise   status=ran            92ba692fcf05  9430   <- stale, and it ran
    diagrams   status=ran            92ba692fcf05  9430   <- stale, and it ran

So a stage that ran can have a hash written under its name that was never computed from
what it read. That is precisely the laundering the comment says the design prevents,
arriving from the other direction: not a skipped stage claiming fresh hashes, but a fresh
stage inheriting a skipped stage's stale one.

The shape, and it is the second half of this document's pattern: **a record that agrees
with itself cannot tell "verified" from "copied".** The manifest exists so a consumer can
ask whether the artifacts on disk were built from THIS gold "rather than trusting file
times", and on a resumed run it answers that question with a number it took on trust.

A full run computes every row and the numbers are correct, which is why this survived: it
only appears when a stage is skipped, and skipping is the normal case for a resumed run.
Recorded, not fixed. The corrected manifest was committed from a full run.
