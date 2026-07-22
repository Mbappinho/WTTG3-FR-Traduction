# Analyse écart vs concurrent UE4SS (2026-07-22)

Pack concurrent analysé : `WTTGSD_Trad_FR … 2026-07-20` (FrenchInject + Wiki.js).

## Méthode

- Leurs textes UI : `translations.lua` (~1688 paires EN→FR) + `WebSites/Global/Wiki.js`.
- Nos maps : `scripts/build_ui_uassetgui_patch.py` + `work/acrs_cryptchat_fr.json` + CSV/batches.
- Scripts : `work/compare_competitor_gaps.py`, `work/refine_competitor_gaps.py`, `work/validate_hud_candidates.py`.

## Synthèse

| Métrique | Valeur |
|----------|--------|
| EN chez eux absents de nos maps | ~213 |
| dont Wiki / sites (exclus volontaires) | ~151 |
| dont candidats jeu | ~71 |
| présents dans extract Steam | ~61 |
| Lot HUD/système retenu et patché | voir ci-dessous |

Beaucoup de « manques » HUD du premier passage étaient des **faux positifs** (déjà dans notre map : fin de run, save overwrite, banners hack, sessions DARE, etc.) — ils nécessitent seulement un rebuild `FR_P`.

## Audit anglais oubliés (concurrent)

| Résultat | Détail |
|----------|--------|
| EN = FR strict | **1** : `47.56 / Min` (déjà traduit chez nous) |
| Oubli flagrant | **1** : dialogue NOPSled quasi non traduit (`lol instant NOPSled freak out…`) |
| Crédits | `VER. 1.0.x` → `Traduit par RNG_KZK` |
| Qualité | fautes / calques fréquents, pas un stock d’UI EN oubliée |

## Lot HUD/système ajouté (rebuild local, pas encore release)

| EN | FR | Asset / notes |
|----|----|---------------|
| `Next Rep Level:` | `Niveau de réputation suivant :` | `WBP_RepXPHoverWidget` |
| `<Bold>SomeAgent</> Sent <XP>1500</> Rep` | `… a envoyé … de rép` | `WBP_RepXPRecPopUp` |
| `[CONNECTING]` | `[CONNEXION]` | `WBP_FakeVMBrowser` |
| `Online` | `En ligne` | FString Title Case (ex. ACRS) ; **≠** `ONLINE` ALL CAPS (runtime, absent cook) |
| `Uploading...` | `Envoi...` | CryptChat / Ronald |
| `Processing` | `Traitement` | BitHit / DARE / Settings |
| `Status:` / `Total:` / `Items:` / `ETA:` / `QTY` / `Qty: 99` | FR courte | DARE / DarkDrop |
| `Unknown` | `Inconnu` | DARE (et évent. topics) |
| `999,999.00 DOS Coin For 999,999.00.00 YoloYen` | `… pour …` | BitHit |
| tip freezing webpages / PDFs | tip FR settings | Pause / Title Settings |

## Vérif restante (2026-07-22)

Script : `work/verify_remaining_gaps.py` + `work/inspect_offline_price.py` → `verify_remaining.tsv`.

| Candidat | Verdict |
|----------|---------|
| `Offline` (Title Case) | **Faux positif** — aucune FString seule `Offline` ; seulement `User Offline...` (déjà mappé). Les hits « Offline » étaient des sous-chaînes. |
| `OFFLINE` | Déjà mappé → `HORS LIGNE` (simulation). |
| Lot HUD précédent | **Déjà couvert** (Online, Connecting, Uploading, Status, QTY, rep, BitHit, tip settings, etc.). |
| Bruit concurrent (~37) | Cosmétiques / RP / noms produits / `>./TOKENINE` — **ne pas traduire**. |
| `Price` | **Vrai reste** — FString dans `WBP_DAREdash` (+ widgets produit). **Ajouté en map** (`Prix`), rebuild pending. |
| `2 - 4 mins` | **Vrai reste** — FString dans `WBP_DAREdash`. **Ajouté en map** (`2 - 4 min`), rebuild pending. |
| `pay up` | FString courte WikiHolder NoDOS23 (+ déjà couvert dans longs dialogues). **Ajouté** → `paie`, rebuild pending. |
| `Payment???` | WikiHolder NoDOS15. **Ajouté** → `Le paiement ???`, rebuild pending. |
| `Upload to \r\nX` | CryptChat. **Ajouté** → `Envoyer vers\r\nX`, rebuild pending. |
