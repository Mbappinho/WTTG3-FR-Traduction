# Checklist QA in-game

## Menus / systeme

- [ ] Menus : Jouer / Continuer / Parametres / Quitter
- [ ] Pause / options graphiques & audio en FR
- [ ] Difficulte / credits en FR
- [ ] UE4SS off (`dwmapi.dll.off`)

## Tutoriel / CryptChat

- [ ] Ronald open + VirtMesh / ShadowFetch / Dark Drop
- [ ] Wrap-up Ronald (deconnexion VirtMesh + wiki + guide + ODDroot/Goggin + Good luck)
- [ ] Message ODDroot / Goggin (offre [PRICE]) en FR
- [ ] Apres paiement : lien `[LINK]` + ShadowFetch en FR

## ACRS / CryptChat agents

- [ ] ACRS sous-titre VelvetRoad + barre CHAT DESACTIVE en FR
- [ ] Messages salon (Noobs, scams, pubs decryptors/hitmen/dealers) en FR
- [ ] MP CryptChat decryptor / hitman / dealer / hacker / dox / seekers en FR

## Apps / inventaire

- [ ] DarkDrop : VirtMesh, ShadowFetch, bouton ACHETER
- [ ] ShadowFetch : messages ChoiceTree (URL Fetch, telechargement, erreurs)
- [ ] Inventaire titre INVENTAIRE + Lettre d'expulsion + descriptions
- [ ] Pensees Simon (porte fermee, cle, etc.)

## PDF / web

- [ ] PDF VirtMesh / Hacks / Threats / Contestants en FR
- [ ] Aucun fichier sous `WebSites/` modifie

## Limites connues (encore EN attendu)

- [x] Intro Simon Zhao (texture `AptLoadingScreen` FR dans `FR_P`)
- [ ] Prompts `[W,A,S,D] Move` / `[SHIFT] Run` / `[TAB] Inventory` / `Pick Up`
  (libellés IA_* non patchables ; avec option AZERTY les **binds** deviennent ZQSD)

## Option AZERTY (`FR_AZERTY_P` + runtime Full)

Prérequis : `build_azerty_imc_patch.py` + `build_azerty_runtime.ps1` ; pack Full.
Windows reste en **AZERTY**.

- [x] Sans `FR_AZERTY_P` : W avance
- [x] Avec `FR_AZERTY_P` : **Z** avance, **Q** gauche, S/D inchangés
- [ ] MemDealloc / ShiftSEQ : swap AHK pendant le hack (flag UE4SS)
- [ ] KernalCompiler : swap **off** (saisie OK)
- [ ] Full INSTALLER : prompt O/N ; N n’installe pas pak ni runtime
- [ ] DESINSTALLER retire `FR_AZERTY_P.*` + desactive dwmapi / AHK
- [ ] Maj GitHub depuis ancien pack : **un** INSTALLER.bat → nouveau script (relance)
- [ ] Inventaire : touche **A** (remap de Q) si applicable
- [ ] Saisie CryptChat : layout Windows intact

## Rollback

- [ ] `restore_english.ps1` + suppression `WTTGSD-Windows_FR_P.*` (et `FR_AZERTY_P.*`) testes une fois
