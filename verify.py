#!/usr/bin/env python3
r"""Check the gold annotation against the patent it says it came from.

An LLM wrote the annotation in `output/relevant_output/gold/`. An LLM can invent a
number, attach a real number to the wrong molecule, or quote a sentence that is not
in the document. Nothing downstream of the extraction passes has ever asked the one
question that catches all three:

    Is this value actually on the source lines this record itself cites?

This stage asks it, once per field, for every field that holds a number or a quote,
and writes the answers into `output/relevant_output/verification/checks-<PATENT>.json`
as a queue of atomic, human-answerable claims. `contracts/VERIFICATION-CONTRACT.md`
is the shape; this file is the machine that fills it.

THE READER IS NOT A CHEMIST AND HAS TWENTY MINUTES. There are 114 records and
several hundred field values, and they cannot read the patent, which is in Chinese.
Three consequences run through every line below:

  - every human-facing string is English and ends in `_en`. Chinese never reaches
    the artifact, not in a quote, not in a note, not in a label. The index built by
    resolve_translations.py is what makes that possible, and where it has no
    English this file emits an English sentence saying so rather than the Chinese.
  - every claim carries the evidence that would settle it, inline, already
    translated. The reviewer never goes and finds the source text.
  - the machine states its verdict first. The human agrees or overrules.

THE VERDICT THAT MATTERS IS `not_found`: a number or a quote in the annotation that
is NOT in the source lines the annotation cites. That is the hallucination signal
and it sorts to the top of the queue. `found` is what lets the reviewer bulk-accept
the other several hundred and spend the twenty minutes on the handful that need
them.

WHAT COUNTS AS "THE LINES THIS RECORD CITES"

    reactions-provenance.json   source_lines of length 2 read as [start, end] and
                                the whole inclusive range is cited. Example 1 step 1
                                declares [182, 188], and 183 to 187 carry the
                                drawing, the paragraph marker and the procedure
                                itself. Reading those two numbers as two lines would
                                throw the procedure away.
    reactions-provenance.json   source_lines of length 3 or more are exact. Claims
                                step 1 declares [45, 46, 77, 82]: two lines of claim
                                1 plus two scattered lines of claim 2. As a span
                                that is 45 to 82, thirty-eight lines, most of them
                                about other steps.
    compounds-provenance.json   exact lines, unioned over every row for that
                                identifier, since a compound is quoted in several
                                places and each row cites its own.
    every cited Chinese line    also pulls in its own "    > EN: " partner, which is
                                a translation of that line and not independent
                                content. Without this a number printed only in the
                                machine translation reads as absent.

NUMBERS ARE MATCHED AS QUANTITIES, NOT AS STRINGS. A substring search for "5" finds
it on ninety lines. So each source line is tokenised into (value, unit) pairs and
the claim is matched against those:

    record  mmol = 200.0        source  "2-氯甲苯25.3g(0.2mol)"
                                tokens  (25.3, g) (0.2, mol)
                                0.2 mol converts to 200 mmol            -> found

    record  mass_g = 71.4       source  "滴加氯化亚砜71.4(0.6mol)"
                                tokens  (71.4, None) (0.6, mol)
                                the value is there, the unit is not     -> partial

The second is not a matcher failure. The patent really does print a bare 71.4 with
no unit at that step, and `partial` is the correct thing to put in front of a human.

Ranges are tokenised as ranges, so "15-20℃" yields (15, C) and (20, C) rather than a
bare 15 and a 20 that happens to carry the degree sign. Full-width digits and
full-width punctuation are folded to ASCII first. Chinese numerals are deliberately
NOT folded: all 110 of them in this document sit inside chemical names (三氯化铝,
二氯甲烷, 四口反应瓶) and converting them would make "3" match sixty-one lines that
say aluminium trichloride.

QUOTES ARE MATCHED BY COVERING THEM, NOT BY CONTAINMENT. `cover()` in
resolve_translations.py already solved this and is imported rather than
reimplemented, so the two stages cannot drift apart about where a quote lives. The
quotes are not clean substrings: they elide with " ... ", " | " and " / ", they fold
the patent's full-width punctuation to ASCII, some are English annotator prose with
a Chinese citation embedded, and some quote text that is not on the lines the row
declares. Covering the quote greedily with the longest span each source line can
supply handles all four, and the line each span lands on is what decides the
verdict: covered entirely from the cited lines is `found`, covered from somewhere
else in the document is `not_found` and names where the text really is.

WHAT DID WE MISS is the other half, and no per-record check can answer it. Every
numbered line is walked, marked cited or not, and the uncited ones are scanned for
chemistry: a quantity with a unit, a temperature, a duration, a yield, a ratio, a
drawn structure, or the name of a compound the gold already knows. An uncited line
carrying chemistry is a candidate miss and gets its own claim with
`field: "__coverage__"`, so it queues beside the hallucinations instead of sitting
in a report nobody opens.

Reads the gold, the provenance, the structures, the translation index and the
numbered source. Writes exactly one file, into verification/. Never touches gold/
or provenance/. No network. Re-running is byte-identical apart from `generated_at`,
and setting SOURCE_DATE_EPOCH pins that too.

Exits non-zero when any grounding check fails, so the pipeline stops on a
hallucination rather than shipping one.

Usage:  python3 verify.py                  # defaults to CN104292137A
        python3 verify.py CN104292137A     # any patent id
        python3 verify.py --check          # check and report, write nothing
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors

# The pipeline's one definition of "this string is a structure, not a name".
from resolve_structures import looks_like_smiles
# The quote matcher, imported rather than rewritten. See the module docstring: a
# containment test fails on all four shapes the quotes actually take.
from resolve_translations import (
    CJK,
    EN_MARK,
    FULLWIDTH,
    cover,
    english_by_line,
    has_chinese,
    normalise,
    read_numbered,
)

RDLogger.DisableLog("rdApp.*")

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REL = OUT / "relevant_output"
STAGES = OUT / "stages"

DEFAULT_PATENT_ID = "CN104292137A"
ENGINE_VERSION = 1

# Evidence is shown inline so the reviewer never leaves the row. A compound quoted
# in seven places cites twenty-five lines, which is a wall rather than evidence, so
# the panel is capped. Lines that actually carried the match are never dropped, and
# `cited_lines` still holds the complete citation, so nothing is hidden - only the
# rendering is bounded.
EVIDENCE_LINE_CAP = 24


# ---------------------------------------------------------------- normalisation

# The patent prints full-width digits and punctuation in places and the annotation
# quotes them back as ASCII. Folded before any number is read, never in a key.
FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９．－～", "0123456789.-~")

# Every spelling of "degrees Celsius" this corpus uses, on both sides: the Chinese
# lines print ℃, the machine translations print °C, "degrees C" and "degree C".
CELSIUS = re.compile(r"\s*(?:℃|°\s*C|deg(?:ree)?s?\.?\s+C)(?![A-Za-z])", re.IGNORECASE)
CELSIUS_MARK = "°"

# Longest first, so mmol is never read as "m" + "mol" and min is never read as "m".
UNIT_ALTERNATION = r"mmol|mol|min|kg|mg|ml|hrs|hr|[gLl]|h|%|°"

NUMBER = r"\d+(?:\.\d+)?"

# Two different boundaries, and the difference is measured rather than tidy.
#
# After a UNIT, only a lowercase letter or a digit disqualifies the match, because
# the patent writes "100mlTHF" and "36%HCl" with the next reagent jammed straight
# onto the unit. Requiring any non-letter there loses the 100 ml of solvent in
# Example 1 step 6 outright, and the check then reports a real quantity as printed
# only in the translation.
#
# After a BARE number the boundary stays strict, because NMR lines are full of
# "3H" and "2H" and a bare 3 that swallows its H is a number this stage would go on
# to match against a claimed mass.
UNIT_BOUNDARY = r"(?![a-z0-9])"
BARE_BOUNDARY = r"(?![A-Za-z0-9])"

RANGE_TOKEN = re.compile(
    rf"(?P<lo>{NUMBER})\s*(?P<lounit>{UNIT_ALTERNATION})?\s*[-~]\s*"
    rf"(?P<hi>{NUMBER})\s*"
    rf"(?:(?P<hiunit>{UNIT_ALTERNATION}){UNIT_BOUNDARY}|{BARE_BOUNDARY})"
)
PLAIN_TOKEN = re.compile(
    rf"(?P<value>{NUMBER})\s*"
    rf"(?:(?P<unit>{UNIT_ALTERNATION}){UNIT_BOUNDARY}|{BARE_BOUNDARY})"
)
# A comma used as a decimal point. Read only as a fallback, because this document is
# full of "1,2-dichloroethane" and "N,N-dimethylformamide" and reading those commas
# as decimal points would invent a 1.2 on every solvent line.
COMMA_DECIMAL = re.compile(rf"(?<!\d)(\d+),(\d+)(?![\d,-])")

# value -> canonical unit, and the factor onto it. `None` unit means the number was
# printed bare, which is a real and reportable state rather than a failure.
UNIT_CANON = {
    "kg": ("g", 1000.0), "g": ("g", 1.0), "mg": ("g", 0.001),
    "l": ("ml", 1000.0), "L": ("ml", 1000.0), "ml": ("ml", 1.0),
    "mol": ("mmol", 1000.0), "mmol": ("mmol", 1.0),
    "h": ("h", 1.0), "hr": ("h", 1.0), "hrs": ("h", 1.0), "min": ("h", 1.0 / 60.0),
    "%": ("%", 1.0),
    CELSIUS_MARK: ("C", 1.0),
}

# Field -> the canonical unit its value is stated in.
FIELD_UNIT = {
    "mass_g": "g", "volume_ml": "ml", "mmol": "mmol", "yield_pct": "%",
    "purity_pct": "%", "time_h": "h", "celsius": "C", "percent": "%",
    "equivalents": None,
}

# How near two quantities must sit to be the same quantity. Relative, because 0.2 mol
# converts to 200.00000000000003 mmol in binary floating point and an absolute
# epsilon that works there is meaningless at 500 g.
NUM_EPS = 1e-6


def fold(s: str) -> str:
    """Match form for reading numbers: full-width folded, Celsius unified."""
    t = s.translate(FULLWIDTH).translate(FULLWIDTH_DIGITS)
    return CELSIUS.sub(CELSIUS_MARK, t)


def canon_unit(raw: str | None) -> tuple[str | None, float]:
    if raw is None:
        return None, 1.0
    return UNIT_CANON.get(raw, UNIT_CANON.get(raw.lower(), (None, 1.0)))


class Token:
    """One quantity read off one line: a number, and the unit printed beside it."""

    __slots__ = ("value", "unit", "factor", "raw_unit", "start", "end", "in_range")

    def __init__(self, value, raw_unit, start, end, in_range=False):
        self.value = value
        self.raw_unit = raw_unit
        self.unit, self.factor = canon_unit(raw_unit)
        self.start = start
        self.end = end
        self.in_range = in_range

    def canonical(self) -> float:
        return self.value * self.factor


def tokenise(text: str) -> list[Token]:
    """Every (number, unit) pair on one line, ranges expanded to their endpoints.

    Ranges are read first and their character spans are then withheld from the plain
    pass, because "15-20℃" must yield 15 C and 20 C. Read plainly it yields a bare
    15 and a 20 C, and a claim of min_c = 15 would come back as a value with no unit
    when the line plainly says otherwise.
    """
    folded = fold(text)
    out: list[Token] = []
    taken: set[int] = set()

    for m in RANGE_TOKEN.finditer(folded):
        unit = m.group("hiunit") or m.group("lounit")
        out.append(Token(float(m.group("lo")), m.group("lounit") or unit,
                         m.start("lo"), m.end("lo"), in_range=True))
        out.append(Token(float(m.group("hi")), unit,
                         m.start("hi"), m.end("hi"), in_range=True))
        taken.update(range(m.start(), m.end()))

    for m in PLAIN_TOKEN.finditer(folded):
        if m.start("value") in taken:
            continue
        out.append(Token(float(m.group("value")), m.group("unit"),
                         m.start("value"), m.end("value")))
    out.sort(key=lambda t: (t.start, t.end))
    return out


def comma_decimals(text: str) -> list[float]:
    """Values the line would carry if its commas were decimal points."""
    folded = fold(text)
    return [float(f"{a}.{b}") for a, b in COMMA_DECIMAL.findall(folded)]


def same_number(a: float, b: float) -> bool:
    return abs(a - b) <= max(NUM_EPS, NUM_EPS * abs(b))


# ---------------------------------------------------------------- inputs

def die(msg: str) -> None:
    print(f"\nFAIL  {msg}", file=sys.stderr)
    raise SystemExit(2)


def load(name: str, *dirs: Path) -> object:
    """First existing copy of `name`, searching `dirs` in order.

    Same policy as resolve_structures.py and resolve_translations.py: the working
    copy in output/ and the assembled copy in output/relevant_output/ are both
    correct inputs, so the stage runs whether or not the deliverable has been
    assembled yet.
    """
    for d in dirs:
        p = d / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    die(f"{name} not found in {', '.join(str(d) for d in dirs)}")


def load_inputs(patent_id: str) -> dict:
    gold, prov = REL / "gold", REL / "provenance"
    data = {
        "compounds": load("compounds.json", gold, OUT),
        "reactions": load("reactions.json", gold, OUT),
        "pathways": load("pathways.json", gold, OUT),
        "patent": load("patent.json", gold, OUT),
        "structures": load("structures-resolved.json", gold, OUT),
        "drawings": load("structures.json", gold, OUT),
        "equivalence": load("compounds-equivalence.json", prov, OUT),
        "compound_prov": load("compounds-provenance.json", prov, OUT),
        "reaction_prov": load("reactions-provenance.json", prov, OUT),
        "sections": load("00-sections.json", OUT, STAGES / "A0-sections"),
        "translations": load("translations.json", OUT, gold),
    }

    # The patent id is load-bearing, not decorative. Checking the gold against the
    # requested id is what stops one patent's annotation being verified against
    # another patent's source, which would report every claim as a hallucination.
    wrong = {c.get("patent_id") for c in data["compounds"]} - {patent_id}
    if wrong:
        die(f"gold compounds.json carries patent_id {sorted(wrong)}, "
            f"this run is {patent_id!r}")
    if data["patent"].get("patent_id") != patent_id:
        die(f"gold patent.json is for {data['patent'].get('patent_id')!r}, "
            f"this run is {patent_id!r}")
    return data


# ---------------------------------------------------------------- English text

UNTRANSLATED = "[untranslated Chinese term]"
NO_ENGLISH = ("[This source line is Chinese and the pipeline carries no English "
              "pairing for it. Ask a Chinese reader.]")

PAGE_MARKER = re.compile(r"^<!-- page (?P<page>\S+) :: (?P<label>.*?) :: "
                         r"(?P<type>\S+) :: confidence=(?P<conf>\S+) -->$")

# What build_enriched.py puts at the head of a source paragraph: the patent's own
# [00NN] number, or the literal "None" where the page printed no marker. Only ever
# on the Chinese side, so it is proof that a line is source and not translation.
PARAGRAPH_MARKER = re.compile(r"^(?:\[\d{4}\]|None\s)")

# "tembotrione (tembotrione)", which is what folding 环磺草酮 into English leaves
# behind wherever the source already glossed it. Collapsed rather than shipped.
GLOSS = re.compile(r"(?P<before>[^\s()][^()]*?)\s*\((?P<inner>[^()]+)\)")
# An untranslated run left alone inside brackets, "Galinsoga (辣子草属)". The English
# beside it already carries the meaning, so the bracket is dropped whole.
CJK_PAREN = re.compile(r"\s*[(（]\s*[^()（）]*?"
                       + CJK.pattern + r"[^()（）]*?\s*[)）]")


def _collapse_gloss(s: str) -> str:
    def repl(m):
        before, inner = m.group("before"), m.group("inner").strip()
        if before.strip().lower().endswith(inner.lower()):
            return before
        return m.group(0)
    return GLOSS.sub(repl, s)


def scrub(text: str, index: dict) -> str:
    """Every run of Chinese in `text` replaced by English, or by a statement.

    Three passes in this order, because the order is what stops the output reading
    like a machine: look the run up in the translation index first, then collapse
    the "English (English)" the lookup leaves behind wherever the source had already
    glossed the term, then drop a still-untranslated run that sits inside brackets,
    since the English outside them is already carrying the meaning. Whatever
    survives all three becomes a marker: a reader who has no Chinese must never be
    handed Chinese, and must never be left unable to tell that something was
    dropped.
    """
    if not has_chinese(text):
        return text

    def lookup(m):
        entry = index.get(m.group(0))
        en = (entry or {}).get("en")
        return en if en else m.group(0)

    out = re.sub(CJK.pattern + "+", lookup, text)
    out = _collapse_gloss(out)
    out = CJK_PAREN.sub("", out)
    out = re.sub(CJK.pattern + "+", UNTRANSLATED, out)
    return re.sub(r"\s{2,}", " ", out).strip()


class Source:
    """The numbered source, with an English rendering and a kind for every line."""

    def __init__(self, patent_id: str, index: dict):
        self.path = HERE / "input" / f"{patent_id}-enriched-numbered.md"
        self.lines = read_numbered(patent_id)
        # resolve_translations.py owns the paragraph walk and is still being
        # worked on; it has already grown a third return value once. Unpacked by
        # position at both ends so a fourth does not stop this stage dead. The
        # middle value, when there is one, is the set of lines that ARE English
        # output, which no regex can decide: only the first line of a translation
        # carries "    > EN: " and every continuation line after it looks exactly
        # like a line of the patent.
        walked = english_by_line(patent_id, self.lines)
        self.english, self.walk = walked[0], walked[-1]
        self.en_hint: set[int] = set(walked[1]) if len(walked) > 2 else set()
        self.index = index
        self.numbers = sorted(self.lines)
        self.sha256 = hashlib.sha256(
            self.path.read_bytes()).hexdigest() if self.path.exists() else ""

        self.kind: dict[int, str] = {}
        self.text_en: dict[int, str] = {}
        self.is_translation: dict[int, bool] = {}

        for n in self.numbers:
            raw = self.lines[n]
            self.kind[n] = self._kind(raw)
            text, translated = self._english(n, raw)
            self.text_en[n] = text
            self.is_translation[n] = translated

        self.en_for, self.zh_for, self.pairing = self._pair_blocks()

        # Match forms, computed once. Every line is offered to the quote cover, not
        # only the translated ones, so a quote sitting on an untranslated line is
        # still located and reported rather than silently called missing.
        self.norm = {n: normalise(self.lines[n]) for n in self.numbers
                     if normalise(self.lines[n])}

    # ------------------------------------------------------------ line kinds

    def _kind(self, raw: str) -> str:
        if not raw.strip():
            return "blank"
        if raw.startswith(EN_MARK):
            return "translation"
        if raw.startswith("# ") or PAGE_MARKER.match(raw.strip()):
            return "heading"
        if raw.startswith("[IMAGE_EXTRACT"):
            return "image_extract"
        return "prose"

    def is_zh(self, n: int) -> bool:
        return self.kind[n] == "prose" and has_chinese(self.lines[n])

    def is_en_output(self, n: int, run_open: bool) -> bool:
        """Is line `n` part of the English a Chinese block was translated into?

        The paragraph walk in resolve_translations.py is the authority and is used
        alone wherever it is available, INCLUDING as a negative. Line 199 is the
        NMR shifts of Example 1 step 2, printed in the patent, carrying no Han
        character at all; it looks exactly like an English continuation line and it
        is not one. Absorbing it into line 197's translation would make every one
        of its shift values part of 197's evidence, and a claim of 3.14 g would
        then match an NMR peak.

        The fallback, for a corpus that has no walk, is the same rule spelled out
        by shape: the "    > EN: " mark opens a run, and a line with no Chinese and
        no paragraph marker continues one.
        """
        if self.en_hint:
            return n in self.en_hint or self.kind[n] == "translation"
        if self.kind[n] == "translation":
            return True
        return (run_open and self.kind[n] == "prose"
                and not has_chinese(self.lines[n])
                and not PARAGRAPH_MARKER.match(self.lines[n]))

    # ------------------------------------------------------------ block pairing

    def _pair_blocks(self):
        """Which English line translates which Chinese line. See SOURCE-PAIRING.md.

        Not n + 1. The source alternates Chinese and English 53 times, which is why
        n + 1 looks right, but where the chemistry is it does this:

            45 | 1) ...的合成                        zh, a heading
            46 | 将2-氯甲苯...25.3g(0.2mol)...       zh, THE PROCEDURE
            47 |     > EN: 1) Synthesis of ...       en, the heading
            48 | 2-Chlorotoluene, 25.3 g (0.2 mol)   en, THE PROCEDURE

        Line 46 carries every mass, temperature and time in step 1, and n + 1 hands
        back line 47, a heading with no number in it. A reviewer shown that would
        correctly conclude the evidence does not support "25.3 g of 2-chlorotoluene"
        - and the extraction was right, the pairing was wrong. That is the worst
        failure this tool has, because it accuses a correct extraction and leaves
        the reviewer no way to see it was the tool's fault. Measured at 19% of the
        288 compound citations that point at a Chinese line.

        So: take each maximal run of Chinese lines and the run of English lines
        immediately after it. Equal lengths pair positionally, i-th to i-th, and
        that is exact. Unequal lengths pair what they can and clamp the remainder
        onto the last English line, marked `approximate` so a screen can say so. No
        English in the block at all means no translation, said in English.
        """
        en_for: dict[int, list[int]] = {}
        zh_for: dict[int, list[int]] = {}
        pairing: dict[int, str] = {}

        nums = self.numbers
        i = 0
        while i < len(nums):
            if not self.is_zh(nums[i]):
                i += 1
                continue
            zh_run = []
            while i < len(nums) and self.is_zh(nums[i]):
                zh_run.append(nums[i])
                i += 1
            en_run: list[int] = []
            j = i
            while j < len(nums) and self.is_en_output(nums[j], bool(en_run)):
                en_run.append(nums[j])
                j += 1

            if not en_run:
                for n in zh_run:
                    pairing[n] = "none"
                continue
            exact = len(en_run) == len(zh_run)
            for k, n in enumerate(zh_run):
                partner = en_run[k] if k < len(en_run) else en_run[-1]
                en_for[n] = [partner]
                zh_for.setdefault(partner, []).append(n)
                pairing[n] = "exact" if exact else "approximate"
            # An English run longer than its Chinese run is one paragraph broken
            # over more English lines than Chinese ones. Every leftover English
            # line still belongs to the block, so it hangs off the last Chinese
            # line rather than being orphaned into the uncited pile.
            if len(en_run) > len(zh_run):
                last = zh_run[-1]
                for extra in en_run[len(zh_run):]:
                    en_for[last].append(extra)
                    zh_for.setdefault(extra, []).append(last)
                pairing[last] = "approximate"
            i = j
        return en_for, zh_for, pairing

    # ------------------------------------------------------------ English text

    def _english(self, n: int, raw: str) -> tuple[str, bool]:
        if not raw.strip():
            return "", False
        if raw.startswith(EN_MARK):
            return scrub(raw[len(EN_MARK):], self.index), False
        m = PAGE_MARKER.match(raw.strip())
        if m:
            return (f"Page {m.group('page')}, section type {m.group('type')}, "
                    f"transcription confidence {m.group('conf')}."), True
        if n in self.english:
            return scrub(self.english[n], self.index), True
        if not has_chinese(raw):
            return raw, False
        return NO_ENGLISH, True

    def label_kind(self, n: int, claim_lines: set[int]) -> str:
        """The contract's line kind. `claim` is a prose line inside the claims."""
        k = self.kind[n]
        return "claim" if k == "prose" and n in claim_lines else k

    def with_partners(self, lines) -> list[int]:
        """A citation, plus the English of every Chinese line in it.

        A Chinese line and the English it was translated into are one unit of
        evidence. Citing the first without the second hides the English half from
        the only reader this file has.
        """
        out = set()
        for n in lines:
            if n not in self.lines:
                continue
            out.add(n)
            out.update(self.en_for.get(n, ()))
            out.update(self.zh_for.get(n, ()))
        return sorted(out)


