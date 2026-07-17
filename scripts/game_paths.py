# -*- coding: utf-8 -*-
"""Resolve local game / loc roots without committing personal paths."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def game_root() -> Path:
    env = os.environ.get("WTTG3_GAME", "").strip().strip('"')
    if env:
        return Path(env)
    local = ROOT / "local_game_path.txt"
    if local.exists():
        line = local.read_text(encoding="utf-8").strip().strip('"')
        if line:
            return Path(line)
    raise SystemExit(
        "Chemin du jeu inconnu. Cree local_game_path.txt a la racine du depot "
        "(une ligne = dossier du jeu contenant WTTGSD\\) "
        "ou definis la variable d'environnement WTTG3_GAME."
    )


def paks_dir() -> Path:
    return game_root() / "WTTGSD" / "Content" / "Paks"
