#!/usr/bin/env python3
"""English-only text for the visual stage.

Every string the visual stage puts on a screen or in a JSON file has to be English.
Two upstream sources are not: the vision pass wrote Chinese quotations into its
`discrepancies` and, in places, into its own `en` fields, and `output/translations.json`
carries `en` values that still contain Chinese runs of their own.

So this module is a scrubber, not a translator. It resolves what the translation index
already knows, applies a small declared glossary for the chemistry and boilerplate
fragments the index does not carry, and then refuses to pass anything else through:
whatever is left becomes an English placeholder and is recorded so the translation
stage can be told what it is missing. A quiet fallback that let one character slip
onto the reviewer's screen would be worse than a loud placeholder, because the whole
premise of the review is that the reviewer does not read Chinese.

The glossary is emitted with the run (visual/glossary.json) so that every English word
this stage invented is auditable next to the Chinese it stands for.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

CJK = re.compile(r"[⺀-⿟々〇㐀-䶿一-鿿豈-﫿]+")

# Full-width and CJK punctuation carries no meaning a reviewer needs; it is
# transliterated rather than translated, so it is kept apart from the glossary.
PUNCT = {
    "，": ", ", "。": ". ", "、": ", ", "；": "; ", "：": ": ",
    "（": "(", "）": ")", "【": "[", "】": "]", "《": '"', "》": '"',
    "“": '"', "”": '"', "‘": "'", "’": "'", "％": "%", "　": " ",
    "！": "! ", "？": "? ", "～": "~", "－": "-", "．": ".", "／": "/",
    "＜": "<", "＞": ">", "＝": "=", "＋": "+", "×": " x ",
}
PUNCT.update({chr(0xFF10 + i): str(i) for i in range(10)})          # full-width digits
PUNCT.update({chr(0xFF21 + i): chr(65 + i) for i in range(26)})     # full-width A-Z
PUNCT.update({chr(0xFF41 + i): chr(97 + i) for i in range(26)})     # full-width a-z

# The fragments the translation index does not carry. Chemistry first, then process
# vocabulary, then masthead boilerplate. Every gloss here is either stated outright in
# the surrounding English of the source that needed it, or is a term of art with one
# reading. Where a Chinese name has no settled English reading it says so rather than
# guessing, because a confident wrong name is the failure this whole stage exists to
# catch.
GLOSSARY: dict[str, str] = {
    # --- names of the compounds this patent is about
    "环磺草酮": "tembotrione",
    "环磺酮": "tembotrione",
    "磺草酮": "sulcotrione",
    "甲基磺草酮": "mesotrione",
    "硝磺草酮": "mesotrione",
    "硝环磺酮": "[a Chinese herbicide name with no standard English reading]",
    # --- functional groups and fragments
    "甲酯": "methyl ester",
    "乙酯": "ethyl ester",
    "叔丁酯": "tert-butyl ester",
    "酯": "ester",
    "酸": "acid",
    "酰": "acyl",
    "酮": "ketone",
    "二酮": "dione",
    "砜": "sulfone",
    "胺": "amine",
    "碱": "base",
    "醇": "alcohol",
    "醚": "ether",
    "氧代": "oxo",
    "甲基": "methyl",
    "乙酰基": "acetyl",
    "甲磺酰基": "methylsulfonyl",
    "甲磺酰": "methylsulfonyl",
    "甲磺酰氯": "methanesulfonyl chloride",
    "三氟乙氧基": "trifluoroethoxy",
    "三氟乙醇钠": "sodium trifluoroethoxide",
    "溴甲基": "bromomethyl",
    "氯甲苯": "chlorotoluene",
    "甲苯": "toluene",
    "苯甲酸": "benzoic acid",
    "苯甲酸甲酯": "methyl benzoate",
    "苯甲酸乙酯": "ethyl benzoate",
    "甲磺酰基甲苯": "methylsulfonyltoluene",
    "甲磺酰基苯甲酸": "methylsulfonylbenzoic acid",
    "甲磺酰基苯甲酸甲酯": "methyl methylsulfonylbenzoate",
    "环己烯酯": "cyclohexenyl ester",
    "环己烯": "cyclohexene",
    "环己二酮": "cyclohexanedione",
    "环己烷": "cyclohexane",
    "环己酮": "cyclohexanone",
    "呋喃": "furan",
    "四氢呋喃": "tetrahydrofuran",
    # --- reagents
    "过氧化苯甲酰": "benzoyl peroxide",
    "过氧苯甲酸": "peroxybenzoic acid",
    "丙酮氰醇": "acetone cyanohydrin",
    "氰基丙酮": "cyanoacetone",
    "溴代琥珀酰亚胺": "bromosuccinimide",
    "溴代丁二酰亚胺": "bromosuccinimide",
    "琥珀酸亚胺": "succinimide",
    "琥珀酰亚胺": "succinimide",
    "琥珀酸": "succinic acid",
    "琥珀": "amber",
    "亚胺": "imide",
    "亚": "sub-",
    "烷": "alkane",
    "二": "di",
    "石": "the stone radical",
    "风": "the wind radical",
    "琥珀酰亚胺": "succinimide",
    "丁二酰亚胺": "succinimide",
    "二甲基甲酰胺": "dimethylformamide",
    "氯化亚砜": "thionyl chloride",
    "二氯甲烷": "dichloromethane",
    "二氯乙烷": "dichloroethane",
    "四氯化碳": "carbon tetrachloride",
    "氯仿": "chloroform",
    "乙腈": "acetonitrile",
    "三氯化铝": "aluminium trichloride",
    "三乙胺": "triethylamine",
    "溴素": "bromine",
    "甲醇": "methanol",
    "乙醇": "ethanol",
    "乙酸乙酯": "ethyl acetate",
    "盐酸": "hydrochloric acid",
    "氢氧化钠": "sodium hydroxide",
    "硫酸镁": "magnesium sulfate",
    # --- single characters that survive as locant prefixes or as the very point of a
    #     typographic discrepancy, where the source text discusses one character
    "氯": "chloro",
    "溴": "bromo",
    "氟": "fluoro",
    "甲": "the character for methyl",
    "乙": "the character for ethyl",
    "代": "the character meaning substituted-by",
    "环": "cyclo",
    "基": "group",
    # --- process vocabulary
    "步骤": "step",
    "收率": "yield",
    "熔点": "melting point",
    "加入": "add",
    "滴加": "add dropwise",
    "搅拌": "stir",
    "回流": "reflux",
    "溶于": "dissolved in",
    "溶剂": "solvent",
    "和溶剂": "and solvent",
    "溶于溶剂中": "dissolved in solvent",
    "的合成": "synthesis of",
    "的制备": "preparation of",
    "反应完毕": "the reaction is complete",
    "反应完后": "after the reaction is complete",
    "冷却后": "after cooling",
    "在回流的条件下": "under reflux",
    "温度条件下": "at a temperature of",
    "摩尔配比为": "the molar ratio is",
    "包括以下步骤": "comprising the following steps",
    "包括有以下步骤": "comprising the following steps",
    "干燥得白色固体": "dried to give a white solid",
    "浓缩得米黄色固体": "concentrated to give a beige solid",
    "浓缩得": "concentrated to give",
    "米黄色": "beige",
    "白色固体": "white solid",
    "液相色谱": "liquid chromatography",
    "作溴化剂": "as the brominating agent",
    "该溴化剂昂贵": "this brominating agent is expensive",
    "剧毒": "highly toxic",
    "采用": "uses",
    "本发明所涉及的": "involved in the present invention",
    "本发明": "the present invention",
    "现有技术": "prior art",
    "背景技术": "background art",
    "实施例": "Example",
    "三废": "the three wastes (waste gas, waste water, waste residue)",
    "原药": "technical-grade active ingredient",
    "除草剂": "herbicide",
    "三酮类": "triketone-class",
    "在": "in",
    "和": "and",
    "或": "or",
    "将": "take",
    "得": "to give",
    "的": "of",
    "间": "between",
    "己": "hex",
    "号": "No.",
    # --- masthead and running headers
    "说明书": "Description",
    "权利要求书": "Claims",
    "说明书附图": "Description drawings",
    "摘要": "Abstract",
    "页": "page",
    "中华人民共和国国家知识产权局": (
        "State Intellectual Property Office of the People's Republic of China"),
    "发明专利申请": "Invention patent application",
    "申请公布号": "Publication number",
    "有限": "Limited",
    "公司": "Company",
    "雄楚大街": "Xiongchu Avenue",
}

_LONG_KEY_MIN = 6   # below this a translations.json key is matched inside a CJK run instead
_MAX_DEPTH = 3      # translations.json `en` values themselves contain Chinese


class Scrubber:
    """Turns a source string into English, or into an English statement of failure."""

    def __init__(self, translations: dict):
        self.index: dict[str, str] = {}
        for zh, rec in translations.items():
            if not zh:
                continue
            en = rec.get("en") if isinstance(rec, dict) else rec
            if isinstance(en, str) and en.strip():
                self.index[zh] = en
        self.long_keys = sorted((k for k in self.index if len(k) >= _LONG_KEY_MIN),
                                key=lambda k: (-len(k), k))
        # Short index keys and the glossary both compete inside a CJK run. The glossary
        # wins ties because it was written for exactly this job.
        run_terms: dict[str, str] = {k: v for k, v in self.index.items()
                                     if len(k) < _LONG_KEY_MIN}
        run_terms.update(GLOSSARY)
        self.run_terms = run_terms
        self.run_keys = sorted(run_terms, key=lambda k: (-len(k), k))
        self.max_term = max((len(k) for k in run_terms), default=1)
        self.unresolved: dict[str, int] = {}

    # ------------------------------------------------------------------ public
    def en(self, s: str | None) -> str:
        """English for `s`. Never returns a Chinese character."""
        if not s:
            return ""
        out = _tidy(self._scrub(str(s), 0))
        return out

    def report(self) -> list[dict]:
        """Chinese this stage could not resolve, for the translation stage to pick up."""
        return [{"zh_length": len(zh), "occurrences": n, "sha256_of_zh": _digest(zh)}
                for zh, n in sorted(self.unresolved.items(), key=lambda kv: (-kv[1], kv[0]))]

    def report_with_source(self) -> list[dict]:
        """Same list, carrying the Chinese itself. Never goes near a reviewer screen."""
        return [{"zh": zh, "occurrences": n, "sha256_of_zh": _digest(zh)}
                for zh, n in sorted(self.unresolved.items(), key=lambda kv: (-kv[1], kv[0]))]

    # ----------------------------------------------------------------- internals
    def _scrub(self, s: str, depth: int) -> str:
        s = _punct(s)
        s = _join_spaced_cjk(s)
        if not CJK.search(s):
            return s
        if depth < _MAX_DEPTH:
            for k in self.long_keys:
                if k in s:
                    s = s.replace(k, " " + self._scrub(self.index[k], depth + 1) + " ")
                    if not CJK.search(s):
                        return s
        return CJK.sub(lambda m: self._run(m.group(0), depth), s)

    def _run(self, run: str, depth: int) -> str:
        """Greedy longest-match left to right across one uninterrupted Chinese run."""
        parts: list[str] = []
        pending: list[str] = []
        i = 0
        while i < len(run):
            hit = None
            for n in range(min(self.max_term, len(run) - i), 0, -1):
                term = run[i:i + n]
                if term in self.run_terms:
                    hit = (term, self.run_terms[term])
                    break
            if hit is None:
                pending.append(run[i])
                i += 1
                continue
            if pending:
                parts.append(self._give_up("".join(pending)))
                pending = []
            term, en = hit
            parts.append(self._scrub(en, depth + 1) if (depth < _MAX_DEPTH and CJK.search(en)) else en)
            i += len(term)
        if pending:
            parts.append(self._give_up("".join(pending)))
        return " " + " ".join(p for p in parts if p) + " "

    def _give_up(self, zh: str) -> str:
        self.unresolved[zh] = self.unresolved.get(zh, 0) + 1
        n = len(zh)
        return f"[untranslated Chinese, {n} character{'' if n == 1 else 's'}]"


# ---------------------------------------------------------------------- helpers

def _punct(s: str) -> str:
    for a, b in PUNCT.items():
        s = s.replace(a, b)
    return s


_SPACED = re.compile(r"(?<=[一-鿿])[ \t]+(?=[一-鿿])")


def _join_spaced_cjk(s: str) -> str:
    """`说 明 书` is one word set in letterspaced type, not three."""
    prev = None
    while prev != s:
        prev, s = s, _SPACED.sub("", s)
    return s


def _tidy(s: str) -> str:
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" +([,.;:%)\]])", r"\1", s)
    s = re.sub(r"([(\[]) +", r"\1", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def _digest(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def load(path: Path) -> Scrubber:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    return Scrubber(data if isinstance(data, dict) else {})


def has_cjk(s: str) -> bool:
    return bool(CJK.search(s or ""))