# ---------------------------------------------------------------- sections

def section_index(sections, source: Source):
    """line -> section label, and the claims line set, both in English only."""
    by_line: dict[int, str] = {}
    claim_lines: set[int] = set()
    order: list[str] = []
    for s in sections:
        label = s.get("section_label") or f"Section {s.get('section_index')}"
        if label not in order:
            order.append(label)
        for n in range(int(s["start_line"]), int(s["end_line"]) + 1):
            by_line[n] = label
            if s.get("section_type") == "claims":
                claim_lines.add(n)
    return by_line, claim_lines, order


# ---------------------------------------------------------------- citation sets

def reaction_cited(row) -> list[int]:
    """The lines a reaction provenance row cites. Two numbers are a span.

    See the module docstring: [182, 188] is a block of seven lines and [45, 46, 77,
    82] is four scattered citations. Length is the only signal the artifact gives,
    and it is a reliable one here because every block citation is written as its two
    endpoints and every scattered citation enumerates.
    """
    lines = sorted({n for n in (row.get("source_lines") or []) if isinstance(n, int)})
    if len(lines) == 2:
        return list(range(lines[0], lines[1] + 1))
    return lines


def compound_cited(rows) -> list[int]:
    """The union over every provenance row for one identifier. Exact lines."""
    out: set[int] = set()
    for row in rows:
        out.update(n for n in (row.get("source_lines") or []) if isinstance(n, int))
    return sorted(out)


# ---------------------------------------------------------------- record model

class Record:
    """One gold record, with its identity, its citation and its check results."""

    __slots__ = ("record_id", "kind", "label_en", "section_en", "cited",
                 "claims", "checks", "svg", "uuid", "rec", "flags")

    def __init__(self, record_id, kind, label_en, section_en, cited, svg=None,
                 uuid=None, rec=None, flags=()):
        self.uuid = uuid
        self.record_id = record_id
        self.kind = kind
        self.label_en = label_en
        self.section_en = section_en
        self.cited = cited
        self.svg = svg
        # The verdict key verifier/lib/verdict.ts resolveRec() understands. Emitted
        # rather than left for the UI to reconstruct, because reactions key on
        # reaction_id and everything else keys on a uuid, and a consumer that
        # guesses one rule for all four writes verdicts that never load again.
        self.rec = rec
        # The annotation's own validation_flags. Carried on the record so a check
        # that rediscovers one can say "the annotation flagged this too" instead of
        # presenting it as a new finding.
        self.flags = list(flags)
        self.claims: list[dict] = []
        self.checks: list[dict] = []

    @property
    def stratum(self) -> str:
        return f"{self.kind}:{self.section_en}"

    def failing(self) -> bool:
        return any(c["status"] == "fail" for c in self.checks)



def ascii_key(text: str) -> str:
    """A stable ASCII key for a string that may be Chinese.

    Five of the 75 compound identifiers in this gold are Chinese, so five gold ids
    and every field name built from them are Chinese too. Keys are not human-facing
    strings and are not covered by the `_en` rule, but they still land in a file
    whose whole promise is that a reader who has no Chinese can open it, and they
    are still grepped for Han characters as the last gate before it ships.

    Translating them instead would be worse. `claim_id` is a hash of `(record_id,
    field)` and the contract promises it is stable across runs; a record_id derived
    from the translation table would move the moment somebody improved a name, and
    every verdict a reviewer had already recorded against it would orphan. Hashing
    the Chinese itself is ASCII, is stable forever, and the readable name travels
    beside it as `label_en`, with `uuid` as the join key back into the gold.
    """
    if not has_chinese(text):
        return text
    return "zh-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


def safe_record_id(patent_id: str, gold_id: str, identifier: str) -> str:
    return gold_id if not has_chinese(gold_id) else f"{patent_id}_{ascii_key(identifier)}"


