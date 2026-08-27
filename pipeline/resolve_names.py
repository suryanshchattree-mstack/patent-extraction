#!/usr/bin/env python3
r"""Read every compound name a second time, with a parser instead of a model.

WHY A SECOND READER, AND WHY THIS ONE

Every structure in this pack traces back to one source: a vision pass that looked at
the drawn scheme, or a hand-typed line in input/structures-curated.json. Both are a
model or a person reading the same document once. Agreement with itself proves
nothing, and there is no gold standard for this patent to compare against - the
survey in patent-extraction-verification/ went looking and found none.

OPSIN is the cheapest independent reader available. It converts a systematic
chemical NAME into a structure by grammar, with no knowledge of this patent, no
model, and no shared failure mode with a vision pass. When it lands on the same
molecule the drawing did, two unrelated routes to the same answer agreed. When it
does not, exactly one of them is wrong and the reviewer has somewhere to look.

WHAT IT MAY NOT DO

It may not be the reason a structure exists AND the check on that structure. A
check that reads its own output is not a check. So a parse is consulted LAST as a
provider - after the drawing, after the equivalence groups, after the curated table
- and independently as a cross-check over everything, including the entries it did
not provide.

THREE OUTCOMES, KEPT APART

  parsed        some string OPSIN accepted outright. A structure.
  ambiguous     OPSIN returned WARNING: the name does not pin one molecule down and
                it guessed. Its guess is recorded and is NOT a structure. This is
                the outcome worth having: `cyclohexanedione` is three different
                molecules, all with formula C6H8O2 and mass 112.13, so no arithmetic
                check anywhere in this pipeline can tell them apart. A name parser
                can, and it is the only thing here that can.
  unparseable   trade names (tembotrione), abbreviations (NBS), SMILES used as an
                identifier, and anything not in English. Not a defect by itself.

A WARNING IS NEVER PROMOTED TO A STRUCTURE. Doing so would take OPSIN's guess at an
under-specified name and file it beside a molecule somebody actually drew, at equal
weight and with nothing on screen to say which was which.

QUALIFIERS

"anhydrous aluminium trichloride" fails and "aluminium trichloride" parses. Stripping
a leading qualifier is worth doing and is worth SAYING: the entry records the exact
string that parsed, so a reader can see the parse was of a modified name.

NETWORK

There is no Java runtime on this machine, so this calls the public OPSIN service
rather than the jar. Every answer is cached under input/opsin-cache.json keyed by the
exact query string, so the first run needs the network and no later run does. A name
that is neither cached nor reachable is reported as such and stops the stage; it is
never quietly treated as unparseable, because "we could not ask" and "the answer is
no" are different facts and only one of them is about the chemistry.

Usage:  python3 resolve_names.py                  # discovers the patent id
        python3 resolve_names.py CN104292137A
        python3 resolve_names.py --offline         # cache only, never touch the network
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from rdkit import Chem, RDLogger

from pipeline_context import INPUT, OUTPUT, resolve_patent_id

RDLogger.DisableLog("rdApp.*")

SERVICE = "https://opsin.ch.cam.ac.uk/opsin/"
CACHE = INPUT / "opsin-cache.json"
OUT = OUTPUT / "names-opsin.json"

# Stripped only from the FRONT of a name, only as whole words, and always recorded.
# These say something about the bottle, not about the molecule.
QUALIFIERS = ("anhydrous", "concentrated", "aqueous", "saturated", "dry",
              "glacial", "fuming", "dilute", "ice", "cold", "hot", "fresh",
              "solid", "liquid", "gaseous", "crude", "pure")

# The patent's prose, not the chemistry. "the methyl sulfide" is methyl sulfide.
ARTICLES = {"the", "a", "an", "said", "this", "that"}

# Trailing nouns that describe the bottle rather than the molecule. "aqueous sodium
# hydroxide solution" is sodium hydroxide, in water, and OPSIN parses neither the
# whole phrase nor "sodium hydroxide solution".
TRAILING = {"solution", "solutions", "solvent", "reagent", "salt"}


# ---------------------------------------------------------------- the English form

def load_translations() -> dict[str, str]:
    """Chinese string -> the English this pipeline already carries for it.

    Five identifiers on this patent are Chinese, and a grammar for English chemical
    nomenclature has nothing to say about any of them. Reporting five `unparseable`
    would be true and useless: the pack HAS an English form for all five, sitting in
    input/translations-curated.json, and simply never offered it to the parser.

    Taking the curated file rather than output/translations.json on purpose. The
    curated file is an INPUT, so this stage can run before the translations stage;
    reaching for that stage's output would make two stages depend on each other's
    order for no gain.
    """
    out: dict[str, str] = {}
    f = INPUT / "translations-curated.json"
    if not f.exists():
        return out
    try:
        doc = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    for zh, entry in (doc.get("entries") or {}).items():
        en = entry.get("en") if isinstance(entry, dict) else entry
        if isinstance(en, str) and en.strip():
            out[zh] = en.strip()
    return out


def english_forms(en: str) -> list[str]:
    """The names inside a translation, most literal first.

    A translation is written for a reader, not a parser: 'methyl sulfide (methyl
    thioether)' offers two names and 'xiaohuanhuangtong [herbicide name exactly as
    printed; ...]' offers one name and a note about it. Square brackets are the
    translator talking and are dropped; round brackets are a second name for the same
    thing and are tried.
    """
    en = re.sub(r"\[[^\]]*\]", " ", en)
    inner = re.findall(r"\(([^)]*)\)", en)
    head = re.sub(r"\([^)]*\)", " ", en)
    out = []
    for cand in [head, *inner]:
        cand = " ".join(cand.split()).strip(" ,;:")
        if cand and cand not in out:
            out.append(cand)
    return out


# ---------------------------------------------------------------- the service

class Unreachable(RuntimeError):
    """Not in the cache and the service could not be asked."""


def load_cache() -> dict:
    if not CACHE.exists():
        return {}
    try:
        doc = json.loads(CACHE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return doc.get("answers") or {}


def ask(query: str, cache: dict, offline: bool) -> dict:
    """OPSIN's answer for one exact string. Cache first, always."""
    if query in cache:
        return cache[query]
    if offline:
        raise Unreachable(query)
    url = SERVICE + urllib.parse.quote(query, safe="")
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            doc = json.loads(r.read().decode("utf-8"))
        ans = {"status": doc.get("status"), "smiles": doc.get("smiles"),
               "message": doc.get("message") or ""}
    except urllib.error.HTTPError as e:
        # The service answers 404 for a name it cannot parse at all. That IS an
        # answer and it caches; anything else is a failure to ask and does not.
        if e.code != 404:
            raise Unreachable(f"{query}: HTTP {e.code}") from e
        ans = {"status": "FAILURE", "smiles": None, "message": "not parsed"}
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        raise Unreachable(f"{query}: {e}") from e
    cache[query] = ans
    time.sleep(0.1)          # the service is free and public; do not hammer it
    return ans


