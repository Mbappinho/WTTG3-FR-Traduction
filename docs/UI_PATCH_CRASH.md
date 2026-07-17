# Patch UI — historique / pipeline usmap

## Symptômes passés

| Version | Erreur | Cause |
|---------|--------|--------|
| v1 | ACCESS_VIOLATION | Remplacements non-FString |
| v3 | `Serial size mismatch` | FString plus courte sans maj SerialSize DataAsset |
| v4 | `Bad name index` (`WBP_TitleMenuButton`) | FString plus longue en hex brut sur WBP |
| v5 | (stable) | Même longueur forcée — FR contraint |

## Pipeline actuel (v6) — usmap + UAssetGUI

1. `source/Mappings.usmap` dumpé via UE4SS (voir [DUMP_USMAP.md](DUMP_USMAP.md))
2. `scripts/build_ui_uassetgui_patch.py` :
   - `UAssetGUI tojson` / patch RawExport / `fromjson` (`VER_UE5_6` + usmap)
   - longueurs FR **libres** (`Jouer`, `Continuer`, `Inventaire`…)
3. `retoc to-zen` → `WTTGSD-Windows_FR_P.*`

Ancien script longueur fixe : `scripts/build_ui_binary_patch.py` (secours seulement).

## UE4SS

Reste **désactivé** pour jouer (`dwmapi.dll.off`). Réactiver uniquement pour re-dump usmap.