def claim_id(record_id: str, field: str) -> str:
    return hashlib.sha256(f"{record_id}\x1f{field}".encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------- claim building

FIELD_LABELS = {
    "quantity.mass_g": "Mass charged",
    "quantity.volume_ml": "Volume charged",
    "quantity.mmol": "Amount charged, in millimoles",
    "quantity.equivalents": "Equivalents",
    "quantity.yield_pct": "Yield",
    "melting_point.min_c": "Melting point, low end",
    "melting_point.max_c": "Melting point, high end",
    "purity_pct": "Purity",
    "analytics.value": "Analytical measurement",
    "conditions.temperature.value_c": "Reaction temperature",
    "conditions.temperature.min_c": "Reaction temperature, low end",
    "conditions.temperature.max_c": "Reaction temperature, high end",
    "conditions.time_h": "Reaction time",
    "conditions.concentration.value": "Reagent concentration",
    "product_yield_pct": "Yield of the product",
    "overall_yield_pct": "Overall yield of the route",
    "extraction_rollup.best_overall_yield_pct": "Best overall yield in the patent",
    "molar_ratio_text": "Molar ratio",
    "provenance.quote": "Quoted source text",
    "resolved": "Whether this is a definite molecule",
    "judgement.reaction_class_confidence": "Reaction class, self-declared as "
                                           "uncertain",
    "judgement.linkage_confirmed": "Which step this one follows",
    "judgement.cross_reference_unresolved": "An unresolved cross-reference",
    "judgement.validation_flags": "The annotation's own validation flags",
    "judgement.is_complete": "Whether this step is fully recorded",
    "__coverage__": "Source line no record cites",
}

# A field name carries the row it came from: `compounds[toluene].quantity.mass_g`.
# The label is about the KIND of field, so the row is stripped before the lookup and
# the compound prefix with it, or every row of every reaction would need its own
# label and none of them would have one.
FIELD_INDEX = re.compile(r"\[[^\]]*\]")


def field_label(field: str) -> str:
    bare = FIELD_INDEX.sub("", field)
    for candidate in (bare, bare[len("compounds."):] if
                      bare.startswith("compounds.") else bare):
        if candidate in FIELD_LABELS:
            return FIELD_LABELS[candidate]
    return bare

UNIT_WORDS = {"g": "grams", "ml": "millilitres", "mmol": "millimoles",
              "%": "per cent", "C": "degrees Celsius", "h": "hours", None: ""}

HIGHLIGHT_KIND = {
    "quantity.yield_pct": "yield", "product_yield_pct": "yield",
    "conditions.temperature": "condition", "conditions.time_h": "condition",
}

BASE_RISK = {"not_found": 0.90, "partial": 0.55, "not_checkable": 0.30, "found": 0.05}

# The quantity fields a record can carry, and the unit each is stated in.
QUANTITY_FIELDS = (("mass_g", "g"), ("volume_ml", "ml"), ("mmol", "mmol"),
                   ("equivalents", None), ("yield_pct", "%"))

# What each of the annotation's own validation flags says, in English. These are
# statements about the PATENT, and the wording has to keep that straight: a reviewer
# asked to mark a mass_balance_implausible reaction "wrong" would be being asked to
# reject a correct annotation of a defective document.
FLAG_MEANING_EN = {
    "no_conditions": "the patent states no reaction conditions for this step",
    "route_attribution_unclear": "it is unclear whether this step belongs to the "
                                 "prior art or to the invention",
    "mass_balance_implausible": "the masses printed for this step do not balance",
    "molar_mass_inconsistent": "the mass and the molar amount printed for a "
                               "reagent imply the wrong molecular weight",
    "drawing_text_conflict": "the drawn scheme and the written procedure disagree",
    "reagent_written_not_drawn": "a reagent named in the text is missing from the "
                                 "drawing",
    "reagent_drawn_not_written": "a reagent in the drawing is missing from the text",
    "scale_discontinuity": "the amount carried into this step does not match the "
                           "amount the previous step produced",
}


def derivation(field: str, quantity: dict, mw: float | None,
               name_en: str) -> dict | None:
    """How a field's value could be recomputed, if it is not quoted at all.

    Only `mmol` has one in this schema, and it is the important one. A row printing
    both a mass and a molar amount is an implicit claim about molecular weight, and
    the arithmetic is the same arithmetic verifier/lib/checks.ts already runs from
    the other side, so the tolerance is taken from there rather than reinvented.
    """
    if field != "mmol":
        return None
    mass = quantity.get("mass_g")
    if mass is None:
        return None
    return {"kind": "mmol_from_mass", "mass_g": float(mass), "mw": mw,
            "name_en": name_en}


def fmt_value(value: float) -> str:
    """The shortest honest rendering. 34.0 prints as 34, 25.25 stays 25.25."""
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


def fmt_quantity(value: float, unit: str | None) -> str:
    if unit == "%":
        return f"{fmt_value(value)}%"
    if unit == "C":
        return f"{fmt_value(value)} C"
    return f"{fmt_value(value)} {unit}".strip() if unit else fmt_value(value)


class Engine:
    """Everything the run needs, assembled once and then asked questions."""

    def __init__(self, patent_id: str, data: dict):
        self.patent_id = patent_id
        self.data = data
        self.index = data["translations"]
        self.source = Source(patent_id, self.index)
        self.section_of_line, self.claim_lines, self.section_order = section_index(
            data["sections"], self.source)

        self.structures = {e["identifier"]: e for e in data["structures"]}
        self.group_of: dict[str, str] = {}
        for key, members in data["equivalence"].items():
            for m in members:
                self.group_of[m] = key

        self.compound_by_id = {c["identifier"]: c for c in data["compounds"]}
        self.compound_prov: dict[str, list] = {}
        for row in data["compound_prov"]:
            self.compound_prov.setdefault(row["identifier"], []).append(row)
        self.reaction_prov = {row["reaction_id"]: row for row in data["reaction_prov"]}

        self.records: list[Record] = []
        self.claims: list[dict] = []
        self.record_of: dict[int, Record] = {}
        self.cited_lines: dict[int, set[str]] = {}
        self.bases: dict[str, dict] = {}
        self.agreement = {"both": [], "machine_only": [], "annotation_only": []}

    # -------------------------------------------------------------- helpers

    def english_name(self, name: str | None) -> str:
        if not name:
            return "(unnamed)"
        if has_chinese(name):
            entry = self.index.get(name) or {}
            return scrub(entry.get("en") or name, self.index)
        return name

    def canon_name(self, name: str) -> str:
        return self.group_of.get(name, name)

    def svg_for(self, identifier: str) -> str | None:
        entry = self.structures.get(identifier)
        if entry and entry.get("svg"):
            return f"output/relevant_output/{entry['svg']}"
        return None

    def cumulative_yield(self, pathway) -> float | None:
        """The product of every step yield along a route, as a percentage.

        None when any step has no yield, because a route with a hole in it has no
        overall yield and reporting the product of the steps that do have one would
        silently overstate it.
        """
        product = 1.0
        for st in pathway.get("steps") or []:
            y = st.get("product_yield_pct")
            if y is None:
                return None
            product *= float(y) / 100.0
        return round(product * 100.0, 1)

    # ------------------------------------------------- quoted versus derived

    def resolve_bases(self) -> None:
        """Which numeric fields this document QUOTES, and which it DERIVES.

        Measured, never declared. For every numeric field name, count how many of
        its values are literally printed on the lines the record itself cites. On
        this patent the split is total:

            mass_g      22 of 22 printed        volume_ml   8 of 8 printed
            yield_pct    7 of 7  printed        mmol        0 of 10 printed

        `mmol` is never written in this patent. Every molar amount in the gold was
        calculated by the annotator from a mass and a molecular weight. A grounding
        check that does not know this reports ten hallucinations that are not
        hallucinations, at the top of a queue with about forty real items in it, and
        a reviewer whose first five rows are all the machine being wrong stops
        trusting it. Nothing after that matters.

        So a field nothing ever quotes is not checked for grounding at all. It is
        checked by RECOMPUTING it, which is a stronger test than the string match
        would have been and catches things no string match could. Bromine is the
        one that fails here: 39.6 g against 220 mmol implies 180.0 g/mol and bromine
        is 159.81, so either the mass or the amount is wrong and they cannot both be
        right. That is what tier 1 should be full of.

        Inferred per patent rather than hardcoded, because the next document may
        state its molar amounts and omit its masses, and a constant list would then
        be wrong in the direction that hides defects.
        """
        tally: dict[str, dict] = {}
        for claim in self.claims:
            name = claim.get("_field_name")
            if name is None:
                continue
            t = tally.setdefault(name, {"total": 0, "matched": 0})
            t["total"] += 1
            t["matched"] += 1 if claim.get("_matched") else 0

        for name, t in tally.items():
            t["basis"] = ("derived" if t["matched"] == 0 and t["total"] >= 3
                          else "quoted")
        self.bases = tally

        for claim in self.claims:
            name = claim.get("_field_name")
            if name is None:
                continue
            basis = tally[name]["basis"]
            claim["basis"] = basis
            if basis == "quoted" or claim.get("_matched"):
                continue
            self.rescore_derived(claim, name, tally[name])

    def rescore_derived(self, claim: dict, name: str, tally: dict) -> None:
        """Re-ask a derived field the only question there is about it."""
        d = claim.get("_derive")
        value = claim["_value"]
        preface = (f"This patent never prints a value for {name}: none of the "
                   f"{tally['total']} in the annotation appears on any line any "
                   f"record cites. It is calculated, not quoted, so the question "
                   f"is whether the calculation holds. ")
        claim["question_en"] = (f"The annotation calculated {claim['claimed_en']} "
                                f"for {claim['_subject']}. Does that calculation "
                                f"hold?")
        if d is None:
            claim["auto"] = "not_checkable"
            claim["auto_reason_en"] = (
                preface + "This stage has no way to recompute it from the other "
                "fields on the record, so a human must check it against the "
                "patent.")
            claim["risk_reasons_en"] = ["A calculated number with nothing to check "
                                        "it against."]
            claim["risk"] = 0.35
            claim["load_bearing"] = True
            claim["needs_human"] = True
            return

        if d["mw"] is None:
            claim["auto"] = "not_checkable"
            claim["auto_reason_en"] = (
                preface + f"It should be the {d['mass_g']} g charged divided by the "
                f"molecular weight of {d['name_en']}, but no structure is resolved "
                f"for that molecule, so there is no molecular weight to divide by.")
            claim["risk_reasons_en"] = ["A calculated number whose molecule has no "
                                        "resolved structure."]
            claim["risk"] = 0.35
            claim["load_bearing"] = True
            claim["needs_human"] = True
            return

        implied = d["mass_g"] / (value / 1000.0)
        delta = implied - d["mw"]
        tol = max(ABS_TOL_FLOOR, REL_TOL * d["mw"])
        arithmetic = (f"{d['mass_g']} g of {d['name_en']} at "
                      f"{d['mw']:.2f} g/mol is "
                      f"{d['mass_g'] / d['mw'] * 1000:.1f} mmol")
        if abs(delta) <= tol:
            claim["auto"] = "not_checkable"
            claim["auto_reason_en"] = (
                preface + f"The calculation checks out: {arithmetic}, and the "
                f"annotation records {fmt_value(value)} mmol. Implied molecular "
                f"weight {implied:.2f} against {d['mw']:.2f}, within tolerance "
                f"{tol:.2f}.")
            claim["risk_reasons_en"] = []
            claim["risk"] = 0.10
            claim["load_bearing"] = False
            claim["needs_human"] = True
            return

        rec = self.record_of.get(id(claim))
        flagged = bool(rec and ({"molar_mass_inconsistent",
                                 "mass_balance_implausible"} & set(rec.flags)))
        cl_for_h = abs(delta + CL_FOR_H) < CL_WINDOW
        claim["auto"] = "not_found"
        claim["risk"] = 0.95
        claim["load_bearing"] = True
        claim["needs_human"] = True
        tail = ""
        if cl_for_h:
            tail = (f" The shortfall of {delta:+.2f} is very close to the "
                    f"{-CL_FOR_H:+.2f} that swapping one chlorine for one hydrogen "
                    f"would cost, which is a lead for the reviewer and not a "
                    f"diagnosis.")
        if flagged:
            claim["about"] = "patent"
            claim["question_en"] = (
                f"The patent's own numbers for {claim['_subject']} do not agree "
                f"with each other. The annotation recorded them as printed and "
                f"flagged it. Was that the right call?")
            claim["auto_reason_en"] = (
                preface + f"It does not: {arithmetic}, but the annotation records "
                f"{fmt_value(value)} mmol, an implied molecular weight of "
                f"{implied:.2f} against {d['mw']:.2f}.{tail} The annotation flagged "
                f"this step itself, so this is very likely a defect in the patent "
                f"that was correctly recorded rather than an extraction error.")
            claim["risk_reasons_en"] = [
                "The mass and the molar amount printed for this reagent cannot "
                "both be right.",
                "The annotation already flagged this step, so confirming it is "
                "quick."]
        else:
            claim["auto_reason_en"] = (
                preface + f"It does not: {arithmetic}, but the annotation records "
                f"{fmt_value(value)} mmol, an implied molecular weight of "
                f"{implied:.2f} against {d['mw']:.2f}, outside the tolerance of "
                f"{tol:.2f}.{tail} The annotation did NOT flag this step, so either "
                f"it missed a defect in the patent or one of the two numbers was "
                f"read wrong.")
            claim["risk_reasons_en"] = [
                "The mass and the molar amount cannot both be right.",
                "The annotation did not flag this step, so nobody has looked at "
                "it yet."]

    # ------------------------------------------------- the agreement matrix

    def agreement_matrix(self) -> None:
        """This stage's arithmetic findings against the annotation's own flags.

        Three buckets, and the two disagreements are where the information is.
        Rediscovering `molar_mass_inconsistent` and presenting it as a new finding
        would be this stage taking credit for a defect the annotator had already
        found and written up. What is worth a reviewer's time is a step this stage
        fails that the annotation passed, and what is worth THIS STAGE's authors'
        time is a step the annotation flagged that this stage could not see.
        """
        machine = {r.record_id for r in self.records
                   if r.kind == "reaction"
                   and any(c["family"] == "quantity" and c["status"] == "fail"
                           for c in r.checks)}
        annotated = {r.record_id for r in self.records
                     if r.kind == "reaction"
                     and {"molar_mass_inconsistent", "mass_balance_implausible"}
                     & set(r.flags)}
        label = {r.record_id: r.label_en for r in self.records}
        self.agreement = {
            "both": sorted(label[i] for i in machine & annotated),
            "machine_only": sorted(label[i] for i in machine - annotated),
            "annotation_only": sorted(label[i] for i in annotated - machine),
        }

    # ------------------------------------------------- the three review queues

    def promoted_fields(self) -> dict[str, list[str]]:
        """Record -> the claim-field prefixes some failing check on it names."""
        out: dict[str, list[str]] = {}
        for rec in self.records:
            for c in rec.checks:
                if c["status"] != "fail":
                    continue
                out.setdefault(rec.record_id, [])
                out[rec.record_id].extend(c["about_fields"] or [""])
        return out

    def assign_tiers(self) -> None:
        """Which of the three queues in REVIEW-PROTOCOL.md each claim belongs to.

        Tier is the queue and risk is the order within it. They answer different
        questions: risk says how alarming one claim is, tier says which census a
        reviewer with 900 seconds is working through when they meet it.

            1  everything the machine could not confirm, plus every claim sitting
               on a record with a failed check. A census, not a sample.
            2  the uncited chemistry lines. The recall side. Also a census.
            3  what the machine matched cleanly, sampled rather than read.
        """
        promoted = self.promoted_fields()
        for claim in self.claims:
            prefixes = promoted.get(claim["record_id"], [])
            if claim["field"] == "__coverage__":
                claim["tier"] = 2
            elif claim["auto"] in ("not_found", "partial"):
                claim["tier"] = 1
            elif claim["auto"] == "not_checkable" and claim["load_bearing"]:
                claim["tier"] = 1
            elif any(claim["field"].startswith(pre) for pre in prefixes):
                claim["tier"] = 1
                claim["needs_human"] = True
                claim["risk"] = max(claim["risk"], 0.70)
                claim["risk_reasons_en"] = claim["risk_reasons_en"] + [
                    "A check on this row failed, so the number is worth reading "
                    "even though it is printed where the record says it is."]
            else:
                claim["tier"] = 3

    def note_citation(self, record_id: str, lines) -> None:
        for n in lines:
            self.cited_lines.setdefault(n, set()).add(record_id)

    def evidence(self, cited: list[int], hit_lines: set[int]) -> list[dict]:
        """The evidence panel: every line that mattered, then the rest, capped.

        `pairing` says how the English on a Chinese line was arrived at, so a screen
        can mark the four lines in this document whose translation had to be clamped
        rather than paired one for one. `is_translation` says whether what is shown
        is a translation at all or the literal characters on the line.
        """
        ordered = sorted(cited, key=lambda n: (n not in hit_lines, n))
        shown = sorted(ordered[:EVIDENCE_LINE_CAP])
        return [{"n": n,
                 "text_en": self.source.text_en.get(n, ""),
                 "is_translation": self.source.is_translation.get(n, False),
                 "kind": self.source.label_kind(n, self.claim_lines),
                 "pairing": self.source.pairing.get(n, "self"),
                 "matched": n in hit_lines}
                for n in shown]

    # -------------------------------------------------------------- numeric claim

    def locate(self, cited, value: float, unit: str | None):
        """Where on the cited lines this quantity is printed, if it is at all.

        Three strengths, and the difference between them is what a reviewer needs.
        `exact` is the number with its unit beside it. `loose` is the number with
        no unit, which is a real state in this document: the patent prints thionyl
        chloride as "71.4(0.6mol)" with no g anywhere. `comma` is the number only
        if a comma on the line is read as a decimal point, which is offered last
        and never silently, because this document is full of 1,2-dichloroethane.
        """
        exact, loose, comma = [], [], []
        for n in cited:
            text = self.source.lines.get(n, "")
            for tok in tokenise(text):
                if tok.unit == unit and same_number(tok.canonical(), value):
                    exact.append((n, tok))
                elif tok.unit is None and same_number(tok.value, value):
                    loose.append((n, tok))
                elif unit is None and same_number(tok.value, value):
                    loose.append((n, tok))
            if not exact and not loose:
                if any(same_number(v, value) for v in comma_decimals(text)):
                    comma.append(n)
        return exact, loose, comma

    def numeric_claim(self, rec: Record, field: str, value: float,
                      unit: str | None, subject_en: str,
                      highlight_kind: str = "value",
                      field_name: str | None = None,
                      derive: dict | None = None) -> dict:
        """One number, asked of the lines its own record cites.

        Four verdicts and what each means to a reviewer who cannot read the patent:

            found        the number and its unit are both printed on a cited line
            partial      the number is there without its unit, or only in one of the
                         two languages, or only as a comma-decimal reading
            not_found    the number is on none of the cited lines. Read this one
            not_checkable the record cites no line at all, so nothing can be asked

        The verdict is provisional until `resolve_bases()` has run. A field that no
        record ever quotes is DERIVED rather than absent, and scoring it here as
        ungrounded would fill the review queue with the machine being wrong about a
        field the patent never states. See resolve_bases().
        """
        cited = rec.cited
        claimed_en = fmt_quantity(value, unit)
        question = (f"Does the patent say {claimed_en} of {subject_en}?"
                    if unit in ("g", "ml", "mmol")
                    else f"Does the patent say {claimed_en} for {subject_en}?")
        extra = {"basis": "quoted", "_field_name": field_name or field.split(".")[-1],
                 "_derive": derive, "_value": value, "_unit": unit,
                 "_subject": subject_en}

        if not cited:
            return self._claim(rec, field, question, claimed_en, value, unit,
                               [], [], "not_checkable",
                               "This record cites no source line, so there is "
                               "nothing to check the number against.",
                               ["The record carries no provenance."],
                               highlight_kind, load_bearing=True, extra=extra)

        exact, loose, comma = self.locate(cited, value, unit)
        extra["_matched"] = bool(exact or loose or comma)
        hits = exact or loose
        hit_lines = {n for n, _ in hits} | set(comma)
        zh = sorted(n for n in hit_lines if self.source.kind[n] != "translation")
        en = sorted(n for n in hit_lines if self.source.kind[n] == "translation")

        where = []
        if zh:
            where.append("the Chinese line" + ("s " if len(zh) > 1 else " ")
                         + ", ".join(str(n) for n in zh))
        if en:
            where.append("the English translation on line"
                         + ("s " if len(en) > 1 else " ")
                         + ", ".join(str(n) for n in en))

        risk_reasons: list[str] = []
        if exact:
            auto = "found"
            reason = (f"The number {fmt_value(value)} appears with its unit "
                      f"{UNIT_WORDS.get(unit, unit or '')} on "
                      + " and on ".join(where) + ".")
            if not zh:
                auto = "partial"
                reason += (" It is printed only in the English machine translation, "
                           "not in the Chinese the patent actually says.")
                risk_reasons.append(
                    "The value is in the translation only, and the Chinese is the "
                    "authoritative text.")
        elif loose:
            auto = "partial"
            reason = (f"The number {fmt_value(value)} appears on "
                      + " and on ".join(where)
                      + f", but not with the unit "
                        f"{UNIT_WORDS.get(unit, unit or 'expected')}.")
            risk_reasons.append(
                "The unit was read from context rather than printed beside the "
                "number.")
        elif comma:
            auto = "partial"
            reason = (f"The number {fmt_value(value)} appears on "
                      + " and on ".join(where)
                      + " only if the comma there is read as a decimal point.")
            risk_reasons.append("The match depends on reading a comma as a decimal "
                                "point.")
        else:
            auto = "not_found"
            reason = (f"The number {fmt_value(value)} is on none of the "
                      f"{len(cited)} source lines this record cites "
                      f"({compact_lines(cited)}). Either the patent does not say "
                      f"it, or the record cites the wrong lines.")
            risk_reasons.append("The claimed number is absent from every line the "
                                "record cites.")

        highlights = []
        for n, tok in hits:
            for h in self.highlights_for(n, tok.value, unit, highlight_kind):
                highlights.append(h)
        return self._claim(rec, field, question, claimed_en, value, unit,
                           cited, highlights, auto, reason, risk_reasons,
                           highlight_kind, hit_lines, extra=extra)


    def highlights_for(self, line: int, value: float, unit: str | None,
                       kind: str) -> list[dict]:
        """Offsets of the value inside the English the panel will actually show."""
        text = self.source.text_en.get(line, "")
        out = []
        for tok in tokenise(text):
            if same_number(tok.value, value) or (
                    tok.unit == unit and same_number(tok.canonical(), value)):
                out.append({"line": line, "start": tok.start, "end": tok.end,
                            "kind": kind})
        return out

    # -------------------------------------------------------------- text claim

    def ratio_claim(self, rec: Record, field: str, ratio: str,
                    subject_en: str) -> dict:
        """A molar ratio such as 1:1-3:1-2, matched as printed.

        Ratios are the one numeric field that is not a quantity: there is no unit to
        convert and no single value to compare, so the printed form is the claim and
        a normalised substring search is the honest test of it.
        """
        needle = normalise(ratio)
        hit_lines = {n for n in rec.cited
                     if needle and needle in self.source.norm.get(n, "")}
        question = f"Does the patent state the molar ratio {ratio} for {subject_en}?"
        if not rec.cited:
            return self._claim(rec, field, question, ratio, None, None, [], [],
                               "not_checkable",
                               "This record cites no source line.",
                               ["The record carries no provenance."], "value")
        if hit_lines:
            reason = (f"The ratio {ratio} is printed on line"
                      f"{'s' if len(hit_lines) > 1 else ''} "
                      + ", ".join(str(n) for n in sorted(hit_lines)) + ".")
            auto, risk = "found", []
        else:
            elsewhere = sorted(n for n, t in self.source.norm.items()
                               if needle and needle in t)
            if elsewhere:
                reason = (f"The ratio {ratio} is in the patent, on line"
                          f"{'s' if len(elsewhere) > 1 else ''} "
                          + ", ".join(str(n) for n in elsewhere)
                          + f", but not on the lines this record cites "
                            f"({compact_lines(rec.cited)}).")
                risk = ["The ratio is real but the record cites the wrong lines."]
            else:
                reason = (f"The ratio {ratio} is nowhere in the source.")
                risk = ["The claimed ratio is absent from the whole document."]
            auto = "not_found"
        return self._claim(rec, field, question, ratio, None, None, rec.cited, [],
                           auto, reason, risk, "value", hit_lines)

    # -------------------------------------------------------------- quote claim

    def quote_claim(self, rec: Record, field: str, quote: str,
                    declared: list[int]) -> dict:
        """Is the quoted text on the lines the row that carries it declares?

        The quote itself never reaches the artifact: it is Chinese, and the reader
        has none. What reaches the artifact is the English of the lines the quote
        was found on, plus a sentence saying whether those are the lines the row
        claimed. That is the whole question a reviewer can answer here.
        """
        cited = rec.cited
        question = ("Is the text this record quotes actually on the source lines it "
                    "cites?")
        if not has_chinese(quote):
            # English annotator prose, not verbatim patent text. Tested as ASCII
            # against the cited lines and handed to a human either way, because a
            # sentence someone wrote about the patent is not a sentence in it.
            needle = normalise(quote)
            found = [n for n in cited if needle and needle in self.source.norm.get(n, "")]
            auto = "found" if found else "not_checkable"
            reason = ("This row quotes English annotator prose rather than the "
                      "patent's own words"
                      + (f", and that text is on line "
                         f"{', '.join(str(n) for n in found)}."
                         if found else
                         ", so no string match against the Chinese source can "
                         "settle it. A human must read it."))
            return self._claim(rec, field, question,
                               "an English note rather than a quotation",
                               None, None, cited, [], auto, reason,
                               [] if found else
                               ["The quote is a note, not patent text."],
                               "name", set(found))

        spans, total, uncovered = cover(quote, cited, self.source.norm)
        cited_set = set(cited)
        on, off = 0, 0
        off_lines: set[int] = set()
        on_lines: set[int] = set()
        for a, b, n in spans:
            chars = sum(1 for k in range(a, b) if CJK.match(normalise(quote)[k]))
            if n in cited_set:
                on += chars
                on_lines.add(n)
            else:
                off += chars
                off_lines.add(n)

        risk_reasons: list[str] = []
        if total == 0:
            auto = "not_checkable"
            reason = ("The quotation carries no Chinese characters to locate.")
            risk_reasons.append("Nothing in the quotation can be matched.")
        elif on and not off and not uncovered:
            auto = "found"
            reason = (f"All {total} Chinese characters of the quotation are on line"
                      f"{'s' if len(on_lines) > 1 else ''} "
                      + ", ".join(str(n) for n in sorted(on_lines))
                      + ", which this record cites.")
        elif on:
            auto = "partial"
            bits = [f"{on} of the {total} Chinese characters of the quotation are on "
                    f"the cited line{'s' if len(on_lines) > 1 else ''} "
                    + ", ".join(str(n) for n in sorted(on_lines)) + "."]
            if off:
                bits.append(f"Another {off} were found on line"
                            f"{'s' if len(off_lines) > 1 else ''} "
                            + ", ".join(str(n) for n in sorted(off_lines))
                            + ", which this record does not cite.")
                risk_reasons.append("Part of the quotation is on lines the record "
                                    "does not cite.")
            if uncovered:
                bits.append(f"{uncovered} were found nowhere in the source.")
                risk_reasons.append("Part of the quotation is in no source line at "
                                    "all.")
            reason = " ".join(bits)
        elif off:
            auto = "not_found"
            reason = (f"The quoted text is in the patent, on line"
                      f"{'s' if len(off_lines) > 1 else ''} "
                      + ", ".join(str(n) for n in sorted(off_lines))
                      + f", but on none of the {len(cited)} lines this record cites "
                        f"({compact_lines(cited)}). The record cites the wrong "
                        f"place.")
            risk_reasons.append("The quotation is real but the citation points "
                                "somewhere else.")
        else:
            auto = "not_found"
            reason = (f"None of the {total} Chinese characters of this quotation "
                      f"were found anywhere in the {len(self.source.lines)}-line "
                      f"source. The quotation may be invented.")
            risk_reasons.append("The quotation was not found anywhere in the "
                                "document.")

        # A record anchored only to the drawn scheme has no prose on its cited
        # line to match against. The text it quotes is narrative from nearby, which
        # is a citation pointing at the wrong line and worth reporting, but it is
        # not an invented quotation and must not sit at the top of a queue whose
        # top is reserved for those.
        if auto == "not_found" and cited and all(
                self.source.kind.get(n) in ("image_extract", "blank")
                for n in cited):
            auto = "partial"
            reason += (" This record is anchored to the drawn scheme, which carries "
                       "no prose at all, so what it quotes is narrative from "
                       "elsewhere rather than the evidence the record rests on.")
            risk_reasons = ["The record cites only the drawing, and quotes prose "
                            "that is somewhere else."]

        panel = sorted(cited_set | off_lines)
        panel = self.source.with_partners(panel)
        claim = self._claim(rec, field, question,
                            self.quote_gist(quote, on_lines | off_lines),
                            None, None, cited, [], auto, reason, risk_reasons,
                            "name", on_lines | off_lines, panel_lines=panel)
        return claim

    def quote_gist(self, quote: str, lines: set[int]) -> str:
        """What the row quotes, said in English, without the Chinese.

        The index is keyed on the exact string, so a quote it holds is answered
        directly; otherwise the English of the lines the quote was found on is the
        closest true thing that can be said about it.
        """
        entry = self.index.get(quote) or {}
        if entry.get("en"):
            return scrub(entry["en"], self.index)
        if lines:
            parts = []
            for n in sorted(lines):
                t = self.source.text_en.get(n, "")
                if t and t not in parts:
                    parts.append(t)
            if parts:
                return " ... ".join(parts)
        return ("a passage of Chinese for which the pipeline carries no English")

    # -------------------------------------------------------------- assembly

    def _claim(self, rec: Record, field: str, question: str, claimed_en: str,
               claimed_value, claimed_unit, cited, highlights, auto, reason,
               risk_reasons, highlight_kind, hit_lines=frozenset(),
               panel_lines=None, about="extraction", load_bearing=False,
               rec_field=None, extra=None) -> dict:
        """Assemble one claim. Every field a reviewer or a sampler needs, inline.

        `about` is the question being asked, and it is not decoration. There are two
        completely different things a reviewer can be shown:

            extraction   the annotation says X and the patent says Y. We are wrong.
            patent       the annotation says the patent contradicts itself. We are
                         RIGHT and the document is defective.

        Blurring them asks a reviewer to mark a correct annotation as wrong, which
        is worse than not asking at all. FINDINGS.md is explicit that its items are
        defects in the patent and that the annotation changes nothing, and that
        posture has to survive into every question worded here.
        """
        panel = panel_lines if panel_lines is not None else cited
        risk = BASE_RISK[auto]
        if risk_reasons:
            risk = min(1.0, risk + 0.05 * (len(risk_reasons) - 1))
        claim = {
            "claim_id": claim_id(rec.record_id, field),
            "record_id": rec.record_id,
            "record_kind": rec.kind,
            "rec": rec.rec,
            "rec_field": rec_field if rec_field is not None else field,
            "record_label_en": rec.label_en,
            "section_en": rec.section_en,
            "stratum": rec.stratum,
            "about": about,
            "field": field,
            "field_label_en": field_label(field),
            "question_en": question,
            "claimed_en": claimed_en,
            "claimed_value": claimed_value,
            "claimed_unit": claimed_unit,
            "cited_lines": list(cited),
            "evidence_en": " ".join(
                self.source.text_en.get(n, "") for n in panel).strip(),
            "evidence_lines": self.evidence(panel, set(hit_lines)),
            "highlights": highlights,
            "auto": auto,
            "auto_reason_en": reason,
            "needs_human": auto != "found",
            "load_bearing": bool(load_bearing),
            "risk": round(risk, 2),
            "risk_reasons_en": risk_reasons,
            "structure_svg_path": rec.svg,
            "basis": None,
            "tier": None,
        }
        claim.update(extra or {})
        rec.claims.append(claim)
        self.claims.append(claim)
        self.record_of[id(claim)] = rec
        return claim



def compact_lines(lines) -> str:
    """"45, 46, 77, 82" for a citation, "182-188" for a span."""
    ns = sorted(set(lines))
    if not ns:
        return "none"
    runs, start, prev = [], ns[0], ns[0]
    for n in ns[1:]:
        if n == prev + 1:
            prev = n
            continue
        runs.append((start, prev))
        start = prev = n
    runs.append((start, prev))
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)


