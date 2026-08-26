#!/usr/bin/env python3
"""One entry point for everything deterministic in this pack.

    python3 run_pipeline.py --patent-id CN104292137A

Why this exists
---------------
The annotation passes A0 to A5 produce the gold. Everything that makes the gold
usable - the structures, the translations, the diagrams, the deliverable tree, the
verification file the reviewer UI reads - was a series of scripts run by hand, in an
order held in one person's head. Run patent number two and you got the gold and
nothing else, and nothing said so. This is that order, written down and executed.

What it does NOT do
-------------------
It does not run A0 to A5. Those need an agent with the prompts and the page images,
not a subprocess. What it does instead is check whether their output is there and,
if it is not, print exactly which pass is missing, which prompt produces it and
where the result must land - then stop, before it has half-built anything.

Stages
------
Every stage declares its inputs and its outputs, so:

  - a stage whose outputs are all newer than all its inputs is skipped
  - `--from <stage>` starts there and runs everything after
  - `--only <stage>` runs exactly one
  - `--force` runs everything regardless
  - the plan is printed before anything executes, always

Gates
-----
`resolve_structures.py` and `resolve_translations.py` each exit non-zero when
something a human has to supply is missing: a structure for a molecule that carries
chemistry, an English form for a Chinese string that can reach a screen. Those are
not failures to route around. The runner stops on them, reprints what the stage
asked for, and exits non-zero itself.

Manifest
--------
The last stage writes `output/relevant_output/manifest.json`: every artifact, the
stage that produced it, its sha256 and size, and the sha256 of every input it was
built from. That is what lets a consumer ask "are these assets current for this
gold" and get an answer that is not a guess about file times.

Deliberately no timestamp anywhere in the manifest: the run has to be idempotent
down to the byte, and a `generated_at` field would make every second run a diff.

Exit codes
----------
    0  everything ran or was already current
    1  a stage failed
    2  a coverage gate stopped the run; a human owes the pipeline something
    3  the LLM annotation passes have not been run yet
    4  this pack holds a different patent's work
    5  the bibliographic record is missing or malformed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from pipeline_context import ContextError, resolve_patent_id, validate_biblio

HERE = Path(__file__).resolve().parent
PY = sys.executable or "python3"


# ================================================================== stage model

@dataclass
class Stage:
    name: str
    title: str
    outputs: list[str]
    inputs: list[str] = field(default_factory=list)
    cmds: list[list[str]] = field(default_factory=list)
    fn: object = None
    gate: bool = False
    optional_tool: str = ""      # a script that may not exist yet
    always: bool = False         # runs every time; produces no tracked artifact
    pin_source_date: bool = False
    blocking: bool = True        # a failing gate stops the run; see verify


def stages(pid: str) -> list[Stage]:
    """The real dependency graph, in the only order that satisfies it.

    Two things about this order are not obvious and were worked out by reading the
    scripts rather than the README:

    1. `resolve_structures.py` and `resolve_translations.py` read the gold from
       `output/relevant_output/gold/` FIRST and fall back to `output/` only when it
       is absent. So the deliverable has to be assembled BEFORE they run, or on any
       re-run they resolve against the previous run's gold. That is why
       `make_relevant_output.py` appears twice: once to publish the gold the
       resolvers read, once at the end to pick up what they produced.

    2. `make_relevant_output.py` mirrors `output/structures/` into the deliverable
       and deletes any drawing the resolver no longer claims. Running it before
       `resolve_structures.py` on a fresh patent is therefore harmless, and running
       it after is required.
    """
    gold = "output/relevant_output/gold"
    prov = "output/relevant_output/provenance"
    verif = "output/relevant_output/verification"
    artifacts = ["compounds", "reactions", "pathways", "patent"]

    # Exactly what make_relevant_output.py copies, in its GOLD and PROV lists.
    # Kept here as one list because both stages that run that script have to
    # declare every file it reads. They did not: `assemble` copied
    # output/translations.json into the gold without declaring it as an input, so
    # a translation fixed at stage 9 left the gold copy stale and every screen and
    # the export went on showing the old English. The stage looked current,
    # because the input that changed was not one it had declared. A stage's
    # declared inputs have to be what it actually reads, or the skip logic is
    # confidently wrong.
    global COPY_PAIRS
    COPIED_TO_GOLD = [f"output/{n}.json" for n in artifacts] + [
        "output/structures.json", "output/structures-resolved.json",
        "output/translations.json"]
    COPIED_TO_PROV = ["output/compounds-provenance.json",
                      "output/reactions-provenance.json",
                      "output/compounds-sections.json",
                      "output/compounds-equivalence.json"]
    COPY_PAIRS = ([(src, f"{gold}/{Path(src).name}") for src in COPIED_TO_GOLD]
                  + [(src, f"{prov}/{Path(src).name}") for src in COPIED_TO_PROV])

    return [
        Stage(
            name="prompts",
            title="render the annotation prompts for THIS patent, for the agent to follow",
            cmds=[[PY, "render_prompts.py", "--patent-id", pid]],
            # input/pages/ is here because render_prompts.py counts it for
            # {PAGE_COUNT}. Without it declared, adding a rescanned page to a settled
            # pack never re-rendered, and the V prompt went on asserting "all 9 pages"
            # at an agent looking at 10. A stage's declared inputs have to be what it
            # actually reads, or the skip logic is confidently wrong.
            inputs=["render_prompts.py", "pipeline_context.py", "prompts/*.md",
                    f"input/{pid}-biblio.json", "input/pages/*.png"],
            outputs=[f"output/prompts/{pid}/*.md"],
        ),
        Stage(
            name="enrich",
            title="vision page reads -> enriched markdown in production's IMAGE_EXTRACT format",
            cmds=[[PY, "build_enriched.py", "--patent-id", pid]],
            inputs=["build_enriched.py", "pipeline_context.py", "input/vision/p*.json"],
            outputs=[f"input/{pid}-enriched.md", f"input/{pid}-enriched-numbered.md",
                     "output/structures.json"],
        ),
        Stage(
            name="collect",
            title="publish the A0, A3 and A4 stage files under the names finalise.py reads",
            fn=collect,
            inputs=["output/stages/A0-sections/00-sections.json",
                    "output/stages/A3-pathways/pathways.json",
                    "output/stages/A4-patent/patent-llm.json"],
            outputs=["output/00-sections.json", "output/raw-pathways.json",
                     "output/raw-patent.json"],
        ),
        Stage(
            name="merge",
            title="concatenate the per-section A1 and A2 stage files into the raw arrays",
            cmds=[[PY, "merge_stages.py"]],
            inputs=["merge_stages.py", "output/stages/A1-compounds/*.json",
                    "output/stages/A2-reactions/*.json"],
            outputs=["output/raw-compounds.json", "output/raw-reactions.json",
                     "output/compounds-provenance.json", "output/reactions-provenance.json",
                     "output/chemistry-rollup.json"],
        ),
        Stage(
            name="finalise",
            title="deterministic ids and uuids, rollup, bibliographic merge",
            cmds=[[PY, "finalise.py", "--patent-id", pid]],
            inputs=["finalise.py", "pipeline_context.py", f"input/{pid}-biblio.json",
                    "output/raw-compounds.json", "output/raw-reactions.json",
                    "output/raw-pathways.json", "output/raw-patent.json"],
            outputs=[f"output/{n}.json" for n in artifacts]
                    + ["output/compounds-sections.json", "output/compounds-equivalence.json"],
        ),
        Stage(
            name="validate",
            title="JSON Schema conformance of the finalised artifacts",
            cmds=[[PY, "schemas/validate.py"]],
            inputs=["schemas/validate.py", "schemas/*.schema.json",
                    "output/00-sections.json"] + [f"output/{n}.json" for n in artifacts],
            outputs=[],
            always=True,
        ),
        Stage(
            name="publish-gold",
            title="mirror gold and provenance into the deliverable, so the resolvers read current gold",
            cmds=[[PY, "make_relevant_output.py", "--patent-id", pid]],
            inputs=["make_relevant_output.py", "pipeline_context.py",
                    "output/stages/A5-verify/*.json", "schemas/*.schema.json",
                    "input/vision/p*.json"]
                   + COPIED_TO_GOLD + COPIED_TO_PROV,
            outputs=[f"{gold}/{n}.json" for n in artifacts]
                    + [f"{gold}/structures.json", f"{gold}/*.schema.json",
                       f"{prov}/compounds-provenance.json", f"{prov}/reactions-provenance.json",
                       f"{prov}/compounds-sections.json", f"{prov}/compounds-equivalence.json",
                       # one per A5 report, named after the artifact it audited
                       f"{verif}/*-report.json",
                       "output/relevant_output/FINDINGS.md",
                       "output/relevant_output/AUDIT.md"],
        ),
        Stage(
            name="structures",
            title="identifier -> drawable molecule over five tiers, plus the coverage gate",
            cmds=[[PY, "resolve_structures.py", "--patent-id", pid]],
            inputs=["resolve_structures.py", "pipeline_context.py",
                    "input/structures-curated.json",
                    f"{gold}/compounds.json", f"{gold}/reactions.json",
                    f"{gold}/structures.json", f"{prov}/compounds-equivalence.json"],
            outputs=["output/structures-resolved.json", "output/structures/*.svg"],
            gate=True,
        ),
        Stage(
            name="translations",
            title="Chinese string -> English for everything that can reach a screen, plus the coverage gate",
            # positional, not --patent-id: this script is owned elsewhere and takes
            # the id the way it always has.
            cmds=[[PY, "resolve_translations.py", pid]],
            inputs=["resolve_translations.py", "resolve_structures.py",
                    "pipeline_context.py", "input/translations-curated.json",
                    f"input/{pid}-enriched-numbered.md", f"{gold}/compounds.json",
                    f"{prov}/compounds-provenance.json", f"{prov}/reactions-provenance.json",
                    f"{verif}/compounds-report.json"],
            outputs=["output/translations.json"],
            gate=True,
        ),
        Stage(
            name="diagrams",
            title="the five method diagrams, the route diagram and the one-page summary",
            cmds=[[PY, "make_svgs.py", "--patent-id", pid],
                  [PY, "make_approach.py", "--patent-id", pid]],
            inputs=["make_svgs.py", "make_approach.py", "pipeline_context.py",
                    f"input/{pid}-biblio.json", f"input/{pid}-enriched.md",
                    "input/vision/p*.json", "output/structures.json",
                    "output/stages/A5-verify/*.json"]
                   + [f"output/{n}.json" for n in artifacts],
            outputs=["svg/m1-pass-map.svg", "svg/m2-route.svg", "svg/m3-artifact-joins.svg",
                     "svg/m4-field-provenance.svg", "svg/m5-ocr-comparison.svg",
                     "svg/approach.svg"],
        ),
        Stage(
            name="rasterise",
            title="every SVG also as a JPG, for readers and tools that will not render SVG",
            cmds=[[PY, "svg2jpg.py", "--all"]],
            inputs=["svg2jpg.py", "svg/*.svg"],
            outputs=["svg/*.jpg"],
        ),
        Stage(
            name="assemble",
            title="assemble the deliverable: gold, provenance, audits, structures, diagrams",
            cmds=[[PY, "make_relevant_output.py", "--patent-id", pid]],
            inputs=["make_relevant_output.py", "pipeline_context.py",
                    "output/structures/*.svg", "svg/*.svg", "svg/*.jpg",
                    "output/stages/A5-verify/*.json", "schemas/*.schema.json",
                    "input/vision/p*.json"]
                   + COPIED_TO_GOLD + COPIED_TO_PROV,
            outputs=[f"{gold}/structures-resolved.json", f"{gold}/translations.json",
                     "output/relevant_output/structures/*.svg",
                     "output/relevant_output/svg/*.svg",
                     "output/relevant_output/svg/*.jpg"],
        ),
        Stage(
            name="visual",
            title="the page index, the structure comparisons and the drawing claims the UI shows",
            cmds=[[PY, "make_visual_evidence.py", "--patent-id", pid]],
            inputs=["make_visual_evidence.py", "visual_text.py",
                    "output/translations.json", "output/structures-resolved.json",
                    "input/vision/p*.json", "input/pages/*.png",
                    f"{gold}/structures.json", f"{gold}/compounds.json",
                    "output/00-sections.json",
                    # hand-authored, and it lives inside the deliverable because its
                    # keys are the raw Chinese labels it stands in for. An input to
                    # this stage, not an output of it.
                    "output/relevant_output/visual/quote-translations.json"],
            # Declared by kind rather than by name, because make_visual_evidence.py
            # is still growing asset types (crops/ and glossary.json landed while
            # this ran). Anything it adds outside these globs shows up in the
            # manifest as a stray, which is the system telling me to declare it
            # rather than the system quietly losing track of it.
            outputs=["output/relevant_output/visual/page-index.json",
                     "output/relevant_output/visual/drawing-claims.json",
                     "output/relevant_output/visual/glossary.json",
                     "output/relevant_output/visual/README.md",
                     "output/relevant_output/visual/comparisons/*.png",
                     "output/relevant_output/visual/crops/*.png"],
            optional_tool="make_visual_evidence.py",
            # it refuses to ship Chinese into a tree whose entire promise is that a
            # reader with no Chinese can open it
            gate=True,
        ),
        Stage(
            name="verify",
            title="the verification contract file the reviewer UI reads",
            # positional, not --patent-id: verify.py is owned elsewhere and takes
            # the id the way resolve_translations.py does.
            cmds=[[PY, "verify.py", pid]],
            inputs=["verify.py", "output/translations.json", "output/00-sections.json",
                    f"input/{pid}-enriched-numbered.md",
                    f"{gold}/structures-resolved.json", f"{gold}/structures.json",
                    f"{prov}/compounds-equivalence.json",
                    f"{prov}/compounds-provenance.json", f"{prov}/reactions-provenance.json"]
                   + [f"{gold}/{n}.json" for n in artifacts],
            outputs=[f"{verif}/checks-{pid}.json"],
            optional_tool="verify.py",
            gate=True,
            # A grounding failure means the ANNOTATION is suspect. It does not mean
            # the page images are suspect, and the visual evidence is what a human
            # reaches for at exactly that moment. Blocking the assets behind this
            # gate removes the evidence at the point it is most needed, and it put
            # the visual stage back where it started: only produced when somebody
            # ran the script by hand. So this gate records the failure and sets the
            # exit code, and the run continues. The end-of-run summary says loudly
            # that it did, so nobody reads a finished run as a clean one.
            blocking=False,
            # verify.py stamps the checks file with the wall clock unless
            # SOURCE_DATE_EPOCH says otherwise, which makes two runs of an
            # unchanged pipeline differ by one line. The runner pins it to the
            # newest input mtime: still an honest "as of", and stable while the
            # gold is stable, so a diff between two runs is a real diff.
            pin_source_date=True,
        ),
        Stage(
            name="selfcheck",
            title="grade the verification engine's own output without trusting its exit code",
            cmds=[[PY, "verify_selfcheck.py", pid]],
            inputs=["verify_selfcheck.py", "verify.py",
                    f"{verif}/checks-{pid}.json"],
            outputs=[],
            optional_tool="verify_selfcheck.py",
            always=True,
        ),
        Stage(
            name="manifest",
            title="sha256 of every artifact and of every input it came from",
            fn=write_manifest,
            inputs=[],
            outputs=["output/relevant_output/manifest.json"],
            always=True,
        ),
    ]


# ============================================================== what a human owes

# Nothing in this list can be produced by a subprocess. Each entry is a pass that
# needs an agent holding the prompt and, for V and A5, the rendered page images.
PREREQS = [
    ("pass V", "V-page-vision.md", "input/vision/p*.json",
     "one agent per rendered page in input/pages/, in parallel"),
    ("pass A0", "A0-section-map.md", "output/stages/A0-sections/00-sections.json",
     "one call over the whole enriched document"),
    ("pass A1", "A1-compounds.md", "output/stages/A1-compounds/*.json",
     "one call per section, each writing <section>.json and <section>-provenance.json"),
    ("pass A2", "A2-reactions.md", "output/stages/A2-reactions/*.json",
     "one call per section that carries procedures"),
    ("pass A3", "A3-pathways.md", "output/stages/A3-pathways/pathways.json",
     "one call"),
    ("pass A4", "A4-patent.md", "output/stages/A4-patent/patent-llm.json",
     "one call"),
    ("pass A5", "A5-verify.md", "output/stages/A5-verify/*.json",
     "one call per artifact, each in a FRESH context, each re-opening the page images"),
]


def hand_inputs(pid: str) -> list[tuple[str, str]]:
    """Files a human puts there, in the order a human actually does them.

    The PDF and the page renders come first because they are the literal first
    physical step of onboarding a patent, and they were missing from this list. The
    pass V entry says "one agent per rendered page in input/pages/" while nothing
    ever told anyone to create input/pages/, so the one instruction a person needed
    before any of the rest could happen was the one instruction not given.
    """
    return [
        (f"input/pdf/{pid}.pdf",
         "the patent PDF. Google Patents or the issuing office; no login and no "
         "paid source"),
        ("input/pages/*.png",
         "every page of that PDF rendered to PNG at 200 dpi, named p01.png, p02.png "
         "and so on. Pass V reads these pixels, because the PDF has no text layer."
         f"\n           run    : pdftoppm -r 200 -png input/pdf/{pid}.pdf input/pages/p"),
        (f"input/{pid}-biblio.json",
         "bibliographic record: family_id, dates, assignees, inventors, ipc_codes, abstract_zh"),
        ("input/structures-curated.json",
         f'{{"patent_id": "{pid}", "entries": {{}}, "no_structure_needed": []}} to start; '
         f"the structures stage tells you what to add"),
        ("input/translations-curated.json",
         f'{{"patent_id": "{pid}", "entries": {{}}}} to start; '
         f"the translations stage tells you what to add"),
    ]


def wrap_what(what: str, width: int = 74) -> str:
    """Wrap a `what` line to the column the message is laid out in.

    These lines are read by somebody who is stuck, on a terminal, and a
    160-column run-on is the format least likely to be read. A newline the caller
    put in is honoured as-is, so a shell command keeps its own line.
    """
    indent = " " * len("           what   : ")
    out = []
    for i, para in enumerate(what.split("\n")):
        if para.startswith(" "):          # the caller laid this one out itself
            out.append(para)
            continue
        line = ""
        for w in para.split():
            if line and len(line) + 1 + len(w) > width:
                out.append(line if not out or out[-1].startswith(" ") else line)
                line = w
            else:
                line = f"{line} {w}".strip()
        if line:
            out.append(line)
    return "\n".join(l if l.startswith(" ") else (indent + l if i else l)
                     for i, l in enumerate(out))


# The A0 to A5 stage folders and input/vision/ are NOT scoped by patent: they are
# output/stages/A1-compounds/, not output/stages/US9999999B2/A1-compounds/. So a pack
# that still holds patent one's pass output satisfies patent two's prerequisites
# completely, and the run proceeds on the wrong document. This is the check that
# notices, and it runs before anything is written.
SCOPED_SCAN = ["output/stages/**/*.json", "input/vision/p*.json",
               "input/structures-curated.json", "input/translations-curated.json"]


def foreign_patent_ids(pid: str) -> list[str]:
    """Files under the unscoped paths that claim to be about a different patent."""
    def walk(node, out):
        if isinstance(node, dict):
            v = node.get("patent_id")
            if isinstance(v, str) and v:
                out.add(v)
            for x in node.values():
                walk(x, out)
        elif isinstance(node, list):
            for x in node:
                walk(x, out)

    bad = []
    for f in expand(SCOPED_SCAN):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        found = set()
        walk(doc, found)
        wrong = sorted(found - {pid})
        if wrong:
            bad.append(f"  {rel(f)}  carries patent_id {', '.join(wrong)}")
    return bad


def check_prereqs(pid: str) -> list[str]:
    """Everything a human or an agent owes before any of this can run.

    The prompt named for each pass is the RENDERED copy under
    output/prompts/<id>/, not the template. The templates still carry a patent id,
    because a prompt is read by an agent rather than imported by a process, and an
    agent following the template faithfully would stamp the wrong id into the new
    patent's gold. `render_prompts.py` fills it in; the prompts stage runs before
    this check so the file named here exists.
    """
    missing = []
    rendered = f"output/prompts/{pid}"
    for label, prompt, pattern, how in PREREQS:
        if not expand([pattern]):
            missing.append(f"  {label:8} MISSING\n"
                           f"           prompt : {rendered}/{prompt}\n"
                           f"           writes : {pattern}\n"
                           f"           how    : {how}")
    for path, what in hand_inputs(pid):
        # expand() handles both a literal path and a glob, so input/pages/*.png is
        # reported missing when the directory is empty as well as when it is absent
        if not expand([path]):
            missing.append(f"  {'input':8} MISSING\n"
                           f"           file   : {path}\n"
                           f"           what   : {wrap_what(what)}")
    return missing


# ================================================================== path helpers

def expand(patterns: list[str]) -> list[Path]:
    """Declared paths and globs -> the files that actually exist, sorted, deduped."""
    seen: dict[Path, None] = {}
    for pat in patterns:
        if any(ch in pat for ch in "*?["):
            for p in sorted(HERE.glob(pat)):
                if p.is_file():
                    seen[p] = None
        else:
            p = HERE / pat
            if p.is_file():
                seen[p] = None
    return list(seen)


MANIFEST = "output/relevant_output/manifest.json"

# (source in output/, copy in the deliverable). Filled by stages(); the manifest
# asserts every pair agrees before it certifies anything.
COPY_PAIRS: list[tuple[str, str]] = []


def stale_copies() -> list[str]:
    """Files whose deliverable copy no longer matches the source in output/.

    The deliverable holds a SECOND copy of eleven artifacts, with a stage in
    between. That is a staleness generator, and it hid a real correction for ten
    minutes tonight: resolve_translations.py fixed two concentrations in
    output/translations.json, the copy stage had not run, and the fix was live in
    the pipeline and invisible on every screen and in the export while looking
    applied everywhere else.

    The declared-inputs fix stops that arising. This is the assertion that catches
    it if some future stage reintroduces it, and it belongs in the manifest because
    the manifest's whole job is to answer "are these assets current for this gold".
    A manifest that cannot tell is worse than no manifest.
    """
    bad = []
    for src, dst in COPY_PAIRS:
        a, b = HERE / src, HERE / dst
        if not a.exists():
            continue
        if not b.exists():
            bad.append(f"{dst} is missing; {src} exists")
        elif sha256(a) != sha256(b):
            bad.append(f"{dst} does not match {src}")
    return bad

_SHA: dict[Path, str] = {}


def sha256(path: Path) -> str:
    """Cached, because the plan hashes some files as several stages' inputs."""
    if path not in _SHA:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        _SHA[path] = h.hexdigest()
    return _SHA[path]


