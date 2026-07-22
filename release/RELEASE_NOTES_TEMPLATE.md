# Notes de release GitHub — modèle

Copier / adapter dans `gh release create` (section body).
Mettre à jour `pack_version` dans `release/steam_target.json` avant le pack.

---

## Summary
- (1–3 puces : ce qui change pour le joueur)
- BuildID Steam : `24327711`

## Install (premiere fois)
**GitHub Full** (`WTTG3-FR-Traduction.zip`)
1. Fermer le jeu
2. Dezipper → `INSTALLER.bat`
3. Indiquer le dossier Steam du jeu si besoin
4. Confirmer O → relancer le jeu

**Nexus** (`WTTG3-FR-Traduction-Nexus.zip`)
1. Fermer le jeu
2. Dezipper **dans** le dossier du jeu (celui qui contient `WTTGSD`)
3. Relancer

## Mettre a jour (proprement)
**Auto-update (Full v1.4.1+)** — recommande
1. Relancer `INSTALLER.bat` de ton pack actuel
2. Si « version plus recente » → O
3. Confirmer l'install → O

**Manuel Full**
1. Telecharger la derniere `WTTG3-FR-Traduction.zip`
2. `DESINSTALLER.bat` (ancien) puis `INSTALLER.bat` (nouveau)

**Nexus**
1. Telecharger la derniere `WTTG3-FR-Traduction-Nexus.zip`
2. Re-dezipper par-dessus le dossier jeu (ecrase `FR_P` + PDF)
3. Pas d'auto-update sur Nexus → pour l'auto : pack Full GitHub

## Apres une maj Steam
- BuildID change → il faut une **release FR rebuildée** (pas un vieux zip)
- Crash au lancement → supprimer `WTTGSD-Windows_FR_P.*` / desinstaller, puis release a jour

## Fichiers de la release
- `WTTG3-FR-Traduction.zip` — Full (INSTALLER + auto-update)
- `WTTG3-FR-Traduction-Nexus.zip` — drop-in Nexus
- `steam_target.json` — meta `pack_version` + BuildID (lu par l'auto-update **avant** le gros zip)
