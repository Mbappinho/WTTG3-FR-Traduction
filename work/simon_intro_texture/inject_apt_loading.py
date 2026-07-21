# -*- coding: utf-8 -*-
"""Inject FR PNG into AptLoadingScreen.uexp (PF_B8G8R8A8, header 151 bytes)."""
from __future__ import annotations

import shutil
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "source" / "legacy_ui_steam" / "WTTGSD" / "Content"
STAGED = ROOT / "build" / "uassetgui_patched" / "WTTGSD" / "Content"
FR_PNG = ROOT / "work" / "simon_intro_texture" / "AptLoadingScreen_FR.png"
REL = Path("Images/UI/HUD/AptLoadingScreen")


def inject(src_uasset: Path, src_uexp: Path, png: Path, dst_dir: Path) -> None:
    uexp = src_uexp.read_bytes()
    w, h = struct.unpack_from("<II", uexp, 8)
    hdr_size = len(uexp) - w * h * 4
    assert hdr_size == 151, hdr_size
    header = uexp[:hdr_size]

    im = Image.open(png).convert("RGBA")
    assert im.size == (w, h), (im.size, (w, h))
    # RGBA -> BGRA bytes
    r, g, b, a = im.split()
    bgra = Image.merge("RGBA", (b, g, r, a)).tobytes()
    assert len(bgra) == w * h * 4

    new_uexp = header + bgra
    assert len(new_uexp) == len(uexp)

    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_uasset, dst_dir / src_uasset.name)
    (dst_dir / src_uexp.name).write_bytes(new_uexp)
    print("wrote", dst_dir / src_uexp.name, "bytes", len(new_uexp))


def main() -> None:
    src_uasset = LEGACY / REL.with_suffix(".uasset")
    src_uexp = LEGACY / REL.with_suffix(".uexp")
    dst = STAGED / REL.parent
    inject(src_uasset, src_uexp, FR_PNG, dst)

    # Also keep a copy under work for docs
    aside = ROOT / "work" / "simon_intro_texture" / "cooked"
    aside.mkdir(parents=True, exist_ok=True)
    inject(src_uasset, src_uexp, FR_PNG, aside)
    print("OK")


if __name__ == "__main__":
    main()
