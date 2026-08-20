# -*- coding: utf-8 -*-
"""Inventory + mechanical QA of shipped FR translations (report only)."""
from __future__ import annotations

import ast
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUT = WORK / "translation_qa_scan.json"
sys.path.insert(0, str(ROOT / "scripts"))

PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9_]*\]")
TAG = re.compile(r"</?[A-Za-z][^>]*>")
ASSET_PATH = re.compile(r"^[A-Za-z0-9_./\\-]+\.(html|css|js|jpg|jpeg|png|gif|fetch)$")
VOUS = re.compile(r"\b(vous|votre|vos|êtes|avez|pouvez|voulez|devez)\b", re.I)
TU = re.compile(r"\b(tu|ton|ta|tes|t'|t’|toi)\b", re.I)
EN_LEAK = re.compile(
    r"\b(the|and|you|your|please|download|click|send|message|"
    r"however|therefore|because|don't|can't|won't|I'm|you're|it's)\b",
    re.I,
)
ACCENT_CHECKS = [
    (re.compile(r"\bdeja\b", re.I), "deja→déjà"),
    (re.compile(r"\bapres\b", re.I), "apres→après"),
    (re.compile(r"\btres\b", re.I), "tres→très"),
    (re.compile(r"\bvoila\b", re.I), "voila→voilà"),
    (re.compile(r"(?<![a-zàâäéèêëïîôùûüçA-Z])ca(?![a-zàâäéèêëïîôùûüç])", re.I), "ca→ça"),
    (re.compile(r"\bdesolee?\b", re.I), "desole→désolé"),
    (re.compile(r"\bnecessaire\b", re.I), "necessaire→nécessaire"),
    (re.compile(r"\breseau\b", re.I), "reseau→réseau"),
    (re.compile(r"\bsecurite\b", re.I), "securite→sécurité"),
    (re.compile(r"\bnumero\b", re.I), "numero→numéro"),
    (re.compile(r"\belement\b", re.I), "element→élément"),
    (re.compile(r"\bfenetre\b", re.I), "fenetre→fenêtre"),
    (re.compile(r"\binteresse\b", re.I), "interesse→intéressé"),
    (re.compile(r"\bpreferes?\b", re.I), "prefere→préfère"),
    (re.compile(r"\bconnecte\b", re.I), "connecte→connecté"),
    (re.compile(r"\binstalle\b", re.I), "installe→installé"),
    (re.compile(r"\ba ete\b", re.I), "a ete→a été"),
    (re.compile(r"\bete\b", re.I), "ete→été"),
    (re.compile(r"\bparametres?\b", re.I), "parametre→paramètre"),
    (re.compile(r"\bevenement\b", re.I), "evenement→événement"),
    (re.compile(r"\bderriere\b", re.I), "derriere→derrière"),
    (re.compile(r"\bderouler\b", re.I), "derouler→dérouler"),
    (re.compile(r"\ba rats\b", re.I), "a rats→à rats"),
    (re.compile(r"\ba croire\b", re.I), "a croire→à croire"),
    (re.compile(r"\ba son nom\b", re.I), None),  # à is correct if accented
    (re.compile(r"\bpas a\b", re.I), "pas a→pas à"),
    (re.compile(r"\btrou a\b", re.I), "trou a→trou à"),
]
GLOSSARY_BANNED_FR = [
    (re.compile(r"porte dérobée", re.I), "backdoor should stay EN"),
    (re.compile(r"\bpièce DOS\b", re.I), "DOS Coin not pièce DOS"),
    (re.compile(r"\bhachage\b", re.I), "hash not hachage"),
    (re.compile(r"\bdécrypt", re.I), "préférer déchiffrer"),
]
SUSPECT_MT = [
    (re.compile(r"\bs'il vous plaît\b", re.I), "vouvoiement s'il vous plaît"),
    (re.compile(r"\bVeuillez\b"), "Veuillez (soutenu/MT)"),
    (re.compile(r"\bafin de\b", re.I), "afin de (soutenu chat)"),
    (re.compile(r"\bil convient\b", re.I), "il convient"),
    (re.compile(r"\bnéanmoins\b", re.I), "néanmoins"),
    (re.compile(r"\ben outre\b", re.I), "en outre"),
    (re.compile(r"\bde le\b"), "de le (élision manquante)"),
    (re.compile(r"\bà le\b"), "à le (au)"),
]


