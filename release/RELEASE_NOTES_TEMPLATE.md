# Notes de release GitHub — modèle

Copier / adapter dans `gh release create` (section body).
Mettre à jour `pack_version` dans `release/steam_target.json` avant le pack.

Toujours coller le badge Ko-fi dans le titre Summary (comme README) :
`<a href='https://ko-fi.com/T1P023QR7T' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>`

---

## Summary
- (1–3 puces : ce qui change pour le joueur)
- BuildID Steam : `24463842`
- Pack **v1.7.1** : correctifs installeur (sous-titres N/O, merge UE4SS, Steam VDF, SHA256)

## Install (premiere fois)
**GitHub Full** (`WTTG3-FR-Traduction.zip`)
1. Fermer le jeu
2. Dezipper → `INSTALLER.bat`
3. Indiquer le dossier Steam du jeu si besoin
4. Confirmer O
5. Optionnel : Activer remap AZERTY (ZQSD monde) ? O/N
   (mini-jeux = W/A ou refuse le mod)
6. Optionnel : Activer les sous-titres cinematiques ? O/N (defaut N)
7. Relancer le jeu
8. Si sous-titres : **F9** en jeu = ligne d'essai

**Nexus** (`WTTG3-FR-Traduction-Nexus.zip`)
1. Fermer le jeu
2. Dezipper **dans** le dossier du jeu (celui qui contient `WTTGSD`)
3. Relancer
4. Option AZERTY : copier `optionnel_azerty\WTTGSD-Windows_FR_AZERTY_P.*` vers `WTTGSD\Content\Paks\`
5. Sous-titres : uniquement via le pack Full (pas d'injecteur Nexus)

## Option AZERTY
- Pak seul (pas d'injecteur UE4SS/AHK — retire suite fatal errors)
- Monde = ZQSD ; mini-jeux hack = toujours W/A (positions QWERTY) **ou** ne pas activer AZERTY
- v1.6.0 : si crash, installer 1.6.1+ (nettoie dwmapi) ou DESINSTALLER

## Option sous-titres
- UE4SS **experimental-latest** (layout `ue4ss\`)
- Credit : **iPresing** ([PR #1](https://github.com/Mbappinho/WTTG3-FR-Traduction/pull/1))
- N après un O : retire SousTitresFR et coupe dwmapi s'il ne reste aucun autre mod
- O sur un UE4SS déjà là : merge (n'écrase pas tes autres mods)
- Force `ConsoleEnabled = 0` (pas de fenêtre cmd de debug au lancement)
- Overlay UMG en HitTestInvisible + Collapsed à vide (sinon clics CryptChat avalés)

## Fichiers de la release
- `WTTG3-FR-Traduction.zip` — Full (INSTALLER + auto-update)
- `WTTG3-FR-Traduction-Nexus.zip` — drop-in Nexus
- `steam_target.json` — meta `pack_version` + BuildID (lu par l’auto-update, pas un pack joueur)

Ne **pas** uploader de `.sha256` : l’installeur utilise le digest GitHub du zip. `scripts/hash_release_zips.ps1` reste un contrôle local.