# ---------------------------------------------------------------- the attempts

def is_english(s: str) -> bool:
    return not any(ord(ch) > 0x2E7F for ch in s)


def candidates(identifier: str, aliases: list[str],
               english: dict[str, str]) -> list[tuple[str, str]]:
    """(string to try, how we got it), in the order they should be tried."""
    out: list[tuple[str, str]] = [(identifier, "verbatim")]
    for a in aliases:
        if a and a != identifier:
            out.append((a, "alias"))
    # The pipeline's own English for anything not in English, including aliases: a
    # record can carry a Chinese synonym of an English identifier and that synonym is
    # a second chance at the same molecule.
    for name in [identifier, *aliases]:
        if name and not is_english(name) and name in english:
            for form in english_forms(english[name]):
                out.append((form, f"the pipeline's English for {name}"))
    # Applied REPEATEDLY and from both ends, because they compose: "aqueous sodium
    # hydroxide solution" needs the leading qualifier and the trailing noun gone
    # before OPSIN sees a name it recognises, and one pass from the front leaves
    # "sodium hydroxide solution", which it does not.
    for name, _ in list(out):
        cur, dropped = name, []
        for _ in range(4):
            words = cur.split()
            if len(words) > 1 and words[0].lower().strip(",") in ARTICLES | set(QUALIFIERS):
                dropped.append(words[0])
                cur = " ".join(words[1:])
                continue
            if len(words) > 1 and words[-1].lower().strip(",.") in TRAILING:
                dropped.append(words[-1])
                cur = " ".join(words[:-1])
                continue
            break
        if dropped and cur != name:
            out.append((cur, f"dropped {', '.join(repr(d) for d in dropped)}"))
    seen, uniq = set(), []
    for s, how in out:
        if s not in seen:
            seen.add(s)
            uniq.append((s, how))
    return uniq