def load_raw() -> dict[str, str]:
    src = (ROOT / "scripts" / "build_ui_uassetgui_patch.py").read_text(encoding="utf-8")
    start = src.index("RAW: dict[str, str] = {")
    i = src.index("{", start)
    depth = 0
    for j, c in enumerate(src[i:], i):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                ns: dict = {}
                exec("RAW = " + src[i : j + 1], ns)
                return dict(ns["RAW"])
    raise RuntimeError("RAW parse failed")


def load_pdf() -> list[tuple[str, str]]:
    src = (ROOT / "scripts" / "build_translations.py").read_text(encoding="utf-8")
    start = src.index("PDF_REPLACEMENTS")
    eq = src.index("=", start)
    i = src.index("[", eq)
    depth = 0
    for j, c in enumerate(src[i:], i):
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                ns: dict = {}
                exec("PDF_REPLACEMENTS = " + src[i : j + 1], ns)
                return list(ns["PDF_REPLACEMENTS"])
    raise RuntimeError("PDF parse failed")


def load_acrs() -> dict[str, str]:
    data = json.loads((WORK / "acrs_cryptchat_fr.json").read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}


def load_batches() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    d = WORK / "acrs_batches"
    for p in sorted(d.glob("fr_*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            out[p.name] = {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}
    return out


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues = []
    for b in blocks:
        lines = [ln for ln in b.splitlines() if ln.strip() != ""]
        if len(lines) < 2:
            continue
        idx = 0
        if re.match(r"^\d+$", lines[0].strip()):
            idx = int(lines[0].strip())
            rest = lines[1:]
        else:
            rest = lines
        if not rest:
            continue
        timing = rest[0] if "-->" in rest[0] else ""
        body = "\n".join(rest[1:] if timing else rest)
        cues.append({"index": idx, "timing": timing, "text": body})
    return cues


def load_glossary() -> dict:
    return json.loads((WORK / "glossary.json").read_text(encoding="utf-8"))


def crlf_count(s: str) -> tuple[int, int]:
    return s.count("\r\n"), s.count("\n") - s.count("\r\n")


def scan_pair(en: str, fr: str, corpus: str, gloss: dict, keep_en: set[str]) -> list[dict]:
    issues: list[dict] = []
    if not fr or not str(fr).strip():
        issues.append({"kind": "empty", "corpus": corpus, "en": en[:160], "fr": "", "detail": "empty FR"})
        return issues

    if ASSET_PATH.match(en) and fr != en:
        issues.append({"kind": "translated_path", "corpus": corpus, "en": en, "fr": fr, "detail": "asset path translated"})

    if fr == en:
        if not ASSET_PATH.match(en) and en not in keep_en and len(en) > 12:
            issues.append({"kind": "identity", "corpus": corpus, "en": en[:200], "fr": fr[:200], "detail": "EN=FR"})

    eph, fph = PLACEHOLDER.findall(en), PLACEHOLDER.findall(fr)
    if eph != fph:
        missing = [p for p in eph if p not in fph]
        extra = [p for p in fph if p not in eph]
        if missing:
            issues.append({"kind": "placeholder_missing", "corpus": corpus, "en": en[:180], "fr": fr[:180], "detail": str(missing)})
        if extra:
            issues.append({"kind": "placeholder_extra", "corpus": corpus, "en": en[:180], "fr": fr[:180], "detail": str(extra)})

    en_crlf, _ = crlf_count(en)
    fr_crlf, _ = crlf_count(fr)
    if en_crlf != fr_crlf:
        issues.append({"kind": "crlf", "corpus": corpus, "en": en[:120], "fr": fr[:120], "detail": f"en_crlf={en_crlf} fr_crlf={fr_crlf}"})

    en_tags, fr_tags = TAG.findall(en), TAG.findall(fr)
    if Counter(en_tags) != Counter(fr_tags) and en_tags:
        issues.append({"kind": "html_tags", "corpus": corpus, "en": en[:180], "fr": fr[:180], "detail": f"en={en_tags} fr={fr_tags}"})

    for rx, label in ACCENT_CHECKS:
        if label and rx.search(fr):
            issues.append({"kind": "accent", "corpus": corpus, "en": en[:120], "fr": fr[:160], "detail": label})

    for rx, label in GLOSSARY_BANNED_FR:
        if rx.search(fr):
            issues.append({"kind": "glossary", "corpus": corpus, "en": en[:140], "fr": fr[:160], "detail": label})

    preferred = gloss.get("preferred") or {}
    if en in preferred and fr != preferred[en] and preferred[en] not in fr:
        issues.append({"kind": "glossary_preferred", "corpus": corpus, "en": en[:140], "fr": fr[:160], "detail": f"preferred={preferred[en]!r}"})

    for rx, label in SUSPECT_MT:
        if corpus.startswith("acrs") and rx.search(fr):
            issues.append({"kind": "suspect_mt", "corpus": corpus, "en": en[:140], "fr": fr[:160], "detail": label})

    leaks = []
    for m in EN_LEAK.finditer(fr):
        w = m.group(0)
        if w.lower() in {x.lower() for x in keep_en}:
            continue
        if w in en:
            continue
        leaks.append(w)
    if leaks and corpus != "pdf":
        issues.append({"kind": "en_leak", "corpus": corpus, "en": en[:140], "fr": fr[:160], "detail": str(leaks[:6])})

    vous = bool(VOUS.search(fr))
    tu = bool(TU.search(fr))
    if corpus in {"acrs", "acrs_batch", "ui_raw"} and vous and not tu:
        if re.search(r"\b(vous|votre|vos)\b", fr, re.I):
            issues.append({"kind": "vous_only", "corpus": corpus, "en": en[:140], "fr": fr[:160], "detail": "vouvoiement sans tutoiement"})
    if corpus == "pdf" and tu and not vous:
        issues.append({"kind": "tu_in_pdf", "corpus": corpus, "en": en[:140], "fr": fr[:160], "detail": "tutoiement dans PDF (vouvoiement ailleurs)"})

    # truncated-looking FR vs EN length
    if len(en) > 80 and len(fr) < len(en) * 0.45 and fr != en:
        issues.append({"kind": "possible_truncation", "corpus": corpus, "en": en[:160], "fr": fr[:160], "detail": f"len_en={len(en)} len_fr={len(fr)}"})

    return issues


def main() -> None:
    gloss = load_glossary()
    keep_en: set[str] = set()
    for v in gloss.get("preserve") or []:
        keep_en.add(v)
    for k, v in (gloss.get("preferred") or {}).items():
        keep_en.add(str(k))
        keep_en.add(str(v))

    raw = load_raw()
    acrs = load_acrs()
    pdf = load_pdf()
    batches = load_batches()
    ach = json.loads((WORK / "achievements_fr.json").read_text(encoding="utf-8"))
    intro_src = (WORK / "simon_intro_texture" / "make_fr_png.py").read_text(encoding="utf-8")
    intro_m = re.search(r'fr = \(\s*"(.*?)"\s*"(.*?)"\s*"(.*?)"\s*"(.*?)"', intro_src, re.S)
    intro = "".join(intro_m.groups()) if intro_m else ""

    srt_dir = ROOT / "release" / "subtitles_runtime" / "ue4ss_core" / "Mods" / "SousTitresFR" / "SousTitres"
    srt_files = sorted(srt_dir.glob("*.srt"))
    srt_cues = []
    for p in srt_files:
        for c in parse_srt(p):
            srt_cues.append({"file": p.name, **c})

    # merged shipped UI map (RAW wins)
    shipped_ui = dict(acrs)
    shipped_ui.update(raw)

    # batches vs merged
    batch_merged: dict[str, str] = {}
    for name, d in batches.items():
        batch_merged.update(d)
    batch_not_in_acrs = [k for k in batch_merged if k not in acrs]
    acrs_diff_batch = [
        k for k in batch_merged if k in acrs and acrs[k] != batch_merged[k]
    ]
    raw_overrides_acrs = [k for k in raw if k in acrs and raw[k] != acrs[k]]

    issues: list[dict] = []
    for en, fr in raw.items():
        issues.extend(scan_pair(en, fr, "ui_raw", gloss, keep_en))
    for en, fr in acrs.items():
        if en in raw:
            continue
        issues.extend(scan_pair(en, fr, "acrs", gloss, keep_en))
    for en, fr in pdf:
        issues.extend(scan_pair(en, fr, "pdf", gloss, keep_en))
    for a in ach:
        issues.extend(scan_pair(a.get("displayName_en", ""), a.get("displayName", ""), "achievement", gloss, keep_en))
        issues.extend(scan_pair(a.get("description_en", ""), a.get("description", ""), "achievement", gloss, keep_en))
    issues.extend(scan_pair("intro Simon Zhao texture", intro, "intro", gloss, keep_en))
    for c in srt_cues:
        issues.extend(scan_pair(c["file"], c["text"], "srt", gloss, keep_en))

    # gameplay csv truncated — only if leaked into shipped
    gp_path = WORK / "ui_gameplay_fr.csv"
    leaked_trunc: list[dict] = []
    if gp_path.exists():
        with gp_path.open(encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                notes = (row.get("notes") or "")
                en = row.get("source") or ""
                fr = row.get("translation") or ""
                if "translated_prefix" in notes or "needs_review" in notes:
                    shipped_fr = shipped_ui.get(en)
                    leaked_trunc.append({
                        "notes": notes,
                        "en": en[:160],
                        "csv_fr": fr[:160],
                        "shipped": shipped_fr[:160] if shipped_fr else None,
                        "in_raw": en in raw,
                        "in_acrs": en in acrs,
                    })

    # vous/tu counts
    def address_stats(pairs, corpus):
        vous_n = tu_n = both = neither = 0
        for en, fr in pairs:
            v, t = bool(VOUS.search(fr)), bool(TU.search(fr))
            if v and t:
                both += 1
            elif v:
                vous_n += 1
            elif t:
                tu_n += 1
            else:
                neither += 1
        return {"corpus": corpus, "vous_only": vous_n, "tu_only": tu_n, "both": both, "neither": neither, "n": len(pairs)}

    kind_counts = Counter(i["kind"] for i in issues)
    corpus_counts = Counter(i["corpus"] for i in issues)

    inventory = {
        "ui_raw": len(raw),
        "acrs_cryptchat": len(acrs),
        "shipped_merged_ui_plus_acrs": len(shipped_ui),
        "raw_overrides_acrs": len(raw_overrides_acrs),
        "pdf_replacements": len(pdf),
        "achievements": len(ach),
        "achievement_strings": len(ach) * 2,
        "srt_files": len(srt_files),
        "srt_cues": len(srt_cues),
        "intro_chars": len(intro),
        "batches": {k: len(v) for k, v in batches.items()},
        "batch_keys_total": len(batch_merged),
        "batch_not_in_acrs": len(batch_not_in_acrs),
        "acrs_differs_from_batch": len(acrs_diff_batch),
        "overrides": 3,
    }

    # dump samples per kind
    samples: dict[str, list] = defaultdict(list)
    for i in issues:
        if len(samples[i["kind"]]) < 40:
            samples[i["kind"]].append(i)

    report = {
        "inventory": inventory,
        "address": [
            address_stats(list(raw.items()), "ui_raw"),
            address_stats(list(acrs.items()), "acrs"),
            address_stats(pdf, "pdf"),
        ],
        "kind_counts": dict(kind_counts),
        "corpus_issue_counts": dict(corpus_counts),
        "issue_total": len(issues),
        "issues": issues,
        "samples": {k: v for k, v in samples.items()},
        "batch_not_in_acrs_sample": batch_not_in_acrs[:20],
        "acrs_diff_batch_sample": [
            {"en": k[:120], "batch": batch_merged[k][:80], "acrs": acrs[k][:80]}
            for k in acrs_diff_batch[:20]
        ],
        "raw_overrides_acrs_sample": [
            {"en": k[:120], "raw": raw[k][:80], "acrs": acrs[k][:80]}
            for k in raw_overrides_acrs[:20]
        ],
        "gameplay_csv_stale_or_trunc": leaked_trunc,
        "intro": intro,
        "achievement_names": [{"en": a["displayName_en"], "fr": a["displayName"]} for a in ach],
        "srt_preview": [{"file": c["file"], "text": c["text"]} for c in srt_cues],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("inventory", json.dumps(inventory, ensure_ascii=True, indent=2))
    print("kind_counts", dict(kind_counts))
    print("address", report["address"])
    print("gameplay_csv flagged rows", len(leaked_trunc))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
