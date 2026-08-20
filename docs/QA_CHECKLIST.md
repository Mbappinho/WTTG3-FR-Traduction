# Checklist QA in-game

## Menus / systeme

- [ ] Menus : Jouer / Continuer / Parametres / Quitter
- [ ] Pause / options graphiques & audio en FR
- [ ] Difficulte / credits en FR
- [ ] UE4SS : off (`dwmapi.dll.off`) **sauf** sous-titres O (`dwmapi` + SousTitresFR)
- [ ] Relancer INSTALLER → N aux sous-titres : plus d'injecteur orphelin (dwmapi .off si aucun autre mod)

## Tutoriel / CryptChat

- [ ] Ronald open + VirtMesh / ShadowFetch / Dark Drop
- [ ] Wrap-up Ronald (deconnexion VirtMesh + wiki + guide + ODDroot/Goggin + Good luck ; **4 h du mat'** ce soir)
- [ ] Message ODDroot / Goggin (offre [PRICE]) en FR
- [ ] Apres paiement : lien `[LINK]` + ShadowFetch en FR

## ACRS / CryptChat agents

- [ ] ACRS sous-titre VelvetRoad + barre CHAT DESACTIVE en FR
- [ ] Messages salon (Noobs, scams, pubs decryptors/hitmen/dealers) en FR
- [ ] MP CryptChat decryptor / hitman / dealer / hacker / dox / seekers en FR
- [ ] CryptChat : clic dans le champ de saisie (sous-titres O, après intro Wade)

## Apps / inventaire

- [ ] DarkDrop : VirtMesh, ShadowFetch, bouton ACHETER
- [ ] ShadowFetch : messages ChoiceTree (URL Fetch, telechargement, erreurs)
- [ ] Inventaire titre INVENTAIRE + Lettre d'expulsion + descriptions
- [ ] Pensees Simon (porte fermee, cle, etc.)
- [ ] Judas motel : prompt **Guetter** (Peep)

## PDF / web

- [ ] PDF VirtMesh / Hacks / Threats / Contestants en FR
- [ ] PDF Hacks `shiftSEQ` / `memDEALLOCATER` : binds **[W]/[A]/[S]/[D]** (pas ZQSD)
- [ ] Aucun fichier sous `WebSites/` modifie

## Limites connues (encore EN attendu)

- [x] Intro Simon Zhao (texture `AptLoadingScreen` FR dans `FR_P` — « on vient te réclamer la mise »)
- [ ] Prompts `[W,A,S,D] Move` / `[SHIFT] Run` / `[TAB] Inventory` / `Pick Up`
  (libellés IA_* non patchables ; avec option AZERTY les **binds** deviennent ZQSD)

## Option AZERTY (`FR_AZERTY_P` pak seul, v1.6.1+)

Prérequis : `build_azerty_imc_patch.py` ; pack Full/Nexus.
Windows reste en **AZERTY**. Pas d'injecteur.

- [x] Sans `FR_AZERTY_P` : W avance
- [x] Avec `FR_AZERTY_P` : **Z** avance, **Q** gauche, S/D inchangés
- [ ] Mini-jeux : toujours W/A (PDF Hacks FR = WASD depuis 2026-08-20) — pas de swap auto
- [ ] Full INSTALLER : prompt O/N ; N n’installe pas le pak
- [ ] INSTALLER retire dwmapi/AHK restants d’un vieux 1.6.0
- [ ] DESINSTALLER retire `FR_AZERTY_P.*` + nettoie injecteur restant
- [ ] Saisie CryptChat : layout Windows intact (AZERTY ne remap pas `IMC_Computer`)

## Rollback

- [ ] `restore_english.ps1` + suppression `WTTGSD-Windows_FR_P.*` (et `FR_AZERTY_P.*`) testes une fois
