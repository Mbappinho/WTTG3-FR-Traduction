# -*- coding: utf-8 -*-
"""Extract ASCII + UTF-16LE strings from legacy UI uexp; build FR patch map."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "source" / "legacy_ui" / "WTTGSD" / "Content"
OUT = ROOT / "source" / "uexp_strings_en.csv"
PATCH_MAP = ROOT / "work" / "uexp_patch_fr.csv"

SKIP = re.compile(r"(UltraDynamicSky|StarterContent|Fab\\|Effects\\|Materials\\)", re.I)
INTEREST_FILE = re.compile(
    r"(UI\\|Widgets\\|Titles\\|Menu|Tutorial|Inventory|Chat|Desktop|VirtMesh|Pause|HUD|DT_|ST_|Agents|Data\\)",
    re.I,
)


def ascii_strings(data: bytes, min_len=3, max_len=180) -> list[str]:
    out = []
    for m in re.finditer(rb"[\x20-\x7e]{%d,%d}" % (min_len, max_len), data):
        s = m.group().decode("ascii")
        if re.search(r"[A-Za-z]", s):
            out.append(s)
    return out


def utf16_strings(data: bytes, min_len=3, max_len=180) -> list[str]:
    out = []
    i = 0
    n = len(data)
    while i + 3 < n:
        if data[i + 1] == 0 and 32 <= data[i] <= 126:
            chars = []
            j = i
            while j + 1 < n and data[j + 1] == 0 and 32 <= data[j] <= 126:
                chars.append(chr(data[j]))
                j += 2
            if min_len <= len(chars) <= max_len:
                s = "".join(chars)
                if re.search(r"[A-Za-z]", s):
                    out.append(s)
            i = max(j, i + 2)
        else:
            i += 1
    return out


# Manual high-priority translations (len FR <= len EN when possible; pad with spaces if shorter)
TRANSLATIONS: dict[str, str] = {
    "Play": "Jouer",
    "PLAY": "JOUER",
    "Continue": "Continuer",
    "CONTINUE": "CONTINUER",
    "Settings": "Options",
    "SETTINGS": "OPTIONS",
    "Options": "Options",
    "OPTIONS": "OPTIONS",
    "Quit": "Quitter",
    "QUIT": "QUITTER",
    "Exit": "Quitter",
    "EXIT": "QUITTER",
    "Back": "Retour",
    "BACK": "RETOUR",
    "Apply": "Appliquer",
    "APPLY": "VALIDER",
    "Cancel": "Annuler",
    "CANCEL": "ANNULER",
    "Confirm": "Confirmer",
    "CONFIRM": "VALIDER",
    "Resume": "Reprendre",
    "RESUME": "REPRENDRE",
    "Pause": "Pause",
    "PAUSED": "EN PAUSE",
    "New Game": "Nouv. partie",
    "Load Game": "Charger",
    "Save Game": "Sauvegarder",
    "Inventory": "Inventaire",
    "Enter Desk": "S'asseoir",
    "[TAB] Inventory": "[TAB] Inventaire",
    "[SHIFT] Run": "[SHIFT] Courir",
    "[W,A,S,D] Move": "[Z,Q,S,D] Bouger",
    "Normal": "Normal",
    "Difficulty": "Difficulte",
    "Credits": "Credits",
    "Tutorial": "Tutoriel",
    "Skip": "Passer",
    "Next": "Suivant",
    "Previous": "Precedent",
    "Yes": "Oui",
    "No": "Non",
    "OK": "OK",
    "Close": "Fermer",
    "Start": "Demarrer",
    "Install": "Installer",
    "Uninstall": "Desinstaller",
    "Mount": "Monter",
    "Unmount": "Demonter",
    "Mine": "Miner",
    "Hack": "Pirater",
    "HACK": "PIRATER",
    "Buy": "Acheter",
    "Sell": "Vendre",
    "Upgrade": "Ameliorer",
    "Firewall": "Pare-feu",
    "Desktop": "Bureau",
    "Chat": "Chat",
    "Send": "Envoyer",
    "Submit": "Envoyer",
    "Accept": "Accepter",
    "Decline": "Refuser",
    "Retry": "Reessayer",
    "Hide": "Cacher",
    "Run": "Courir",
    "Loading": "Chargement",
    "Please Wait": "Patientez...",
    "Are you sure?": "Confirmer ?",
    "Main Menu": "Menu principal",
    "Return to Title": "Retour titre",
    "Quit to Desktop": "Quitter",
}


def fit(en: str, fr: str) -> str:
    """Fit French into English byte length (ASCII)."""
    if len(fr) <= len(en):
        return fr + (" " * (len(en) - len(fr)))
    # truncate with ellipsis if needed
    if len(en) <= 3:
        return fr[:len(en)]
    return (fr[: len(en) - 1] + "…")[: len(en)] if len(en) > 1 else fr[:1]


def main() -> None:
    rows = []
    seen = set()
    for uexp in LEGACY.rglob("*.uexp"):
        rel = str(uexp.relative_to(LEGACY)).replace("\\", "/")
        if SKIP.search(rel):
            continue
        if not INTEREST_FILE.search(rel):
            continue
        data = uexp.read_bytes()
        for enc, func in (("ascii", ascii_strings), ("utf16", utf16_strings)):
            for s in func(data):
                key = (s, enc)
                if key in seen:
                    continue
                seen.add(key)
                rows.append({"file": rel, "source": s, "encoding": enc, "len": len(s)})

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "source", "encoding", "len", "translation"])
        w.writeheader()
        for r in sorted(rows, key=lambda x: (-x["len"], x["source"])):
            fr = TRANSLATIONS.get(r["source"], "")
            if fr:
                fr = fit(r["source"], fr) if r["encoding"] == "ascii" else fr
            w.writerow({**r, "translation": fr})

    # patch map: unique source -> translation (prefer known)
    patch = {}
    for r in rows:
        s = r["source"]
        if s in TRANSLATIONS:
            patch[s] = (fit(s, TRANSLATIONS[s]), r["encoding"])

    with PATCH_MAP.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "translation", "encoding"])
        for s, (fr, enc) in sorted(patch.items()):
            w.writerow([s, fr, enc])

    print(f"strings={len(rows)} patchable={len(patch)} -> {OUT}")
    # show menu-related
    for r in rows:
        if re.search(r"^(Play|Continue|Settings|Quit|Options|Inventory|Enter Desk|New Game|Resume|Pause)$", r["source"], re.I):
            print(r["encoding"], r["source"], "->", TRANSLATIONS.get(r["source"], "?"))


if __name__ == "__main__":
    main()
