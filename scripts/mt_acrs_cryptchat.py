# -*- coding: utf-8 -*-
"""DEPRECATED — do not use for production FR.

Historically filled gaps via Google Translate and stripped accents (deaccent).
Final ACRS/CryptChat map is built from work/acrs_batches/fr_*.json via
scripts/merge_acrs_fr_batches.py (human/agent quality + accents).

This script remains only for emergency bootstrap; prefer merge_acrs_fr_batches.py.
"""
from __future__ import annotations

import json
import re
import time
import warnings
from pathlib import Path

from deep_translator import GoogleTranslator

warnings.warn(
    "mt_acrs_cryptchat.py is deprecated (Google + deaccent). "
    "Use work/acrs_batches + merge_acrs_fr_batches.py instead.",
    DeprecationWarning,
    stacklevel=1,
)

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9_]*\]")


def protect(s: str) -> tuple[str, list[str]]:
    found = PLACEHOLDER_RE.findall(s)
    out = s
    for i, ph in enumerate(found):
        out = out.replace(ph, f"ZZPH{i}ZZ", 1)
    return out, found


def restore(s: str, found: list[str]) -> str:
    out = s
    for i, ph in enumerate(found):
        # translator may alter token casing/spacing
        out = re.sub(rf"ZZPH\s*{i}\s*ZZ", ph, out, flags=re.I)
        out = out.replace(f"ZZPH{i}ZZ", ph)
    return out


def deaccent(s: str) -> str:
    table = str.maketrans(
        {
            "à": "a",
            "â": "a",
            "ä": "a",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "î": "i",
            "ï": "i",
            "ô": "o",
            "ö": "o",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ç": "c",
            "À": "A",
            "Â": "A",
            "É": "E",
            "È": "E",
            "Ê": "E",
            "Î": "I",
            "Ô": "O",
            "Ù": "U",
            "Ç": "C",
            "œ": "oe",
            "Œ": "OE",
        }
    )
    return s.translate(table)


def main() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from build_ui_uassetgui_patch import RAW
    from gen_acrs_cryptchat_fr import STATUS, UI

    en_all = json.loads((WORK / "acrs_cryptchat_en_strings.json").read_text(encoding="utf-8"))["strings"]
    cache_path = WORK / "acrs_mt_cache.json"
    cache: dict[str, str] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))

    # Prefer hand maps
    preferred = dict(UI)
    preferred.update(STATUS)

    todo = [s for s in en_all if s not in RAW and s not in preferred and s not in cache]
    print(f"to_translate={len(todo)} cached={len(cache)} preferred={len(preferred)}")

    tr = GoogleTranslator(source="en", target="fr")
    for i, en in enumerate(todo, 1):
        if len(en.strip()) < 2:
            cache[en] = en
            continue
        # Skip pure spam / hash-looking lines: still translate lightly or keep
        prot, found = protect(en)
        try:
            # Google has length limits ~4500
            if len(prot) > 4000:
                parts = [prot[j : j + 3500] for j in range(0, len(prot), 3500)]
                fr_parts = [tr.translate(p) for p in parts]
                fr = "".join(fr_parts)
            else:
                fr = tr.translate(prot)
            fr = restore(fr, found)
            # Keep accents if any; do not strip for new runs
            cache[en] = fr
        except Exception as ex:
            print(f"FAIL {i}: {ex!r} :: {en[:60]!r}")
            time.sleep(2)
            try:
                fr = tr.translate(prot[:4000])
                cache[en] = restore(fr, found)
            except Exception as ex2:
                print(f"FAIL2 {ex2!r}")
                cache[en] = en  # leave EN rather than crash
        if i % 25 == 0:
            cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(f"progress {i}/{len(todo)}")
            time.sleep(0.5)
        else:
            time.sleep(0.12)

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    # Merge final
    fr_map = dict(preferred)
    for en in en_all:
        if en in RAW:
            continue
        if en in preferred:
            fr_map[en] = preferred[en]
        elif en in cache:
            fr_map[en] = cache[en]

    out = WORK / "acrs_cryptchat_fr.json"
    out.write_text(json.dumps(fr_map, ensure_ascii=False, indent=1), encoding="utf-8")
    missing = [s for s in en_all if s not in RAW and s not in fr_map]
    print(f"FINAL entries={len(fr_map)} missing={len(missing)}")
    (WORK / "acrs_cryptchat_fr_missing.json").write_text(
        json.dumps(missing, ensure_ascii=False, indent=1), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