def looks_like_smiles(s: str) -> bool:
    """A SMILES used as an identifier. Asking a name parser about it is meaningless."""
    if " " in s or not s:
        return False
    return bool(Chem.MolFromSmiles(s)) and any(c in s for c in "()[]=#123456789")


def canonical(smiles: str | None) -> str | None:
    if not smiles:
        return None
    m = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(m) if m else None


def read_name(identifier: str, aliases: list[str], cache: dict,
              offline: bool, english: dict[str, str]) -> dict:
    """One identifier, read by OPSIN. See the module docstring for the outcomes."""
    if looks_like_smiles(identifier):
        return {"identifier": identifier, "outcome": "unparseable",
                "reason": "the identifier is itself a SMILES string, so there is no "
                          "name to parse; the structure is already explicit",
                "attempts": []}

    attempts, warning = [], None
    for query, how in candidates(identifier, aliases, english):
        if not is_english(query):
            attempts.append({"query": query, "via": how, "status": "NOT_ASKED",
                             "note": "not English; OPSIN parses English chemical "
                                     "nomenclature only"})
            continue
        ans = ask(query, cache, offline)
        row = {"query": query, "via": how, "status": ans["status"]}
        if ans.get("message"):
            row["note"] = ans["message"]
        attempts.append(row)
        if ans["status"] == "SUCCESS":
            can = canonical(ans["smiles"])
            if can:
                return {"identifier": identifier, "outcome": "parsed",
                        "query": query, "via": how, "smiles": ans["smiles"],
                        "canonical": can, "attempts": attempts}
            row["note"] = "OPSIN succeeded but RDKit could not read the SMILES back"
        elif ans["status"] == "WARNING" and warning is None:
            warning = (query, how, ans["smiles"])

    if warning is not None:
        query, how, smi = warning
        return {"identifier": identifier, "outcome": "ambiguous", "query": query,
                "via": how, "guess_smiles": smi, "guess_canonical": canonical(smi),
                "reason": "OPSIN parsed this name but warned that it does not pin one "
                          "molecule down. Its guess is recorded and is deliberately "
                          "NOT used as a structure.",
                "attempts": attempts}
    tried = [a["query"] for a in attempts if a["status"] != "NOT_ASKED"]
    # Naming what was tried, because "unparseable" alone is unactionable and the list
    # is often the finding. 1,2-dichloromethane is refused because dichloromethane has
    # one carbon and therefore no 1,2 positions; a reader who cannot see that the
    # parser was given that exact string cannot see that either.
    return {"identifier": identifier, "outcome": "unparseable",
            "reason": ("no spelling of this name was accepted"
                       + (f"; tried {', '.join(repr(t) for t in tried)}" if tried
                          else " and no English spelling was available to try")
                       + ". Usually a trade name, an abbreviation, a compound class "
                         "rather than a compound, or a name that cannot be built."),
            "attempts": attempts}


# ---------------------------------------------------------------- the universe

def observed_spans() -> list[str]:
    """Every substance NAME the second reading saw printed on a line.

    The recall sweep asks whether each of these is in some record. It cannot ask
    that of a name it has no structure for, and a name-to-structure answer is
    exactly what this stage produces, so the spans join the same universe and get
    the same cache rather than a second resolver appearing somewhere downstream.

    Only `specific` spans. A generic reference - "the mixture", "an inorganic base"
    - names no molecule by construction and asking a grammar about it would fill the
    cache with 26 guaranteed failures and teach a reader nothing.
    """
    f = INPUT / "substances-observed.json"
    if not f.exists():
        return []
    try:
        doc = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return sorted({m["span"] for row in (doc.get("lines") or {}).values()
                   for m in row if m.get("kind") == "specific"})


