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
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from pipeline_context import ContextError, resolve_patent_id

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

    return [
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
                    "output/structures.json", "output/compounds-sections.json",
                    "output/compounds-equivalence.json", "output/compounds-provenance.json",
                    "output/reactions-provenance.json", "output/stages/A5-verify/*.json",
                    "schemas/*.schema.json", "input/vision/p*.json"]
                   + [f"output/{n}.json" for n in artifacts],
            outputs=[f"{gold}/{n}.json" for n in artifacts]
                    + [f"{gold}/structures.json", f"{gold}/compounds.schema.json",
                       f"{prov}/compounds-provenance.json", f"{prov}/reactions-provenance.json",
                       f"{prov}/compounds-sections.json", f"{prov}/compounds-equivalence.json",
                       f"{verif}/compounds-report.json",
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
            inputs=["make_relevant_output.py", "output/structures-resolved.json",
                    "output/structures/*.svg", "svg/*.svg", "svg/*.jpg",
                    "output/stages/A5-verify/*.json"]
                   + [f"output/{n}.json" for n in artifacts],
            outputs=[f"{gold}/structures-resolved.json",
                     "output/relevant_output/structures/*.svg",
                     "output/relevant_output/svg/*.svg",
                     "output/relevant_output/svg/*.jpg"],
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
    ("pass V", "prompts/V-page-vision.md", "input/vision/p*.json",
     "one agent per rendered page in input/pages/, in parallel"),
    ("pass A0", "prompts/A0-section-map.md", "output/stages/A0-sections/00-sections.json",
     "one call over the whole enriched document"),
    ("pass A1", "prompts/A1-compounds.md", "output/stages/A1-compounds/*.json",
     "one call per section, each writing <section>.json and <section>-provenance.json"),
    ("pass A2", "prompts/A2-reactions.md", "output/stages/A2-reactions/*.json",
     "one call per section that carries procedures"),
    ("pass A3", "prompts/A3-pathways.md", "output/stages/A3-pathways/pathways.json",
     "one call"),
    ("pass A4", "prompts/A4-patent.md", "output/stages/A4-patent/patent-llm.json",
     "one call"),
    ("pass A5", "prompts/A5-verify.md", "output/stages/A5-verify/*.json",
     "one call per artifact, each in a FRESH context, each re-opening the page images"),
]


def hand_inputs(pid: str) -> list[tuple[str, str]]:
    return [
        (f"input/{pid}-biblio.json",
         "bibliographic record: family_id, dates, assignees, inventors, ipc_codes, abstract_zh"),
        ("input/structures-curated.json",
         f'{{"patent_id": "{pid}", "entries": {{}}, "no_structure_needed": []}} to start; '
         f"the structures stage tells you what to add"),
        ("input/translations-curated.json",
         f'{{"patent_id": "{pid}", "entries": {{}}}} to start; '
         f"the translations stage tells you what to add"),
    ]


def check_prereqs(pid: str) -> list[str]:
    """Everything a human or an agent owes before any of this can run."""
    missing = []
    for label, prompt, pattern, how in PREREQS:
        if not expand([pattern]):
            missing.append(f"  {label:8} MISSING\n"
                           f"           prompt : {prompt}\n"
                           f"           writes : {pattern}\n"
                           f"           how    : {how}")
    for path, what in hand_inputs(pid):
        if not (HERE / path).exists():
            missing.append(f"  {'input':8} MISSING\n"
                           f"           file   : {path}\n"
                           f"           what   : {what}")
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


def literal_outputs(patterns: list[str]) -> list[str]:
    return [p for p in patterns if not any(ch in p for ch in "*?[")]


def glob_outputs(patterns: list[str]) -> list[str]:
    return [p for p in patterns if any(ch in p for ch in "*?[")]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p: Path) -> str:
    return str(p.relative_to(HERE))