def rel(p: Path) -> str:
    return str(p.relative_to(HERE))


def previous_run() -> dict[str, dict]:
    """What each stage did last time, and the hashes it did it with.

    The manifest is the state store, and currency is decided on CONTENT, not on
    file times. Two things force that, and both were found by watching a run refuse
    to settle:

    1. `make_relevant_output.py` copies with shutil.copy2, which PRESERVES the
       source mtime. A copied schema file therefore carries the schema's own
       mtime, which is older than the gold it sits next to, so "is every output
       newer than every input" is false immediately after a successful copy and
       stays false forever. The stage never settles and re-runs on every
       invocation.

    2. Every gated stage writes its artifact and THEN fails. A minute later every
       output is present and newer than every input, and an mtime rule walks past
       the failure it just had. The status recorded here is the only memory of it.

    Hashing the tree costs a fraction of a second and buys a skip decision that
    survives a `touch`, a copy, a checkout and a clock change.
    """
    p = HERE / MANIFEST
    if not p.exists():
        return {}
    try:
        return {row["stage"]: row
                for row in json.loads(p.read_text(encoding="utf-8")).get("stages", [])}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def _delta(was: dict[str, str], now: dict[str, str]) -> str:
    """First difference between two path -> sha256 maps, in words."""
    for path in sorted(set(was) | set(now)):
        if path not in was:
            return f"{path} is new"
        if path not in now:
            return f"{path} is gone"
        if was[path] != now[path]:
            return f"{path} changed"
    return ""


