# -*- coding: utf-8 -*-
"""Dump dialogue-like FStrings from Steam ACRS/Agents extract; find unmapped EN."""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "source" / "legacy_ui_steam" / "WTTGSD" / "Content"
OUT_NEW = ROOT / "work" / "acrs_new_en_unmapped.json"
OUT_ALL = ROOT / "work" / "acrs_steam_en_dump.json"
FR_MAP = ROOT / "work" / "acrs_cryptchat_fr.json"
OLD_EN = ROOT / "work" / "acrs_cryptchat_en_strings.json"
UEXP_CSV = ROOT / "work" / "uexp_patch_fr.csv"

SCAN_DIRS = [
    LEGACY / "Data" / "DataAssets" / "ACRS",
    LEGACY / "Data" / "DataAssets" / "Agents",
]

# Also UI widgets that show chat
UI_GLOBS = [
    "**/WBP_ACRS*.uexp",
    "**/WBP_*Crypt*.uexp",
    "**/WBP_*Chat*.uexp",
    "**/WBP_*Velvet*.uexp",
]

SKIP_RE = re.compile(
    r"(/Game/|Blueprint|Default__|None$|^\d+$|^[A-Z][a-z]+[A-Z]|"
    r"\.uasset|\.uexp|SK_|MI_|T_|NS_|FX_|WBP_|DA_|BP_|"
    r"^[A-Za-z0-9_./\\-]+\.(html|css|js|png|jpg|jpeg|gif|fetch)$)",
    re.I,
)


def read_fstrings(data: bytes) -> list[str]:
    """Parse UE FString length-prefixed (ASCII + UTF-16LE negative length)."""
    out: list[str] = []
    i = 0
    n = len(data)
    while i + 4 <= n:
        try:
            raw_len = struct.unpack_from("<i", data, i)[0]
        except struct.error:
            i += 1
            continue
        if raw_len == 0:
            i += 4
            continue
        if 2 <= raw_len <= 2000:
            # ASCII / UTF-8 style: length includes null
            nbytes = raw_len
            start = i + 4
            end = start + nbytes
            if end > n:
                i += 1
                continue
            chunk = data[start:end]
            if chunk.endswith(b"\x00"):
                body = chunk[:-1]
            else:
                body = chunk
            try:
                s = body.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    s = body.decode("latin-1")
                except UnicodeDecodeError:
                    i += 1
                    continue
            if looks_like_dialogue(s):
                out.append(s)
            i = end
            continue
        if -2000 <= raw_len <= -2:
            # UTF-16LE, length is negative char count incl null
            nchars = -raw_len
            nbytes = nchars * 2
            start = i + 4
            end = start + nbytes
            if end > n:
                i += 1
                continue
            chunk = data[start:end]
            try:
                s = chunk.decode("utf-16-le")
            except UnicodeDecodeError:
                i += 1
                continue
            if s.endswith("\x00"):
                s = s[:-1]
            if looks_like_dialogue(s):
                out.append(s)
            i = end
            continue
        i += 1
    return out


def looks_like_dialogue(s: str) -> bool:
    if len(s) < 12:
        return False
    if SKIP_RE.search(s) and len(s) < 40:
        return False
    # Need some letters and spaces or punctuation typical of chat
    letters = sum(c.isalpha() for c in s)
    if letters < 8:
        return False
    # Exclude pure identifiers
    if re.fullmatch(r"[A-Za-z0-9_]+", s):
        return False
    if s.count("/") >= 3 and " " not in s:
        return False
    # Prefer English-looking (has common EN words or Latin sentence)
    if not re.search(r"[A-Za-z]", s):
        return False
    return True


def load_fr_keys() -> set[str]:
    keys: set[str] = set()
    if FR_MAP.exists():
        data = json.loads(FR_MAP.read_text(encoding="utf-8"))
        keys.update(data.keys())
    if OLD_EN.exists():
        data = json.loads(OLD_EN.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "strings" in data:
            keys.update(data["strings"])
        elif isinstance(data, list):
            keys.update(data)
    if UEXP_CSV.exists():
        import csv

        with UEXP_CSV.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                keys.add(row["source"])
    return keys


def fr_covers(en: str, fr_map: dict[str, str]) -> bool:
    if en in fr_map and fr_map[en] != en:
        return True
    # normalize CRLF
    alt = en.replace("\r\n", "\n").replace("\n", "\r\n")
    if alt in fr_map and fr_map[alt] != alt:
        return True
    return False


def main() -> None:
    fr_map = json.loads(FR_MAP.read_text(encoding="utf-8")) if FR_MAP.exists() else {}
    known = load_fr_keys()

    files: list[Path] = []
    for d in SCAN_DIRS:
        if d.exists():
            files.extend(d.rglob("*.uexp"))
    for pattern in UI_GLOBS:
        files.extend(LEGACY.glob(pattern))
    files = sorted(set(files))

    found: set[str] = set()
    for fp in files:
        data = fp.read_bytes()
        for s in read_fstrings(data):
            found.add(s)

    # Also brute ascii for long lines that FString parser might miss
    for fp in files:
        data = fp.read_bytes()
        for m in re.finditer(rb"[\x20-\x7e\r\n\t]{25,1200}", data):
            try:
                s = m.group().decode("ascii")
            except UnicodeDecodeError:
                continue
            if looks_like_dialogue(s):
                found.add(s)

    unmapped = sorted(
        s
        for s in found
        if s not in known
        and not fr_covers(s, fr_map)
        and not re.match(
            r"^[A-Za-z0-9_./\\-]+\.(html|css|js|png|jpg|jpeg|gif|fetch)$", s
        )
    )

    # Filter: keep those that look like player-facing English sentences
    dialogue_new = []
    for s in unmapped:
        # skip if mostly French already
        if re.search(r"[àâäéèêëïîôùûüçœ]", s, re.I):
            continue
        # skip engine noise
        if s.startswith("Transient") or "ExecuteUbergraph" in s:
            continue
        if re.search(
            r"\b(the|you|your|I |I'm|don't|can't|please|pay|send|hack|chat|DOS)\b",
            s,
            re.I,
        ) or len(s) > 40:
            dialogue_new.append(s)

    OUT_ALL.write_text(
        json.dumps({"count": len(found), "strings": sorted(found)}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    OUT_NEW.write_text(
        json.dumps(
            {"count": len(dialogue_new), "strings": dialogue_new[:500]},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"files={len(files)} found={len(found)} unmapped_dialogueish={len(dialogue_new)}")
    for s in dialogue_new[:40]:
        print("---")
        print(s[:200].replace("\r", "\\r").replace("\n", "\\n"))


if __name__ == "__main__":
    main()
