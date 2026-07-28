# Notes de release GitHub — modèle

Copier / adapter dans `gh release create` (section body).
Mettre à jour `pack_version` dans `release/steam_target.json` avant le pack.

---

## Summary
- (1–3 puces : ce qui change pour le joueur)
- BuildID Steam : `24415407`
- Pack **v1.6.1** : retrait injecteur AZERTY ; pak ZQSD seul

## Install (premiere fois)
**GitHub Full** (`WTTG3-FR-Traduction.zip`)
1. Fermer le jeu
2. Dezipper → `INSTALLER.bat`
3. Indiquer le dossier Steam du jeu si besoin
4. Confirmer O
5. Optionnel : Activer remap AZERTY (ZQSD monde) ? O/N
   (mini-jeux = W/A ou refuse le mod)
6. Relancer le jeu

**Nexus** (`WTTG3-FR-Traduction-Nexus.zip`)
1. Fermer le jeu
2. Dezipper **dans** le dossier du jeu (celui qui contient `WTTGSD`)
3. Relancer
4. Option AZERTY : copier `optionnel_azerty\WTTGSD-Windows_FR_AZERTY_P.*` vers `WTTGSD\Content\Paks\`

## Option AZERTY
- Pak seul (pas d'injecteur UE4SS/AHK — retire suite fatal errors)
- Monde = ZQSD ; mini-jeux hack = toujours W/A (positions QWERTY) **ou** ne pas activer AZERTY
- v1.6.0 : si crash, installer 1.6.1+ (nettoie dwmapi) ou DESINSTALLER

## Fichiers de la release
- `WTTG3-FR-Traduction.zip` — Full (INSTALLER + auto-update)
- `WTTG3-FR-Traduction-Nexus.zip` — drop-in Nexus
- `steam_target.json` — meta `pack_version` + BuildID