def literal_outputs(patterns: list[str]) -> list[str]:
    return [p for p in patterns if not any(ch in p for ch in "*?[")]


def glob_outputs(patterns: list[str]) -> list[str]:
    return [p for p in patterns if any(ch in p for ch in "*?[")]


def hashed(patterns: list[str]) -> dict[str, str]:
    return {rel(p): sha256(p) for p in expand(patterns)}


def is_current(st: Stage, prior: dict[str, dict]) -> tuple[bool, str]:
    """True when this stage's inputs and outputs are exactly what it last ran with."""
    if st.always or not st.outputs:
        return False, "produces no tracked artifact, always runs"
    row = prior.get(st.name)
    if row is None:
        return False, "no record of a previous run in the manifest"
    status = str(row.get("status", ""))
    if status.startswith("failed") or status == "not reached":
        return False, f"last run: {status}"
    for pat in literal_outputs(st.outputs):
        if not (HERE / pat).exists():
            return False, f"missing output {pat}"
    for pat in glob_outputs(st.outputs):
        if not expand([pat]):
            return False, f"nothing matches output {pat}"
    d = _delta({e["path"]: e["sha256"] for e in row.get("inputs") or []}, hashed(st.inputs))
    if d:
        return False, f"input {d}"
    d = _delta({e["path"]: e["sha256"] for e in row.get("outputs") or []}, hashed(st.outputs))
    if d:
        return False, f"output {d}"
    return True, "every input and output matches the manifest"