# ---------------------------------------------------------------- record checks

def check(cid: str, family: str, status: str, title: str, detail: str,
          needs_human: bool = False, about_fields=()) -> dict:
    """One machine finding about one record.

    `about_fields` names the claim fields this check is about, and it is what keeps
    tier 1 small enough to be read. Promoting every claim on a record with one
    failing check puts about a hundred cleanly-matched numbers in front of a
    reviewer who has time for fifty items, purely because one row of the same
    reaction failed a mass balance. The failing check names the row; only that row's
    claims are promoted. Empty means the check is about the record as a whole.
    """
    return {"id": cid, "family": family, "status": status, "title_en": title,
            "detail_en": detail, "needs_human": needs_human,
            "about_fields": list(about_fields)}


# Cl (35.453) minus H (1.008), to the two decimals the annotator used. Every
# constant in this block is taken from verifier/lib/checks.ts and must stay equal to
# it: the UI shows the reviewer one explanation and the engine writes another, and
# the two disagreeing about whether a row passes is worse than neither checking.
CL_FOR_H = 34.45
CL_WINDOW = 1.5
REL_TOL = 0.015
ABS_TOL_FLOOR = 0.5


def mass_check(name_en: str, mass_g: float, mmol: float,
               true_mw: float | None) -> tuple[str, str, dict]:
    """Implied molecular weight against the weight of the resolved structure.

    Ported from `classify` in verifier/lib/checks.ts, tolerance for tolerance. The
    chlorine-for-hydrogen classification is preserved because it is the finding this
    patent turns on: three of the printed mass and mole pairs imply the des-chloro
    weights, and calling that an unexplained offset would throw away the one lead a
    reviewer can act on.
    """
    implied = mass_g / (mmol / 1000.0)
    facts = {"mass_g": mass_g, "mmol": mmol,
             "implied_mw": round(implied, 3),
             "true_mw": true_mw,
             "delta": None if true_mw is None else round(implied - true_mw, 3)}
    if true_mw is None:
        return ("skip",
                f"No structure is resolved for \"{name_en}\", so the implied "
                f"molecular weight of {implied:.3f} has nothing to be compared "
                f"against.", facts)

    delta = implied - true_mw
    tol = max(ABS_TOL_FLOOR, REL_TOL * true_mw)
    if abs(delta) <= tol:
        return ("pass",
                f"Implied {implied:.3f} against {true_mw:.3f}, offset "
                f"{delta:+.2f}, within tolerance {tol:.2f}.", facts)
    if abs(delta + CL_FOR_H) < CL_WINDOW:
        return ("fail",
                f"Offset {delta:+.2f} (implied {implied:.3f} against "
                f"{true_mw:.3f}) is consistent with a chlorine-for-hydrogen "
                f"substitution, which shifts molecular weight by {-CL_FOR_H:+.2f}. "
                f"That is a lead for the reviewer, not a diagnosis.", facts)
    if delta > 0:
        return ("fail",
                f"The implied mass is OVER by {delta:.2f}: implied {implied:.3f} "
                f"against {true_mw:.3f}.", facts)
    return ("fail",
            f"Unexplained offset of {delta:+.2f}: implied {implied:.3f} against "
            f"{true_mw:.3f}.", facts)


