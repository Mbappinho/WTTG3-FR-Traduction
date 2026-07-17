# -*- coding: utf-8 -*-
"""Binary-patch ASCII/UTF-16 strings in legacy uexp (same byte length)."""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "source" / "legacy_ui" / "WTTGSD" / "Content"
PATCHED = ROOT / "build" / "legacy_patched" / "WTTGSD" / "Content"
MAP = ROOT / "work" / "uexp_patch_fr.csv"


def main() -> None:
    mapping = []
    with MAP.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mapping.append((row["source"], row["translation"], row["encoding"]))

    if PATCHED.exists():
        shutil.rmtree(PATCHED.parent)
    shutil.copytree(LEGACY, PATCHED)

    files_touched = 0
    replacements = 0
    for uexp in PATCHED.rglob("*.uexp"):
        data = bytearray(uexp.read_bytes())
        original = bytes(data)
        for src, dst, enc in mapping:
            if enc == "ascii":
                bsrc, bdst = src.encode("ascii"), dst.encode("ascii")
            else:
                bsrc, bdst = src.encode("utf-16le"), dst.encode("utf-16le")
            if len(bsrc) != len(bdst):
                continue
            if bsrc not in data:
                continue
            data = bytearray(bytes(data).replace(bsrc, bdst))
            replacements += bytes(original).count(bsrc)  # approx
        if bytes(data) != original:
            uexp.write_bytes(data)
            files_touched += 1
            # also patch sibling uasset if string appears (rare)
            uasset = uexp.with_suffix(".uasset")
            if uasset.exists():
                ad = bytearray(uasset.read_bytes())
                ao = bytes(ad)
                for src, dst, enc in mapping:
                    if enc == "ascii":
                        bsrc, bdst = src.encode("ascii"), dst.encode("ascii")
                    else:
                        bsrc, bdst = src.encode("utf-16le"), dst.encode("utf-16le")
                    if len(bsrc) == len(bdst) and bsrc in ad:
                        ad = bytearray(bytes(ad).replace(bsrc, bdst))
                if bytes(ad) != ao:
                    uasset.write_bytes(ad)

    print(f"files_touched={files_touched} mapping_entries={len(mapping)}")


if __name__ == "__main__":
    main()
