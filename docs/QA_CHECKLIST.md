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

## Option AZERTY (`FR_AZERTY_P`)

Prérequis : `python scripts\build_azerty_imc_patch.py` + pak présent dans `Paks`.
Windows reste en **AZERTY** (ne pas basculer en QWERTY pour ce test).

- [x] Sans `FR_AZERTY_P` : W avance
- [x] Avec `FR_AZERTY_P` : **Z** avance, **Q** gauche, S/D inchangés
- [ ] Inventaire : touche **A** (remap de Q) si applicable
- [ ] Saisie CryptChat / champs texte : toujours le layout Windows (pas cassée)
- [ ] Full INSTALLER : prompt O/N ; N n’installe pas `FR_AZERTY_P`
- [ ] DESINSTALLER retire aussi `FR_AZERTY_P.*`

## Rollback

- [ ] `restore_english.ps1` + suppression `WTTGSD-Windows_FR_P.*` (et `FR_AZERTY_P.*`) testes une fois
