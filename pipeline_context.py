#!/usr/bin/env python3
"""One place the pipeline works out which patent it is running on.

Every stage used to carry the literal string "CN104292137A" somewhere: in an output
filename, in a document heading, in a diagram title, in a module constant. Running
the pack on a second patent therefore produced files named after the first one and
diagrams that claimed, in print, to be about it. Nothing said so.

This module removes the guess. The id comes from, in order:

  1. --patent-id X  or  --patent-id=X  on the command line
  2. the first bare positional argument, which is how resolve_structures.py and
     resolve_translations.py have always taken it
  3. $ANNOTATION_PATENT_ID
  4. discovery: the one input/<id>-biblio.json in the pack

Discovery is last and deliberately refuses to choose when there is more than one
candidate. A pack holding two patents that silently picked one would reintroduce
exactly the failure this module exists to remove.

`facts()` is the second half of the job. A diagram that says "9 scanned pages" or
"page 6 carries the whole route" is as patent-specific as the id is, so those
numbers are counted from the run rather than typed into the source.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE / "input"
OUTPUT = HERE / "output"


class ContextError(RuntimeError):
    """The pipeline cannot tell which patent it is running on."""


# ---------------------------------------------------------------- the id

def discover_patent_id() -> str:
    """The one patent this pack holds, from the biblio file that names it."""
    cands = sorted(p.name[: -len("-biblio.json")] for p in INPUT.glob("*-biblio.json"))
    if len(cands) == 1:
        return cands[0]
    if not cands:
        raise ContextError(
            f"no patent id given and no input/*-biblio.json to discover one from.\n"
            f"  Pass --patent-id <ID> and add input/<ID>-biblio.json.")
    raise ContextError(
        f"no patent id given and input/ holds {len(cands)}: {', '.join(cands)}.\n"
        f"  Pass --patent-id <ID> to say which one.")


def resolve_patent_id(argv: list[str] | None = None, *, required: bool = True) -> str:
    """Patent id for this process. See the module docstring for the order."""
    args = list(sys.argv[1:] if argv is None else argv)
    for i, a in enumerate(args):
        if a == "--patent-id" and i + 1 < len(args):
            return args[i + 1]
        if a.startswith("--patent-id="):
            return a.split("=", 1)[1]
    for a in args:
        if not a.startswith("-"):
            return a
    env = os.environ.get("ANNOTATION_PATENT_ID")
    if env:
        return env
    if not required:
        return ""
    return discover_patent_id()


def strip_patent_args(argv: list[str]) -> list[str]:
    """`argv` with the --patent-id pair removed, for scripts that parse the rest."""
    out, skip = [], False
    for i, a in enumerate(argv):
        if skip:
            skip = False
            continue
        if a == "--patent-id":
            skip = True
            continue
        if a.startswith("--patent-id="):
            continue
        out.append(a)
    return out


# ---------------------------------------------------------------- paths

def biblio_path(patent_id: str) -> Path:
    return INPUT / f"{patent_id}-biblio.json"


def enriched_path(patent_id: str) -> Path:
    return INPUT / f"{patent_id}-enriched.md"


def enriched_numbered_path(patent_id: str) -> Path:
    return INPUT / f"{patent_id}-enriched-numbered.md"


def load_biblio(patent_id: str) -> dict:
    p = biblio_path(patent_id)
    if not p.exists():
        raise ContextError(f"{p} not found. Every run needs the bibliographic record.")
    b = json.loads(p.read_text(encoding="utf-8"))
    if b.get("patent_id") and b["patent_id"] != patent_id:
        raise ContextError(
            f"{p.name} carries patent_id {b['patent_id']!r}, this run is {patent_id!r}")
    return b


# ---------------------------------------------------------------- counted facts

def _json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def facts(patent_id: str) -> dict:
    """Numbers the diagrams need, counted from the run rather than typed in.

    Everything here degrades to None rather than raising: the diagram stage runs
    late enough that all of it exists, but make_svgs.py is also run by hand while
    iterating on a figure, and a missing pathways.json should soften a caption, not
    stop the drawing.
    """
    vision = sorted((INPUT / "vision").glob("p*.json"))
    enriched = enriched_path(patent_id)
    b = _json(biblio_path(patent_id)) or {}

    # The page that carries the most drawn structures is the scheme page. On this
    # patent that is page 6, which m1 and m5 both name; on another patent it will
    # not be, and a caption naming the wrong page is worse than no caption.
    scheme_page, scheme_count = None, 0
    drawings = _json(OUTPUT / "structures.json") or []
    per_page: dict[str, int] = {}
    for d in drawings if isinstance(drawings, list) else []:
        page = str(d.get("page") or "")
        per_page[page] = per_page.get(page, 0) + len(d.get("structures") or [])
    if per_page:
        scheme_page, scheme_count = max(per_page.items(), key=lambda kv: (kv[1], kv[0]))

    return {
        "patent_id": patent_id,
        "family_id": b.get("family_id"),
        "title_en": b.get("title_en"),
        "jurisdiction": b.get("jurisdiction"),
        "assignee": ((b.get("assignees") or [{}])[0]).get("name"),
        "page_count": len(vision) or None,
        "source_kb": round(enriched.stat().st_size / 1024) if enriched.exists() else None,
        "scheme_page": _page_number(scheme_page),
        "scheme_page_structures": scheme_count or None,
    }


def _page_number(stem: str | None) -> int | None:
    if not stem:
        return None
    m = re.search(r"(\d+)", stem)
    return int(m.group(1)) if m else None


def route(patent_id: str) -> dict | None:
    """The longest pathway in the gold, flattened for a route diagram.

    Read from pathways.json and reactions.json so a patent nobody has hand-drawn a
    route for still gets one. Returns None when the gold is not there yet.
    """
    pws = _json(OUTPUT / "pathways.json")
    rxns = _json(OUTPUT / "reactions.json")
    if not pws or not rxns:
        return None
    by_uuid = {r.get("reaction_uuid"): r for r in rxns}
    by_rid = {r.get("reaction_id"): r for r in rxns}
    # Prefer the patent-scope pathway that actually carries a cumulative yield: it is
    # the one the annotation is prepared to stand behind end to end.
    best = max(pws, key=lambda p: (p.get("scope") == "patent",
                                   p.get("overall_yield_pct") is not None,
                                   len(p.get("steps") or [])))
    steps = []
    for i, s in enumerate(best.get("steps") or [], 1):
        r = by_uuid.get(s.get("reaction_uuid")) or by_rid.get(s.get("reaction_id")) or {}
        steps.append({
            "n": str(i),
            "transformation": (r.get("named_reaction")
                               or (r.get("reaction_class") or "step").replace("_", " ")),
            "conditions": _condition_line(r),
            "yield_pct": r.get("product_yield_pct") if r.get("product_yield_pct") is not None
                         else s.get("yield_pct"),
            "one_pot": bool(r.get("is_one_pot")),
            "flagged": bool(r.get("validation_flags")),
        })
    return {
        "scope": best.get("scope"),
        "section": best.get("section_label"),
        "ksm": (best.get("ksm") or {}).get("identifier"),
        "product": (best.get("product") or {}).get("identifier"),
        "overall_yield_pct": best.get("overall_yield_pct"),
        "steps": steps,
    }


def _condition_line(r: dict) -> str:
    """A short, readable condition string from a ReactionRecord."""
    c = r.get("conditions") or {}
    bits = []
    reagents = [x.get("identifier") for x in (r.get("compounds") or [])
                if x.get("role") in ("reagent", "catalyst", "base", "acid", "oxidant",
                                     "reductant") and x.get("identifier")]
    bits += reagents[:2]
    solvent = next((x.get("identifier") for x in (r.get("compounds") or [])
                    if x.get("role") == "solvent" and x.get("identifier")), None)
    if solvent:
        bits.append(solvent)
    t = c.get("temperature") or {}
    for k in ("value_c", "min_c"):
        if t.get(k) is not None:
            bits.append(f"{t[k]:g} C")
            break
    # Two wrapped lines at the size m2 draws conditions, and no more: a third line
    # runs into the yield and the flag marker along the bottom of the step box, and
    # make_svgs.py's collision checker fails the whole figure for it.
    line = ", ".join(bits)
    return line if len(line) <= 52 else line[:49].rstrip(" ,") + "..."


def gold_counts(patent_id: str) -> dict:
    """Record counts for a summary figure, read from the gold rather than typed in.

    make_approach.py used to print "75 compounds / 33 reactions / 18 structures"
    as literals, so the poster kept asserting the first patent's numbers over the
    second patent's data. Every value here degrades to None when its artifact is
    not there yet.
    """
    def n(path):
        d = _json(OUTPUT / path)
        return len(d) if isinstance(d, list) else None

    drawings = _json(OUTPUT / "structures.json")
    rxns = _json(OUTPUT / "reactions.json") or []
    r = route(patent_id) or {}
    return {
        "compounds": n("compounds.json"),
        "reactions": n("reactions.json"),
        "pathways": n("pathways.json"),
        "patents": 1 if (OUTPUT / "patent.json").exists() else None,
        "drawn_structures": (sum(len(d.get("structures") or []) for d in drawings)
                             if isinstance(drawings, list) else None),
        "flagged_reactions": sum(1 for x in rxns if x.get("validation_flags")) or None,
        "audits": len(list((OUTPUT / "stages" / "A5-verify").glob("*.json"))) or None,
        "overall_yield_pct": r.get("overall_yield_pct"),
    }


# The office that published the scan, for a caption. Not authoritative and not used
# for anything but a label; an unknown jurisdiction gets the generic word.
PATENT_OFFICES = {"cn": "CNIPA", "us": "USPTO", "ep": "EPO", "jp": "JPO",
                  "kr": "KIPO", "wo": "WIPO", "gb": "UKIPO", "in": "IPO"}


def patent_office(jurisdiction: str | None) -> str:
    return PATENT_OFFICES.get((jurisdiction or "").lower(), "patent office")