# ============================================================= internal stages

def collect(pid: str, ctx: dict) -> int:
    """Publish the single-file passes under the names finalise.py reads.

    A0, A3 and A4 each write one file into their stage folder and finalise.py reads
    them from output/ under a different name. That copy was a `cp` somebody typed,
    which is exactly the kind of step that does not survive a second patent. It is a
    stage now, and it is a copy rather than a move so the stage folder stays the
    untouched record of what the pass returned.
    """
    pairs = [("output/stages/A0-sections/00-sections.json", "output/00-sections.json"),
             ("output/stages/A3-pathways/pathways.json", "output/raw-pathways.json"),
             ("output/stages/A4-patent/patent-llm.json", "output/raw-patent.json")]
    for src, dst in pairs:
        s, d = HERE / src, HERE / dst
        if not s.exists():
            print(f"  FAIL  {src} not found", file=sys.stderr)
            return 1
        if d.exists() and d.read_bytes() == s.read_bytes():
            print(f"  {dst:36} already identical")
            continue
        shutil.copy2(s, d)
        print(f"  {src}  ->  {dst}")
    return 0


def write_manifest(pid: str, ctx: dict) -> int:
    """Every artifact, its stage, its bytes, and the bytes it was built from.

    Written last, because it hashes what the other stages produced. Two properties
    make it worth having:

      - a consumer can ask whether the structures and the diagrams on disk were
        built from THIS gold, by comparing the input hashes recorded here against
        the gold's own hashes, rather than trusting file times
      - anything sitting in the deliverable that no declared stage produced is
        listed with a null stage. That is the whole failure this pipeline exists to
        fix, so it is reported rather than hidden.
    """
    all_stages = ctx["stages"]
    results = ctx["results"]

    # The plan hashed these files BEFORE the stages rewrote them, so the cache is
    # stale by definition here. Clearing it is what makes the manifest a record of
    # what is on disk now rather than of what was there when the plan was printed.
    _SHA.clear()
    hashes: dict[str, dict] = {}

    def entry(p: Path) -> dict:
        r = rel(p)
        if r not in hashes:
            hashes[r] = {"path": r, "sha256": sha256(p), "bytes": p.stat().st_size}
        return hashes[r]

    prior = ctx.get("prior") or {}

    stage_rows, artifacts, produced = [], [], set()
    consumed: dict[str, str] = {}   # in-tree file -> the stage that reads it
    for st in all_stages:
        if st.name == "manifest":
            continue
        status = results.get(st.name, "not planned")

        # A stage row means "this stage last RAN with these hashes". So a stage that
        # did NOT run this time carries its previous row forward rather than having
        # today's disk state written under its name.
        #
        # Re-reading disk for a skipped stage is how the frozen-plan bug survived a
        # second run: the buggy run left publish-gold stale, then wrote publish-gold's
        # row from the tree it had just failed to update. The row then agreed with
        # disk, is_current() called the stage current, and the staleness was laundered
        # into the record. A stage's row is now only rewritten by that stage running.
        old_row = prior.get(st.name)
        if status == "ran" or old_row is None:
            ins = [entry(p) for p in expand(st.inputs)]
            outs = [entry(p) for p in expand(st.outputs)]
        else:
            ins = old_row.get("inputs") or []
            outs = old_row.get("outputs") or []
            for e in ins + outs:
                hashes.setdefault(e["path"], e)

        input_sha = [i["sha256"] for i in ins]
        for i in ins:
            consumed.setdefault(i["path"], st.name)
        stage_rows.append({
            "stage": st.name,
            "title": st.title,
            "status": status,
            "commands": [" ".join(c) for c in st.cmds] or (["<internal>"] if st.fn else []),
            "gate": st.gate,
            "inputs": ins,
            "outputs": outs,
        })
        # stages[].outputs is what the stage last ran with; artifacts[] is what is
        # on disk now. They are usually the same and are allowed to differ: when
        # they do, somebody edited an artifact by hand and that is worth seeing.
        for pth in expand(st.outputs):
            r = rel(pth)
            # Two stages run make_relevant_output.py, so they declare overlapping
            # outputs on purpose. An artifact is attributed to the first stage that
            # produces it, and listed once.
            if r in produced:
                continue
            produced.add(r)
            live = {"path": r, "sha256": sha256(pth), "bytes": pth.stat().st_size}
            row = {**live, "stage": st.name, "input_sha256": input_sha}
            recorded = next((o["sha256"] for o in outs if o["path"] == r), None)
            if recorded is not None and recorded != live["sha256"]:
                row["note"] = (f"on disk now, but the {st.name} stage last ran "
                               f"producing sha256 {recorded[:16]}...")
            artifacts.append(row)

    # Anything in the deliverable that no stage claims. Two kinds, and the
    # difference matters: a hand-authored file some stage READS is a legitimate
    # input that happens to live in the tree, while a file nothing reads and
    # nothing writes is a stray, and a stray is the exact failure this pipeline
    # exists to fix. On a healthy run the strays are the hand-written README and
    # the reviewer's own verdict log, and nothing else.
    rel_root = HERE / "output" / "relevant_output"
    unclaimed, strays = [], []
    for p in sorted(rel_root.rglob("*")):
        if not p.is_file() or p.name in (".DS_Store", "manifest.json"):
            continue
        r = rel(p)
        if r in produced:
            continue
        if r in consumed:
            unclaimed.append({**entry(p), "stage": None,
                              "note": f"hand-authored input to the {consumed[r]} stage, "
                                      f"not produced by the pipeline"})
        else:
            row = {**entry(p), "stage": None,
                   "note": "present in the deliverable, produced by no declared stage "
                           "and read by none"}
            unclaimed.append(row)
            strays.append(row)

    manifest = {
        "schema": 1,
        "patent_id": pid,
        "note": ("No timestamp anywhere in this file, on purpose: the pipeline is "
                 "idempotent to the byte and a generated_at field would make every "
                 "second run a diff. Currency is established by hash, not by clock."),
        "stages": stage_rows,
        "artifacts": sorted(artifacts + unclaimed, key=lambda a: a["path"]),
        "totals": {
            "stages": len(stage_rows),
            "artifacts_produced": len(artifacts),
            "artifacts_unclaimed": len(unclaimed),
            "artifacts_stray": len(strays),
            "bytes_produced": sum(a["bytes"] for a in artifacts),
        },
    }
    # Asserted before the file is written, and recorded in it, so a consumer never
    # has to take the manifest's word for the thing the manifest is for.
    stale = stale_copies()
    manifest["deliverable_matches_output"] = not stale
    manifest["stale_copies"] = stale

    out = rel_root / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"  {len(artifacts)} artifacts over {len(stage_rows)} stages, "
          f"{sum(a['bytes'] for a in artifacts):,} bytes")
    inputs_in_tree = len(unclaimed) - len(strays)
    if inputs_in_tree:
        print(f"  {inputs_in_tree} hand-authored input(s) living in the deliverable, "
              f"read by a stage")
    if strays:
        print(f"  {len(strays)} file(s) in the deliverable that no stage produced "
              f"and none reads:")
        for u in strays:
            print(f"    {u['path']}")
    print(f"  wrote {rel(out)}")
    if stale:
        print(f"\n  FAIL  {len(stale)} artifact(s) in the deliverable do not match "
              f"their source in output/.")
        for x in stale:
            print(f"    {x}")
        print(f"\n  The pipeline holds a second copy of these, and the screen and the "
              f"export read\n  the copy. A fix landed in output/ is invisible until the "
              f"copy stage runs, so a\n  divergence here means something is fixed "
              f"everywhere except where it is read.\n\n"
              f"  Run: {PY} run_pipeline.py --patent-id {pid} --from publish-gold")
        return 1
    print(f"  deliverable matches output/ on all {len(COPY_PAIRS)} copied artifacts")
    return 0