IMAGE_EXTRACT = re.compile(r"^\[IMAGE_EXTRACT:\s*(?P<json>.*)\]\s*$")


def image_extract_molecules(raw: str):
    """Every molecule an IMAGE_EXTRACT span declares, with what it says about it."""
    m = IMAGE_EXTRACT.match(raw.strip())
    if not m:
        return []
    try:
        payload = json.loads(m.group("json"))
    except json.JSONDecodeError:
        return [{"smiles": None, "broken": True}]
    out = []
    for mol in payload.get("molecules") or []:
        out.append(mol)
    for rxn in payload.get("reactions") or []:
        for side in ("reactants", "products"):
            out.extend(rxn.get(side) or [])
    return out


# ---------------------------------------------------------------- the run

# Fields whose value no string match can settle. They are emitted as claims only
# where the annotation has already said it is unsure, because the queue is a budget:
# a reviewer with twenty minutes and 114 records cannot be handed 141 judgement
# calls beside the hallucinations, and a judgement the annotator was confident about
# is not what that budget should buy.
JUDGEMENT_TRIGGERS_EN = {
    "reaction_class_confidence": "The annotation records its own confidence in the "
                                 "reaction class as {value}, not high.",
    "linkage_confirmed": "The annotation could not confirm which step this one "
                         "follows.",
    "cross_reference_unresolved": "The annotation records an unresolved "
                                  "cross-reference.",
    "validation_flags": "The annotation raised its own validation flags: {value}.",
    "is_complete": "The annotation records this step as incomplete.",
}


