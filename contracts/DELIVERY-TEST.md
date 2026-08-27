# Detection is proven. Delivery is proven for one defect class in four.

Four defects planted in a full copy of the tree, engine run there, and a separate UI
served from that lab. Each followed through all four links: does the engine flag it,
does it land in a census tier, does it render, and would a non-chemist catch it.

The real tree was untouched and verified unchanged afterwards.

    defect                  engine        tier          on screen?     caught?
    D1 fabricated value     not_found     1, census     YES, first     YES
    D2 misattachment        found         3, sampled    NO, not drawn  NO
    D3 wrong structure      check failed  1, as a quote report only    NO
    D4 dropped qualifier    nothing       -             NO             NO

## D1, a value on no line of the document. Delivered.

`mass_g 25.25 -> 77.77`. **The `critical` severity band fired for the first time**, having
been 0 all night, which is also the only test it has ever had.

The card says the number is on none of the 12 cited lines "and it is on no other line
of the 256-line document either", and under what to do: "This value is on no line of
the patent. Either it was invented or it came from somewhere nobody recorded. Read this
one first." The evidence panel shows line 187 reading "methanesulfonyl chloride 25.25 g".

A non-chemist compares 77.77 with 25.25 and answers. No chemistry needed. This is the
system working exactly as designed.

## D2, a real number moved to the wrong compound. Never reaches a screen.

`2-chlorotoluene mass_g 25.3 -> 40.5`. 40.5 g is real: it is aluminium trichloride's
charge, printed on the same line 187 the record cites.

    engine   auto=found, tier 3, severity none
    reason   "The number 40.5 appears with its unit grams on line 187"
    action   "The machine found this where the record says it is. Bulk-acceptable."

Every word true, the conclusion wrong. Then: tier 3 drew 50 of 285 and **D2 was not in
the draw**. At that seed it appears on no screen in the product.

So a misattachment is invisible about **82%** of the time, and in the 18% where it is
drawn, the screen tells the reviewer it is bulk-acceptable and shows them a line that
really does contain "40.5 g". They answer Correct.

**This is the defect class the whole tool exists for and it is the one that gets
through.** Not because the reviewer is shown too little: because the only thing
separating right from wrong is which substance the 40.5 belongs to, and the page does
not and cannot say.

## D3, a wrong structure. The check fires; no claim carries it.

The drawing cross-check worked and its wording is good: "The vision pass read this
molecule off page p06 as `Cc1c(Cl)cccc1S(C)(=O)=O`. The gold resolves
`Cc1ccccc1S(C)(=O)=O`, which is a different molecule."

But **zero claims mention it**. The two tier-1 claims a reviewer meets on that record
both ask "Is the text this record quotes actually on the source lines it cites?", with
the action "a check on this row failed, so it is worth reading" - never saying which
check or what is wrong. The reviewer verifies the quote, answers Correct, moves on.

The finding is only visible on `/report`, a screen a fifteen-minute reviewer has no
reason to open.

**And the report heading asserts the opposite of the finding:**

> "The page drawing and the gold agree about this molecule - The vision pass read...
> which is a different molecule."

`check()` takes `title_en` as the assertion being TESTED, so it reads correctly when it
passes and states a falsehood when it fails. Same class as the "Machine could NOT find
this" banner. About 50 strings.

## D4, a dropped qualifier. Nothing at all.

Removed `anhydrous aluminium trichloride` and `无水三氯化铝` from the aliases of the record
carrying the quantity. **No check, no claim, no risk change. Zero checks in the entire
file mention aliases.** The numbers still ground, the structure still resolves, the
references still resolve.

The engine has nothing to say about it and does not know that it does not. This is the
defect that actually reached the deliverable tonight, in its real form.

## The finding nobody went looking for

**The tier-4 demotion is inert end to end.** `verifier/lib/claims.ts:501` keeps `tier`
only when it is 1, 2 or 3 and nulls anything else into `tier_raw`; `tierOf` then returns
**1** for any claim carrying one. So all 38 tier-4 claims are worked inside tier 1.

