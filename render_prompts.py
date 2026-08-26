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

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "prompts"
RENDERED = HERE / "output" / "prompts"


def fields(patent_id: str) -> dict[str, str | None]:
    """The allowlist. Everything else in a prompt stays a placeholder."""
    try:
        b = ctx.load_biblio(patent_id)
    except ctx.ContextError:
        b = {}
    pages = sorted((HERE / "input" / "pages").glob("*.png"))
    return {
        "PATENT_ID": patent_id,
        "TITLE_ZH": b.get("title_zh"),
        "TITLE_EN": b.get("title_en"),
        "PAGE_COUNT": str(len(pages)) if pages else None,
        "PATENT_OFFICE": ctx.patent_office(b.get("jurisdiction")) if b else None,
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
        print(f"  {len(written)} prompt(s) -> {RENDERED.relative_to(HERE)}/{patent_id}/")
        if unfilled:
            print(f"  left as placeholders, not in this pack's biblio: "
                  f"{', '.join(sorted(unfilled))}")
        for name in stale:
            print(f"  WARNING  {name} still names a patent that is not {patent_id}")

    return written, sorted(unfilled)


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