def is_current(st: Stage) -> tuple[bool, str]:
    """True when every output is present and no input is newer than any of them."""
    if st.always or not st.outputs:
        return False, "produces no tracked artifact, always runs"
    for pat in literal_outputs(st.outputs):
        if not (HERE / pat).exists():
            return False, f"missing output {pat}"
    for pat in glob_outputs(st.outputs):
        if not expand([pat]):
            return False, f"nothing matches output {pat}"
    outs = expand(st.outputs)
    ins = expand(st.inputs)
    if not ins:
        return True, "no inputs declared, outputs present"
    newest_in = max(ins, key=lambda p: p.stat().st_mtime)
    oldest_out = min(outs, key=lambda p: p.stat().st_mtime)
    if newest_in.stat().st_mtime > oldest_out.stat().st_mtime:
        return False, f"{rel(newest_in)} is newer than {rel(oldest_out)}"
    return True, f"all {len(outs)} outputs newer than all {len(ins)} inputs"


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

    hashes: dict[str, dict] = {}

    def entry(p: Path) -> dict:
        r = rel(p)
        if r not in hashes:
            hashes[r] = {"path": r, "sha256": sha256(p), "bytes": p.stat().st_size}
        return hashes[r]

    stage_rows, artifacts, produced = [], [], set()
    for st in all_stages:
        if st.name == "manifest":
            continue
        ins = [entry(p) for p in expand(st.inputs)]
        outs = [entry(p) for p in expand(st.outputs)]
        input_sha = [i["sha256"] for i in ins]
        stage_rows.append({
            "stage": st.name,
            "title": st.title,
            "status": results.get(st.name, "not planned"),
            "commands": [" ".join(c) for c in st.cmds] or (["<internal>"] if st.fn else []),
            "gate": st.gate,
            "inputs": ins,
            "outputs": outs,
        })
        for o in outs:
            produced.add(o["path"])
            artifacts.append({**o, "stage": st.name, "input_sha256": input_sha})

    # Anything in the deliverable that no stage claims. On a healthy run this is the
    # hand-written README and the reviewer's own verdict log, and nothing else.
    rel_root = HERE / "output" / "relevant_output"
    unclaimed = []
    for p in sorted(rel_root.rglob("*")):
        if not p.is_file() or p.name in (".DS_Store", "manifest.json"):
            continue
        if rel(p) in produced:
            continue
        unclaimed.append({**entry(p), "stage": None,
                          "note": "present in the deliverable, produced by no declared stage"})

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
            "bytes_produced": sum(a["bytes"] for a in artifacts),
        },
    }
    out = rel_root / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"  {len(artifacts)} artifacts over {len(stage_rows)} stages, "
          f"{sum(a['bytes'] for a in artifacts):,} bytes")
    if unclaimed:
        print(f"  {len(unclaimed)} file(s) in the deliverable that no stage produced:")
        for u in unclaimed:
            print(f"    {u['path']}")
    print(f"  wrote {rel(out)}")
    return 0


# ======================================================================= running

def run_stage(st: Stage, pid: str, ctx: dict) -> int:
    if st.fn is not None:
        return st.fn(pid, ctx)
    code = 0
    for cmd in st.cmds:
        print(f"  $ {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=HERE)
        code = proc.returncode
        if code != 0:
            return code
    return code


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run every deterministic stage of the manual annotation pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes: 0 ok, 1 stage failed, 2 coverage gate, 3 LLM passes not run.")
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

    # ---- what a human owes, checked before anything runs --------------------
    missing = check_prereqs(pid)
    if missing:
        print(f"\npipeline: {pid}\n")
        print("The LLM annotation passes are not run by this script - they need an "
              "agent holding\nthe prompt and, for V and A5, the rendered page images. "
              "This run cannot start until\nthe following exist. Nothing has been "
              "written.\n")
        print("\n".join(missing))
        print(f"\nEach pass writes into output/stages/<pass>/ and nothing later "
              f"rewrites it.\nSee prompts/ for the instructions and "
              f"output/stages/README.md for the layout.\n"
              f"Then: python3 run_pipeline.py --patent-id {pid}")
        return 3

    # ---- select --------------------------------------------------------------
    if args.only:
        selected = [by_name[args.only]]
    elif args.from_stage:
        i = [s.name for s in all_stages].index(args.from_stage)
        selected = all_stages[i:]
    else:
        selected = all_stages

    # ---- plan ----------------------------------------------------------------
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
        current, why = is_current(st)
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
    ctx = {"stages": all_stages, "results": {}}
    for st, action, _ in plan:
        ctx["results"][st.name] = {"run": "ran", "skip": "current",
                                   "absent": "absent", "not selected": "not selected"}[action]
        if action != "run":
            continue
        print(f"=== {st.name} " + "=" * max(0, 66 - len(st.name)))
        code = run_stage(st, pid, ctx)
        if code == 0:
            continue
        ctx["results"][st.name] = f"failed ({code})"
        print()
        if st.gate:
            print(f"STOP  the {st.name} stage gate did not pass (exit {code}).")
            print(f"      The stage printed above exactly what it still needs. It is a "
                  f"human\n      judgement, not something the pipeline can fill in: a "
                  f"wrong structure or a\n      wrong translation does not fail loudly, "
                  f"it corrupts the deliverable quietly.")
            print(f"\n      Supply it, then: {PY} run_pipeline.py --patent-id {pid} "
                  f"--from {st.name}")
            return 2
        print(f"STOP  stage {st.name!r} failed with exit {code}. Nothing after it ran.")
        return 1

    print("=" * 72)
    print(f"pipeline complete: {pid}")
    print(f"deliverable      : output/relevant_output/")
    print(f"manifest         : output/relevant_output/manifest.json")
    absent = [s.name for s, a, _ in plan if a == "absent"]
    if absent:
        print(f"stages absent    : {', '.join(absent)} "
              f"(the tool does not exist yet; nothing was skipped silently)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
