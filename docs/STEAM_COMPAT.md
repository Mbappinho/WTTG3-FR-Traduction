# Compatibilité Steam — pack FR

Le mod `WTTGSD-Windows_FR_P` doit matcher le **cook exact** du jeu Steam installé.

## Version validée (pack v1.7.3)

| Champ | Valeur |
|-------|--------|
| Jeu | Welcome to the Game III (Steam) |
| AppID Steam | `3869850` |
| **BuildID** | **`26306350`** |
| Depot | `3869851` |
| Manifest depot | `2133450490465218873` |
| Dernière maj Steam (locale) | BuildID lu 2026-11-24 (Halloween Update v1.1, jeu « VER. 1.1.0 ») |
| Source | `steamapps/appmanifest_3869850.acf` |

Si ton `buildid` dans `appmanifest_3869850.acf` est **différent**, désinstalle le mod ou attends / installe une release FR rebuildée pour ce build.

## Détection automatique (pack débutant)

`INSTALLER.bat` lit `fichiers/steam_target.json` (BuildID du pack) et le compare à
`appmanifest_3869850.acf`. Les bibliothèques Steam sont lues via le registre et
`steamapps/libraryfolders.vdf` (pas seulement Program Files / D: / E:).

- **OK** — BuildID identique → installation normale  
- **ATTENTION** — BuildID différent → avertissement + confirmation pour forcer (déconseillé)  
- **INFO** — manifest introuvable (copie non Steam) → confirmation manuelle  

## Vérifier ton BuildID à la main

Ouvre (chemins typiques) :

`C:\Program Files (x86)\Steam\steamapps\appmanifest_3869850.acf`  
ou `C:\Steam\steamapps\appmanifest_3869850.acf`

Cherche la ligne :

```
"buildid"		"........"
```

Mettre à jour `release/steam_target.json` à chaque rebuild post-MAJ avant de publier une release.

## Historique packs ↔ builds

| Release FR | BuildID Steam cible | Notes |
|------------|---------------------|--------|
| v1.7.3 | `26306350` | Rebuild post-MAJ Steam (Halloween v1.1, ex-24463842) ; aucune ligne FR perdue ; contenu fin secrète (File Decryptor, clé USB) en EN |
| v1.7.2 | `24463842` | Loc FR QA (WASD PDF, tutoiement, calques) ; overlay sous-titres HitTestInvisible (CryptChat) ; console UE4SS coupée |
| v1.7.1 | `24463842` | Installeur : N apres O coupe dwmapi ; merge UE4SS tiers ; Steam libraryfolders.vdf ; SHA256 auto-update |
| v1.7.0 | `24463842` | Sous-titres cinematiques optionnels (UE4SS, O/N) ; credit iPresing PR #1 |
| v1.6.3 | `24463842` | Rebuild post-MAJ Steam (ex-24415407) |
| v1.6.2 | `24415407` | INSTALLER ne desactive plus dwmapi.dll sauf si AzertyRemap present (PR #1) |
| v1.6.1 | `24415407` | Retrait injecteur AZERTY (fatal errors) ; pak ZQSD seul + doc mini-jeux W/A |
| v1.6.0 | `24415407` | ~~UE4SS/AHK mini-jeux~~ retire en 1.6.1 ; INSTALLER relance apres maj GitHub |
| v1.5.3 | `24415407` | Rebuild post-MAJ Steam + option AZERTY (`FR_AZERTY_P`, ZQSD) |
| v1.5.2 | `24359942` | Auto-update : sync pack local + stamp version dans Paks (plus de fausse maj au 2e lancement) |
| v1.5.1 | `24359942` | Fix Normal+ / tooltip résolution / DAREDash footer+catalogue Drugs / accents clé employé |
| v1.5.0 | `24359942` | Rebuild post-MAJ Steam ; labels rôles CryptChat (Hacker/Doxeur/…) |
| v1.4.2 | `24327711` | Saluts ACRS Difficulty + Tier 1 hacker for hire ; gaps Online/Rep exe documentés |
| v1.4.1 | `24327711` | HUD polish (pay up, Payment, Upload to, Price, DARE mins) ; auto-update GitHub dans INSTALLER.bat |
| v1.4 | `24327711` | Rebuild post-MAJ Steam ; Nexus = drop-in sans scripts |
| v1.3 | `24303741` | Même contenu que v1.2.9 (intro Simon + PDF Hacks vanilla) ; renommage version |
