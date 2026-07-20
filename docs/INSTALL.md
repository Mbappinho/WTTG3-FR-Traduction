# Installation — patch FR WTTG3 (hors sites web)

## Contenu du patch

| Élément | Statut |
|---------|--------|
| PDF in-game (`RawFiles/PDFS`) | Traduits → `apply_patch.ps1` |
| Achievements | Traduits (steam_settings local) |
| UI Unreal | Mod IoStore `_P` via **usmap + UAssetGUI** ; **base = extract Steam** (`legacy_ui_steam`) |
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

**Important :** le cook Steam ≠ copie Desktop. Extraire depuis le jeu cible :

```powershell
tools\retoc\retoc.exe to-legacy --version UE5_6 `
  "C:\Steam\steamapps\common\Welcome to the Game III\WTTGSD\Content\Paks" `
  source\legacy_ui_steam
```

Puis :

```powershell
# Depuis la racine du depot
python scripts\build_translations.py
python scripts\build_ui_uassetgui_patch.py
```

`build_ui_uassetgui_patch.py` préfère `source/legacy_ui_steam` s’il existe.

## MAJ Steam (maintenance — lire avant de paniquer)

Le pak `WTTGSD-Windows_FR_P` **écrase** des assets du jeu. Il doit matcher le **cook exact** de l’install.

- **Après une mise à jour Steam**, un ancien `FR_P` peut re-crash (`Bad export index`, souvent menu Settings) même si la trad n’a pas changé.
- **Test :** enlever `WTTGSD-Windows_FR_P.*` → si le jeu vanilla boote, le mod est périmé → **re-extract Steam + rebuild** (pas seulement réinstaller le même zip).
- Détail + historique : [UI_PATCH_CRASH.md](UI_PATCH_CRASH.md)

Ne pas mélanger : pack buildé Desktop sur Steam (ou l’inverse) = même famille de crash.

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

## Mise a jour du pack (joueurs)

Procedure propre apres une **MAJ Steam** ou une **nouvelle release FR** :

1. Fermer le jeu.
2. `DESINSTALLER.bat` (retire `FR_P` + remet les PDF EN de backup).
3. Telecharger / dezipper la **derniere** release GitHub.
4. `INSTALLER.bat` (repose `FR_P` + PDF FR + achievements si presents).
5. Relancer.

**Crash au boot ?** → desinstaller tout de suite (`DESINSTALLER.bat`), confirmer que vanilla marche, puis installer **seulement** une release rebuildée pour la maj en cours. Un vieux zip ne “répare” en general pas un cook Steam change. Voir aussi [UI_PATCH_CRASH.md](UI_PATCH_CRASH.md).

**PDF revenus en anglais sans crash ?** → Steam a souvent ecrase `RawFiles/PDFS` : reinstaller la derniere release (etape desinstall + install ci-dessus).

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
- `BluePrints\Cinema` / `BluePrints\Pawns` / `BluePrints\GameActors`

Les libellés UI avec accents sont stockés en FString **UTF-16** (longueur négative). Le cp1252 faisait **disparaître** les lettres accentuées à l’affichage (police / décodage UE).

Regénérer la map ACRS/CryptChat (qualité + accents) :

```powershell
# Éditer / ajouter des lots FR dans work\acrs_batches\fr_*.json
python scripts\merge_acrs_fr_batches.py --write --strict
python scripts\build_ui_uassetgui_patch.py
```

