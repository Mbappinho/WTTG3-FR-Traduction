# -*- coding: utf-8 -*-
"""QA focused on CryptChat private dialogs (not ACRS lobby topics)."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
BATCH = WORK / "acrs_batches"
OUT = WORK / "cryptchat_dialogs_qa_report.json"

DIALOG_FILES = [
    "fr_dialogs_00_02.json",
    "fr_dialogs_03_05.json",
    "fr_dialogs_06_09.json",
    "fr_extras.json",
]

PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9_]*\]")
VOUS = re.compile(r"\b(vous|votre|vos)\b", re.I)
TU = re.compile(r"\b(tu|ton|ta|tes|t'|t’)\b", re.I)
DECRYPTER = re.compile(r"\bdécrypt", re.I)
ACCENTS_MISSING = [
    (re.compile(r"\bdeja\b", re.I), "deja"),
    (re.compile(r"\bapres\b", re.I), "apres"),
    (re.compile(r"\btres\b", re.I), "tres"),
    (re.compile(r"\bvoila\b", re.I), "voila"),
    (re.compile(r"(?<![a-zàâäéèêëïîôùûüç])ca(?![a-zàâäéèêëïîôùûüç])", re.I), "ca"),
    (re.compile(r"\bdesole\b", re.I), "desole"),
    (re.compile(r"\bnecessaire\b", re.I), "necessaire"),
    (re.compile(r"\breseau\b", re.I), "reseau"),
]


def load_dialogs() -> dict[str, str]:
    merged: dict[str, str] = {}
    per_file: dict[str, int] = {}
    for name in DIALOG_FILES:
        p = BATCH / name
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        per_file[name] = len(data)
        for k, v in data.items():
            if isinstance(k, str) and isinstance(v, str):
                merged[k] = v
    return merged


def main() -> None:
    fr = load_dialogs()
    en_list_path = WORK / "acrs_dialogs_en.json"
    en_keys: list[str] = []
    if en_list_path.exists():
        raw = json.loads(en_list_path.read_text(encoding="utf-8"))
        en_keys = raw if isinstance(raw, list) else list(raw.keys())

    map_all = json.loads((WORK / "acrs_cryptchat_fr.json").read_text(encoding="utf-8"))

    missing_in_batches = [k for k in en_keys if k not in fr]
    identity = [(k, v) for k, v in fr.items() if k == v and len(k) > 25]
    missing_ph = []
    extra_ph = []
    vous_only = []
    decrypter = []
    accent_hits = []
    not_in_merged = [k for k in fr if k not in map_all]
    merged_diff = []

    for en, frs in fr.items():
        eph, fph = PLACEHOLDER.findall(en), PLACEHOLDER.findall(frs)
        if eph != fph:
            if set(eph) - set(fph):
                missing_ph.append((en[:100], sorted(set(eph) - set(fph)), frs[:100]))
            if set(fph) - set(eph):
                extra_ph.append((en[:100], sorted(set(fph) - set(eph)), frs[:100]))
        if VOUS.search(frs) and not TU.search(frs):
            vous_only.append(frs[:140])
        if DECRYPTER.search(frs):
            decrypter.append(frs[:120])
        for rx, lab in ACCENTS_MISSING:
            if rx.search(frs):
                accent_hits.append((lab, frs[:110]))
        if en in map_all and map_all[en] != frs:
            merged_diff.append((en[:80], frs[:60], map_all[en][:60]))

    # Keyword buckets for sampling
    buckets = defaultdict(list)
    for en, frs in fr.items():
        low = en.lower()
        if "ronald" in low or "game master" in low or "virtmesh" in low and "install" in low:
            buckets["ronaldish"].append(en)
        if "goggin" in low or "who's coming" in low or "fighting chance" in low:
            buckets["gogginish"].append(en)
        if "oddroot" in low or "hacks you'll need" in low:
            buckets["oddrootish"].append(en)
        if "decrypt" in low or "key hash" in low or "plaintext" in low:
            buckets["decrypt"].append(en)
        if "hitman" in low or "eliminate" in low or "kill confirmed" in low:
            buckets["hitman"].append(en)
        if "dealer" in low or "daredash" in low or "delivery" in low:
            buckets["dealer"].append(en)

    report = {
        "scope": "CryptChat private dialogs only (fr_dialogs_* + fr_extras)",
        "total_dialog_entries": len(fr),
        "en_dialogs_list": len(en_keys),
        "missing_from_batches": len(missing_in_batches),
        "missing_from_batches_sample": missing_in_batches[:20],
        "identity_en_fr": len(identity),
        "identity_sample": [k[:120] for k, _ in identity[:20]],
        "placeholder_missing": len(missing_ph),
        "placeholder_missing_sample": missing_ph[:20],
        "placeholder_extra": len(extra_ph),
        "vous_only": len(vous_only),
        "vous_sample": vous_only[:25],
        "decrypter_hits": len(decrypter),
        "decrypter_sample": decrypter[:10],
        "accent_counts": dict(Counter(l for l, _ in accent_hits).most_common()),
        "accent_sample": accent_hits[:30],
        "not_in_merged_map": len(not_in_merged),
        "merged_differs_from_batch": len(merged_diff),
        "merged_diff_sample": merged_diff[:15],
        "bucket_sizes": {k: len(v) for k, v in buckets.items()},
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if not k.endswith("sample") and k != "accent_sample"}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
