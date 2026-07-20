# UI Patch Crash notes — historique / Steam

## Symptômes passés

| Version | Erreur | Cause |
|---------|--------|--------|
| v1 | ACCESS_VIOLATION | Remplacements non-FString |
| v3 | `Serial size mismatch` | FString plus courte sans maj SerialSize DataAsset |
| v4 | `Bad name index` (`WBP_TitleMenuButton`) | FString plus longue en hex brut sur WBP |
| v5 | (stable) | Même longueur forcée — FR contraint |
| v6 | free-length UAssetGUI sur extract **Desktop** | Crash Steam : `Bad export index` sur `WBP_MainTitleSettingsWidget` |
| v6.2 | Overlay Desktop (même unpatched) sur Steam | Crash — cook Desktop ≠ Steam (tailles uexp différentes) |

## Preuve cook Desktop ≠ Steam

| Asset | Desktop `.uexp` | Steam `.uexp` |
|-------|-----------------|---------------|
| `WBP_MainTitleSettingsWidget` | 10081 | 11249 |
| `WBP_MainTitleWidget` | 4226 | 5220 |
| `WBP_Pause` | 19489 | 20657 |

## Correctif v6.3

1. Extract Steam : `retoc to-legacy --version UE5_6 <Steam>/WTTGSD/Content/Paks` → `source/legacy_ui_steam/`
2. `build_ui_uassetgui_patch.py` utilise **`legacy_ui_steam`** s’il existe (sinon `legacy_ui` Desktop)
3. Rebuild + deploy `WTTGSD-Windows_FR_P.*` sur l’install Steam

Vanilla Steam sans `FR_P` boote. Le mod doit être rebuildé **depuis l’extract Steam**.

## Pipeline actuel

1. `source/Mappings.usmap` (voir [DUMP_USMAP.md](DUMP_USMAP.md))
2. Extract legacy depuis **le même build** que le jeu cible (Steam)
3. `scripts/build_ui_uassetgui_patch.py` — UAssetGUI free-length
4. `retoc to-zen` → `WTTGSD-Windows_FR_P.*`

## UE4SS

Reste **désactivé** pour jouer (`dwmapi.dll.off`). Réactiver uniquement pour re-dump usmap.