The census a reviewer actually gets is **94**, which is exactly the size the pace
measurement says dies at the pessimistic rate with tier 3 sampled zero times. **The fix
shipped tonight has not reached the product**, and neither side could see that alone:
the engine emits tier 4 correctly and the UI's fallback is defensible on its own terms.

## What this means

Detection was proven hours ago and is not in question. What was never tested is whether
a detected defect reaches a human, and for three classes in four it does not.

The ranking that follows:

1. **D4 needs a check that does not exist.** An alias set losing a qualifier is
   invisible to every check here, and it is the failure that actually shipped.
2. **D3 needs its failing check to become a claim.** The detection is already correct
   and legible; it simply never reaches the queue.
3. **D2 may be irreducible.** No cheap machine test separates it. What can improve is
   the screen: a reviewer told which substances the cited line mentions has a chance.
4. **D1 works.** Leave it alone.

---

# Re-run, 08:30. Two in four reach a reviewer, and the two that changed were not
# changed by the fixes we thought

Same method as above: four defects planted in a full copy of the tree, the engine run
there, a separate UI served from that lab on port 3300 with `ANNOTATIONS_ROOT` pointed
at it. **The real tree was not written to. Proof and one caveat are at the bottom.**

    defect                  engine                    tier          on screen?         caught?
    D1 fabricated value     not_found, critical       1, census     YES, first         YES        (was YES)
    D2 misattachment        found, severity none      3, sampled    NO, not drawn      NO         (was NO)
    D3 wrong structure      claim, was report only    1, census     YES, 57 of 132     NO         (was NO)
    D4 dropped qualifier    check + claim, was none   1, census     YES, 67 of 132     YES        (was NO)

**Two in four, up from one.** D4 moved. D3 moved halfway and stopped.

## What the four planted defects were, byte for byte

Reproduced exactly from the earlier run rather than re-invented.

    D1  compounds.json   methanesulfonyl chloride  quantity.mass_g  25.25 -> 77.77
    D2  compounds.json   2-chlorotoluene           quantity.mass_g  25.3  -> 40.5
    D3  structures-resolved.json  2-chloro-6-(methanesulfonyl)toluene
        smiles and canonical  Cc1c(Cl)cccc1S(C)(=O)=O -> Cc1ccccc1S(C)(=O)=O
        formula C8H9ClO2S -> C8H10O2S, mw 204.68 -> 170.23
    D4  compounds.json   aluminium trichloride  aliases: drop the English alias
        "anhydrous aluminium trichloride", keep the Chinese one

**One ambiguity, resolved explicitly.** The prose above says D4 removed *both* aliases.
Every artifact of that run shows only the English one removed. The file state is what
produced the measurement, so the file state is what was reproduced. The other reading
was measured too, and it is a finding in its own right; see "What it would take to pass
while being wrong".

## The before row was re-measured, not taken on trust

`manual_annotations` was cloned at `10fd893` (02:48, the commit immediately before
`c8489a7`, which is this document), the same four defects planted, and `verify.py` run:

    tier 1 = 56 engine claims, tier 3 = 285, tier 4 = 38
    D1  tier 1, not_found, critical
    D2  tier 3, found, none
    D3  drawing.smiles check FAIL. Claims carrying it: ZERO
    D4  no naming.qualifier check exists at all. Claims: ZERO

`285` and the census of `94` (56 plus the 38 tier-4 claims the UI folded into tier 1)
both reproduce the numbers recorded above. **The before row is sound.**

## The credit belongs to a commit nobody listed

The four fixes credited for this re-run were all in `verifier`. Three of them are not
what moved D3 or D4.

`fb176a3` in **manual_annotations** at 03:00, eight minutes after this document was
written, added to `verify.py` both the `naming.qualifier` check and the rule that turns
a failing check into a claim in its own right. Every claim that carries D3 and D4 today
is emitted by `verify.py` and arrives in `claims[]` already formed:

    tier 1, auto not_checkable:  naming.qualifier x3, consistency.equivalence x3,
                                 drawing.smiles x1

`checkCarriage` in `lib/claims.ts` then finds those already carried by its `asks` rule
and derives nothing for them. What it does derive is **eight** `quantity.mass_mmol[...]`
claims for the failing mass balances, at tier 1 positions 13 to 47. Those are real and
they are new. They are not D3 and they are not D4.