class Run(Engine):
    """Builds every record, every claim and every check, then the artifact."""

    # ------------------------------------------------------------ records

    def build(self) -> None:
        self.build_compounds()
        self.build_reactions()
        self.build_pathways()
        self.build_patent()
        self.referential_integrity()
        self.structure_checks()
        self.drawing_checks()
        self.consistency_checks()
        self.build_coverage()
        # Order matters from here. Bases rewrite verdicts, the agreement matrix
        # reads the checks those verdicts sit beside, and tiering reads both.
        self.resolve_bases()
        self.agreement_matrix()
        self.assign_tiers()

    def section_en_of(self, label) -> str:
        return label or "Whole patent"

    def build_compounds(self) -> None:
        for c in self.data["compounds"]:
            rows = self.compound_prov.get(c["identifier"], [])
            cited = self.source.with_partners(compound_cited(rows))
            rec = Record(safe_record_id(self.patent_id, c["id"], c["identifier"]),
                         "compound", self.english_name(c["identifier"]),
                         self.section_en_of(c.get("section_label")), cited,
                         self.svg_for(c["identifier"]), c.get("compound_uuid"),
                         f"cmp:{c.get('compound_uuid')}")
            self.records.append(rec)
            self.note_citation(rec.record_id, cited)

            q = c.get("quantity") or {}
            mw = (self.structures.get(c["identifier"]) or {}).get("mw")
            for field, unit in QUANTITY_FIELDS:
                if q.get(field) is not None:
                    self.numeric_claim(rec, f"quantity.{field}", float(q[field]),
                                       unit, rec.label_en,
                                       HIGHLIGHT_KIND.get(f"quantity.{field}",
                                                          "value"),
                                       field_name=field,
                                       derive=derivation(field, q, mw,
                                                         rec.label_en))
            mp = c.get("melting_point") or {}
            for bound in ("min_c", "max_c"):
                if mp.get(bound) is not None:
                    self.numeric_claim(rec, f"melting_point.{bound}",
                                       float(mp[bound]), "C",
                                       f"the melting point of {rec.label_en}",
                                       "condition", field_name="melting_point_c")
            if c.get("purity_pct") is not None:
                self.numeric_claim(rec, "purity_pct", float(c["purity_pct"]), "%",
                                   f"the purity of {rec.label_en}", "yield",
                                   field_name="purity_pct")
            for i, a in enumerate(c.get("analytics") or []):
                if a.get("value") is not None:
                    self.numeric_claim(rec, f"analytics[{i}].value",
                                       float(a["value"]), None,
                                       f"the {a.get('method') or 'analysis'} of "
                                       f"{rec.label_en}", "value",
                                       field_name="analytics_value")

            for i, row in enumerate(rows):
                sub = Record(rec.record_id, "compound", rec.label_en,
                             rec.section_en,
                             self.source.with_partners(
                                 [n for n in (row.get("source_lines") or [])
                                  if isinstance(n, int)]),
                             rec.svg)
                sub.claims = rec.claims
                self.quote_claim(sub, f"provenance[{i}].quote",
                                 row.get("quote_zh") or "", sub.cited)
                self.note_citation(rec.record_id, sub.cited)

            if not c.get("resolved", True) or c.get("unresolved_reference"):
                self.judgement_claim(
                    rec, "resolved",
                    f"Is \"{rec.label_en}\" really a compound the patent names?",
                    "The annotation records this identifier as a class term or an "
                    "unresolved reference rather than a definite molecule, which "
                    "only a reader can settle.")

    def build_reactions(self) -> None:
        for r in self.data["reactions"]:
            row = self.reaction_prov.get(r["reaction_id"]) or {}
            cited = self.source.with_partners(reaction_cited(row))
            label = (f"{r.get('section_label')} {r.get('step_label')}: "
                     f"{self.english_name(r.get('product_name'))}")
            rec = Record(r["id"], "reaction", label,
                         self.section_en_of(r.get("section_label")), cited,
                         self.svg_for(r.get("product_name") or ""),
                         r.get("reaction_uuid"), f"rx:{r['reaction_id']}",
                         r.get("validation_flags") or [])
            self.records.append(rec)
            self.note_citation(rec.record_id, cited)

            cond = r.get("conditions") or {}
            temp = cond.get("temperature") or {}
            for bound, tag in (("value_c", "the reaction temperature"),
                               ("min_c", "the low end of the temperature range"),
                               ("max_c", "the high end of the temperature range")):
                if temp.get(bound) is not None:
                    self.numeric_claim(rec, f"conditions.temperature.{bound}",
                                       float(temp[bound]), "C",
                                       f"{tag} of this step", "condition",
                                       field_name="temperature_c")
            if cond.get("time_h") is not None:
                self.numeric_claim(rec, "conditions.time_h", float(cond["time_h"]),
                                   "h", "the reaction time of this step",
                                   "condition", field_name="time_h")
            conc = cond.get("concentration") or {}
            if conc.get("value") is not None:
                unit = "%" if (conc.get("unit") or "").strip() in ("%", "％") else None
                self.numeric_claim(rec, "conditions.concentration.value",
                                   float(conc["value"]), unit,
                                   f"the concentration of "
                                   f"{self.english_name(conc.get('reagent'))}",
                                   "condition", field_name="concentration")
            if r.get("product_yield_pct") is not None:
                self.numeric_claim(rec, "product_yield_pct",
                                   float(r["product_yield_pct"]), "%",
                                   f"the yield of "
                                   f"{self.english_name(r.get('product_name'))}",
                                   "yield", field_name="product_yield_pct")
            if r.get("molar_ratio_text"):
                for i, ratio in enumerate(molar_ratios(r["molar_ratio_text"])):
                    self.ratio_claim(rec, f"molar_ratio_text[{i}]", ratio,
                                     "this step")

            seen: dict[str, int] = {}
            for c in r.get("compounds") or []:
                ident = c.get("identifier") or ""
                seen[ident] = seen.get(ident, 0) + 1
                key = ascii_key(ident)
                tag = key if seen[ident] == 1 else f"{key}#{seen[ident]}"
                q = c.get("quantity") or {}
                mw = (self.structures.get(ident) or {}).get("mw")
                for field, unit in QUANTITY_FIELDS:
                    if q.get(field) is not None:
                        self.numeric_claim(
                            rec, f"compounds[{tag}].quantity.{field}",
                            float(q[field]), unit, self.english_name(ident),
                            HIGHLIGHT_KIND.get(f"quantity.{field}", "value"),
                            field_name=field,
                            derive=derivation(field, q, mw,
                                              self.english_name(ident)))

            if row.get("quote_zh"):
                self.quote_claim(rec, "provenance.quote", row["quote_zh"], cited)

            # The annotation's own doubts. Only the validation flags become a
            # claim, because only they name a specific thing wrong with the
            # DOCUMENT. Confidence, linkage and completeness are recorded as
            # checks: they are true of most of this patent, they discriminate
            # nothing, and 58 judgement calls in a 15-minute queue would crowd out
            # the dozen findings that are actually worth the reviewer's time.
            for key, en, ok in (
                    ("reaction_class_confidence",
                     f"The annotation records its own confidence in the reaction "
                     f"class as {r.get('reaction_class_confidence')}, not high.",
                     (r.get("reaction_class_confidence") or "high") == "high"),
                    ("linkage_confirmed",
                     "The annotation could not confirm which step this one follows.",
                     bool(r.get("linkage_confirmed"))),
                    ("cross_reference_unresolved",
                     "The annotation records an unresolved cross-reference.",
                     not r.get("cross_reference_unresolved")),
                    ("is_complete",
                     "The annotation records this step as not fully captured, "
                     "usually because the patent states no conditions for it.",
                     bool(r.get("is_complete", True)))):
                rec.checks.append(check(
                    f"consistency.{key}", "consistency",
                    "pass" if ok else "warn",
                    "The annotation is confident about this step"
                    if key == "reaction_class_confidence" else
                    FIELD_LABELS.get(f"judgement.{key}", key),
                    "The annotation raises nothing here." if ok else en,
                    needs_human=False))

            if r.get("validation_flags"):
                flags_en = english_list([FLAG_MEANING_EN.get(f, f)
                                         for f in sorted(r["validation_flags"])])
                self._claim(
                    rec, "validation_flags",
                    "The annotation says the PATENT is defective here. Reading the "
                    "evidence, was it right to say so?",
                    flags_en, None, None, cited, [], "not_checkable",
                    "This is not a claim that the annotation got something wrong. "
                    "The annotation read this step and recorded that the document "
                    "itself does not hold together: " + flags_en + ". A reviewer "
                    "confirms that the document really does say what the flag "
                    "says, and marks the annotation correct if it does.",
                    ["The annotation flagged the patent here and a human should "
                     "confirm the flag."],
                    "name", about="patent", load_bearing=True)

    def build_pathways(self) -> None:
        for p in self.data["pathways"]:
            uuid = p.get("pathway_uuid") or ""
            label = (f"{p.get('scope')} route to "
                     f"{self.english_name((p.get('product') or {}).get('identifier'))}"
                     f" from "
                     f"{self.english_name((p.get('ksm') or {}).get('identifier'))}"
                     f" ({len(p.get('steps') or [])} steps)")
            cited: list[int] = []
            for st in p.get("steps") or []:
                prov = self.reaction_prov.get(st.get("reaction_id")) or {}
                cited.extend(reaction_cited(prov))
            cited = self.source.with_partners(sorted(set(cited)))
            rec = Record(f"{self.patent_id}_pathway_{uuid}", "pathway", label,
                         self.section_en_of(p.get("section_label")), cited,
                         None, uuid, f"pw:{uuid}")
            self.records.append(rec)
            self.note_citation(rec.record_id, cited)
            stated = p.get("overall_yield_pct")
            computed = self.cumulative_yield(p)
            if stated is not None or computed is not None:
                ok = (stated is not None and computed is not None
                      and abs(float(stated) - computed) <= 0.15)
                rec.checks.append(check(
                    "quantity.overall_yield", "quantity",
                    "pass" if ok else ("skip" if computed is None or stated is None
                                       else "fail"),
                    "The route yield is the product of its step yields",
                    (f"The record states {stated}%. " if stated is not None
                     else "The record states no overall yield. ")
                    + ("At least one step has no yield, so there is nothing to "
                       "multiply." if computed is None else
                       f"Multiplying the {len(p.get('steps') or [])} step yields "
                       f"gives {computed}%."
                       + ("" if ok else " These disagree.")),
                    needs_human=not ok and computed is not None
                                and stated is not None))

    def build_patent(self) -> None:
        p = self.data["patent"]
        cited = self.source.with_partners(
            [n for n, k in self.source.kind.items()
             if self.section_of_line.get(n) in ("Bibliographic Data", "Abstract")
             and k in ("prose", "translation")])
        rec = Record(f"{self.patent_id}_patent", "patent",
                     p.get("title") or self.patent_id, "Whole patent", cited,
                     None, p.get("patent_uuid"), f"pt:{self.patent_id}")
        self.records.append(rec)
        self.note_citation(rec.record_id, cited)

        rollup = p.get("extraction_rollup") or {}
        for field, actual, name in (
                ("reaction_count", len(self.data["reactions"]), "reactions"),
                ("compound_count", len(self.data["compounds"]), "compounds"),
                ("pathway_count", len(self.data["pathways"]), "pathways")):
            stated = rollup.get(field)
            if stated is None:
                continue
            ok = int(stated) == actual
            rec.checks.append(check(
                f"completeness.{field}", "completeness",
                "pass" if ok else "fail",
                f"The patent record's count of {name}",
                f"The record states {stated}; the gold holds {actual}."
                + ("" if ok else " These disagree.")))
        # Not a grounding claim. 28.4 is the product of the eight step yields and
        # is printed nowhere in the patent, so asking whether it is on a cited line
        # would put a guaranteed false alarm at the top of the queue. Checked as
        # arithmetic instead, which is the only question there is about it.
        stated = rollup.get("best_overall_yield_pct")
        if stated is not None:
            best = max([y for y in (self.cumulative_yield(pw)
                                    for pw in self.data["pathways"])
                        if y is not None] or [None]) if self.data["pathways"] else None
            ok = best is not None and abs(best - float(stated)) <= 0.15
            rec.checks.append(check(
                "quantity.best_overall_yield", "quantity",
                "pass" if ok else ("skip" if best is None else "fail"),
                "The best overall yield is the product of the step yields",
                f"The record states {stated}%."
                + (" No route in the gold has a yield on every step, so there is "
                   "nothing to multiply." if best is None else
                   f" Multiplying the step yields of the best route gives "
                   f"{best:.1f}%."
                   + ("" if ok else " These disagree.")),
                needs_human=not ok and best is not None))

    def judgement_claim(self, rec: Record, field: str, question: str,
                        why: str, about: str = "extraction") -> dict:
        return self._claim(
            rec, field, question, "a judgement, not a number", None, None,
            rec.cited, [], "not_checkable",
            why + " No string match can settle it, so a human must read the "
                  "evidence below and decide.",
            ["The annotation flagged its own uncertainty here."], "name",
            about=about, load_bearing=True)

    # ------------------------------------------------------------ reference

    def referential_integrity(self) -> None:
        """Every name a record uses must be a record, and every record used.

        Reported both ways round, because the two failures are different bugs. A
        reaction naming a compound that does not exist is a dangling pointer and the
        scheme cannot be drawn. A compound nothing references is either a
        hallucinated molecule or a step the extraction dropped, and only a reader
        can tell which.
        """
        by_record = {r.record_id: r for r in self.records}
        known = set()
        for c in self.data["compounds"]:
            known.add(self.canon_name(c["identifier"]))
            for a in c.get("aliases") or []:
                known.add(self.canon_name(a))

        referenced_compounds: set[str] = set()
        for r in self.data["reactions"]:
            rec = by_record.get(r["id"])
            names = [c.get("identifier") for c in (r.get("compounds") or [])]
            names += r.get("reactant_names") or []
            names.append(r.get("product_name"))
            missing = sorted({n for n in names if n and
                              self.canon_name(n) not in known})
            referenced_compounds.update(self.canon_name(n) for n in names if n)
            rec.checks.append(check(
                "reference.compounds", "reference",
                "pass" if not missing else "fail",
                "Every compound this step names has a record",
                (f"All {len({n for n in names if n})} named compounds resolve to a "
                 f"compound record.") if not missing else
                (f"{len(missing)} named compounds have no record: "
                 + ", ".join(self.english_name(n) for n in missing) + "."),
                needs_human=bool(missing)))

        reaction_ids = {r["reaction_id"] for r in self.data["reactions"]}
        referenced_reactions: set[str] = set()
        for p in self.data["pathways"]:
            uuid = p.get("pathway_uuid") or ""
            rec = by_record.get(f"{self.patent_id}_pathway_{uuid}")
            steps = [st.get("reaction_id") for st in (p.get("steps") or [])]
            referenced_reactions.update(s for s in steps if s)
            missing = sorted({s for s in steps if s not in reaction_ids})
            rec.checks.append(check(
                "reference.reactions", "reference",
                "pass" if not missing else "fail",
                "Every step of this route has a reaction record",
                f"All {len(steps)} steps resolve to a reaction record."
                if not missing else
                f"{len(missing)} steps name a reaction that does not exist: "
                + ", ".join(missing) + ".",
                needs_human=bool(missing)))
            names = [(p.get("ksm") or {}).get("identifier"),
                     (p.get("product") or {}).get("identifier")]
            names += [i.get("identifier") for i in (p.get("intermediates") or [])]
            referenced_compounds.update(self.canon_name(n) for n in names if n)
            gone = sorted({n for n in names if n and
                           self.canon_name(n) not in known})
            rec.checks.append(check(
                "reference.compounds", "reference",
                "pass" if not gone else "fail",
                "Every molecule this route names has a record",
                f"All {len([n for n in names if n])} named molecules resolve."
                if not gone else
                f"{len(gone)} named molecules have no record: "
                + ", ".join(self.english_name(n) for n in gone) + ".",
                needs_human=bool(gone)))

        for c in self.data["compounds"]:
            rec = by_record[safe_record_id(self.patent_id, c["id"], c["identifier"])]
            used = self.canon_name(c["identifier"]) in referenced_compounds
            rec.checks.append(check(
                "reference.orphan", "reference", "pass" if used else "warn",
                "Some reaction or route uses this compound",
                "At least one reaction or route names it." if used else
                "No reaction and no route names this compound. It is either a "
                "molecule the annotation invented, or a step the extraction did "
                "not connect up.",
                needs_human=not used))

        for r in self.data["reactions"]:
            rec = by_record[r["id"]]
            used = r["reaction_id"] in referenced_reactions
            rec.checks.append(check(
                "reference.orphan", "reference", "pass" if used else "warn",
                "Some route uses this reaction",
                "At least one route lists it as a step." if used else
                "No route lists this reaction as a step.",
                needs_human=not used))

    # ------------------------------------------------------------ structure

    def structure_checks(self) -> None:
        """Does the drawn chemistry hold together, and does it agree with itself?

        Four questions, and only the first is about RDKit. The second compares the
        formula the vision pass WROTE DOWN beside a structure against the formula
        RDKit computes from the SMILES it read off the same drawing, which is the
        only place in this pipeline where a structure read is checked against
        anything. The third and fourth are about identity: the gold deliberately
        carries one molecule under three names, so the names must agree about the
        molecule, and two molecules that turn out to be the same one must be
        noticed rather than counted twice.
        """
        by_record = {r.record_id: r for r in self.records}
        patent_rec = by_record[f"{self.patent_id}_patent"]

        for c in self.data["compounds"]:
            rec = by_record[safe_record_id(self.patent_id, c["id"], c["identifier"])]
            entry = self.structures.get(c["identifier"]) or {}
            smiles = entry.get("smiles")
            if not smiles:
                rec.checks.append(check(
                    "structure.smiles", "structure", "skip",
                    "A 2D structure is resolved for this compound",
                    "No structure is resolved. " + (entry.get("note") or "")))
                continue
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                rec.checks.append(check(
                    "structure.smiles", "structure", "fail",
                    "The resolved SMILES parses",
                    f"RDKit cannot parse {smiles!r}.", needs_human=True))
                continue
            formula = rdMolDescriptors.CalcMolFormula(mol)
            stated = entry.get("formula")
            ok = stated is None or stated == formula
            rec.checks.append(check(
                "structure.formula", "structure", "pass" if ok else "fail",
                "The molecular formula agrees with the drawn structure",
                f"RDKit computes {formula} from the structure, molecular weight "
                f"{Descriptors.MolWt(mol):.2f}."
                + ("" if ok else f" The record states {stated}, which disagrees."),
                needs_human=not ok))

        # Formula and InChI key as the vision pass wrote them, against what RDKit
        # computes from the SMILES the same pass read off the same drawing.
        agree = disagree = unparseable = 0
        problems: list[str] = []
        for n in self.source.numbers:
            if self.source.kind[n] != "image_extract":
                continue
            for mol_entry in image_extract_molecules(self.source.lines[n]):
                smiles = mol_entry.get("smiles")
                if not smiles:
                    continue
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    unparseable += 1
                    problems.append(f"line {n}: RDKit cannot parse {smiles!r}")
                    continue
                stated = mol_entry.get("molecular_formula")
                computed = rdMolDescriptors.CalcMolFormula(mol)
                if stated and stated != computed:
                    disagree += 1
                    problems.append(f"line {n}: the span states {stated}, RDKit "
                                    f"computes {computed} from {smiles!r}")
                else:
                    agree += 1
        status = "pass" if not problems else "fail"
        patent_rec.checks.append(check(
            "structure.drawn_formula", "structure", status,
            "Every drawn structure's stated formula matches its SMILES",
            f"{agree} of {agree + disagree + unparseable} structures read off the "
            f"page drawings have a stated molecular formula that RDKit reproduces "
            f"from the SMILES read beside it."
            + ("" if not problems else " " + "; ".join(problems) + "."),
            needs_human=bool(problems)))

        # One molecule under three names: the names must agree about the molecule.
        for key, members in sorted(self.data["equivalence"].items()):
            canons = {}
            for m in members:
                e = self.structures.get(m) or {}
                if e.get("canonical"):
                    canons.setdefault(e["canonical"], []).append(m)
            for m in members:
                rec = by_record.get(f"{self.patent_id}_{ascii_key(m)}")
                if rec is None:
                    continue
                ok = len(canons) <= 1
                rec.checks.append(check(
                    "consistency.equivalence", "consistency",
                    "pass" if ok else "fail",
                    "Every spelling of this molecule resolves to one structure",
                    f"The gold spells this molecule {len(members)} ways and all "
                    f"resolved spellings give one structure."
                    if ok else
                    "The spellings of this molecule resolve to different "
                    "structures: " + "; ".join(
                        f"{', '.join(self.english_name(x) for x in v)} give "
                        f"{k}" for k, v in sorted(canons.items())) + ".",
                    needs_human=not ok))

        # Two records, one molecule, and no equivalence group saying so.
        by_canonical: dict[str, list[str]] = {}
        for c in self.data["compounds"]:
            e = self.structures.get(c["identifier"]) or {}
            if e.get("canonical"):
                by_canonical.setdefault(e["canonical"], []).append(c["identifier"])
        for canonical, idents in sorted(by_canonical.items()):
            groups = {self.canon_name(i) for i in idents}
            duplicate = len(idents) > 1 and len(groups) > 1
            for ident in idents:
                rec = by_record.get(f"{self.patent_id}_{ascii_key(ident)}")
                if rec is None:
                    continue
                others = [self.english_name(i) for i in idents if i != ident]
                rec.checks.append(check(
                    "consistency.duplicate", "consistency",
                    "warn" if duplicate else "pass",
                    "No other compound record is this same molecule",
                    "No other record resolves to this structure."
                    if not others else
                    (f"{len(others)} other records resolve to the same structure: "
                     + ", ".join(others) + ". "
                     + ("They are grouped as one substance in "
                        "provenance/compounds-equivalence.json, so this is "
                        "expected." if not duplicate else
                        "They are NOT grouped as one substance, so this may be a "
                        "duplicate record.")),
                    needs_human=duplicate))

    # ------------------------------------------------------------ drawing

    def drawing_checks(self) -> None:
        """The gold's structure for a molecule against the one read off the page.

        gold/structures.json is an INDEPENDENT reading: a vision pass looked at the
        rendered page and wrote down the substituents and their ring positions,
        without seeing the compound records. Where that reading and the gold's
        resolved structure name the same molecule and give different structures,
        one of the two is wrong, and no amount of text matching would ever find it.

        The join is on the name here, and only here, which is the opposite of what
        resolve_structures.py does and for the opposite reason. That stage joins on
        canonical SMILES because it is asking "is this molecule drawn", and a name
        join would answer no for molecules that plainly are. This check is asking
        "do the two readings of THIS NAME agree", and a SMILES join would make the
        question vacuous: it would only ever compare structures that were already
        equal. So the names are normalised hard - case, brackets, hyphens, spaces
        and the sulfonyl/sulphonyl and methanesulfonyl/methylsulfonyl spellings all
        folded - and a pair that survives that is compared.
        """
        by_record = {r.record_id: r for r in self.records}
        drawn: dict[str, dict] = {}
        for page in self.data["drawings"]:
            for struct in page.get("structures") or []:
                name, smiles = struct.get("name"), struct.get("smiles")
                if not name or not smiles:
                    continue
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    continue
                drawn.setdefault(drawing_key(name), {
                    "canonical": Chem.MolToSmiles(mol), "name": name,
                    "page": page.get("page", "?")})

        agree = disagree = 0
        for c in self.data["compounds"]:
            rec = by_record[safe_record_id(self.patent_id, c["id"],
                                           c["identifier"])]
            entry = self.structures.get(c["identifier"]) or {}
            names = [c["identifier"], *(c.get("aliases") or [])]
            hit = next((drawn[k] for k in map(drawing_key, names) if k in drawn),
                       None)
            if hit is None or not entry.get("canonical"):
                rec.checks.append(check(
                    "drawing.smiles", "drawing", "skip",
                    "The page drawing and the gold agree about this molecule",
                    "No structure drawn on any page carries this molecule's name, "
                    "so there is no second reading to compare against."
                    if hit is None else
                    "No structure is resolved for this record, so there is nothing "
                    "to compare the drawing against."))
                continue
            same = hit["canonical"] == entry["canonical"]
            agree += 1 if same else 0
            disagree += 0 if same else 1
            rec.checks.append(check(
                "drawing.smiles", "drawing", "pass" if same else "fail",
                "The page drawing and the gold agree about this molecule",
                f"The vision pass read this molecule off page {hit['page']} as "
                f"{hit['canonical']}."
                + (" The gold resolves the same structure." if same else
                   f" The gold resolves {entry['canonical']}, which is a different "
                   f"molecule. One of the two readings is wrong."),
                needs_human=not same))
        self.drawing_tally = (agree, disagree)

    # ------------------------------------------------------------ quantity

    def consistency_checks(self) -> None:
        """Mass over molar amount against the weight of the molecule named.

        The single most valuable arithmetic in this document. A row that prints both
        a mass and a mole count is an implicit claim about molecular weight, and on
        this patent several of those claims come out at the des-chloro weights. The
        tolerance and the chlorine-for-hydrogen classification are copied exactly
        from verifier/lib/checks.ts so the engine and the UI can never disagree
        about whether a row passes.
        """
        by_record = {r.record_id: r for r in self.records}
        for r in self.data["reactions"]:
            rec = by_record[r["id"]]
            rows = []
            for c in r.get("compounds") or []:
                q = c.get("quantity") or {}
                mass, mmol = q.get("mass_g"), q.get("mmol")
                if mass is None or mmol is None or mmol <= 0:
                    continue
                ident = c.get("identifier") or ""
                mw = (self.structures.get(ident) or {}).get("mw")
                status, detail, facts = mass_check(self.english_name(ident),
                                                   float(mass), float(mmol), mw)
                rows.append((ident, status, detail, facts))
            for ident, status, detail, facts in rows:
                rec.checks.append(check(
                    f"quantity.mass_mmol[{ascii_key(ident)}]", "quantity", status,
                    f"Mass and moles agree for {self.english_name(ident)}",
                    detail, needs_human=status == "fail",
                    about_fields=[f"compounds[{ascii_key(ident)}].quantity."]))

    # ------------------------------------------------------------ coverage

    # What makes an uncited line worth a reviewer's attention. Each signal is a fact
    # about the line, never a guess about its meaning, so a line that trips one can
    # be shown to a non-chemist with an English sentence saying exactly why.
    SIGNAL_LABELS_EN = {
        "quantity": "a quantity with a unit",
        "temperature": "a temperature",
        "duration": "a duration",
        "yield": "a percentage",
        "ratio": "a ratio",
        "structure": "a drawn chemical structure",
        "reagent": "the name of a compound the annotation knows",
    }

    def signals(self, n: int, reagent_names: dict[str, str]) -> list[str]:
        raw = self.source.lines[n]
        found: list[str] = []
        if self.source.kind[n] == "image_extract":
            found.append("structure")
        for tok in tokenise(raw):
            if tok.unit in ("g", "ml", "mmol"):
                found.append("quantity")
            elif tok.unit == "C":
                found.append("temperature")
            elif tok.unit == "h":
                found.append("duration")
            elif tok.unit == "%":
                found.append("yield")
        if re.search(r"\d+\s*:\s*\d+", fold(raw)):
            found.append("ratio")
        norm = self.source.norm.get(n, "")
        low = raw.lower()
        for name, needle in reagent_names.items():
            if (needle and needle in norm) or (len(name) > 6 and name in low):
                found.append("reagent")
                break
        seen, ordered = set(), []
        for s in found:
            if s not in seen:
                seen.add(s)
                ordered.append(s)
        return ordered

    def build_coverage(self) -> None:
        reagent_names: dict[str, str] = {}
        for c in self.data["compounds"]:
            for name in [c["identifier"], *(c.get("aliases") or [])]:
                if not name or looks_like_smiles(name):
                    continue
                reagent_names[name.lower()] = normalise(name) if has_chinese(name) else ""

        patent_rec = next(r for r in self.records
                          if r.record_id == f"{self.patent_id}_patent")

        self.coverage_lines: list[dict] = []
        self.uncited_chemistry: list[int] = []
        for n in self.source.numbers:
            kind = self.source.label_kind(n, self.claim_lines)
            citers = sorted(self.cited_lines.get(n, ()))
            if kind == "blank":
                status, sigs = "covered" if citers else "uncited_plain", []
            else:
                sigs = self.signals(n, reagent_names)
                if citers:
                    status = "covered"
                elif sigs:
                    status = "uncited_with_chemistry"
                    self.uncited_chemistry.append(n)
                else:
                    status = "uncited_plain"
            self.coverage_lines.append({
                "n": n,
                "kind": kind,
                "has_english": n in self.source.english
                               or kind in ("translation", "heading")
                               or not has_chinese(self.source.lines[n]),
                "text_en": self.source.text_en[n],
                "section_en": self.section_of_line.get(n, "Unassigned"),
                "cited_by": citers,
                "signals": sigs,
                "status": status,
            })

        for n in self.uncited_chemistry:
            sigs = next(l["signals"] for l in self.coverage_lines if l["n"] == n)
            # A candidate miss belongs to the patent as a whole, so its verdict
            # keys on the patent with the line number in the field. The convention
            # in verifier/lib/verdict.ts has no slot for a source line, and
            # inventing one would write verdicts that resolveRec cannot load.
            rec = Record(f"{self.patent_id}_line_{n}", "source_line",
                         f"Source line {n}",
                         self.section_of_line.get(n, "Unassigned"),
                         self.source.with_partners([n]),
                         None, None, f"pt:{self.patent_id}")
            self.records.append(rec)
            reason = ("No record in the whole annotation cites this line, and it "
                      "carries " + english_list(
                          [self.SIGNAL_LABELS_EN[s] for s in sigs])
                      + ". Either the extraction missed something here, or the "
                        "line repeats what a nearby record already captured.")
            self._claim(rec, "__coverage__",
                        f"Line {n} carries chemistry that no record cites. Did the "
                        f"annotation miss it?",
                        f"line {n}: " + self.source.text_en[n][:200], None, None,
                        rec.cited, [], "not_checkable", reason,
                        ["An uncited line carrying chemistry is a candidate miss."],
                        "name", {n}, load_bearing=True,
                        rec_field=f"__coverage__.line_{n}")