# ======================================================================= running

# Files under input/ that no stage writes. Everything else in input/ is either a
# pipeline output (the enriched markdown) or reference material.
HUMAN_INPUTS = ["input/*-biblio.json", "input/*-curated.json", "input/vision/p*.json"]


def source_date_epoch() -> int:
    """A build timestamp that is a function of the inputs, not of the clock.

    The newest mtime among the files a HUMAN owns. Deliberately not the newest
    mtime among the stage's own inputs: those include files the pipeline
    regenerates, so --force would move the timestamp on every run and two
    identical rebuilds would differ by one line for no reason. This moves when
    somebody changes an input, which is the only time it should.
    """
    return int(max((p.stat().st_mtime for p in expand(HUMAN_INPUTS)), default=0))


def run_stage(st: Stage, pid: str, ctx: dict) -> int:
    if st.fn is not None:
        return st.fn(pid, ctx)
    env = None
    if st.pin_source_date:
        epoch = source_date_epoch()
        env = {**os.environ, "SOURCE_DATE_EPOCH": str(epoch)}
        print(f"  SOURCE_DATE_EPOCH={epoch}  (newest hand-authored input, so two "
              f"rebuilds diff to nothing)")
    code = 0
    for cmd in st.cmds:
        print(f"  $ {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=HERE, env=env)
        code = proc.returncode
        if code != 0:
            return code
    return code


def main() -> int:
    # Subprocess output goes straight to the terminal while the parent's own prints
    # sit in a block buffer, so redirecting a run to a file used to interleave the
    # plan into the middle of a stage's report. Line buffering puts them back in
    # the order they happened.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass

    ap = argparse.ArgumentParser(
        description="Run every deterministic stage of the manual annotation pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes: 0 ok, 1 stage failed, 2 coverage gate, 3 LLM passes not "
               "run, 4 this pack holds a different patent, 5 bad biblio.")
    ap.add_argument("--patent-id", help="patent to run; discovered from input/*-biblio.json if omitted")
    ap.add_argument("--from", dest="from_stage", metavar="STAGE", help="start here, run everything after")
    ap.add_argument("--only", metavar="STAGE", help="run exactly this stage")
    ap.add_argument("--force", action="store_true", help="run stages even when their outputs are current")
    ap.add_argument("--plan", action="store_true", help="print the plan and stop")
    ap.add_argument("--list", action="store_true", help="list the stages and stop")
    args = ap.parse_args()

    try:
        pid = args.patent_id or resolve_patent_id([])
    except ContextError as e:
        print(f"FAIL  {e}", file=sys.stderr)
        return 1

    all_stages = stages(pid)
    by_name = {s.name: s for s in all_stages}

    if args.list:
        for s in all_stages:
            print(f"  {s.name:14} {s.title}")
        return 0

    for label, val in (("--from", args.from_stage), ("--only", args.only)):
        if val and val not in by_name:
            print(f"FAIL  {label} {val!r} is not a stage. Known: "
                  f"{', '.join(by_name)}", file=sys.stderr)
            return 1

    # ---- select --------------------------------------------------------------
    if args.only:
        selected = [by_name[args.only]]
    elif args.from_stage:
        i = [s.name for s in all_stages].index(args.from_stage)
        selected = all_stages[i:]
    else:
        selected = all_stages

    # ---- plan ----------------------------------------------------------------
    prior = previous_run()
    plan = []
    for st in all_stages:
        if st not in selected:
            plan.append((st, "not selected", ""))
            continue
        if args.force:
            plan.append((st, "run", "--force"))
            continue
        if st.optional_tool and not (HERE / st.optional_tool).exists():
            plan.append((st, "absent", f"{st.optional_tool} does not exist yet"))
            continue
        current, why = is_current(st, prior)
        plan.append((st, "skip" if current else "run", why))

    print(f"\npipeline: {pid}")
    print(f"plan     {sum(1 for _, a, _ in plan if a == 'run')} to run, "
          f"{sum(1 for _, a, _ in plan if a == 'skip')} current, "
          f"{sum(1 for _, a, _ in plan if a == 'absent')} absent, "
          f"{sum(1 for _, a, _ in plan if a == 'not selected')} not selected\n")
    MARK = {"run": "RUN ", "skip": "----", "absent": "ABS ", "not selected": "    "}
    for st, action, why in plan:
        gate = " [gate]" if st.gate else ""
        print(f"  {MARK[action]} {st.name:14}{gate:7} {st.title}")
        if why and action != "skip":
            print(f"       {'':14}{'':7} {why}")
    print()
    if args.plan:
        return 0

    # ---- run -----------------------------------------------------------------
    ctx = {"stages": all_stages, "results": {}, "prior": prior}
    deferred: list[tuple[str, int]] = []   # non-blocking gates that failed

    # ---- the prompts stage, then what a human owes ---------------------------
    #
    # Ordered this way on purpose. The prerequisite message names the prompt that
    # produces each missing pass, and the prompt it must name is the one rendered
    # for THIS patent. So the prompts stage runs first, and only then is the check
    # made. Nothing else has run at this point.
    pst = by_name["prompts"]
    pact = dict((s_.name, a) for s_, a, _ in plan)["prompts"]
    if pact == "run":
        print("=== prompts " + "=" * 61)
        if run_stage(pst, pid, ctx) != 0:
            ctx["results"]["prompts"] = "failed"
            print("\nSTOP  the prompts could not be rendered for this patent.")
            return 1
    ctx["results"]["prompts"] = {"run": "ran", "skip": "current", "absent": "absent",
                                 "not selected": "not selected"}[pact]

    # A malformed biblio before either. Every id, every uuid and half the patent
    # record are built from it, and it is the one hand-authored input that used to
    # have no contract: thirteen fields read through bare b["key"], failing one at a
    # time, several stages in.
    biblio_problems = validate_biblio(pid)
    if biblio_problems:
        print(f"\nSTOP  input/{pid}-biblio.json does not satisfy "
              f"schemas/biblio.schema.json.\n")
        for x in biblio_problems[:15]:
            print(f"  {x}")
        if len(biblio_problems) > 15:
            print(f"  ... and {len(biblio_problems) - 15} more")
        print(f"\n  Every id and uuid in every artifact is built from this file, and "
              f"the patent\n  record is half made of it. It is checked as a whole here "
              f"rather than one\n  key at a time, several stages in.\n\n"
              f"  The schema documents every field, which are optional, and why "
              f"grant_date\n  is nullable: most published applications are never "
              f"granted.")
        return 5

    # Wrong patent BEFORE missing patent. A pack holding a complete annotation of a
    # different patent has no missing prerequisites at all, so the missing-file
    # check would pass it straight through.
    foreign = foreign_patent_ids(pid)
    if foreign:
        print(f"\nSTOP  this pack does not hold {pid}. It holds another patent's work.\n")
        print("\n".join(foreign[:12]))
        if len(foreign) > 12:
            print(f"  ... and {len(foreign) - 12} more")
        print(f"\n  output/stages/ and input/vision/ are not scoped by patent, so this\n"
              f"  pack satisfies every prerequisite for {pid} using the other patent's\n"
              f"  files. Finalising that produces records whose ids are built from\n"
              f"  {pid} while the records themselves belong to the other patent, which\n"
              f"  is schema-valid, internally consistent and wrong.\n\n"
              f"  This pack holds one patent at a time. Either run the pipeline on the\n"
              f"  patent it holds, or start a clean pack for {pid}: copy the scripts,\n"
              f"  prompts, schemas and contracts, and leave output/ and input/vision/\n"
              f"  empty.")
        return 4

    missing = check_prereqs(pid)
    if missing:
        print("\nThe LLM annotation passes are not run by this script - they need an "
              "agent holding\nthe prompt and, for V and A5, the rendered page images. "
              "This run cannot start until\nthe following exist. Nothing has been "
              "written except the rendered prompts above.\n")
        print("\n".join(missing))
        tail = ("\nEach pass writes into output/stages/<pass>/, one folder per pass, "
                "and nothing\nlater rewrites it, so each stage stays the record of "
                "what that pass returned.")
        if (HERE / "output" / "stages" / "README.md").exists():
            tail += "\nSee output/stages/README.md for the layout."
        print(f"{tail}\nThen: python3 run_pipeline.py --patent-id {pid}")
        return 3

    def finish(rc: int) -> int:
        """Write the manifest even on a stop, then return rc.

        The manifest is an observation of what is on disk, not a product of the
        run, and a stopped run is exactly when a consumer most needs to be told
        that the assets are not current for the gold. It records the failing
        stage's status, so nothing is being papered over.
        """
        # Every exit path comes through here, so this is where a non-blocking gate
        # failure gets reported. Printing it only on the happy path would mean a
        # later stage crashing could hide the fact that a gate went red.
        if deferred:
            order = [s_.name for s_, _, _ in plan]
            first = min(order.index(n) for n, _ in deferred)
            ran_after = [n for n in order[first + 1:]
                         if ctx["results"].get(n) == "ran" and n != "manifest"]
            print("=" * 72)
            for name, code in deferred:
                print(f"GATE FAILED: {name} (exit {code}). THIS RUN IS NOT CLEAN.")
            if ran_after:
                print(f"Stages that ran anyway, because they consume nothing the "
                      f"failed gate\nproduces:  {', '.join(ran_after)}")
            print("Their output is current for this gold. The gold itself is what the "
                  "gate is\nquestioning, so read the gate's message above before "
                  "trusting any of it.")
            rc = rc or 2
        if by_name["manifest"] in selected:
            print("=== manifest " + "=" * 60)
            # A stale copy means the screen is showing something the gold does not
            # say, so it fails the run rather than being written down and ignored.
            if write_manifest(pid, ctx) != 0:
                ctx["results"]["manifest"] = "failed (1)"
                rc = rc or 1
        return rc

    # THE PLAN ABOVE IS A FORECAST. THE DECISION IS MADE HERE, ONE STAGE AT A TIME.
    #
    # Judging all sixteen stages up front and then executing that frozen list is
    # wrong, and wrong in the way that matters most. Running a stage rewrites the
    # next stage's inputs, but the next stage was already judged against the tree
    # as it looked before any of this ran. Change one field in the biblio and the
    # forecast says "RUN finalise, skip publish-gold", which was true when it was
    # computed and false one second later: finalise rewrote patent.json, so
    # publish-gold's input no longer matches what the manifest recorded.
    #
    # The result was a deliverable holding the old value while output/ held the new
    # one, and a manifest recording publish-gold as current - which is precisely
    # the one question the manifest exists to answer, answered wrongly.
    #
    # So currency is re-evaluated immediately before each stage. A stage that was
    # forecast to skip and now has to run says so. This costs one re-hash of a
    # stage's own declared paths, and only after some earlier stage actually wrote
    # something.
    for st, forecast, _ in plan:
        if forecast in ("absent", "not selected") or st.name in ("manifest", "prompts"):
            label = {"run": "ran", "skip": "current", "absent": "absent",
                     "not selected": "not selected"}[forecast]
            was = str(prior.get(st.name, {}).get("status", ""))
            if forecast != "run" and (was.startswith("failed") or was == "not reached"):
                label = was
            ctx["results"][st.name] = label
            continue

        if args.force:
            action, why = "run", "--force"
        else:
            current, why = is_current(st, prior)
            action = "skip" if current else "run"

        label = "ran" if action == "run" else "current"
        was = str(prior.get(st.name, {}).get("status", ""))
        if action != "run" and (was.startswith("failed") or was == "not reached"):
            label = was
        ctx["results"][st.name] = label

        if action != forecast:
            print(f"--- {st.name}: forecast said {forecast}, running it: {why}"
                  if action == "run"
                  else f"--- {st.name}: forecast said run, now current: {why}")
        if action != "run":
            continue
        print(f"=== {st.name} " + "=" * max(0, 66 - len(st.name)))
        code = run_stage(st, pid, ctx)
        if code == 0:
            # This stage has just rewritten files that later stages hash. Anything
            # cached from the forecast is stale by definition now.
            _SHA.clear()
            continue
        ctx["results"][st.name] = f"failed ({code})"

        # A non-blocking gate records the failure, sets the exit code, and lets the
        # rest of the run finish. Only `verify` is one, and only because a grounding
        # failure says the annotation is suspect, not that the page images are.
        if st.gate and not st.blocking:
            deferred.append((st.name, code))
            print(f"\nGATE FAILED  {st.name} (exit {code}). The run CONTINUES: nothing "
                  f"after this\n             stage consumes what it produces, and the "
                  f"assets below are what a\n             human reaches for when "
                  f"grounding is in doubt. The exit code\n             carries the "
                  f"failure; see the summary at the end.")
            continue

        for later in all_stages[all_stages.index(st) + 1:]:
            ctx["results"][later.name] = "not reached"
        print()
        if st.gate:
            print(f"STOP  the {st.name} stage gate did not pass (exit {code}).")
            print(f"      The stage printed above exactly what it still needs. It is a "
                  f"human\n      judgement, not something the pipeline can fill in: a "
                  f"wrong structure or a\n      wrong translation does not fail loudly, "
                  f"it corrupts the deliverable quietly.")
            print(f"\n      Supply it, then: {PY} run_pipeline.py --patent-id {pid} "
                  f"--from {st.name}")
            return finish(2)
        print(f"STOP  stage {st.name!r} failed with exit {code}. Nothing after it ran.")
        return finish(1)

    print("=" * 72)
    print(f"pipeline complete: {pid}" if not deferred
          else f"pipeline reached the end: {pid}  (A GATE FAILED, see below)")
    print(f"deliverable      : output/relevant_output/")
    print(f"manifest         : output/relevant_output/manifest.json")
    absent = [s.name for s, a, _ in plan if a == "absent"]
    if absent:
        print(f"stages absent    : {', '.join(absent)} "
              f"(the tool does not exist yet; nothing was skipped silently)")
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
