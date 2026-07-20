# Compatibilité Steam — pack FR

Le mod `WTTGSD-Windows_FR_P` doit matcher le **cook exact** du jeu Steam installé.

## Version validée (pack v1.2.5)

| Champ | Valeur |
|-------|--------|
| Jeu | Welcome to the Game III (Steam) |
| AppID Steam | `3869850` |
| **BuildID** | **`24303741`** |
| Depot | `3869851` |
| Manifest depot | `3484320614349195729` |
| Dernière maj Steam (locale) | 2026-07-21 ~00:31 (heure locale) |
| Source | `steamapps/appmanifest_3869850.acf` |

Si ton `buildid` dans `appmanifest_3869850.acf` est **différent**, désinstalle le mod ou attends / installe une release FR rebuildée pour ce build.

## Comment vérifier ton BuildID

Ouvre (chemins typiques) :

`C:\Program Files (x86)\Steam\steamapps\appmanifest_3869850.acf`  
ou `C:\Steam\steamapps\appmanifest_3869850.acf`

Cherche la ligne :

```
"buildid"		"........"
```

## Historique packs ↔ builds

| Release FR | BuildID Steam cible | Notes |
|------------|---------------------|--------|
| v1.2.5 | `24303741` | Rebuild post-MAJ 2026-07-21 + Contestants PDF + polish CryptChat |
| v1.2.4 | cook Steam 2026-07-21 (même famille) | Rebuild crash post-MAJ |
| v1.2.2–v1.2.3 | extract Steam antérieur | Obsolète si cook a changé |

Après chaque maj Steam qui change le `buildid`, un **rebuild** est en général obligatoire (voir [UI_PATCH_CRASH.md](UI_PATCH_CRASH.md)).