`mt_acrs_cryptchat.py` (Google + strip d'accents) est **déprécié** — ne plus l'utiliser pour le livrable.

Les dialogues CryptChat doivent matcher la **FString exacte** du `.uexp` (souvent un seul bloc avec `\r\n` et placeholders `[LINK]` / `[PRICE]` / `[WIKI]`). Des morceaux découpés ne matchent pas.

## Chemins de fichiers (ne jamais traduire)

Les FString du type `Threats/index.html`, `Hacks/index.html` sont des **chemins** vers `RawFiles/PDFS/…`.  
Les traduire (ex. `Menaces/index.html`) provoque `ERR_FILE_NOT_FOUND` in-game.  
Le merge ACRS et `build_ui_uassetgui_patch.py` forcent l’identité EN=FR pour ces chemins.

## PDF Hacks — bouton `TEST HACK`

Le bouton appelle `HackClick` → `LaunchHackClicked`.  
Traduire le libellé n’a **pas** été la cause : le mini-jeu de test **ne marche pas non plus en vanilla** (confirmé 2026-07-20).  
On laisse le libellé en **`TEST HACK`** (EN) par prudence ; ce n’est pas un bug du mod FR.

## Limites connues (pas de FString extractible)

- Intro Simon (« You are Simon Zhao… ») : introuvable dans les assets / exe (ni ASCII ni UTF-16) — probablement texture, séquence ou génération runtime.
- Boutons « génériques » de `work/ui_fr.csv` **sans FString UI** (ex. Apply, Yes/No génériques, Credits menu, Install, Next…) : **non patchables** par cette méthode. Yes/No n’apparaissent que sur des assets Dark Net (`dontwasteit_*`, hors périmètre).

### HUD mouvement / Enhanced Input (bilan confirmé)

Les libellés `Move` / `Run` / `Inventory` (et variantes `[W,A,S,D] Move`, `[SHIFT] Run`, `[TAB] Inventory` dans les CSV) **n’existent pas** comme FString dans les `.uexp`.

Ils viennent d’**Enhanced Input** : le HUD affiche le nom « leaf » de l’asset InputAction.

| Asset | Affichage typique |
|-------|-------------------|
| `Input/Default/IA_Default_Move` | Move |
| `Input/Default/IA_Default_Run` | Run |
| `Input/Default/IA_Default_Inventory` | Inventory |
| `Input/Default/IA_Default_Look` | Look |
| `Input/Default/IA_Default_Flashlight` | Flashlight |
| `Input/Default/IA_Default_QuickUse` | QuickUse |
| `Input/Default/IA_Default_AidPods` / `Ringonome` / `Alpha` / `Beta` | idem |

Ces `.uexp` sont quasi vides (pas de `DisplayName` cooked). Un rename casserait les chemins `/Game/Input/Default/IA_Default_*` (IMC / blueprints) — **non tenté**.

`Pick Up` : aucune occurrence FString ni dans l’exe Shipping.  
`Crouch` dans l’exe = API CharacterMovement (`IsCrouching`, etc.), pas un prompt HUD de ce jeu.

Les lignes CSV concernées sont marquées `unpatchable_inputaction` (documentation seule, pas injectées par le build).

## Boutons / prompts interaction patchés

| EN | FR | Où |
|----|----|-----|
| `BUY` | `ACHETER` | DarkDrop |
| `Confirm` / `Connect` / `Checkout` | `Confirmer` / `Connecter` / `Commander` | DAREDash |
| `BACK` / `CANCEL` / `GO BACK` / `RETURN HOME` | `RETOUR` / `ANNULER` / … | Settings / DARE |
| `Hide` | `Se cacher` | Pawns (casier / chariot) |
| `[RMB] Exit` / `[RMB] - Exit` | `[Clic droit] Quitter` / `… - Quitter` | Panic / Peep / Hide |
| `[RMB] Get Up From Desk` | `[Clic droit] Se lever du bureau` | Bureau |
| `[RMB] Leave Computer` | `[Clic droit] Quitter l'ordinateur` | Moniteur |
| `Exit To VertMesh` | `Passer à VirtMesh` | Switch VM |
| `Open` / `Close` / `Lock` / `Unlock` | `Ouvrir` / `Fermer` / `Verrouiller` / `Déverrouiller` | Portes (`GameActors`) |
| `Turn On` / `Turn Off` | `Allumer` / `Éteindre` | Interrupteurs / disjoncteurs |
| `Turn On Computer` | `Allumer l'ordinateur` | PC principal |
| `Enter Computer` | `Entrer dans l'ordinateur` | Tooltip input |
| `Peep` / `Repair` | `Regarder` / `Réparer` | Judas / hub réseau |
| `Attempt Defusal` | `Tenter désamorçage` | Bombe |
| `Enter Panic Mode` | `Mode panique` | Bouton panique |
| `Head To Work` | `Aller au travail` | Quitter l'appart |
| `Mount` / `Unmount` / `MINE` / `UNMINE` / `HACK` / `Enter` | `MONTER` / `DÉMONTER` / `MINER` / `DÉMINER` / `PIRATER` / `Entrer` | VirtMesh (menu nœud) |
| `[EXIT]` / `[MOUNTING]` | `[QUITTER]` / `[MONTAGE]` | VirtMesh |

## QA in-game

1. Menu : **Jouer / Continuer / Paramètres / Quitter** (accents visibles)
2. Pause / réglages en FR (Paramètres graphiques / audio…)
3. Tutoriel Ronald + Key Finding en FR (wrap-up complet + Good luck)
4. CryptChat ODDroot/Goggin : message de paiement **et** message avec lien ShadowFetch
5. DarkDrop : descriptions VirtMesh / ShadowFetch + bouton **ACHETER**
6. DAREDash : **Confirmer** / **Commander** / **Annuler** / **Retour**
7. Inventaire : Lettre d'expulsion + descriptions items
8. Interactions monde : **Ouvrir / Déverrouiller**, **Allumer / Éteindre**, **Se cacher**, **Regarder**, etc.
9. PDF FR ; WebSites toujours EN
10. UE4SS désactivé (`dwmapi.dll.off`)
11. Fermer le jeu avant rebuild (sinon verrouillage `FR_P.ucas`)
