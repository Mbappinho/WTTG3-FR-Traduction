# Générer Mappings.usmap (étape UI)

## État actuel (2026-07-17) — SUCCÈS

Moteur : **UE 5.6.1** (`44394996+++UE5+Release-5.6`).

Fichier généré :

- `source/Mappings.usmap`
- Original UE4SS : `Binaries/Win64/ue4ss/WTTGSD-5.6.1-44394996+++UE5+Release-5.6-c838a8ac.usmap`

### Ce qui a marché

1. Proxy `dwmapi.dll` (UE4SS experimental)
2. AOB `UE4SS_Signatures/StaticConstructObject.lua` (prologue UE 5.6.1)
3. Profil **dump-only** : seuls `AutoDumpUSMAP` + `Keybinds` actifs
4. `DumpUSMAP()` à t+2s → *Mappings Generation Completed Successfully!*
5. UE4SS **re-désactivé** après dump (`dwmapi.dll.off`)

### Config dump-only

- `bUseUObjectArrayCache = false`
- `UseCache = 0`, `DoEarlyScan = 1`
- `MajorVersion = 5`, `MinorVersion = 6`, `DebugBuild = 0`
- Mods gameplay désactivés (CheatManager, BPModLoader, etc.)

Hotkey manuel (si besoin) : **Ctrl + Pavé 6** → `DumpUSMAP`

## Re-dump

```powershell
# 1. Activer proxy
Move-Item ...\Win64\dwmapi.dll.off ...\Win64\dwmapi.dll
# 2. AutoDumpUSMAP : 1 dans ue4ss\Mods\mods.txt
# 3. Lancer WTTGSD-Win64-Shipping.exe, attendre ~3s
# 4. Copier ue4ss\*.usmap → Projects\WTTG3-FR-Loc\source\Mappings.usmap
# 5. Désactiver proxy (dwmapi.dll → .off), AutoDumpUSMAP : 0
```

## Désactiver UE4SS (jeu normal)

Renomme `dwmapi.dll` → `dwmapi.dll.off`
