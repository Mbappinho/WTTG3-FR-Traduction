# Installation — patch FR WTTG3 (hors sites web)

## Contenu du patch

| Élément | Statut |
|---------|--------|
| PDF in-game (`RawFiles/PDFS`) | Traduits → `apply_patch.ps1` |
| Achievements | Traduits (steam_settings local) |
| UI Unreal | Mod IoStore `_P` via **usmap + UAssetGUI** (longueurs FR libres) |
| DarkDrop / Products | Inclus (`Data/DataAssets/Products`) |
| Inventaire items | Inclus (`Data/DataAssets/PlayerItems`) |
| ACRS (UI + salon + pubs agents) | Inclus (`UI/.../WBP_ACRSApp` + `Data/DataAssets/ACRS` + status agents) |
| CryptChat (tutoriel + MP agents) | Inclus — map `work/acrs_cryptchat_fr.json` (~1343 chaines) |
| Sites web (`RawFiles/WebSites`) | **Exclus** |
| Doublage audio | Exclu |

## Prérequis

- Python 3, .NET 8 (UAssetGUI)
- `source/Mappings.usmap` (voir [DUMP_USMAP.md](DUMP_USMAP.md))
- `tools/UAssetGUI/UAssetGUI.exe`, `tools/retoc/retoc.exe`
- Jeu : dossier contenant `WTTGSD\Content\Paks` (Steam ou autre)

## Build

```powershell
# Depuis la racine du depot
python scripts\build_translations.py
python scripts\build_ui_uassetgui_patch.py
```

Configure le chemin du jeu dans les scripts (`GameRoot` / variable) avant apply.

## Pack debutant (recommande pour partager)

Apres un build UI + PDF, genere le dossier a zipper :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_beginner_pack.ps1
```

Sortie : `release\WTTG3-FR-Beginner\`

| Fichier | Role |
|---------|------|
| `LIREMOI.txt` | Mode d'emploi |
| `INSTALLER.bat` | Double-clic = installer FR |
| `DESINSTALLER.bat` | Double-clic = retirer FR / PDF EN |

Le script demande le dossier du jeu (detection auto si possible). Fermer le jeu avant.

## Appliquer (dev / avance)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\apply_patch.ps1 -GameRoot "CHEMIN\VERS\LE\JEU"
# UI deja copiee par build_ui_uassetgui_patch.py
```

## Rollback (dev / avance)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\restore_english.ps1 -GameRoot "CHEMIN\VERS\LE\JEU"
Remove-Item "CHEMIN\VERS\LE\JEU\WTTGSD\Content\Paks\WTTGSD-Windows_FR_P.*"
```

## Périmètre `COPY_PREFIXES` (patcher)

Voir `scripts/build_ui_uassetgui_patch.py` :

- `UI\Widgets`
- `Data\DataAssets\Agents` / `Products` / `PlayerItems` / `SimonThoughts` / `ChoiceTrees` / `Difficulty` / `ACRS`
- `Data\DataTables`
- `BluePrints\Cinema`

Regenerer la grosse map ACRS/CryptChat :

```powershell
python scripts\gen_acrs_cryptchat_fr.py   # status/UI manuels + chunks
python scripts\mt_acrs_cryptchat.py       # complete les manquants (Google Translate + cache)
python scripts\build_ui_uassetgui_patch.py
```

Les dialogues CryptChat doivent matcher la **FString exacte** du `.uexp` (souvent un seul bloc avec `\r\n` et placeholders `[LINK]` / `[PRICE]` / `[WIKI]`). Des morceaux découpés ne matchent pas.

## Limites connues (pas de FString extractible)

- Intro Simon (« You are Simon Zhao… ») : introuvable dans les assets / exe (ni ASCII ni UTF-16) — probablement texture, séquence ou génération runtime.
- Prompts HUD `Move` / `Run` / `Inventory` / `Pick Up` : absents en FString ; très probablement dérivés des noms d’InputAction (`IA_Default_Move` → `Move`) côté moteur.

## QA in-game

1. Menu : **Jouer / Continuer / Parametres / Quitter** (mots complets)
2. Pause / réglages en FR
3. Tutoriel Ronald + Key Finding en FR (wrap-up complet + Good luck)
4. CryptChat ODDroot/Goggin : message de paiement **et** message avec lien ShadowFetch
5. DarkDrop : descriptions VirtMesh / ShadowFetch + bouton **ACHETER**
6. Inventaire : Lettre d'expulsion + descriptions items
7. PDF FR ; WebSites toujours EN
8. UE4SS désactivé (`dwmapi.dll.off`)
9. Fermer le jeu avant rebuild (sinon verrouillage `FR_P.ucas`)