**A collision worth fixing.** Sixteen claims in the merged set carry `basis: "derived"`:
eight `yield_identity` claims that `verify.py` marks that way, and the eight the UI
derives. `engine.derived_claims.length` is 8. Anything counting `basis === "derived"`
gets 16 and anything reading `derived_claims` gets 8.

## D1. Unchanged, and the reason it works is narrower than it looks

Position 1 of 132, `not_found`, severity `critical`. The card names the 12 cited lines,
says the value is on no other line of the 256-line document, and prints line 187 reading
`methanesulfonyl chloride 25.25 g`. A non-chemist compares two numbers. Caught.

**What it would take for this to pass while being wrong: choosing a different number.**
Measured, on two further copies of the tree:

    25.25 -> 34.0   a mass the patent prints, on lines it does NOT cite
                    still tier 1, still not_found, severity drops critical -> low
                    reason becomes "the value is real and the citation points
                    somewhere else". Still answerable. Still caught.

    25.25 -> 40.5   a mass the patent prints, ON A LINE THIS RECORD CITES
                    tier 3, auto found, severity none, risk 0.05
                    reason: "The number 40.5 appears with its unit grams on the
                    Chinese line 187 and on the English translation on line 188."

**The second of those is D2.** D1 and D2 are not two defect classes. They are one check
and two draws, and which one you get depends on whether the invented number happens to
sit on a cited line. These records cite blocks of twelve lines that include the whole
procedure, so that is not a remote coincidence.

## D2. Not drawn, not worse, and NOT irreducible

At seed `CN104292137A` the compound-record claim is one of 274 in tier 3 and is not in
the 50 drawn. It appears on no screen. Unchanged from before.

**Did working bulk accept make it worse? Measured both branches.**

*Branch one, the shipped default.* Bulk accept is tier 3 only and draws only from
`queues.tier3.asked`, the sampled 50. D2 is not in that list. Pressing `b` and confirming
wrote 50 verdicts, all `verdict: "correct"`, all `attention: "batch"`, all
`note: "bulk-glance"`. None of them was D2. **Bulk accept cannot reach an undrawn claim.
At the default, no change.**

*Branch two, when D2 is in the draw.* Forced with `?n=5000`, which draws all 274. D2
appears in the confirmation list as one row:

    [=] line 187   2-chlorotoluene   Mass charged   40.5 g   has a structure drawing

Nothing on that row says the patent prints 25.3 g for this substance. One keypress wrote
274 lines, D2 among them:

    {"field": "quantity.mass_g", "artifact_says": "40.5 g", "verdict": "correct",
     "note": "bulk-glance", "attention": "batch", "rec": "cmp:e63b6978-..."}

**So: the outcome is the same and the attention is lower.** The earlier run recorded that
a drawn D2 was answered Correct by hand anyway, so the catch rate did not fall. What
changed is that the Correct is now reachable without the card ever being rendered. Set
against that, the line is tagged, and the report reads the tag: it prints
`ACCEPTED IN A BATCH` and "accepted in a list without being opened individually. Weaker
evidence, and never added to the count on the left." Before, there was no line at all.
**Net: not worse on catch rate, one new way to file an unseen Correct, honestly labelled.**

**D2 is not irreducible.** The earlier finding said no cheap machine test separates it.
There is one, and half of it is already written.

    compound record 2-chlorotoluene   40.5 g / 200.0 mmol  -> implied MW 202.5
    structures-resolved 2-chlorotoluene                        MW 126.59
    pristine record                   25.3 g / 200.0 mmol  -> implied MW 126.5

A 60% error against a molecular weight the pipeline already resolved. `quantity.mass_mmol`
does exactly this arithmetic, and it runs on reaction-compound rows only. Ten of the 75
compound records carry both a mass and a molar amount and none of them is checked.

**And the two tellings disagree without anything noticing.** The defect was planted on
the compound record only. The reaction record for the same substance in the same step
still says 25.3 g. `quantity.mass_mmol[2-chlorotoluene]` on the reaction PASSES, because
the reaction's own copy is still right. Both records reached tier 3, both read `found`,
and both were accepted in the same batch, one saying 40.5 g and one saying 25.3 g.

