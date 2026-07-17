# -*- coding: utf-8 -*-
"""Minimal safe UI patch: long unique strings only, menu/pause widgets only.

Does NOT auto-install into the game. Output: build/pak_safe/
"""
from __future__ import annotations

import csv
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "source" / "legacy_ui" / "WTTGSD" / "Content"
STAGED = ROOT / "build" / "legacy_safe" / "WTTGSD" / "Content"
OUT = ROOT / "build" / "pak_safe"
RETOC = ROOT / "tools" / "retoc" / "retoc.exe"
MAP = ROOT / "work" / "uexp_patch_fr_safe.csv"
MOD = "WTTGSD-Windows_FR_SAFE_P"

# Only these relative stems (under Content)
ALLOW = {
    "UI/Widgets/Titles/WBP_MainTitleWidget",
    "UI/Widgets/Titles/WBP_MainTitleSettingsWidget",
    "UI/Widgets/Titles/WBP_MainTitlePlayWidget",
    "UI/Widgets/Titles/WBP_TitleMenuButton",
    "UI/Widgets/Settings/WBP_Pause",
}

# Long / unique only — never patch 2-6 letter tokens
RAW = {
    "Graphics Settings": "Graphismes",
    "Audio Settings": "Audio",
    "Game Settings": "Jeu",
    "Mouse Sensitivity": "Sensibilite souris",
    "Show Tooltips": "Info-bulles",
    "Anti-aliasing": "Anticrenelage",
    "Window Mode": "Mode fenetre",
    "Global Illumination": "Illumination globale",
    "Post Processing": "Post-traitement",
    "Resolution Scale": "Echelle resol.",
    "View Distance": "Distance vue",
    "Pause Music": "Musique pause",
    "Game Audio": "Audio jeu",
    "Title Music": "Musique titre",
    "Quit to main menu": "Menu principal",
    "Quit Game": "Quitter",
    "Select Your Difficulty:": "Choisissez la difficulte:",
    "This will overwrite your current save file.": "Ceci ecrasera votre sauvegarde actuelle.",
    "Are you sure?": "Confirmer ?",
    "Tanner's Crime Scene": "Scene de crime Tanner",
    "Continue": "Contin.",
    "Settings": "Options",
}


def fit(en: str, fr: str) -> str:
    fr = fr.encode("ascii", "ignore").decode("ascii")
    return fr + (" " * (len(en) - len(fr))) if len(fr) < len(en) else fr[: len(en)]


def main() -> None:
    pairs = []
    for en, fr in RAW.items():
        fr2 = fit(en, fr)
        assert len(fr2) == len(en)
        assert len(en) >= 7, en
        pairs.append((en, fr2))

    with MAP.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "translation"])
        w.writerows(pairs)

    if STAGED.parent.exists():
        shutil.rmtree(STAGED.parent)
    STAGED.mkdir(parents=True)

    for rel in ALLOW:
        for ext in (".uasset", ".uexp"):
            src = LEGACY / Path(rel.replace("/", "\\") + ext)
            if not src.exists():
                print("missing", src)
                continue
            dst = STAGED / Path(rel.replace("/", "\\") + ext)
            dst.parent.mkdir(parents=True, exist_ok=True)
            data = src.read_bytes()
            for en, fr in pairs:
                data = data.replace(en.encode("ascii"), fr.encode("ascii"))
            dst.write_bytes(data)
            print("patched", rel + ext)

    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob(f"{MOD}*"):
        p.unlink()
    zen = OUT / f"{MOD}.utoc"
    cmd = [str(RETOC), "to-zen", "--version", "UE5_6", str(STAGED.parent), str(zen)]
    print(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-1500:] if r.stdout else "")
    print(r.stderr[-1500:] if r.stderr else "")
    if r.returncode != 0:
        raise SystemExit(r.returncode)
    print("Output in", OUT)
    print("NOT installed. Copy manually after vanilla boot OK.")


if __name__ == "__main__":
    main()
