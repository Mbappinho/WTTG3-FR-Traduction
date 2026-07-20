# -*- coding: utf-8 -*-
"""Apply ACRS polish fixes across batches + regenerate map."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "work" / "acrs_batches"
GLOSS = ROOT / "work" / "glossary.json"

# Exact EN-key → new FR (when present)
EXACT: dict[str, str] = {}

# Substring / whole-value replacements on FR side (applied carefully)
VALUE_REPLACEMENTS: list[tuple[str, str]] = [
    ("EN PAGNE", "EN PAGAILLE"),
    ("en pagne", "en pagaille"),
    ("DÉNICHÉR", "DÉNICHER"),
    ("dénichér", "dénicher"),
    ("compétir", "rivaliser"),
    ("l'estimé pour", "l'estimation pour"),
    ("c'est quoi l'estimé", "c'est quoi l'estimation"),
    ("tape-toi dans le dos", "félicite-toi"),
    ("la loi des moyennes", "la loi des grands nombres"),
    ("T'l'as, hein ?", "Tu l'as, hein ?"),
    ("T'l'as", "Tu l'as"),
]

# Insult normalization in FR values
PUSSY_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bpd\b", re.I), "tafiole"),
    (re.compile(r"\bpoule mouillée\b", re.I), "tafiole"),
]

# Harmonize porte dérobée → backdoor (game jargon, keep EN like glossary)
BACKDOOR_TO_EN = [
    (re.compile(r"\bune porte dérobée\b", re.I), "une backdoor"),
    (re.compile(r"\bla porte dérobée\b", re.I), "la backdoor"),
    (re.compile(r"\bta porte dérobée\b", re.I), "ta backdoor"),
    (re.compile(r"\bporte dérobée\b", re.I), "backdoor"),
    (re.compile(r"\bportes dérobées\b", re.I), "backdoors"),
]


def polish_fr(fr: str) -> str:
    out = fr
    for a, b in VALUE_REPLACEMENTS:
        if a in out:
            out = out.replace(a, b)
    for rx, repl in PUSSY_REPLACEMENTS:
        out = rx.sub(repl, out)
    for rx, repl in BACKDOOR_TO_EN:
        out = rx.sub(repl, out)
    return out


def main() -> None:
    changed_files = 0
    changed_entries = 0
    for path in sorted(BATCH.glob("fr_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        n = 0
        for k, v in list(data.items()):
            if not isinstance(v, str):
                continue
            if k in EXACT:
                nv = EXACT[k]
            else:
                nv = polish_fr(v)
            if nv != v:
                data[k] = nv
                n += 1
        if n:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed_files += 1
            changed_entries += n
            print(f"{path.name}: {n} entries")

    # glossary note
    gloss = json.loads(GLOSS.read_text(encoding="utf-8"))
    preferred = gloss.setdefault("preferred", {})
    preferred["backdoor"] = "backdoor"
    preferred["porte dérobée"] = "backdoor"
    preferred["pussy"] = "tafiole"
    preferred["pat on the back"] = "félicite-toi"
    rules = gloss.setdefault("rules", [])
    rule = "backdoor : garder l'anglais (pas « porte dérobée »). pussy → tafiole (registre stable)."
    if rule not in rules:
        rules.append(rule)
    GLOSS.write_text(json.dumps(gloss, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"done files={changed_files} entries={changed_entries}")


if __name__ == "__main__":
    main()
