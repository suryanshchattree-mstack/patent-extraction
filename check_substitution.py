#!/usr/bin/env python3
r"""Read the artifact the way a consumer reads it, and say whether it comes out readable.

resolve_translations.py proves every Chinese string HAS an English form. That is a
different question from whether substituting those forms into the annotator's own
English produces a sentence a chemist can read, and the gap between the two questions
is where every defect in this stage has actually lived. All four found so far produce
output with NO CHINESE CHARACTER IN IT, so a CJK grep certifies them and a reader does
not:

    has done away with the strong-smellingsodium methanethiolate
        two names replaced back to back. Chinese has no inter-word space, so a
        boundary that was invisible in the source is a missing one in English

    the substrate charged is the methyl ester (methyl ester)
        the annotator had already glossed the term in English, and substituting
        printed it twice

    says the invention The beneficial effects of the present invention are: ...
        a 14-character phrase answered with the 695-character translation of the
        whole paragraph it was quoted out of

    2-chloro-3-methyl-4-(methanesulfonyl)benzoic acid
        for 2-氯-3-(2,2,2-三氟乙氧基)甲基-4-甲磺酰基苯甲酸, because a bracketed
        substituent was deleted as though it were a Chinese gloss. Not a mangled
        name: the name of a DIFFERENT molecule this same patent makes

THIS SCRIPT MODELS THE CONSUMER, NOT THE PRODUCER, and the duplication is the point.
verifier/lib/english.ts is what actually renders, and it is a separate implementation
in a separate language. Reimplementing its rules here and running them over the real
provenance is what catches the two drifting apart. If this script and the screen ever
disagree, one of them is wrong and this says so while there is still time.

    python3 check_substitution.py                 # CN104292137A
    python3 check_substitution.py CN104292137A
    python3 check_substitution.py --verbose        # print every rewritten field

Exit 0 when every annotator-prose field comes out clean, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REL = OUT / "relevant_output"

DEFAULT_PATENT_ID = "CN104292137A"

CJK = r"[㐀-䶿一-鿿豈-﫿]"
CJK_RUN = re.compile(CJK + "+")

# The two provenance fields that are the annotator's OWN English with the patent's
# Chinese quoted inside them. The same pair resolve_translations.py gates on; see
# PROSE_FIELDS there for why it is only these two.
PROSE_FIELDS = ("arithmetic_check", "drawing_evidence")

# ---- the consumer's rules, mirrored from verifier/lib/english.ts ----------------

CHINESE_THEN_GLOSS = re.compile(
    CJK + r"+[　-〿\s]*[(（]([^()（）]*[A-Za-z][^()（）]*)[)）]"
)
PARENTHESISED_CHINESE = re.compile(
    r"([A-Za-z])[　-〿\s]*[(（][^()（）]*"
    + CJK
    + r"[^()（）]*[)）]"
)
UNTRANSLATED = "[untranslated]"
MAX_DEPTH = 3


def reads_as_a_gloss(gloss: str) -> bool:
    """A bracket after a Chinese name holds a translation only sometimes.

    Line 243 charges N,N-二甲基甲酰胺(0.05g), where it holds the charge, and promoting
    that prints "0.05g" and deletes the solvent.
    """
    return not re.match(r"^\s*\d", gloss) and re.search(r"[A-Za-z]{3}", gloss) is not None


def promote(text: str) -> str:
    """Drop the Chinese half of any pair that already carries both languages."""
    text = CHINESE_THEN_GLOSS.sub(
        lambda m: m.group(1) if reads_as_a_gloss(m.group(1)) else m.group(0), text
    )
    return PARENTHESISED_CHINESE.sub(r"\1", text)


def substitute(text: str, index: dict, keys: list[str], depth: int = 0,
               space: bool = True) -> str:
    """Longest key first, always, and a space between two replacements that touched.

    `space` exists to be turned OFF. Two names replaced back to back fuse into
    "strong-smellingsodium methanethiolate", and no regex over the finished text can
    see that: the join is between two lowercase letters and English is full of those.
    The boundary is only knowable here, while it is being made, so the way to prove
    the rule is load-bearing is to run the field again without it and see the output
    change.
    """
    if depth >= MAX_DEPTH or not CJK_RUN.search(text):
        return text
    out: list[str] = []
    previous_was_english = False
    i = 0
    while i < len(text):
        hit = next((k for k in keys if text.startswith(k, i)), None)
        if hit is None:
            out.append(text[i])
            previous_was_english = False
            i += 1
            continue
        if previous_was_english and space:
            out.append(" ")
        out.append(substitute(promote(index[hit]["en"]), index, keys, depth + 1, space))
        previous_was_english = True
        i += len(hit)
    return "".join(out)


def english_prose(text: str, index: dict, keys: list[str], space: bool = True) -> str:
    if not CJK_RUN.search(text):
        return text
    whole = (index.get(text.strip()) or {}).get("en")
    out = promote(whole if whole is not None else text)
    out = substitute(out, index, keys, space=space)
    return re.sub(r"\s{2,}", " ", CJK_RUN.sub(UNTRANSLATED, out)).strip()


# ---- what counts as a bad rewrite ----------------------------------------------

# "the methyl ester (methyl ester)" and "an appropriate amount (an appropriate
# amount)". Only ever produced BY substitution: the annotator wrote the gloss for a
# reader who could not read the Chinese, and once the Chinese is English the gloss is
# the same words twice.
DOUBLED = re.compile(
    r"\b(?:the |a |an )?([A-Za-z][^()]{1,60}?)\s*[(（]\s*(?:the |a |an )?\1\s*[)）]",
    re.IGNORECASE,
)

def faults(rewritten: str) -> list[str]:
    out = []
    for run in CJK_RUN.findall(rewritten):
        out.append(f"Chinese survived: {run}")
    if UNTRANSLATED in rewritten:
        out.append(f"fell back to {UNTRANSLATED}, so the index is stale")
    for m in DOUBLED.finditer(rewritten):
        out.append(f"gloss printed twice: {m.group(0)[:60]}")
    return out


# ---- the second question: is the artifact usable by a run-splitting consumer? ----


def per_run(text: str, index: dict) -> str:
    """What a consumer gets if it looks up each run of Chinese instead of the longest key.

    This is not a strawman. verify.py's scrub() does exactly this, and it is why
    2-氯-3-甲基-4-甲磺酰基苯甲酸甲酯 comes back untouched: the ASCII locants break it
    into 氯, 甲基 and 甲磺酰基苯甲酸甲酯, the index holds the whole name and none of
    those three, so every lookup misses.
    """
    return CJK_RUN.sub(lambda m: (index.get(m.group(0)) or {}).get("en") or m.group(0), text)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in sys.argv
    patent_id = args[0] if args else DEFAULT_PATENT_ID

    # THE COPY THE APP READS, not the one the stage writes. resolve_translations.py
    # writes output/translations.json and make_relevant_output.py copies it into
    # output/relevant_output/gold/, which is the path verifier/lib/paths.ts resolves.
    # Two copies means they can differ, and when they do the fix looks applied
    # everywhere except on the screen. That is checked first, because measuring the
    # wrong file would make every number below a statement about nothing.
    artifact = REL / "gold" / "translations.json"
    written = OUT / "translations.json"
    if not artifact.exists():
        print(f"{artifact} not found. Run resolve_translations.py first.")
        return 1
    index = json.loads(artifact.read_text(encoding="utf-8"))
    keys = sorted(index, key=lambda s: (-len(s), s))

    stale = []
    if written.exists():
        fresh = json.loads(written.read_text(encoding="utf-8"))
        for k in sorted(set(fresh) | set(index)):
            a = (index.get(k) or {}).get("en")
            b = (fresh.get(k) or {}).get("en")
            if a != b:
                stale.append((k, a, b))

    rows = []
    for name in ("compounds-provenance.json", "reactions-provenance.json"):
        path = REL / "provenance" / name
        if path.exists():
            rows.extend(json.loads(path.read_text(encoding="utf-8")))

    print(f"patent   : {patent_id}")
    print(f"index    : {len(index)} entries, read from the path the app reads")
    if stale:
        print(f"\nSTALE. {len(stale)} entries differ between what the stage wrote and "
              f"what the app reads.\n  make_relevant_output.py has not copied "
              f"output/translations.json into gold/ since the\n  last run, so every "
              f"fix below is live in the pipeline and invisible on the screen.")
        for k, app, stage in stale[:6]:
            print(f"    {k}\n      app reads : {app!r}\n      stage wrote: {stage!r}")
        if len(stale) > 6:
            print(f"    ... and {len(stale) - 6} more")
    print(f"provenance: {len(rows)} rows, fields {', '.join(PROSE_FIELDS)}")

    checked = 0
    needs_space: list[tuple[str, str]] = []
    broken: list[tuple[str, str, list[str], str]] = []
    widest = (0.0, "", "")
    for row in rows:
        for field in PROSE_FIELDS:
            text = row.get(field)
            if not isinstance(text, str) or not CJK_RUN.search(text):
                continue
            checked += 1
            rewritten = english_prose(text, index, keys)
            found = faults(rewritten)
            if found:
                broken.append((field, text, found, rewritten))
            without = english_prose(text, index, keys, space=False)
            if without != rewritten:
                # Name the word that actually fused, by diffing the two word lists
                # rather than excerpting, so the report shows the defect and not
                # whatever happened to sit near it.
                spaced = set(rewritten.split())
                fused = [w for w in without.split() if w not in spaced]
                needs_space.append((field, ", ".join(fused[:3]) or without[:60]))
            if verbose:
                print(f"\n--- {field}\n ZH: {text[:150]}\n EN: {rewritten[:220]}")
            # The widest single splice, which is the ratio gate's subject seen from
            # the consumer's side rather than the artifact's.
            i = 0
            while i < len(text):
                hit = next((k for k in keys if text.startswith(k, i)), None)
                if hit is None:
                    i += 1
                    continue
                ratio = len(index[hit]["en"]) / len(hit)
                if ratio > widest[0]:
                    widest = (ratio, hit, index[hit]["en"])
                i += len(hit)

    print(f"\nannotator-prose fields carrying Chinese: {checked}")
    print(f"fields that fuse two names without the spacing rule: {len(needs_space)}")
    for field, fused in needs_space:
        print(f"  {field}: without it these words run together -> {fused}")
    print(f"widest single splice: {widest[0]:.1f}x  ({widest[1]} -> "
          f"{len(widest[2])} characters)")

    if broken:
        print(f"\n{len(broken)} field(s) do not come out readable. FAIL")
        for field, text, found, rewritten in broken:
            print(f"\n  {field}")
            print(f"    ZH: {text[:120]}")
            print(f"    EN: {rewritten[:200]}")
            for f in found:
                print(f"    !!  {f}")
    else:
        print(f"all {checked} come out as readable English, with no Chinese, no "
              f"placeholder\n  and no doubled gloss. PASS")

    # The second question, reported rather than gated: this script does not own
    # verify.py and cannot fix it, but the number should be visible on every run.
    unresolved = [k for k in index if CJK_RUN.search(per_run(k, index))]
    runs = {r for k in index for r in CJK_RUN.findall(k)}
    print(f"\nconsumer contract: the index is keyed by whole strings and MUST be read "
          f"longest key first.")
    print(f"  a consumer that looks up each run of Chinese instead splits the 274 keys "
          f"into {len(runs)} runs,")
    print(f"  {len([r for r in runs if r not in index])} of which are not keys, and "
          f"fails to resolve {len(unresolved)} of the {len(index)} entries.")
    print(f"  Those runs are mostly not chemistry: 加入 is \"add\", 水洗 is \"wash with "
          f"water\", 浓缩得 is\n  \"concentrate to give\". Curating them would be "
          f"hand-translating the patent one clause\n  at a time, and assembling a name "
          f"from them gives Chinese word order in Latin script.")

    return 1 if (broken or stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