def universe(patent_id: str) -> list[tuple[str, list[str]]]:
    """Every identifier the structures stage will be asked about, with its aliases.

    Read from structures-resolved.json when it exists, because that is where the
    equivalence groups have already been collapsed and the alias lists are complete.
    Falling back to gold/compounds.json keeps this stage runnable on a fresh pack
    where structures has never run.
    """
    extra = observed_spans()

    prior = OUTPUT / "structures-resolved.json"
    if prior.exists():
        rows = json.loads(prior.read_text(encoding="utf-8"))
        out = [(r["identifier"], list(r.get("aliases") or [])) for r in rows]
        known = {i for i, _ in out}
        return out + [(s, []) for s in extra if s not in known]

    for cand in (OUTPUT / "relevant_output" / "gold" / "compounds.json",
                 OUTPUT / "compounds.json"):
        if cand.exists():
            doc = json.loads(cand.read_text(encoding="utf-8"))
            recs = doc if isinstance(doc, list) else doc.get("compounds") or []
            out, seen = [], set()
            for r in recs:
                ident = (r.get("identifier") or "").strip()
                if ident and ident not in seen:
                    seen.add(ident)
                    out.append((ident, [a for a in (r.get("aliases") or []) if a]))
            return out + [(s, []) for s in extra if s not in seen]
    sys.exit("no structures-resolved.json and no compounds.json to take identifiers from")


# ---------------------------------------------------------------- report

def main() -> int:
    argv = sys.argv[1:]
    offline = "--offline" in argv
    patent_id = resolve_patent_id([a for a in argv if a != "--offline"])

    cache = load_cache()
    english = load_translations()
    cached_before = len(cache)
    ids = universe(patent_id)

    rows, unreachable = [], []
    for ident, aliases in ids:
        try:
            rows.append(read_name(ident, aliases, cache, offline, english))
        except Unreachable as e:
            unreachable.append(str(e))

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(
        {"service": SERVICE,
         "what": "OPSIN's answer for one exact query string. Written so that a re-run "
                 "needs no network and returns exactly what this run saw.",
         "answers": dict(sorted(cache.items()))}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")

    if unreachable:
        print(f"\nFAIL  {len(unreachable)} name(s) are neither cached nor reachable. "
              f"This is not\n      a statement about the chemistry, so the stage stops "
              f"rather than filing\n      them as unparseable:", file=sys.stderr)
        for u in unreachable[:10]:
            print(f"        {u}", file=sys.stderr)
        return 1

    by = {}
    for r in rows:
        by.setdefault(r["outcome"], []).append(r)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"patent_id": patent_id,
         "engine": "OPSIN via " + SERVICE,
         "what_this_is_en":
             "Every compound identifier in the gold, read a second time by a name "
             "parser that knows nothing about this patent. A parse is used as a "
             "structure only where nothing better exists, and is compared against "
             "every structure the pipeline already had.",
         "summary": {k: len(v) for k, v in sorted(by.items())},
         "names": rows}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"patent    : {patent_id}")
    print(f"identifiers: {len(ids)}")
    for k in ("parsed", "ambiguous", "unparseable"):
        print(f"  {k:12} {len(by.get(k, [])):3}")
    print(f"cache     : {cached_before} -> {len(cache)} answers in "
          f"{CACHE.relative_to(INPUT.parent)}")

    amb = by.get("ambiguous") or []
    if amb:
        print(f"\n{len(amb)} name(s) OPSIN will not pin down. These are worth a human, "
              f"because no\nformula or mass check in this pipeline can separate the "
              f"molecules they could mean:")
        for r in amb:
            print(f"    {r['identifier']}  (OPSIN's guess: {r.get('guess_canonical')})")

    print(f"\nwrote {OUT.relative_to(OUTPUT.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