## D3. The claim is produced. It is still not delivered

Four claims now reach the tier 1 census, two of them on the defected record itself
and two on its sibling spellings:

    position 56   consistency.equivalence
    position 57   drawing.smiles
                  "The machine checked whether the page drawing and the gold agree
                   about this molecule, and the answer is no. Is it right?"
                  "The vision pass read this molecule off page p06 as
                   Cc1c(Cl)cccc1S(C)(=O)=O. The gold resolves Cc1ccccc1S(C)(=O)=O,
                   which is a different molecule. One of the two readings is wrong."
    positions 61 and 63   consistency.equivalence on the other two spellings

That is the half that works, and it is a real change: before, this appeared only on
`/report`.

**The other half does not work, for three separate reasons.**

*The card is not answerable by a non-chemist.* The only structural content is two SMILES
strings. The evidence panel below is five blocks of patent prose about reaction
conditions, none of which says anything about the structure. The claimed value renders as
"a machine finding, not a number".

*The picture on the card looks correct.* The card shows
`/structures/2-chloro-6-methylsulfonyltoluene.svg`. That SVG was rendered from the
pristine SMILES and is byte-identical to the pristine file, because the defect edits
`structures-resolved.json` and nothing re-renders the drawing. So the reviewer is told two
strings disagree while being shown a picture that is right.

*The one picture-against-picture card that covers this molecule is blind to the defect.*
`CN104292137A_p06_d2`, tier 1 position 125, "Do these two pictures show the same
molecule?", with that same unchanged SVG beside the patent's own crop. Both images load.
Because our side of the comparison is byte-identical to what a clean tree renders, this
card cannot distinguish the defected tree from the pristine one. It is not that a
reviewer might miss the difference. There is no difference on screen to miss.

*And the agree key files it as clean.* The buttons are the ordinary
`1 Correct / 2 Wrong / 3 Unsure`, with no wording specific to this question. Pressing 1,
which the card's own phrasing invites as "yes, the machine is right", writes:

    {"field": "drawing.smiles", "verdict": "correct",
     "artifact_says": "a machine finding, not a number"}

and the report then counts that claim among the reviewed and prints **"No confirmed
defect in the annotation."** The verb pair
that `claimsForUncarriedChecks` deliberately avoids, for exactly this reason, is the pair
these engine claims get.

**Verdict: claim produced, still not delivered.** A careful reviewer presses 3 Unsure and
the finding survives as unsettled. A hurried one presses 1 and it is recorded as clean.
Neither is a non-chemist catching a wrong structure.

## D4. Caught

Position 67 of 132, tier 1 census.

    "The patent calls this 'anhydrous aluminium trichloride'. The record calls it
     'aluminium trichloride'. Is whether it is anhydrous a fact that has been lost?"

    "The record's English names are 'aluminium trichloride', none of which says the
     word 'anhydrous'. The qualifier is not decoration: it is what was charged."

    footer: "The record's English name drops the word 'anhydrous' its Chinese name
             carries. A qualifier on a reagent name changes what was charged."

Evidence is lines 187 and 197 in English, both printing "anhydrous aluminium trichloride".
This is a comparison between two English strings, one from the patent and one from the
record, and it needs no chemistry at all. A reviewer reads both, sees the missing word,
and acts. **Caught.**

The verb ambiguity described under D3 applies here too and it is worth fixing, but it does
not defeat this card: the finding is stated in the footer as a fact, not only as a
question.

### What it would take for THIS to pass while being wrong

Remove the Chinese alias as well, which is what the prose above describes:

    aliases [the Chinese alias, 'anhydrous aluminium trichloride']  ->  []

    naming.qualifier on aluminium trichloride:  PASS

Not silent. **Pass.** `bareChineseNames` anchors the search on the record's own Chinese
name and strips the qualifier off it, so with no Chinese name there is nothing to search
in front of, and the record reports a clean result on precisely the fact that was
destroyed. A bigger version of the same defect turns a fail into a green tick. The
`cannot_compute` guard exists in the coverage layer, where zero findings is reported as
"we did not check", but the per-record status the reviewer sees is `pass`.

## Two things that changed underneath the measurement

