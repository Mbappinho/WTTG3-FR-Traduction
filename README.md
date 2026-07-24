# WTTG3 - Traduction francaise [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T1P023QR7T)

Fan patch de localisation francaise **non officiel** pour *Welcome to the Game III*.

> **Joueur / debutant :** telecharge le pack pret a l'emploi dans
> [Releases](https://github.com/Mbappinho/WTTG3-FR-Traduction/releases)
> (`WTTG3-FR-Traduction.zip` → `INSTALLER.bat` / `DESINSTALLER.bat`).
> Pour **Nexus Mods**, utiliser `WTTG3-FR-Traduction-Nexus.zip` (**drop-in** sans `.bat`/`.ps1` : dézipper dans le dossier du jeu).
> Maj auto Nexus : [docs/NEXUS_AUTOMATION.md](docs/NEXUS_AUTOMATION.md).

Ce depot contient le **code source du pipeline de traduction** (scripts, docs, dictionnaires FR), **pas** le jeu.

## Compatibilite Steam (importante)

| | |
|--|--|
| **Pack actuel** | **v1.5.2** |
| **Steam BuildID** | **`24359942`** (AppID `3869850`) |
| Verifier | fichier `steamapps/appmanifest_3869850.acf` → ligne `"buildid"` |

`INSTALLER.bat` **detecte automatiquement** ton BuildID et indique si le pack est compatible.  
Si different → crash possible → telecharge une release FR pour **ce** build. Details : [docs/STEAM_COMPAT.md](docs/STEAM_COMPAT.md).

## Mise a jour du mod (joueurs) — a lire

Apres **chaque mise a jour Steam** du jeu, la trad peut casser (textes EN, PDF EN, ou **crash** au lancement).

### Mise a jour propre (recommandee)

Tu as deja INSTALLER.bat (Full **v1.4.1+**)
Tu n'as pas besoin de retelecharger manuellement ni de desinstaller :

Ferme le jeu
Relance INSTALLER.bat de ton pack actuel
Accepte la maj GitHub (O) quand il propose une version plus recente
Confirme l'installation → relance le jeu
(Depuis **v1.5.2**, le dossier pack local est synchronise apres maj : un 2e lancement doit dire « Deja a jour ».
Si ton pack est <= v1.5.1 : telecharge UNE FOIS le zip v1.5.2 pour avoir les nouveaux scripts.)

Nexus / premiere install / pack sans .bat
Full : telecharger WTTG3-FR-Traduction.zip → INSTALLER.bat
Nexus : telecharger WTTG3-FR-Traduction-Nexus.zip → dezipper dans le dossier du jeu (ecrase FR_P + PDF)

### Si le jeu crash au lancement

1. `DESINSTALLER.bat` **immediatement** (ou supprime `WTTGSD\Content\Paks\WTTGSD-Windows_FR_P.*`).
2. Verifie que le jeu **vanilla** (sans mod) demarre.
3. Installe uniquement la **derniere** release FR rebuildée pour cette maj Steam.  
   Reinstaller un vieux pack ne suffit en general **pas**.
4. Si aucune release a jour n’existe encore : joue sans mod jusqu’a ce qu’elle sorte.

Details techniques : [docs/UI_PATCH_CRASH.md](docs/UI_PATCH_CRASH.md) · [docs/INSTALL.md](docs/INSTALL.md)

## Contenu traduit (pack Release)

- Menus / UI / inventaire / DarkDrop (accents FR via FString UTF-16)
- Prompts interaction monde (Ouvrir, Déverrouiller, Allumer, Se cacher, etc.)
- Prompts `[RMB]` (Quitter / Se lever du bureau / Quitter l'ordinateur)
- CryptChat + ACRS (salon + dialogues agents, FR soigné avec accents)
- PDF in-game dont Contestants (lieux / métiers / infos) ; chemins `Threats/index.html` etc. **non traduits** — sinon 404
- Sites web Dark Net : **exclus** (volontaire)
- Doublage audio : exclus
- HUD mouvement (`Move` / `Run` / `Inventory`) : **non patchable** (noms Enhanced Input `IA_Default_*`)
- **Steam :** pack buildé depuis l’extract officiel — ne pas overlay un build Desktop sur Steam
- **Après une MAJ Steam :** si crash → desinstaller le mod ou mettre a jour vers la derniere release (voir ci-dessus)

## Structure du code

| Dossier | Role |
|---------|------|
| `scripts/` | Build du mod UI (`build_ui_uassetgui_patch.py`), ACRS/CryptChat, pack debutant |
| `docs/` | INSTALL, dump usmap, QA, notes de crash |
| `work/` | Dictionnaires FR (CSV / JSON), map ACRS/CryptChat |
| `work/acrs_batches/` | Lots ACRS (`fr_status.json` : pubs/UI ; `fr_dialogs_*.json` : dialogues agents ; `fr_topics.json` : 299 topics/spam lobby) |
| `release/` | Template `LIREMOI` pour le pack debutant |

Non versionne (trop gros / contenus jeu) : `source/` (extracts), `tools/` (retoc, UAssetGUI, UE4SS…), `build/`, `backup/`.

## Pipeline (resume)

1. Extraire les assets legacy avec **retoc** (`to-legacy`)
2. Obtenir un **usmap** UE 5.6 (voir `docs/DUMP_USMAP.md`)
3. Patcher les FStrings via **UAssetGUI** JSON + dictionnaire FR (`scripts/build_ui_uassetgui_patch.py`)
4. Empaqueter en IoStore `_P` avec `retoc to-zen`
5. Generer le pack debutant : `scripts/build_beginner_pack.ps1`  
   (variante Nexus : `-Distribution Nexus`)

Details : [docs/INSTALL.md](docs/INSTALL.md)

## Build local (avance)

Prerequis : Python 3, .NET 8 (UAssetGUI), `tools/retoc`, `tools/UAssetGUI`, `source/Mappings.usmap`, extract **Steam** dans `source/legacy_ui_steam` (voir `docs/INSTALL.md`).

```powershell
pip install -r requirements.txt
python scripts\build_translations.py
python scripts\build_ui_uassetgui_patch.py
powershell -ExecutionPolicy Bypass -File scripts\build_beginner_pack.ps1
```

## Disclaimer

Projet communautaire / personnel. Non affilie aux developpeurs du jeu.
