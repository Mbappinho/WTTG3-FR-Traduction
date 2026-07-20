# Relecture humaine — notes

## P0 (fait, à revalider in-game)

- PDF VirtMesh / Hacks / Threats : traduits ; noms techniques (INJ3KT-R, K3RN3LC0MP1L3R, sujets) **conservés**.
- **Bug fix** : `Threats/index.html` avait été traduit en `Menaces/index.html` (Agent_Goggin / ACRS) → PDF Threats en `ERR_FILE_NOT_FOUND`. Remis à `Threats/index.html` ; garde-fou chemins `*.html` dans merge + build.
- Labels Contestants (PLAYER NAME, LOCATION, etc.).
- Achievements (27) dans `work/achievements_fr.json`.
- **Accents UI** : dict `RAW` avec accents ; patch en FString **UTF-16** (pas cp1252 — les glyphes disparaissaient in-game).
- **Boutons / HUD interaction** : `BUY`→ACHETER ; DARE Confirm/Connect/Checkout ; `Hide`→Se cacher ; portes Open/Close/Lock/Unlock ; Turn On/Off ; Peep, Repair, Attempt Defusal, Enter Panic Mode, Head To Work (`BluePrints\GameActors`) ; VirtMesh `MONTER`/`DÉMONTER`/`MINER`/`DÉMINER`/`PIRATER`/`Entrer`.
- **Prompts [RMB]** : `[RMB] Exit` / `- Exit` → `[Clic droit] Quitter` ; Get Up From Desk ; Leave Computer ; `Exit To VertMesh` → Passer à VirtMesh.
- **Crash Steam** (`Bad export index`) : extract Desktop ≠ cook Steam (ex. Settings 10081 vs 11249). Fix = `source/legacy_ui_steam` + rebuild. Voir `docs/UI_PATCH_CRASH.md`.
- **HUD mouvement** (`Move`/`Run`/`Inventory`/`Pick Up`/`Crouch`) : **confirmé non patchable** — labels dérivés des noms `IA_Default_*` (Enhanced Input), pas de FString. CSV annotés `unpatchable_inputaction`. Pas de rename IA (casse les références IMC).

## P1

- Messages spam chat DOS Coin : traduits dans `ui_fr.csv` (ton argotique volontaire).
- ACRS/CryptChat : **retraduction qualité** (~1354 chaînes) avec accents via `work/acrs_batches/fr_*.json` + `merge_acrs_fr_batches.py`. Ancien Google MT (`acrs_mt_cache`) déprécié.
- Batch ACRS status ads + UI VelvetRoad/ACRS : `work/acrs_batches/fr_status.json` (119 entrées, accents + glossaire).
- Batch ACRS dialogs agents CryptChat EN→FR (lots 00–02) : `work/acrs_batches/fr_dialogs_00_02.json` (300 entrées, tutoiement, accents, placeholders / glossaire).
- Batch ACRS dialogs agents CryptChat EN→FR (lots 03–05) : `work/acrs_batches/fr_dialogs_03_05.json` (300 entrées, tutoiement, accents, placeholders / glossaire).
- Batch ACRS dialogs agents CryptChat EN→FR (lots 06–09) : `work/acrs_batches/fr_dialogs_06_09.json` (321 entrées, tutoiement, accents, placeholders / glossaire).
- Batch ACRS lobby topics/spam EN→FR (`_en_topics_00`–`02`) : `work/acrs_batches/fr_topics.json` (299 entrées, tutoiement, accents, spam/RP argotique, placeholders / glossaire ; DOS Coin & The Game préservés).

## P2

- Textes libres Contestants (ADDITIONAL INFO, couleurs de cheveux, métiers) : encore largement EN — faible priorité.
- Overlay Steam officiel : non modifiable sans Steamworks ; fichier local steam_settings mis à jour pour usage perso.
- Entrées `ui_fr.csv` sans FString correspondante (Apply, Yes/No génériques, etc.) : **ne peuvent pas** être injectées telles quelles.

## Glossaire

Voir `work/glossary.json`.