# Folded before a drawn name is compared with a record name. Every fold here is a
# spelling of the same thing in this corpus, never a chemical claim: the drawing
# pass writes "methylsulfonyl" where the records write "methanesulfonyl", and
# treating those as different names would make the check pass by never running.
_DRAWING_FOLDS = (("methanesulfon", "methylsulfon"), ("methanesulfan", "methylsulfan"),
                  ("sulphon", "sulfon"), ("sulphan", "sulfan"))


def drawing_key(name: str) -> str:
    t = name.lower()
    for a, b in _DRAWING_FOLDS:
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "", t)


def english_list(items) -> str:
    items = list(items)
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


MOLAR_RATIO = re.compile(r"\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?"
                         r"(?::\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)+")


def molar_ratios(text: str) -> list[str]:
    """The ratio itself, lifted out of the Chinese sentence that states it.

    `molar_ratio_text` is a whole Chinese clause and none of it may reach the
    artifact. The ratio inside it is ASCII, is the entire claim the field makes, and
    is exactly what a reviewer can check against the printed page, so it is lifted
    out and the sentence is left behind.
    """
    seen, out = set(), []
    for m in MOLAR_RATIO.finditer(fold(text)):
        s = re.sub(r"\s+", "", m.group(0))
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


# ---------------------------------------------------------------- the artifact

RISK_BANDS = (("high", 0.60), ("medium", 0.30), ("low", 0.0))

VERDICTS = ["not_found", "partial", "not_checkable", "found"]
CHECK_STATUSES = ["fail", "warn", "pass", "skip"]
FAMILIES = ["grounding", "reference", "structure", "drawing", "quantity",
            "consistency", "completeness"]

TIERS = [1, 2, 3]

TIER_MEANING = {
    1: "census of the suspicious: every claim the machine could not confirm",
    2: "census of the candidate misses: chemistry on a line no record cites",
    3: "what the machine matched cleanly, to be sampled rather than read",
}

# Keys the engine uses to carry a claim between passes. They are working state, not
# contract, and are stripped before the file is written so a consumer can never
# come to depend on one.
PRIVATE = ("_field_name", "_matched", "_derive", "_value", "_unit", "_subject")

# Which family a claim belongs to, for the roll-up. Everything a claim can be is a
# grounding question except the coverage sweep, which asks the opposite question.
def claim_family(claim: dict) -> str:
    if claim["field"] == "__coverage__":
        return "completeness"
    if claim["field"] in ("validation_flags", "resolved"):
        return "consistency"
    if claim["basis"] == "derived":
        return "quantity"
    return "grounding"


def band(risk: float) -> str:
    for name, floor in RISK_BANDS:
        if risk >= floor:
            return name
    return "low"


