# -*- coding: utf-8 -*-
"""Merge ACRS/CryptChat FR batch JSON files and validate placeholders/accents."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
BATCH_DIR = WORK / "acrs_batches"
OUT = WORK / "acrs_cryptchat_fr.json"
EN_LISTS = (
    WORK / "acrs_status_en.json",
    WORK / "acrs_dialogs_en.json",
    WORK / "acrs_topics_en.json",
)
EN_STRINGS_FILE = WORK / "acrs_cryptchat_en_strings.json"

PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9_]*\]")
ACCENT_RE = re.compile(r"[àâäéèêëïîôùûüçœÀÂÄÉÈÊËÏÎÔÙÛÜÇŒ]")
# File-relative paths must stay EN (game loads RawFiles/PDFS/<path>)
ASSET_PATH_RE = re.compile(r"^[A-Za-z0-9_./\\-]+\.(html|css|js|jpg|jpeg|png|gif|fetch)$")


def load_en_keys() -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()

    def add_many(items: list) -> None:
        for s in items:
            if isinstance(s, str) and s not in seen:
                seen.add(s)
                keys.append(s)

    if EN_STRINGS_FILE.exists():
        data = json.loads(EN_STRINGS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("strings"), list):
            add_many(data["strings"])
        elif isinstance(data, list):
            add_many(data)

    for path in EN_LISTS:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else list(data.keys())
        add_many(items)

    ui = [
        "[#VelvetRoad]: Buy / Sell Decryption Services, Hitman Services, Drugs, Dark Net Files & Sites, +more",
        "[#VelvetRoad] Read & Interact only - CHAT DISABLED",
        "PINGS DISABLED",
        "A.C.R.S - Anon Chat Relay Service",
    ]
    add_many(ui)
    return keys


def placeholders(s: str) -> list[str]:
    return PLACEHOLDER_RE.findall(s)


def load_batches() -> dict[str, str]:
    merged: dict[str, str] = {}
    if not BATCH_DIR.exists():
        return merged
    # Only agent/human FR maps (ignore _en_* manifests and misc leftovers)
    for path in sorted(BATCH_DIR.glob("fr_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"Batch must be object: {path}")
        for k, v in data.items():
            if isinstance(k, str) and isinstance(v, str) and v.strip():
                # Never localize asset/file paths (e.g. Threats/index.html)
                merged[k] = k if ASSET_PATH_RE.match(k) else v
    return merged


def validate(en_keys: list[str], fr: dict[str, str]) -> list[str]:
    errors: list[str] = []
    missing = [k for k in en_keys if k not in fr or not fr[k].strip()]
    if missing:
        errors.append(f"missing_or_empty={len(missing)} (e.g. {missing[0][:60]!r})")
    ph_bad = 0
    path_bad = 0
    for k in en_keys:
        if k not in fr:
            continue
        if ASSET_PATH_RE.match(k) and fr[k] != k:
            path_bad += 1
            if path_bad <= 5:
                errors.append(f"asset_path_translated {k!r} -> {fr[k]!r}")
        if placeholders(k) != placeholders(fr[k]):
            ph_bad += 1
            if ph_bad <= 5:
                errors.append(
                    f"placeholder_mismatch EN={placeholders(k)} FR={placeholders(fr[k])} :: {k[:50]!r}"
                )
    if ph_bad > 5:
        errors.append(f"placeholder_mismatch_total={ph_bad}")
    if path_bad > 5:
        errors.append(f"asset_path_translated_total={path_bad}")
    with_acc = sum(1 for k in en_keys if k in fr and ACCENT_RE.search(fr[k]))
    # French of length > 20 should often have accents; soft check
    long_fr = [k for k in en_keys if k in fr and len(fr[k]) > 40]
    long_acc = sum(1 for k in long_fr if ACCENT_RE.search(fr[k]))
    ratio = (100 * long_acc / len(long_fr)) if long_fr else 100.0
    if ratio < 50:
        errors.append(f"low_accent_ratio_long_strings={ratio:.0f}% ({long_acc}/{len(long_fr)})")
    print(f"keys_en={len(en_keys)} fr_map={len(fr)} accents_any={with_acc} long_accent_ratio={ratio:.0f}%")
    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write acrs_cryptchat_fr.json")
    ap.add_argument("--strict", action="store_true", help="Exit 1 on validation errors")
    args = ap.parse_args()

    en_keys = load_en_keys()
    fr = load_batches()
    # Do not fall back to legacy Google MT map (no accents / poor quality).

    errors = validate(en_keys, fr)
    for e in errors:
        print("ERROR:", e)

    if args.write:
        # EN lists first, then any extra batch keys (e.g. lobby gaps found in Steam extract)
        out_map = {k: fr[k] for k in en_keys if k in fr and fr[k].strip()}
        for k, v in fr.items():
            if k not in out_map and isinstance(v, str) and v.strip():
                out_map[k] = v
        OUT.write_text(json.dumps(out_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Wrote", OUT, "entries", len(out_map), "batch_extras", len(out_map) - len(en_keys))

    if args.strict and errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