**The census grew from 94 to 132, plus 6 in tier 2.** The tier-4 demotion recorded above
as "inert end to end" is now live: tier 4 is its own tab, 38 claims, 20 drawn, 53%. That
is the fix landing. The cost is that at the p90 rate in PACE-MEASUREMENT.md, 8.7 s per
claim, the tier 1 census alone is 19.1 minutes and busts the fifteen-minute budget on its
own. D3 at position 57 is reached at 8.3 minutes and D4 at 67 at 9.7 minutes, so both
survive the pessimistic rate. The p06_d2 picture card at 125 needs 18.1 minutes and does
not. Note also that PACE-MEASUREMENT proposes demoting `not_checkable` out of the census
to fix the budget: the seven claims that carry D3 and D4 are all `not_checkable`, so that
change would move both of them into a sampled tier.

**The page index no longer parses.** Every screen carries the banner "The page index
exists but does not match the shape this screen reads, so the patent pages cannot be
opened." The drawing claims still load and their crops still render, so the picture
comparisons survive; what is lost is the reviewer's ability to open the patent page
behind any other claim.

## Also verified working

**Bulk accept.** 50 of 50 written at the default draw, 274 of 274 at `?n=5000`, every
line `attention: "batch"` with `note: "bulk-glance"`, and the report counts them apart
from confirmed answers. No console errors, no failed requests.

**Undo.** Answering D1 wrote one line. Pressing `u` wrote a **second** line carrying
`note: "retracted"` and left the first in place. The file grew from 5 to 6 lines. The
footer says so: "take back your last answer. It writes a line that supersedes it, and
puts you back on that claim."

## The real tree

`manual_annotations` was checksummed before any work: 546 files, manifest sha256
`e304820fbed717d391ab69631e3a45ec9901fd05ecdada5f47fcbf6b645e9901`. Re-checksummed after.

**Nothing in this run wrote to it.** `compounds.json`, which carries three of the four
defects, is byte-identical. `verdicts-CN104292137A.jsonl`, the only file the app writes,
is byte-identical, which is the proof that the lab server never escaped its
`ANNOTATIONS_ROOT`. `structures-resolved.json` still carries `Cc1c(Cl)cccc1S(C)(=O)=O`,
`C8H9ClO2S`, `204.68`.

Ten files did change during the run, all of them other agents' work and all accounted for:
commits `8de5183` (08:32) and `729f05f` (08:38), plus one uncommitted
`checks-CN104292137A.json` from an engine run in the real tree that was not this one.

**One caveat, stated because it is not provable either way.** Two dev servers were
listening at the start, on 3000 and 3100. After tearing down the lab server on 3300 with
a `pkill` matched on 3300, port 3000 is still listening and port 3100 is not. The pattern
should not have matched it. Whoever owns 3100 should restart it.

Measured against: `verifier` at `67de7b4` with `lib/claims.ts` at
`7e1782d2c606feeccd52c4c8cc2a21fe649a612cf2c6a6f62ecf1935a078755f` and `lib/checks.ts` at
`ad17d336d8a0100b527b5ae435b44ef47abc4bbc86c50436af99adce418d9b87`;
`manual_annotations` at `9a75904`, clean.

## Ranked, again

1. **D2 has a cheap machine test after all.** Run `quantity.mass_mmol` on compound
   records, not only on reaction-compound rows. Ten records qualify and the defect is a
   60% miss against a molecular weight the pipeline already holds. This was ranked
   "may be irreducible" and it is not.
2. **D3 needs a picture, not a SMILES.** The claim reaches the census and cannot be
   answered there. Either re-render the drawing from the gold SMILES so the comparison
   cards can see the defect, or put the two structures side by side on the
   `drawing.smiles` card itself.
3. **The engine's `not_checkable` claims need the patent verbs.** `Correct` on
   "the machine says they disagree, is it right?" is ambiguous in the reviewer's head and
   unambiguous in the file, and the two readings are opposite.
4. **`naming.qualifier` reports `pass` when it cannot see.** It needs the same
   `cannot_compute` honesty the coverage layer already applies.
5. **D4 works.** Leave it alone.
6. **D1 works, for now.** It is one draw of the same check that produces D2.
