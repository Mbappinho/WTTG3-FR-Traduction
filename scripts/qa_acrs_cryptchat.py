# -*- coding: utf-8 -*-
"""Heuristic QA pass over ACRS/CryptChat FR map."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "work" / "acrs_cryptchat_fr.json"
GLOSS = ROOT / "work" / "glossary.json"

PLACEHOLDER = re.compile(r"\[[A-Z0-9_]+\]")
VOUS = re.compile(
    r"\b(vous|votre|vos|êtes|avez|pouvez|voulez|devez|faites|allez)\b",
    re.I,
)
TU = re.compile(
    r"\b(tu|ton|ta|tes|t'|t’|es|as|peux|veux|dois|fais|vas)\b",
    re.I,
)

# Rough MT / awkward FR markers
SUSPECT = [
    (r"\bde le\b", "de le"),
    (r"\bà le\b", "à le"),
    (r"\bde les\b", "de les"),
    (r"\bs'il vous plaît\b", "vouvoiement s'il vous plaît"),
    (r"\bJe vous\b", "Je vous"),
    (r"\bVeuillez\b", "Veuillez"),
    (r"\bMonsieur\b", "Monsieur (souvent MT)"),
    (r"\bafin de\b", "afin de (soutenu)"),
    (r"\ben outre\b", "en outre"),
    (r"\bil convient\b", "il convient"),
    (r"\bcependant\b", "cependant (soutenu chat)"),
    (r"\bnéanmoins\b", "néanmoins"),
]

# Common EN words that shouldn't remain (except glossary brands)
EN_LEAK = re.compile(
    r"\b(the|and|you|your|please|download|click|send|message|money|"
    r"password|website|however|therefore|because|with|from|this|that|"
    r"will|would|should|could|have|has|been|are|is|was|were|not|"
    r"don't|can't|won't|I'm|you're|it's|there's)\b",
    re.I,
)

# Accents expected in common FR words if present without accent
MISSING_ACCENT = [
    (r"\bcafe\b", "café"),
    (r"\bete\b", "été"),
    (r"\ba\b(?= (été|été|été))", None),  # skip
    (r"\bdeja\b", "déjà"),
    (r"\bapres\b", "après"),
    (r"\bmeme\b", "même"),
    (r"\btres\b", "très"),
    (r"\bvoila\b", "voilà"),
    (r"\bvoici\b", "ok"),
    (r"\bca\b", "ça"),
    (r"\bea\b", None),
    (r"\bnumero\b", "numéro"),
    (r"\binformations\b", None),
    (r"\bsecurite\b", "sécurité"),
    (r"\belement\b", "élément"),
    (r"\bfenetre\b", "fenêtre"),
    (r"\breseau\b", "réseau"),
    (r"\binteresse\b", "intéressé"),
    (r"\bpreferes?\b", "préfère"),
    (r"\bdesole\b", "désolé"),
    (r"\bdesolee\b", "désolée"),
    (r"\bete\b", "été"),
    (r"\bete\b", "été"),
]

ACCENT_CHECKS = [
    (re.compile(r"\bdeja\b", re.I), "deja→déjà"),
    (re.compile(r"\bapres\b", re.I), "apres→après"),
    (re.compile(r"(?<![a-zàâäéèêëïîôùûüç])meme(?![a-z])", re.I), "meme→même"),
    (re.compile(r"\btres\b", re.I), "tres→très"),
    (re.compile(r"\bvoila\b", re.I), "voila→voilà"),
    (re.compile(r"(?<![a-zàâäéèêëïîôùûüç])ca(?![a-zàâäéèêëïîôùûüç])", re.I), "ca→ça"),
    (re.compile(r"\bsecurite\b", re.I), "securite→sécurité"),
    (re.compile(r"\breseau\b", re.I), "reseau→réseau"),
    (re.compile(r"\bdesole\b", re.I), "desole→désolé"),
    (re.compile(r"\binteresse\b", re.I), "interesse→intéressé"),
    (re.compile(r"\bpreferes?\b", re.I), "prefere→préfère"),
    (re.compile(r"\bnumero\b", re.I), "numero→numéro"),
    (re.compile(r"\belement\b", re.I), "element→élément"),
    (re.compile(r"\bfenetre\b", re.I), "fenetre→fenêtre"),
    (re.compile(r"\bete\b", re.I), "ete→été"),
    (re.compile(r"\ba ete\b", re.I), "a ete→a été"),
    (re.compile(r"\bconnecte\b", re.I), "connecte→connecté"),
    (re.compile(r"\binstalle\b", re.I), "installe→installé"),
    (re.compile(r"\bpaye\b", re.I), "paye→payé?"),
    (re.compile(r"\benvoie\b", re.I), None),  # imperative ok
    (re.compile(r"\bnecessaire\b", re.I), "necessaire→nécessaire"),
    (re.compile(r"\binformations?\b", re.I), None),
]


def main() -> None:
    data = json.loads(MAP.read_text(encoding="utf-8"))
    gloss = json.loads(GLOSS.read_text(encoding="utf-8"))
    keep_en = set()
    if isinstance(gloss, dict):
        for v in gloss.values():
            if isinstance(v, list):
                keep_en.update(v)
            elif isinstance(v, str):
                keep_en.add(v)
            elif isinstance(v, dict):
                keep_en.update(str(x) for x in v.values())

    issues = defaultdict(list)
    untranslated = []
    missing_ph = []
    extra_ph = []
    vous_hits = []
    accent_hits = []
    en_leak = []
    suspect_hits = []
    empty = []

    for en, fr in data.items():
        if not fr or not str(fr).strip():
            empty.append(en[:80])
            continue
        if fr == en:
            # allow brand-only / short paths
            if len(en) > 20 or " " in en:
                untranslated.append((en[:100], fr[:100]))
            continue

        en_ph = set(PLACEHOLDER.findall(en))
        fr_ph = set(PLACEHOLDER.findall(fr))
        if en_ph - fr_ph:
            missing_ph.append((sorted(en_ph - fr_ph), en[:90], fr[:90]))
        if fr_ph - en_ph:
            extra_ph.append((sorted(fr_ph - en_ph), en[:90], fr[:90]))

        # Tutoiement preferred for CryptChat; flag strong vous
        if VOUS.search(fr) and not TU.search(fr):
            # ignore status-like formal if short
            if re.search(r"\b(vous|votre|vos)\b", fr, re.I):
                vous_hits.append(fr[:120])

        for rx, label in ACCENT_CHECKS:
            if label and rx.search(fr):
                accent_hits.append((label, fr[:110]))

        # EN leak: ignore if word is in glossary or appears in EN as proper noun product
        leaks = []
        for m in EN_LEAK.finditer(fr):
            w = m.group(0)
            if w.lower() in {x.lower() for x in keep_en}:
                continue
            # allow if also in EN source as code-like
            if w in en:
                continue
            leaks.append(w)
        if leaks:
            en_leak.append((leaks[:5], fr[:110]))

        for pat, label in SUSPECT:
            if re.search(pat, fr, re.I):
                suspect_hits.append((label, fr[:110]))

    # Dedup accent by label counts
    accent_c = Counter(l for l, _ in accent_hits)
    vous_c = len(vous_hits)
    print("=== ACRS CryptChat QA ===")
    print(f"total={len(data)}")
    print(f"empty={len(empty)}")
    print(f"untranslated_identity={len(untranslated)}")
    print(f"missing_placeholders={len(missing_ph)}")
    print(f"extra_placeholders={len(extra_ph)}")
    print(f"vous_only_approx={vous_c}")
    print(f"accent_issue_hits={len(accent_hits)} unique_labels={dict(accent_c.most_common(20))}".encode("ascii", "replace").decode())
    print(f"en_leak_hits={len(en_leak)}")
    print(f"suspect_style={len(suspect_hits)}")

    out = ROOT / "work" / "acrs_qa_report.json"
    report = {
        "total": len(data),
        "empty": empty[:20],
        "untranslated_sample": untranslated[:40],
        "missing_placeholders": missing_ph[:40],
        "extra_placeholders": extra_ph[:20],
        "vous_sample": vous_hits[:40],
        "accent_sample": accent_hits[:60],
        "accent_counts": dict(accent_c.most_common()),
        "en_leak_sample": en_leak[:40],
        "suspect_sample": suspect_hits[:40],
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
