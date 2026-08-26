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