def generated_at() -> str:
    """Now, in UTC, or the pinned time SOURCE_DATE_EPOCH names.

    The contract asks for a real timestamp and also for two runs to diff to nothing.
    Those pull against each other, so the timestamp is honest by default and
    pinnable when a diff is what is wanted. Nothing else in the file moves.
    """
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    when = (datetime.fromtimestamp(int(epoch), tz=timezone.utc) if epoch
            else datetime.now(timezone.utc))
    return when.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def assemble(run: Run) -> dict:
    records = []
    for rec in run.records:
        risk = max([c["risk"] for c in rec.claims] or [0.0])
        if any(c["status"] == "fail" for c in rec.checks):
            risk = max(risk, 0.8)
        elif any(c["status"] == "warn" for c in rec.checks):
            risk = max(risk, 0.4)
        records.append({
            "record_id": rec.record_id,
            "record_kind": rec.kind,
            "uuid": rec.uuid,
            "rec": rec.rec,
            "stratum": rec.stratum,
            "annotation_flags_en": [FLAG_MEANING_EN.get(f, f)
                                    for f in sorted(rec.flags)],
            "label_en": rec.label_en,
            "section_en": rec.section_en,
            "cited_lines": rec.cited,
            "claim_ids": [c["claim_id"] for c in rec.claims],
            "checks": rec.checks,
            "risk": round(risk, 2),
            "risk_band": band(risk),
        })

    # Highest risk first, then by source position, then by id. Every key is a
    # function of the inputs, so the order is stable across runs and a diff between
    # two artifacts is a diff in the data.
    claims = sorted(run.claims,
                    key=lambda c: (c["tier"], -c["risk"],
                                   min(c["cited_lines"]) if c["cited_lines"] else 10**6,
                                   c["record_id"], c["field"]))
    for c in claims:
        for k in PRIVATE:
            c.pop(k, None)

    verdicts = {v: sum(1 for c in claims if c["auto"] == v) for v in VERDICTS}
    families = {f: sum(1 for c in claims if claim_family(c) == f) for f in FAMILIES}
    tiers = {str(t): sum(1 for c in claims if c["tier"] == t) for t in TIERS}
    # The denominators ui-report needs. A stratified sample cannot be drawn, and a
    # confidence bound cannot be computed, from a filtered list: both need the
    # population size of every stratum, including the ones that end up with no
    # sampled claim at all.
    strata: dict[str, int] = {}
    for c in claims:
        if c["tier"] == 3:
            strata[c["stratum"]] = strata.get(c["stratum"], 0) + 1
    about = {a: sum(1 for c in claims if c["about"] == a)
             for a in ("extraction", "patent")}
    all_checks = [c for r in records for c in r["checks"]]
    statuses = {s: sum(1 for c in all_checks if c["status"] == s)
                for s in CHECK_STATUSES}
    check_families = {f: sum(1 for c in all_checks if c["family"] == f)
                      for f in FAMILIES}

    cov = run.coverage_lines
    cov_summary = {
        "total": len(cov),
        "covered": sum(1 for l in cov if l["status"] == "covered"),
        "uncited_with_chemistry": sum(1 for l in cov
                                      if l["status"] == "uncited_with_chemistry"),
        "uncited_plain": sum(1 for l in cov if l["status"] == "uncited_plain"),
    }

    by_section = []
    for label in run.section_order:
        sec_claims = [c for c in claims if c["section_en"] == label]
        sec_records = [r for r in records if r["section_en"] == label]
        by_section.append({
            "section_en": label,
            "records": len(sec_records),
            "claims": len(sec_claims),
            "found": sum(1 for c in sec_claims if c["auto"] == "found"),
            "partial": sum(1 for c in sec_claims if c["auto"] == "partial"),
            "not_found": sum(1 for c in sec_claims if c["auto"] == "not_found"),
            "not_checkable": sum(1 for c in sec_claims
                                 if c["auto"] == "not_checkable"),
            "uncited_chemistry_lines": sum(
                1 for l in cov if l["section_en"] == label
                and l["status"] == "uncited_with_chemistry"),
        })

    grounding = [c for c in claims if claim_family(c) == "grounding"]
    checkable = [c for c in grounding if c["auto"] != "not_checkable"]
    grounded_pct = (round(100.0 * sum(1 for c in checkable
                                      if c["auto"] == "found") / len(checkable), 1)
                    if checkable else 0.0)
    lines_worth_citing = [l for l in cov if l["kind"] not in ("blank",)]
    covered_pct = (round(100.0 * sum(1 for l in lines_worth_citing
                                     if l["status"] == "covered")
                         / len(lines_worth_citing), 1)
                   if lines_worth_citing else 0.0)
    resolved = sum(1 for e in run.data["structures"] if e.get("formula"))
    structure_pct = (round(100.0 * resolved / len(run.data["structures"]), 1)
                     if run.data["structures"] else 0.0)

    not_found = [c for c in grounding if c["auto"] == "not_found"]
    failing = [c for c in all_checks if c["status"] == "fail"]

    blocking = []
    for c in not_found[:20]:
        blocking.append(f"{c['record_label_en']} - {c['field_label_en']}: "
                        f"{c['auto_reason_en']}")
    for c in failing[:20]:
        blocking.append(f"{c['title_en']}: {c['detail_en']}")

    verdict = (
        f"{len(claims)} claims were put to the source. "
        f"{verdicts['found']} were found on the lines the annotation itself cites, "
        f"{verdicts['partial']} were only partly found, "
        f"{verdicts['not_found']} were NOT found and are the ones to read first, "
        f"and {verdicts['not_checkable']} are judgements no string match can "
        f"settle. Of the {len(checkable)} grounding claims a machine can decide, "
        f"{grounded_pct}% are grounded. "
        f"{cov_summary['uncited_with_chemistry']} source lines carry chemistry that "
        f"no record cites, and each has its own entry in the queue. "
        f"{statuses['fail']} record checks fail and {statuses['warn']} warn. "
        f"{resolved} of {len(run.data['structures'])} compound identifiers resolve "
        f"to a drawable structure. "
        + ("Nothing here is a verdict: every line is a prompt for a human to agree "
           "or overrule."))

    return {
        "patent_id": run.patent_id,
        "engine_version": ENGINE_VERSION,
        "generated_at": generated_at(),
        "source": {
            "file": str(run.source.path.relative_to(HERE)),
            "sha256": run.source.sha256,
            "line_count": len(run.source.lines),
        },
        "summary": {
            "records": {
                "total": len([r for r in records
                              if r["record_kind"] != "source_line"]),
                "compound": sum(1 for r in records
                                if r["record_kind"] == "compound"),
                "reaction": sum(1 for r in records
                                if r["record_kind"] == "reaction"),
                "pathway": sum(1 for r in records if r["record_kind"] == "pathway"),
                "patent": sum(1 for r in records if r["record_kind"] == "patent"),
                "source_line": sum(1 for r in records
                                   if r["record_kind"] == "source_line"),
            },
            "claims": {"total": len(claims),
                       "needs_human": sum(1 for c in claims if c["needs_human"]),
                       **verdicts},
            "claims_by_family": families,
            "claims_by_tier": tiers,
            "tier3_population_by_stratum": dict(sorted(strata.items())),
            "claims_by_subject": about,
            "field_basis": {k: dict(sorted(v.items()))
                            for k, v in sorted(run.bases.items())},
            "agreement_with_annotation": {
                k: len(v) for k, v in sorted(run.agreement.items())},
            "checks": {"total": len(all_checks), **statuses},
            "checks_by_family": check_families,
            "source_coverage": cov_summary,
            "grounding_failed": bool(not_found),
        },
        "claims": claims,
        "records": records,
        "source_coverage": {"lines": cov, "summary": cov_summary},
        "completeness": {
            "score": {"grounded_pct": grounded_pct,
                      "covered_pct": covered_pct,
                      "structure_pct": structure_pct},
            "verdict_en": verdict,
            "blocking_en": blocking,
            "by_section": by_section,
        },
    }


# ---------------------------------------------------------------- the gate

def chinese_runs(text: str) -> list[str]:
    return re.findall(CJK.pattern + "+", text)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    patent_id = args[0] if args else DEFAULT_PATENT_ID

    data = load_inputs(patent_id)
    run = Run(patent_id, data)
    run.build()
    artifact = assemble(run)

    body = json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    # The one gate that is not about the patent at all. Every string in this file
    # reaches a screen belonging to a reader who has no Chinese, so a single Han
    # character surviving into it is a defect in this stage and not a finding about
    # the annotation. Checked on the bytes actually about to be written, never on
    # the intent.
    leaked = chinese_runs(body)
    if leaked:
        die(f"{len(leaked)} runs of Chinese survived into the artifact, which is "
            f"unreadable for the reviewer this file exists for: "
            + ", ".join(sorted(set(leaked))[:20]))

    out_dir = REL / "verification"
    out_path = out_dir / f"checks-{patent_id}.json"
    if not check_only:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(body, encoding="utf-8")

    return report(run, artifact, out_path, check_only)


def report(run: Run, artifact: dict, out_path: Path, check_only: bool) -> int:
    s = artifact["summary"]
    cov = s["source_coverage"]
    claims = artifact["claims"]

    print(f"patent    : {run.patent_id}")
    print(f"source    : {artifact['source']['line_count']} lines, "
          f"{artifact['source']['file']}")
    print(f"            sha256 {artifact['source']['sha256'][:16]}")
    print(f"            {sum(1 for v in run.source.pairing.values() if v == 'exact')}"
          f" Chinese lines pair one-for-one with their English, "
          f"{sum(1 for v in run.source.pairing.values() if v == 'approximate')}"
          f" had to be clamped, "
          f"{sum(1 for v in run.source.pairing.values() if v == 'none')}"
          f" have no English at all")
    print(f"gold      : {s['records']['compound']} compounds, "
          f"{s['records']['reaction']} reactions, {s['records']['pathway']} "
          f"pathways, {s['records']['patent']} patent record "
          f"= {s['records']['total']} records")
    print()

    # Which numeric fields this patent QUOTES and which it DERIVES, inferred from
    # the data. Printed so a human can sanity-check the inference rather than
    # trusting it: getting this wrong in one direction fills the queue with false
    # alarms and in the other hides real ones.
    print("numeric fields, quoted or derived (measured, not declared):")
    for name, t in artifact["summary"]["field_basis"].items():
        print(f"  {name:20} {t['matched']:4}/{t['total']:<4} printed on a cited "
              f"line   {t['basis']}")
    print()

    print(f"{s['claims']['total']} claims put to the source:")
    for v in VERDICTS:
        print(f"  {v:14} {s['claims'][v]:5}   {VERDICT_MEANING[v]}")
    print(f"  {'needs_human':14} {s['claims']['needs_human']:5}   "
          f"the review queue")
    print()
    print("the three review queues (REVIEW-PROTOCOL.md):")
    for t in TIERS:
        print(f"  tier {t}        {s['claims_by_tier'][str(t)]:5}   {TIER_MEANING[t]}")
    print(f"\n  tier 3 population by stratum, which is what a proportional sample "
          f"needs:")
    for k, v in list(s["tier3_population_by_stratum"].items()):
        print(f"    {k:52} {v:4}")
    print()
    print(f"what each claim is ABOUT: {s['claims_by_subject']['extraction']} ask "
          f"whether the annotation is right,")
    print(f"                          {s['claims_by_subject']['patent']} ask "
          f"whether the PATENT is defective and we recorded that correctly")
    print()

    print(f"{s['checks']['total']} record checks:")
    for st in CHECK_STATUSES:
        print(f"  {st:14} {s['checks'][st]:5}")
    for f in FAMILIES:
        if s["checks_by_family"].get(f):
            print(f"    {f:12} {s['checks_by_family'][f]:5}   {FAMILY_MEANING[f]}")
    print()

    # This stage grading itself against the annotator who went first.
    a = run.agreement
    print("mass-and-moles arithmetic against the annotation's own flags:")
    print(f"  both flag it              {len(a['both']):4}   high confidence, the "
          f"annotator was already awake here")
    print(f"  this stage only           {len(a['machine_only']):4}   either a real "
          f"defect the annotation missed, or this check is too aggressive")
    for label in a["machine_only"]:
        print(f"      {label}")
    print(f"  the annotation only       {len(a['annotation_only']):4}   this "
          f"stage's coverage ends here")
    for label in a["annotation_only"]:
        print(f"      {label}")
    print()

    agree, disagree = getattr(run, "drawing_tally", (0, 0))
    print(f"drawn structure against gold structure: {agree} agree, "
          f"{disagree} disagree, over the names that appear in both")
    print()

    print(f"source coverage over {cov['total']} numbered lines:")
    print(f"  covered                  {cov['covered']:5}   at least one record "
          f"cites the line")
    print(f"  uncited, chemistry       {cov['uncited_with_chemistry']:5}   "
          f"candidate misses, each one a claim in tier 2")
    print(f"  uncited, plain           {cov['uncited_plain']:5}   nothing on the "
          f"line for a record to hold")
    if run.uncited_chemistry:
        print("  " + compact_lines(run.uncited_chemistry))
    else:
        print("  Tier 2 is a complete and EMPTY census: every line of this patent "
              "carrying a\n  quantity, a temperature, a duration, a yield, a ratio "
              "or a drawn structure is\n  cited by some record. That is a result, "
              "not a check that did not run.")
    print()

    score = artifact["completeness"]["score"]
    print(f"grounded {score['grounded_pct']}%   covered {score['covered_pct']}%   "
          f"structures {score['structure_pct']}%")
    print()

    if not check_only:
        print(f"wrote {out_path.relative_to(HERE)} "
              f"({out_path.stat().st_size / 1024:.0f} kB)")
    else:
        print("--check: nothing written")

    failed = [c for c in claims
              if claim_family(c) == "grounding" and c["auto"] == "not_found"]
    if not failed:
        print(f"\ngrounding gate: every checkable number and quote is on a line "
              f"its own record cites. PASS")
        return 0

    print(f"\ngrounding gate: {len(failed)} claims are NOT on the lines their own "
          f"record cites. FAIL")
    print("\n  Read these first. Each is either a value the annotation invented, "
          "or a\n  citation pointing at the wrong line. Both are defects, and only "
          "a reader\n  of the patent can say which:\n")
    for c in failed[:40]:
        print(f"    {c['record_label_en']}")
        print(f"      {c['field']} = {c['claimed_en'][:90]}")
        print(f"      {c['auto_reason_en']}")
    if len(failed) > 40:
        print(f"    ... and {len(failed) - 40} more, all in "
              f"{out_path.name} under claims[] with auto = not_found")
    print(f"\n  The full queue is claims[] in {out_path.relative_to(HERE)}, "
          f"ordered by tier\n  then by risk. Work tier 1 first: it is a census and "
          f"it is meant to be finished.")
    return 1


VERDICT_MEANING = {
    "found": "the value is on a line the record cites. Bulk-acceptable",
    "partial": "some of it is there. Needs a human",
    "not_found": "it is NOT there. The hallucination signal",
    "not_checkable": "a judgement no string match can settle",
}

FAMILY_MEANING = {
    "grounding": "a number or a quote against the lines it cites",
    "reference": "a name pointing at a record that does not exist",
    "structure": "a SMILES or a formula that does not hold",
    "drawing": "the page drawing against the gold's structure for one molecule",
    "quantity": "mass and moles against the molecular weight",
    "consistency": "the annotation against itself",
    "completeness": "a source line no record cites",
}


if __name__ == "__main__":
    raise SystemExit(main())
