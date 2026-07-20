# UI Patch Crash notes — historique / Steam / MAJ

## Règle d’or (à retenir)

Le mod `WTTGSD-Windows_FR_P` **remplace** des packages IoStore du jeu.  
Ces overrides doivent être rebuildés depuis **exactement le même cook** que le jeu installé.

| Situation | Résultat typique |
|-----------|------------------|
| Pack FR buildé depuis extract **Steam**, joué sur **Steam** (même version) | OK |
| Pack FR buildé depuis **Desktop** / autre dump, joué sur **Steam** | Crash `Bad export index` |
| Pack FR Steam, joué sur vieille copie **Desktop** | Peut planter (inverse) |
| **MAJ Steam** qui recook des assets overridés, ancien `FR_P` | Peut **replanter** comme avant |

Ce n’est **pas** un bug de la traduction FR en soi : c’est une **incompatibilité de cook** (tailles / structure `.uasset`+`.uexp` différentes).

## Symptômes passés

| Version | Erreur | Cause |
|---------|--------|--------|
| v1 | ACCESS_VIOLATION | Remplacements non-FString |
| v3 | `Serial size mismatch` | FString plus courte sans maj SerialSize DataAsset |
| v4 | `Bad name index` (`WBP_TitleMenuButton`) | FString plus longue en hex brut sur WBP |
| v5 | (stable) | Même longueur forcée — FR contraint |
| v6 | free-length UAssetGUI sur extract **Desktop** | Crash Steam : `Bad export index` sur `WBP_MainTitleSettingsWidget` |
| v6.2 | Overlay Desktop (même unpatched) sur Steam | Crash — cook Desktop ≠ Steam |
| v6.3 | Rebuild depuis `legacy_ui_steam` | Stable sur Steam (v1.2.2+) |

## Preuve cook Desktop ≠ Steam (audit 2026-07-20)

Sur le périmètre patché : ~1,6 % des `.uexp` différaient ; les écarts critiques :

| Asset | Desktop `.uexp` | Steam `.uexp` |
|-------|-----------------|---------------|
| `WBP_MainTitleSettingsWidget` | 10081 | 11249 |
| `WBP_MainTitleWidget` | 4226 | 5220 |
| `WBP_MainTitlePlayWidget` | 5879 | 6852 |
| `WBP_Pause` | 19489 | 20657 |

Les `.uasset` de ces widgets différaient aussi (pas seulement le `.uexp`).

## MAJ Steam — que faire à l’avenir

### Symptômes possibles après une maj du jeu

- Crash au lancement : `ObjectSerializationError` / `Bad export index` (Titles/Settings **ou** DataAssets, ex. `LeetMode2` après maj 2026-07-20 ; **nouveau cook Steam 2026-07-21** → même procédure re-extract + rebuild)
- Ou, plus rare : jeu qui boote mais trad partielle / textes EN revenus sur des écrans

### Diagnostic rapide

1. Renommer / supprimer `WTTGSD\Content\Paks\WTTGSD-Windows_FR_P.*`
2. Relancer le jeu **vanilla**
3. Si vanilla OK et crash avec le mod → le `FR_P` est **périmé** par rapport au nouveau cook → **rebuild obligatoire**

### Procédure de rebuild (mainteneur)

```powershell
# 1. Fermer le jeu
# 2. Re-extraire depuis l’install Steam à jour
tools\retoc\retoc.exe to-legacy --version UE5_6 `
  "<STEAM>\Welcome to the Game III\WTTGSD\Content\Paks" `
  source\legacy_ui_steam

# 3. Rebuild + deploy (local_game_path.txt / WTTG3_GAME = Steam)
python scripts\build_ui_uassetgui_patch.py

# 4. Pack release
powershell -ExecutionPolicy Bypass -File scripts\build_beginner_pack.ps1
# zipper release\WTTG3-FR-Beginner → nouvelle release GitHub
```

`build_ui_uassetgui_patch.py` préfère automatiquement `source/legacy_ui_steam` s’il existe.

### Côté joueur (pack débutant)

Mise à jour **propre** (après MAJ Steam ou nouvelle release FR) :

1. Fermer le jeu
2. `DESINSTALLER.bat`
3. Installer la **dernière** release GitHub (`INSTALLER.bat`)
4. Relancer

Si **crash** au boot :

1. `DESINSTALLER.bat` immédiatement (retour vanilla)
2. Confirmer que le jeu sans mod démarre
3. Installer uniquement une **nouvelle** release FR rebuildée pour cette maj  
   (réinstaller l’**ancien** zip ne suffit en général **pas** si le cook a changé)

Si seuls les **PDF** sont revenus en anglais (pas de crash) : même procédure désinstall + réinstall — Steam écrase souvent `RawFiles/PDFS`.

## Correctif v6.3 (rappel)

1. Extract Steam → `source/legacy_ui_steam/`
2. Build UI depuis cette base
3. Deploy `WTTGSD-Windows_FR_P.*` sur Steam

## Piège casing Steam : `Blueprints` vs `BluePrints`

L’extract Steam crée le dossier **`Blueprints`** (p minuscule).  
L’ancien dump Desktop utilisait **`BluePrints`**.  

Si le filtre `COPY_PREFIXES` est sensible à la casse, **tous** les prompts monde (`GameActors` / `Pawns` / Cinema) sont **exclus** du pak FR → texte EN in-game alors que le menu FR marche.  
`should_copy()` compare désormais **sans tenir compte de la casse**.

## Pipeline actuel

1. `source/Mappings.usmap` (voir [DUMP_USMAP.md](DUMP_USMAP.md))
2. Extract legacy depuis **le même build** que le jeu cible (Steam)
3. `scripts/build_ui_uassetgui_patch.py` — UAssetGUI free-length
4. `retoc to-zen` → `WTTGSD-Windows_FR_P.*`

## UE4SS

Reste **désactivé** pour jouer (`dwmapi.dll.off`). Réactiver uniquement pour re-dump usmap.
