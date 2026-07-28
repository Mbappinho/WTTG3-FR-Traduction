# Notes de release GitHub — modèle

Copier / adapter dans `gh release create` (section body).
Mettre à jour `pack_version` dans `release/steam_target.json` avant le pack.

---

## Summary
- (1–3 puces : ce qui change pour le joueur)
- BuildID Steam : `24415407`
- Pack **v1.6.0** : AZERTY complet (pak + UE4SS/AHK mini-jeux) ; INSTALLER relance apres maj

## Install (premiere fois)
**GitHub Full** (`WTTG3-FR-Traduction.zip`)
1. Fermer le jeu
2. Dezipper → `INSTALLER.bat`
3. Indiquer le dossier Steam du jeu si besoin
4. Confirmer O
5. Optionnel : Activer remap AZERTY (ZQSD) ? O/N
6. Relancer le jeu

**Nexus** (`WTTG3-FR-Traduction-Nexus.zip`)
1. Fermer le jeu
2. Dezipper **dans** le dossier du jeu (celui qui contient `WTTGSD`)
3. Relancer
4. Option AZERTY : copier `optionnel_azerty\WTTGSD-Windows_FR_AZERTY_P.*` vers `WTTGSD\Content\Paks\` (voir LIREMOI)

## Mettre a jour (proprement)
**Auto-update (Full v1.4.1+)** — recommande
Si tu as deja le zip Full avec `INSTALLER.bat` (**v1.4.1+**, dont **v1.5.2**) :
1. Relancer `INSTALLER.bat` de ton pack actuel
2. Si « version plus recente » → O
3. Confirmer l'install → O
(Pas besoin de desinstaller avant pour une maj normale / post-Steam si le script propose la bonne release.)

Les packs **sans** ce `INSTALLER.bat` (Nexus drop-in, ou Full avant 1.4.1) doivent
telecharger le nouveau zip a la main (Methode manuelle ci-dessous).

**Manuel Full**
1. Telecharger la derniere `WTTG3-FR-Traduction.zip`
2. `DESINSTALLER.bat` (ancien) puis `INSTALLER.bat` (nouveau)

**Nexus**
1. Telecharger la derniere `WTTG3-FR-Traduction-Nexus.zip`
2. Re-dezipper par-dessus le dossier jeu (ecrase `FR_P` + PDF)
3. Pas d'auto-update sur Nexus → pour l'auto : pack Full GitHub

## Apres une maj Steam
- BuildID change → il faut une **release FR rebuildée** (pas un vieux zip)
- Crash au lancement → supprimer `WTTGSD-Windows_FR_P.*` (+ `FR_AZERTY_P.*` si present) / desinstaller, puis release a jour

## Option AZERTY
- Full : prompt O/N → pak `FR_AZERTY_P` + runtime `fichiers/azerty_runtime` (UE4SS + AHK)
- Apres maj GitHub : l'installeur **relance** le nouveau script (un seul INSTALLER.bat)
- Nexus : `optionnel_azerty\` pak seul ; mini-jeux = pack Full
- Rebuild : `build_azerty_imc_patch.py` + `build_azerty_runtime.ps1`

## Fichiers de la release
- `WTTG3-FR-Traduction.zip` — Full (INSTALLER + auto-update)
- `WTTG3-FR-Traduction-Nexus.zip` — drop-in Nexus
- `steam_target.json` — meta `pack_version` + BuildID (lu par l'auto-update **avant** le gros zip)
