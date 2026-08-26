# A single-valued field where the world has two values

Four instances, found independently by four agents in four different files. Worth
stating as a property of the schema rather than as four bugs, because they share a
signature and no existing check catches any of them.

## The four

**1. `conditions.time_h` is one float.** Example 1 step 6 runs 16 hours at room
temperature then 4 hours at reflux, in one flask. The field holds 4.0. The 16 survives
only in prose notes. Eight more records print a time RANGE (`1-10h`) and hold null,
each documenting the loss in its own notes. `time_h` is null on 25 of 33 reactions.

**2. `about` had two values and needed three.** `extraction` and `patent` could not
express "the annotation read the page correctly and the field it had to use could not
hold the answer". Folding that into `extraction` tells a reviewer the annotator was
careless when the schema simply had nowhere to put a range.

**3. `section_label` is one string and a record can span three sections.** The merge
writes `Summary of the Invention` on a record carrying a quantity read from Example 1.
The line-level provenance is correct and complete; the human-readable location field,
which is the one a reader follows, is false.

**4. A compound record belongs to one section and several substances belong to
several.** The same substance appears under different spellings per section, so one
molecule becomes three records with three join keys. Not merging is the right call, but
the artifact cannot say "this is the same thing, seen from three places" in the field
where a reader would look.

## The shared signature, which is why they are one finding

    the extraction is correct
    the record validates
    nothing looks wrong
    and the artifact quietly asserts ONE of two true things as if it were the only one

**None of the four was caught by schema validation, by field agreement between
approaches, or by any numeric gate.** A schema cannot express "this field must be able
to hold as many values as the world has", and every one of these records is
structurally valid and semantically incomplete.

## What did catch them

Three of the four were caught by asking a different question: **is this value where the
record says it is?**

- the 16 hours, by sweeping every quantity on every cited line against what the claims
  assert
- the `section_label`, by scoping a grounding check to lines rather than to sections,
  which took a run from 70.3% to 98.3% and reframed "the citation is false" into "the
  location field is false"
- the duplicate families, by joining records on the Chinese alias they share rather
  than on the English name they do not

That is a reason to keep a location check in CI beyond the single defect it found
tonight. It is the only instrument here that sees this class.

## The rule

**Before fixing an instance, ask whether the field can represent the world.** A range
in a float, two stages in one slot, three sections in one string and a third subject in
a two-valued enum are the same defect wearing four costumes, and patching any one of
them leaves the other three.

Where the field genuinely cannot be widened, the schema should carry the loss
explicitly rather than leaving it to prose: a `notes` field that a human wrote and no
consumer reads is information successfully captured and then discarded.
