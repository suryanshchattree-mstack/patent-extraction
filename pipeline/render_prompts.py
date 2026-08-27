#!/usr/bin/env python3
"""Render the annotation prompts for the patent actually being run.

Why this exists
---------------
`pipeline_context.py` removed the literal patent id from every script. It could not
remove it from `prompts/`, because a prompt is read by an agent, not imported by a
process. So the id survived there, in the one place where it does the most damage.

The chain was this. Run the pipeline on a second patent and it stops, correctly,
saying pass A1 has not been run and `prompts/A1-compounds.md` is the prompt that
produces it. That prompt then said, in its own Input block:

    PATENT_ID: `CN104292137A`

and showed an output example whose every record carried `"patent_id":
"CN104292137A"`. An agent following it faithfully stamps the first patent's id into
the second patent's gold. Nothing downstream objects: `finalise.py` builds ids from
`(patent_id, identifier)`, so the compound ids, the reaction ids and the uuids all
come out internally consistent and all belong to the wrong patent. The gold set then
joins cleanly against the wrong document.

That is worse than a crash. A crash is a message; this is a deliverable.

What it does
------------
Substitutes an allowlist of fields into `prompts/*.md` and writes the result to
`output/prompts/<patent-id>/`. The runner points a human at those rendered copies
rather than at the templates.

Only the allowlist is substituted. `{SECTION_TEXT}`, `{CLAIMS_TEXT}`, `{ABSTRACT}`
and the rest are filled per call by whoever runs the pass, and are deliberately left
standing: this is a `str.replace` over known tokens and not `str.format`, which
would consume them.

A field that cannot be filled is left as its own placeholder and reported, rather
than being replaced with an empty string. An unfilled `{TITLE_ZH}` is visible to the
agent reading it; a silently blank title is not.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pipeline_context as ctx

from pipeline_context import RUN_ROOT, shown
HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "prompts"
RENDERED = RUN_ROOT / "output" / "prompts"


def text_layer(patent_id: str) -> str | None:
    """One measured sentence about whether this PDF carries extractable text.

    The V prompt used to assert, as fact, that the patent "has no text layer at all".
    That was true of the patent this pack was built on and was carried forward as
    prose with a new id stamped on it. A CNIPA scan usually has no text layer; a US or
    EP patent is usually born digital and carries its full text. On one of those the
    rendered prompt would have told an agent to read pixels because the text is
    unavailable, while the text was right there, and the stated reason for the whole
    pass would have been a false statement inside the instruction being followed.

    So it is counted rather than asserted. Absent a PDF this returns None and the
    placeholder stays visible, which is the honest answer before the PDF arrives.
    """
    pdfs = sorted((RUN_ROOT / "input" / "pdf").glob(f"{patent_id}.pdf")) \
        or sorted((RUN_ROOT / "input" / "pdf").glob("*.pdf"))
    if not pdfs:
        return None
    try:
        import pymupdf
    except ImportError:
        return None
    try:
        with pymupdf.open(pdfs[0]) as doc:
            chars = sum(len(p.get_text().strip()) for p in doc)
            pages = doc.page_count
    except Exception:
        return None

    if chars == 0:
        return (f"It exists because {patent_id} has **no text layer at all** - all "
                f"{pages} pages are scanned images, measured at 0 characters of "
                f"extractable text - and because")
    return (f"{patent_id} does carry a text layer, {chars:,} characters across "
            f"{pages} pages, so the prose can be read without this pass. It runs "
            f"anyway because")


def fields(patent_id: str) -> dict[str, str | None]:
    """The allowlist. Everything else in a prompt stays a placeholder."""
    try:
        b = ctx.load_biblio(patent_id)
    except ctx.ContextError:
        b = {}
    pages = sorted((RUN_ROOT / "input" / "pages").glob("*.png"))
    return {
        "PATENT_ID": patent_id,
        "TITLE_ZH": b.get("title_zh"),
        "TITLE_EN": b.get("title_en"),
        "PAGE_COUNT": str(len(pages)) if pages else None,
        "PATENT_OFFICE": ctx.patent_office(b.get("jurisdiction")) if b else None,
        "TEXT_LAYER": text_layer(patent_id),
    }


# Placeholders the pass itself fills, one per call. Rendering leaves them standing on
# purpose; this table exists so the operator is told that at the moment the prompts
# appear, rather than discovering it when A1 asks for a {SECTION_TEXT} nobody
# mentioned. Anything not listed here falls back to a generic line.
FILLED_PER_CALL = {
    "SECTION_LABEL": "from the A0 section map, one call per section",
    "SECTION_TYPE": "from the A0 section map",
    "SECTION_TEXT": "the lines of that section, from input/<id>-enriched-numbered.md",
    "START_LINE": "from the A0 section map",
    "END_LINE": "from the A0 section map",
    "TOTAL_LINES": "line count of input/<id>-enriched-numbered.md",
    "NUMBERED_TEXT": "the whole of input/<id>-enriched-numbered.md",
    "ESTIMATED_STEPS": "from the A0 section map",
    "PRIOR_REGISTRY": "the compounds A1 has already emitted, to keep ids stable",
    "ABSTRACT": "from input/<id>-biblio.json, field abstract_zh",
    "CLAIMS_TEXT": "the claims section, located by the A0 section map",
    "CHEMISTRY_ROLLUP": "output/chemistry-rollup.json, written by merge_stages.py",
    "COMPOUNDS_JSON": "output/compounds.json",
    "REACTIONS_JSON": "output/reactions.json",
    "PROVENANCE_JSON": "the matching *-provenance.json for the artifact under audit",
    "ARTIFACT_NAME": "the artifact being audited, one A5 call each",
    "ARTIFACT_JSON": "that artifact's JSON",
}


def render(patent_id: str, *, quiet: bool = False) -> tuple[list[Path], list[str]]:
    """Write every prompt with this patent's fields in it.

    Returns the files written and the names of any allowlisted field that some
    prompt asked for and this pack could not supply.
    """
    if not TEMPLATES.is_dir():
        raise ctx.ContextError(f"{TEMPLATES} not found; there are no prompts to render.")

    values = fields(patent_id)
    out_dir = RENDERED / patent_id
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    unfilled: set[str] = set()

    for src in sorted(TEMPLATES.glob("*.md")):
        text = src.read_text(encoding="utf-8")
        for name, value in values.items():
            token = "{" + name + "}"
            if token not in text:
                continue
            if value is None:
                unfilled.add(name)
                continue
            text = text.replace(token, value)
        dst = out_dir / src.name
        # Byte-compare before writing so a re-run does not restamp mtimes and make
        # every downstream staleness check think the prompts changed.
        if not dst.exists() or dst.read_text(encoding="utf-8") != text:
            dst.write_text(text, encoding="utf-8")
        written.append(dst)

    # A template that still names a patent id after rendering is a template someone
    # added a literal back into. Say so; do not quietly ship it.
    stale = [p.name for p in written
             if patent_id not in (t := p.read_text(encoding="utf-8"))
             and _looks_like_a_patent_id_other_than(t, patent_id)]

    if not quiet:
        print(f"  {len(written)} prompt(s) -> {shown(RENDERED)}/{patent_id}/")
        if unfilled:
            print(f"  left as placeholders, this pack cannot supply them yet: "
                  f"{', '.join(sorted(unfilled))}")
        for name in stale:
            print(f"  WARNING  {name} still names a patent that is not {patent_id}")
        report_per_call(written)

    return written, sorted(unfilled)


def report_per_call(written: list[Path]) -> None:
    """Say which placeholders the pass still has to fill, and where each comes from.

    A rendered prompt is still a template. Seventeen placeholders survive rendering on
    purpose, because they are per-call values: A1 runs once per section and gets a
    different {SECTION_TEXT} each time. That is documented in this module's docstring,
    which is a file nobody running the pipeline has any reason to open. Printing it
    here puts it in front of the operator at the moment the prompts appear.
    """
    import re
    per_file: dict[str, list[str]] = {}
    for p in written:
        names = sorted(set(re.findall(r"\{([A-Z][A-Z_]*)\}", p.read_text(encoding="utf-8"))))
        if names:
            per_file[p.name] = names
    if not per_file:
        return
    print("\n  These prompts are templates still. Each pass fills the rest per call:")
    for name, names in sorted(per_file.items()):
        print(f"    {name}")
        for n in names:
            print(f"      {{{n}}}  {FILLED_PER_CALL.get(n, 'supplied by whoever runs the pass')}")


def _looks_like_a_patent_id_other_than(text: str, patent_id: str) -> bool:
    import re
    for m in re.finditer(r"\b(?:CN|US|EP|JP|KR|WO|GB|IN)\d{6,}[A-Z]?\d?\b", text):
        if m.group(0) != patent_id:
            return True
    return False


def main() -> int:
    try:
        pid = ctx.resolve_patent_id()
        render(pid)
    except ctx.ContextError as e:
        print(f"FAIL  {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
