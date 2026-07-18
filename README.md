# WTTG3 - Traduction francaise

Fan patch de localisation francaise **non officiel** pour *Welcome to the Game III*.

> **Joueur / debutant :** telecharge le pack pret a l'emploi dans
> [Releases](https://github.com/Mbappinho/WTTG3-FR-Traduction/releases)
> (`WTTG3-FR-Traduction.zip` → `INSTALLER.bat` / `DESINSTALLER.bat`).

Ce depot contient le **code source du pipeline de traduction** (scripts, docs, dictionnaires FR), **pas** le jeu.

## Contenu traduit (pack Release)

- Menus / UI / inventaire / DarkDrop (accents FR via FString UTF-16)
- Prompts interaction monde (Ouvrir, Déverrouiller, Allumer, Se cacher, etc.)
- CryptChat + ACRS (salon + dialogues agents)
- PDF in-game
- Sites web Dark Net : **exclus** (volontaire)
- Doublage audio : exclus
- HUD mouvement (`Move` / `Run` / `Inventory`) : **non patchable** (noms Enhanced Input `IA_Default_*`)

## Structure du code

| Dossier | Role |
|---------|------|
| `scripts/` | Build du mod UI (`build_ui_uassetgui_patch.py`), ACRS/CryptChat, pack debutant |
| `docs/` | INSTALL, dump usmap, QA, notes de crash |
| `work/` | Dictionnaires FR (CSV / JSON), map ACRS/CryptChat |
| `release/` | Template `LIREMOI` pour le pack debutant |

Non versionne (trop gros / contenus jeu) : `source/` (extracts), `tools/` (retoc, UAssetGUI, UE4SS…), `build/`, `backup/`.

## Pipeline (resume)

1. Extraire les assets legacy avec **retoc** (`to-legacy`)
2. Obtenir un **usmap** UE 5.6 (voir `docs/DUMP_USMAP.md`)
3. Patcher les FStrings via **UAssetGUI** JSON + dictionnaire FR (`scripts/build_ui_uassetgui_patch.py`)
4. Empaqueter en IoStore `_P` avec `retoc to-zen`
5. Generer le pack debutant : `scripts/build_beginner_pack.ps1`

Details : [docs/INSTALL.md](docs/INSTALL.md)

## Build local (avance)

Prerequis : Python 3, .NET 8 (UAssetGUI), `tools/retoc`, `tools/UAssetGUI`, `source/Mappings.usmap`, extracts dans `source/legacy_ui`.

```powershell
pip install -r requirements.txt
python scripts\build_translations.py
python scripts\build_ui_uassetgui_patch.py
powershell -ExecutionPolicy Bypass -File scripts\build_beginner_pack.ps1
```

## Disclaimer

Projet communautaire / personnel. Non affilie aux developpeurs du jeu.
