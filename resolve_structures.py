#!/usr/bin/env python3
r"""Resolve every gold compound identifier to a drawable 2D structure.

The extraction passes emit no structures at all. 0 of the 75 CompoundRecords carry
`smiles`, `inchi_key` or `molecular_formula`, and that is deliberate: structure
resolution is a lookup service in production, not something a prompt can do
honestly. But the artifacts are close to unusable without it. A reader cannot see
what "methyl 2-chloro-3-(bromomethyl)-4-(methylsulfonyl)benzoate" is, and the
mass-balance check cannot weigh a row it has no molecular weight for.

This stage closes that gap INSIDE the pipeline. It used to be done by hand in a
downstream consumer, which meant that running the pipeline on a second patent
produced no structures whatsoever and nothing said so.

Resolution tiers, in order. The first one that fires wins.

    identifier
       |
       +-- 1. the string itself parses as SMILES .............. patent_scheme
       |
       +-- 2. a SMILES we can attach to it canonicalises to
       |      one DRAWN in gold/structures.json .............. patent_drawing
       |
       +-- 3. a synonym in the same equivalence group has
       |      already resolved ................................ derived
       |
       +-- 4. input/structures-curated.json has an entry ...... curated
       |
       +-- 5. nothing ........................................ none

THE TIER-2 JOIN IS ON RDKIT CANONICAL SMILES, NEVER ON NAMES. gold/structures.json
holds 18 SMILES entries for only 11 unique molecules, because the drawn scheme is
read more than once and the reads name things differently:

    drawn (p06)  methyl 3-(bromomethyl)-2-chloro-4-(methylsulfonyl)benzoate
    drawn (p08)  methyl 3-(bromomethyl)-2-chloro-4-(methanesulfonyl)benzoate
    record       methyl 2-chloro-3-(bromomethyl)-4-(methylsulfonyl)benzoate
                  \______ three strings, one molecule, no string equality ______/

12 of the 16 distinct drawn names match no record name in compounds.json or in the
equivalence groups. A name join would fall through and report molecules that ARE
drawn in the patent as not drawn, inverting the single distinction this stage
exists to make. Canonicalising collapses all three strings onto one key.

THE COVERAGE GATE is the point of the whole stage. It exits non-zero when a
molecule that CARRIES CHEMISTRY has no structure. Carrying chemistry means: the
molecule is the product of some reaction, or it appears in a reaction-compound row
with both `mass_g` and `mmol`, because those rows feed the mass-balance check and
are useless without a formula. Trivial workup species (water, hydrochloric acid,
magnesium sulfate) are reported as needing no structure and never gate. On failure
the report prints the exact missing identifiers and a JSON stub ready to paste into
input/structures-curated.json, so the answer to "what do I still owe this patent"
is on screen rather than latent.

Reads the gold artifacts and the curated table. Writes only new files: no gold JSON
and no provenance file is modified.

Usage:  python3 resolve_structures.py                  # discovers the patent id
        python3 resolve_structures.py CN104292137A     # any patent id
        python3 resolve_structures.py --patent-id CN104292137A
        python3 resolve_structures.py --check          # resolve and report, write nothing

With no id given the pack is asked which patent it holds, from the one
input/<id>-biblio.json in it. It used to fall back to a literal instead, so a pack
holding a different patent silently resolved that patent's names against this
patent's curated table until the patent_id guard below caught it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pipeline_context import ContextError, resolve_patent_id
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

RDLogger.DisableLog("rdApp.*")  # parse failures are reported here, with context

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REL = OUT / "relevant_output"
CURATED = HERE / "input" / "structures-curated.json"


# Rendered at the size the artifacts are read at, monochrome. See render().
WIDTH, HEIGHT = 320, 240

# Where the SVG land relative to the deliverable root, which is what the `svg`
# field of each resolved entry holds. make_relevant_output.py mirrors
# output/structures/ to output/relevant_output/structures/ alongside gold/.
SVG_SUBDIR = "structures"


# ---------------------------------------------------------------- trivial species

# Species that are real chemistry but carry none of THIS patent's chemistry:
# reaction media, mineral acids, drying agents, inert gases. Drawing them is noise,
# and demanding a hand-authored structure for water would make the gate cry wolf
# often enough that a human would stop reading it.
#
# Deliberately NOT in this list: hydroxides, hypochlorites and carbonates. They look
# equally boring but they are charged stoichiometrically in this document and in
# plenty of others, so a mass-balance check does need their formula. A patent that
# genuinely needs more exemptions adds them to `no_structure_needed` in the curated
# table rather than editing this list, so nothing here is patent-specific.
TRIVIAL_SPECIES = {
    "water", "ice", "ice water", "brine", "sodium chloride",
    "hydrochloric acid", "hydrogen chloride", "hydrobromic acid",
    "sulfuric acid", "nitric acid", "phosphoric acid", "acetic acid",
    "magnesium sulfate", "sodium sulfate", "calcium chloride",
    "sodium bicarbonate", "sodium hydrogen carbonate",
    "nitrogen", "argon", "air", "celite", "silica gel",
}

# Adjectives that describe a bottle rather than a molecule. Stripped before the
# trivial-species test so "anhydrous magnesium sulfate" and "saturated brine" match.
_QUALIFIERS = ("anhydrous", "saturated", "aqueous", "concentrated", "dilute",
               "dry", "fuming", "glacial", "cold", "hot", "solid", "liquid")


def normalise_name(s: str) -> str:
    t = s.lower().strip()
    t = re.sub(r"[\s_]+", " ", t)
    for q in _QUALIFIERS:
        t = re.sub(rf"\b{q}\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def is_trivial(identifier: str, extra: set[str]) -> bool:
    n = normalise_name(identifier)
    return n in TRIVIAL_SPECIES or n in extra


# ---------------------------------------------------------------- SMILES handling

_BONDS = set("-=#$:/\\.@+")
_ORGANIC = set("BCNOPSFIbcnops")
_AROMATIC = set("bcnops")


def looks_like_smiles(s: str) -> bool:
    """True when `s` is a well-formed SMILES over the organic subset.

    A syntax check, not a chemistry check: its only job is to stop a NAME from being
    mistaken for a structure, because RDKit is happy to parse strings that are
    plainly abbreviations. Two real identifiers in this gold need it:

      NBS   tokenises, since N, B and S are all organic-subset atoms, and RDKit
            parses it into a molecule. Rejected by the shape test below: no ring, no
            branch, no multiple bond, no aromatic atom. It abbreviates
            N-bromosuccinimide.
      Br2   tokenises as Br followed by ring-bond label 2. Rejected by the ring
            parity test, since label 2 is never closed. RDKit refuses it too. It is
            the gold's alias for bromine.

    Deliberately conservative: it also rejects "CO" and "[Na+]", which are valid
    SMILES but indistinguishable from shorthand. A record's own `identifier_type`
    is the authoritative signal and skips this test entirely.
    """
    open_rings: set[str] = set()
    depth = atoms = 0
    has_shape = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == "[":
            end = s.find("]", i)
            if end < 0:
                return False
            atoms += 1
            i = end + 1
        elif c == "(":
            depth += 1
            has_shape = True
            i += 1
        elif c == ")":
            depth -= 1
            if depth < 0:
                return False
            i += 1
        elif c == "%":
            label = s[i:i + 3]
            if not re.fullmatch(r"%\d\d", label):
                return False
            open_rings ^= {label}  # ring labels pair up, so track parity not count
            has_shape = True
            i += 3
        elif c.isdigit():
            open_rings ^= {c}
            has_shape = True
            i += 1
        elif c in _BONDS:
            has_shape = has_shape or c in "=#"
            i += 1
        elif s.startswith(("Cl", "Br"), i):
            atoms += 1
            i += 2
        elif c in _ORGANIC:
            atoms += 1
            has_shape = has_shape or c in _AROMATIC
            i += 1
        else:
            return False
    return depth == 0 and not open_rings and atoms >= 2 and has_shape


def as_smiles(s: str, identifier_type: str | None = None) -> Chem.Mol | None:
    """Parse `s` as a structure, or return None if it is a name."""
    if identifier_type != "smiles" and not looks_like_smiles(s):
        return None
    return Chem.MolFromSmiles(s)


def describe(mol: Chem.Mol) -> tuple[str, str, float]:
    """canonical SMILES, molecular formula, molecular weight."""
    return (Chem.MolToSmiles(mol),
            rdMolDescriptors.CalcMolFormula(mol),
            round(Descriptors.MolWt(mol), 2))


def slugify(s: str) -> str:
    t = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return t[:60].strip("-") or "structure"


# ---------------------------------------------------------------- inputs

def die(msg: str) -> None:
    print(f"\nFAIL  {msg}", file=sys.stderr)
    raise SystemExit(2)


def load(name: str, *dirs: Path) -> object:
    """First existing copy of `name`, searching `dirs` in order.

    finalise.py writes the working copy into output/ and make_relevant_output.py
    copies it into output/relevant_output/. Either is a correct input, so the stage
    runs whether or not relevant_output has been assembled yet.
    """
    for d in dirs:
        p = d / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    die(f"{name} not found in {', '.join(str(d) for d in dirs)}")


def load_inputs(patent_id: str):
    gold = REL / "gold"
    prov = REL / "provenance"
    compounds = load("compounds.json", gold, OUT)
    reactions = load("reactions.json", gold, OUT)
    drawings = load("structures.json", gold, OUT)
    equivalence = load("compounds-equivalence.json", prov, OUT)

    if not CURATED.exists():
        die(f"{CURATED} not found. Create it with an empty 'entries' object to start.")
    curated = json.loads(CURATED.read_text(encoding="utf-8"))

    # The patent id is load-bearing, not decorative: pointing this stage at one
    # patent's gold and another patent's curated table would resolve names onto the
    # wrong molecules and every downstream mass balance would be quietly wrong.
    if curated.get("patent_id") != patent_id:
        die(f"{CURATED.name} is for patent {curated.get('patent_id')!r}, "
            f"this run is {patent_id!r}")
    wrong = {c.get("patent_id") for c in compounds} - {patent_id}
    if wrong:
        die(f"gold compounds.json carries patent_id {sorted(wrong)}, "
            f"this run is {patent_id!r}")
    return compounds, reactions, drawings, equivalence, curated


# ---------------------------------------------------------------- gold indices

def identifier_universe(compounds, reactions):
    """Every distinct identifier the gold refers to, in first-appearance order.

    compounds.json is the authority, but a reaction can name a product or a charged
    species that never became its own CompoundRecord, and a molecule that appears
    only in a reaction row is exactly the kind the gate cares about. Union, never
    intersection.
    """
    order: list[str] = []
    seen: set[str] = set()

    def add(ident):
        if ident and ident not in seen:
            seen.add(ident)
            order.append(ident)

    for c in compounds:
        add(c.get("identifier"))
    for r in reactions:
        for c in r.get("compounds") or []:
            add(c.get("identifier"))
        add(r.get("product_name"))
    return order


def drawn_index(drawings):
    """canonical SMILES -> the pages that draw it, plus the names used there.

    A SMILES the vision pass read but RDKit cannot parse is reported and skipped
    rather than aborting the run: build_enriched.py has the same policy, and the
    gate below is what decides whether the gap actually matters.
    """
    pages: dict[str, set[str]] = {}
    names: dict[str, set[str]] = {}
    entries = 0
    raw_strings: set[str] = set()
    bad: list[str] = []
    for rec in drawings:
        page = rec.get("page", "?")
        for struct in rec.get("structures") or []:
            raw = struct.get("smiles")
            if not raw:
                continue
            entries += 1
            raw_strings.add(raw)
            mol = Chem.MolFromSmiles(raw)
            if mol is None:
                bad.append(f"{page} {struct.get('name')!r}: RDKit cannot parse {raw!r}")
                continue
            canonical = Chem.MolToSmiles(mol)
            pages.setdefault(canonical, set()).add(page)
            names.setdefault(canonical, set()).add(struct.get("name") or raw)
    return pages, names, entries, raw_strings, bad


def chemistry_carriers(reactions):
    """The identifiers whose structure the artifacts actually need.

    Two populations, for two different reasons:

      products      a route with an unknown product is not a route. Every product of
                    every reaction has to be drawable or the scheme has a hole in it.
      mass + mmol   a row stating both a mass and a mole count is an implicit claim
                    about molecular weight, and checking that claim is the single
                    most valuable thing to do with this patent (its printed pairs
                    imply the des-chloro weights, see FINDINGS.md). Without a formula
                    the row cannot be checked at all.
    """
    products: set[str] = set()
    weighed: set[str] = set()
    for r in reactions:
        for c in r.get("compounds") or []:
            ident = c.get("identifier")
            if not ident:
                continue
            if c.get("is_product"):
                products.add(ident)
            q = c.get("quantity") or {}
            if q.get("mass_g") is not None and q.get("mmol") is not None:
                weighed.add(ident)
        if r.get("product_name"):
            products.add(r["product_name"])
    return products, weighed


# ---------------------------------------------------------------- curated table

def index_curated(curated, universe: list[str]):
    """identifier -> (key, entry, mol), over every entry key and alias.

    Validated hard, because this is the one hand-typed file in the stage. A typo in
    a key silently produces an entry that resolves nothing, and a wrong SMILES
    silently corrupts a mass balance, so both abort the run instead.
    """
    entries = curated.get("entries") or {}
    known = set(universe)
    by_identifier: dict[str, tuple[str, dict, Chem.Mol]] = {}
    claimed: dict[str, str] = {}
    by_slug: dict[str, str] = {}
    by_molecule: dict[str, str] = {}

    for key, entry in entries.items():
        smiles = entry.get("smiles")
        if not smiles:
            die(f"curated {key!r}: no smiles")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            die(f"curated {key!r}: RDKit cannot parse {smiles!r}")
        canonical = Chem.MolToSmiles(mol)

        # Two keys for one molecule should have been a key plus an alias. Left
        # alone it writes one drawing and silently orphans the other entry's slug.
        if by_molecule.get(canonical, key) != key:
            die(f"curated {key!r} is the same molecule as {by_molecule[canonical]!r}; "
                f"make one an alias of the other")
        by_molecule[canonical] = key

        slug = entry.get("slug") or slugify(key)
        if by_slug.get(slug, canonical) != canonical:
            die(f"curated slug {slug!r} is used by two different molecules")
        by_slug[slug] = canonical

        for name in [key, *(entry.get("aliases") or [])]:
            if name not in known:
                die(f"curated {key!r}: {name!r} is not an identifier anywhere in the gold")
            if claimed.get(name, key) != key:
                die(f"identifier {name!r} is claimed by both {claimed[name]!r} and {key!r}")
            claimed[name] = key
            by_identifier[name] = (key, entry, mol)
    return by_identifier, claimed


# ---------------------------------------------------------------- resolution

def resolve(universe, compounds, curated_index, equivalence, drawn_pages):
    """Run the five tiers over every identifier. Returns identifier -> record."""
    types = {c["identifier"]: c.get("identifier_type") for c in compounds}

    # A record's aliases[] is where a structure read off the drawing arrives, which
    # is the same place MolScribe output lands in production. It is the gold's own
    # evidence about its own molecule, so it outranks the hand-authored table.
    own: dict[str, tuple[str, Chem.Mol]] = {}
    for c in compounds:
        if c["identifier"] in own:
            continue
        for a in c.get("aliases") or []:
            mol = as_smiles(a)
            if mol is not None:
                own[c["identifier"]] = (a, mol)
                break

    group_of: dict[str, list[str]] = {}
    for members in equivalence.values():
        for m in members:
            group_of[m] = members

    resolved: dict[str, dict] = {}

    def record(ident, raw, mol, origin, source, note_bits):
        """`raw` is the SMILES as written at its source; `canonical` is RDKit's.

        Both are kept. The written form is what a human can diff against the page or
        the curated table, the canonical form is the join key.
        """
        canonical, formula, mw = describe(mol)
        resolved[ident] = {
            "identifier": ident,
            "smiles": raw,
            "mol": mol,
            "canonical": canonical,
            "formula": formula,
            "mw": mw,
            "origin": origin,
            "source": source,
            "note_bits": list(note_bits),
        }

    # --- tiers 1, 2 and 4: everything an identifier can establish on its own ------
    for ident in universe:
        mol = as_smiles(ident, types.get(ident))
        if mol is not None:
            record(ident, ident, mol, "patent_scheme", ident, [
                "The identifier string is itself a SMILES, read off the drawn scheme."])
            continue

        candidates = []
        if ident in own:
            candidates.append(("the record's own aliases[]", *own[ident]))
        if ident in curated_index:
            entry = curated_index[ident][1]
            candidates.append(("input/structures-curated.json", entry["smiles"],
                               curated_index[ident][2]))
        if not candidates:
            continue

        # Where the record and the table disagree about the molecule, say so and
        # take neither. Picking one silently is how a wrong formula gets shipped.
        canons = {Chem.MolToSmiles(m) for _, _, m in candidates}
        if len(canons) > 1:
            resolved[ident] = {"conflict": sorted(canons)}
            continue

        where, raw, mol = candidates[0]
        canonical = Chem.MolToSmiles(mol)
        if canonical in drawn_pages:
            pages = ", ".join(sorted(drawn_pages[canonical]))
            record(ident, raw, mol, "patent_drawing", ident,
                   [f"Drawn in the patent on {pages}.",
                    f"Structure from {where}."])
        else:
            record(ident, raw, mol, "curated", ident,
                   ["Named in the patent but never drawn.",
                    f"Structure from {where}."])

    # --- tier 3: propagate across equivalence groups -----------------------------
    #
    # finalise.py deliberately does NOT merge the spelling variants, because
    # buildCompoundId is a pure function of the identifier string and production
    # fragments them identically. So the gold carries one molecule under up to three
    # names, and the structure has to travel along the equivalence index instead.
    #
    # Donors are taken from a snapshot of the tiers above, never from another
    # derived entry. Deriving from a derivation would make the note point at a
    # record that is itself second-hand, and the whole value of the note is that it
    # names where the structure actually came from. Strongest origin wins the credit.
    settled = dict(resolved)
    rank = {"patent_scheme": 0, "patent_drawing": 1, "curated": 2}
    for ident in universe:
        if ident in resolved or ident not in group_of:
            continue
        donors = [m for m in group_of[ident]
                  if m != ident and settled.get(m, {}).get("mol") is not None]
        if not donors:
            continue
        canons = {settled[d]["canonical"] for d in donors}
        if len(canons) > 1:
            resolved[ident] = {"conflict": sorted(canons)}
            continue
        donor = sorted(donors, key=lambda d: (rank[settled[d]["origin"]], d))[0]
        src = settled[donor]
        drawn = " It is drawn in the patent." if src["origin"] == "patent_drawing" else ""
        record(ident, src["smiles"], src["mol"], "derived", donor,
               [f"Same molecule as {donor!r}, via provenance/compounds-equivalence.json.{drawn}"])

    return resolved


def assemble(universe, resolved, curated_index, no_structure_needed):
    """Turn the resolution into the artifact: one entry per distinct identifier."""
    by_canonical: dict[str, list[str]] = {}
    for ident in universe:
        r = resolved.get(ident)
        if r and r.get("canonical"):
            by_canonical.setdefault(r["canonical"], []).append(ident)

    # One slug per MOLECULE, not per identifier, so the three spellings of one
    # intermediate share one SVG instead of writing the same drawing three times.
    slugs: dict[str, str] = {}
    for canonical, idents in by_canonical.items():
        named = [i for i in idents if not looks_like_smiles(i)]
        curated_slug = next((curated_index[i][1].get("slug")
                             for i in idents if i in curated_index
                             and curated_index[i][1].get("slug")), None)
        # Deterministic without the curated hint too: prefer a human name over a
        # SMILES identifier, then the shortest, then alphabetical.
        preferred = sorted(named or idents, key=lambda s: (len(s), s))[0]
        slugs[canonical] = curated_slug or slugify(preferred)

    out = []
    for ident in universe:
        r = resolved.get(ident) or {}
        curated_note = (curated_index[ident][1].get("note")
                        if ident in curated_index else None)
        if r.get("conflict"):
            note = ("UNRESOLVED, CONFLICT: two sources give this identifier different "
                    "molecules: " + " vs ".join(r["conflict"]))
            out.append({"identifier": ident, "smiles": None, "canonical": None,
                        "formula": None, "mw": None, "origin": "none", "svg": None,
                        "aliases": [], "note": note})
            continue
        if not r:
            if is_trivial(ident, no_structure_needed):
                note = "No structure needed: trivial species, carries none of this patent's chemistry."
            else:
                note = ("No structure. Not drawn in the patent, no entry in "
                        "input/structures-curated.json, and no resolved synonym.")
            out.append({"identifier": ident, "smiles": None, "canonical": None,
                        "formula": None, "mw": None, "origin": "none", "svg": None,
                        "aliases": [], "note": " ".join(x for x in (note, curated_note) if x)})
            continue

        canonical = r["canonical"]
        aliases = [i for i in by_canonical[canonical] if i != ident]
        out.append({
            "identifier": ident,
            "smiles": r["smiles"],
            "canonical": canonical,
            "formula": r["formula"],
            "mw": r["mw"],
            "origin": r["origin"],
            "svg": f"{SVG_SUBDIR}/{slugs[canonical]}.svg",
            "aliases": aliases,
            "note": " ".join(x for x in r["note_bits"] + [curated_note] if x),
        })
    return out, by_canonical, slugs


# ---------------------------------------------------------------- rendering

def render(mol: Chem.Mol, path: Path) -> None:
    """One monochrome drawing on a transparent ground.

    Monochrome because no meaning may rest on colour, and because a flat black
    drawing over a transparent ground survives `filter: invert(1)` on a dark
    background: black lines become white, the ground stays transparent. An
    element-coloured drawing inverts into nonsense, red O becoming cyan O.
    """
    drawer = rdMolDraw2D.MolDraw2DSVG(WIDTH, HEIGHT)
    opts = drawer.drawOptions()
    opts.useBWAtomPalette()
    opts.clearBackground = False
    opts.bondLineWidth = 2
    opts.padding = 0.08
    opts.addStereoAnnotation = False
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
    drawer.FinishDrawing()
    path.write_text(drawer.GetDrawingText(), encoding="utf-8")


def write_svgs(resolved, by_canonical, slugs, svg_dir: Path):
    svg_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for canonical, idents in by_canonical.items():
        slug = slugs[canonical]
        render(resolved[idents[0]]["mol"], svg_dir / f"{slug}.svg")
        written.append(slug)
    # Re-running after an identifier is renamed or dropped must converge, so a
    # drawing no molecule claims any more is removed rather than left to rot.
    stale = sorted({p.name for p in svg_dir.glob("*.svg")} - {f"{s}.svg" for s in written})
    for name in stale:
        (svg_dir / name).unlink()
    return sorted(written), stale


# ---------------------------------------------------------------- the gate

def gate(entries, products, weighed, no_structure_needed):
    """Which identifiers carry chemistry, and which of those have no structure."""
    by_ident = {e["identifier"]: e for e in entries}
    carriers = []
    for ident in by_ident:
        why = []
        if ident in products:
            why.append("product")
        if ident in weighed:
            why.append("mass_g + mmol")
        if why:
            carriers.append((ident, why))

    missing, exempt = [], []
    for ident, why in carriers:
        if by_ident[ident]["formula"] is not None:
            continue
        (exempt if is_trivial(ident, no_structure_needed) else missing).append((ident, why))
    return carriers, missing, exempt


def stub(missing) -> str:
    """A ready-to-paste block for input/structures-curated.json."""
    lines = ['  "entries": {']
    for i, (ident, why) in enumerate(missing):
        tail = "" if i == len(missing) - 1 else ","
        lines.append(f'    {json.dumps(ident, ensure_ascii=False)}: {{')
        lines.append('      "smiles": "",')
        lines.append(f'      "note": "{" and ".join(why)}. Structure hand-authored, '
                     'checked atom by atom against the name."')
        lines.append(f"    }}{tail}")
    lines.append("  }")
    return "\n".join(lines)


# ---------------------------------------------------------------- report

ORIGINS = ["patent_scheme", "patent_drawing", "derived", "curated", "none"]

ORIGIN_MEANING = {
    "patent_scheme": "the identifier string is itself a SMILES",
    "patent_drawing": "the molecule is drawn in the patent",
    "derived": "same molecule as a synonym, via the equivalence index",
    "curated": "named but never drawn, from input/structures-curated.json",
    "none": "no structure",
}


def main() -> int:
    check = "--check" in sys.argv
    try:
        patent_id = resolve_patent_id()
    except ContextError as e:
        print(f"FAIL  {e}", file=sys.stderr)
        return 2

    compounds, reactions, drawings, equivalence, curated = load_inputs(patent_id)
    no_structure_needed = {normalise_name(s)
                           for s in curated.get("no_structure_needed") or []}

    universe = identifier_universe(compounds, reactions)
    drawn_pages, drawn_names, drawn_entries, drawn_raw, bad_drawn = drawn_index(drawings)
    curated_index, claimed = index_curated(curated, universe)
    products, weighed = chemistry_carriers(reactions)

    resolved = resolve(universe, compounds, curated_index, equivalence, drawn_pages)
    entries, by_canonical, slugs = assemble(universe, resolved, curated_index,
                                            no_structure_needed)

    svg_dir = OUT / SVG_SUBDIR
    if check:
        written, stale = sorted(slugs.values()), []
    else:
        (OUT / "structures-resolved.json").write_text(
            json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written, stale = write_svgs(resolved, by_canonical, slugs, svg_dir)

    carriers, missing, exempt = gate(entries, products, weighed, no_structure_needed)

    # ---- report -------------------------------------------------------------
    print(f"patent    : {patent_id}")
    print(f"drawings  : {drawn_entries} SMILES entries in structures.json, "
          f"{len(drawn_raw)} distinct strings, {len(drawn_pages)} unique molecules")
    print(f"            {sum(len(v) for v in drawn_names.values())} distinct drawn names "
          f"over those {len(drawn_pages)} molecules")
    for b in bad_drawn:
        print(f"            UNPARSEABLE, skipped: {b}")
    print(f"curated   : {len(curated.get('entries') or {})} entries covering "
          f"{len(claimed)} identifiers")
    print()

    counts = {o: sum(1 for e in entries if e["origin"] == o) for o in ORIGINS}
    print(f"{len(entries)} distinct compound identifiers resolved:")
    for o in ORIGINS:
        print(f"  {o:16} {counts[o]:4}   {ORIGIN_MEANING[o]}")
    covered = len(set(drawn_pages) & set(by_canonical))
    print(f"\n  {len(by_canonical)} unique molecules, {len(written)} SVG at "
          f"{WIDTH}x{HEIGHT}, monochrome{' (--check, not written)' if check else ''}")
    print(f"  {covered}/{len(drawn_pages)} molecules drawn in the patent are resolved")
    for name in stale:
        print(f"  removed stale drawing no molecule claims: {name}")
    if not check:
        print(f"\nwrote {(OUT / 'structures-resolved.json').relative_to(HERE)}"
              f" and {len(written)} drawings in {svg_dir.relative_to(HERE)}/")

    conflicts = [i for i, r in resolved.items() if r.get("conflict")]
    if conflicts:
        print(f"\nsources disagree about the molecule, so neither was taken ({len(conflicts)}):")
        for i in conflicts:
            print(f"  {i}\n    " + " vs ".join(resolved[i]["conflict"]))

    print(f"\ncoverage gate: {len(carriers)} identifiers carry chemistry "
          f"({len(products)} are a reaction product, {len(weighed)} carry mass_g + mmol)")
    if exempt:
        print(f"  no structure needed, not demanded ({len(exempt)}): "
              + ", ".join(i for i, _ in exempt))
    if not missing:
        print(f"  all {len(carriers)} resolve to a structure with a formula. PASS")
        return 0

    print(f"\n  {len(missing)} carry chemistry and have NO structure. FAIL")
    for ident, why in missing:
        print(f"    {ident}   ({' and '.join(why)})")
    print("\n  Hand-author them, checking each SMILES atom by atom against the name,")
    print(f"  and merge this into {CURATED.relative_to(HERE)}:\n")
    print(stub(missing))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
