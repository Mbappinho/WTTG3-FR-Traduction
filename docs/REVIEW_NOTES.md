# Relecture humaine — notes

## P0 (fait, à revalider in-game)

- PDF VirtMesh / Hacks / Threats : traduits ; noms techniques (INJ3KT-R, K3RN3LC0MP1L3R, sujets) **conservés**.
- **TEST HACK** (PDF) : bug **vanilla** confirmé (même sans mod FR) — pas un souci de trad.
- Settings restants : `Master Audio`, `Browser & Files` / Resolution / FPS / GPU Acceleration / Requires Restart.
- Difficulté : bullets Normal+ (`Same as Normal` / `Perma Death` / `Experimental`) + `Challenging`.
- **Crash Steam post-MAJ** (`LeetMode2` Bad export index, 2026-07-20) : re-extract `legacy_ui_steam` + rebuild FR_P (cook a changé, ex. LeetMode2 3406→3410).
- **Crash Steam post-MAJ** (2026-07-21) : base `WTTGSD-Windows.*` plus récente que `FR_P` → même fix (re-extract + rebuild + PDF FR réappliqués).
- **Bug fix** : `Threats/index.html` avait été traduit en `Menaces/index.html` (Agent_Goggin / ACRS) → PDF Threats en `ERR_FILE_NOT_FOUND`. Remis à `Threats/index.html` ; garde-fou chemins `*.html` dans merge + build.
- Labels Contestants (PLAYER NAME, LOCATION, etc.).
- Achievements (27) dans `work/achievements_fr.json`.
- **Accents UI** : dict `RAW` avec accents ; patch en FString **UTF-16** (pas cp1252 — les glyphes disparaissaient in-game).
- **Boutons / HUD interaction** : `BUY`→ACHETER ; DARE Confirm/Connect/Checkout ; `Hide`→Se cacher ; portes Open/Close/Lock/Unlock ; Turn On/Off ; Peep, Repair, Attempt Defusal, Enter Panic Mode, Head To Work (`BluePrints\GameActors`) ; VirtMesh `MONTER`/`DÉMONTER`/`MINER`/`DÉMINER`/`PIRATER`/`Entrer`.
- **Prompts [RMB]** : `[RMB] Exit` / `- Exit` → `[Clic droit] Quitter` ; Get Up From Desk ; Leave Computer ; `Exit To VertMesh` → Passer à VirtMesh.
- **Crash Steam** (`Bad export index`) : extract Desktop ≠ cook Steam. Fix = `legacy_ui_steam` + rebuild (v1.2.2).  
  **MAJ Steam future** : même risque si le cook change → re-extract + rebuild (pas seulement réinstaller l’ancien zip). Voir `docs/UI_PATCH_CRASH.md`.
- **Prompts monde EN après rebuild Steam** : casse dossier `Blueprints` vs `BluePrints` excluait GameActors/Pawns du pak ; filtre case-insensitive + `PawnSwitchers` / `Enter Desk`.
- **HUD mouvement** (`Move`/`Run`/`Inventory`/`Pick Up`/`Crouch`) : **confirmé non patchable** — labels dérivés des noms `IA_Default_*` (Enhanced Input), pas de FString. CSV annotés `unpatchable_inputaction`. Pas de rename IA (casse les références IMC).
- **DarkDrop noms trop longs** : titres FR raccourcis pour ne plus chevaucher le prix (`Boost signal`, `Capteur mvt`, `Pare-feu II`, `Montage VM III`, etc.).
- **ACRS polish QA** : `en pagne`→`en pagaille`, calques, `backdoor` harmonisé (EN), `pussy`→`tafiole` ; glossaire mis à jour.
- **CryptChat polish** : `ton idée`, `délai de carence`, `Threats/index.html` dans extras, casse The Game/Game Master (Ronald), 1× vous→tu.
- **Lobby ACRS EN oublié** : ~59 topics/spam présents dans l’extract Steam mais absents de `acrs_cryptchat_fr.json` (étaient seulement dans `ui_gameplay_fr.csv`, non injecté). Ajoutés via `work/acrs_batches/fr_lobby_gap.json` + merge.

## P1

- Messages spam chat DOS Coin : traduits dans `ui_fr.csv` (ton argotique volontaire).
- ACRS/CryptChat : **retraduction qualité** (~1354 chaînes) avec accents via `work/acrs_batches/fr_*.json` + `merge_acrs_fr_batches.py`. Ancien Google MT (`acrs_mt_cache`) déprécié.
- Batch ACRS status ads + UI VelvetRoad/ACRS : `work/acrs_batches/fr_status.json` (119 entrées, accents + glossaire).
- Batch ACRS dialogs agents CryptChat EN→FR (lots 00–02) : `work/acrs_batches/fr_dialogs_00_02.json` (300 entrées, tutoiement, accents, placeholders / glossaire).
- Batch ACRS dialogs agents CryptChat EN→FR (lots 03–05) : `work/acrs_batches/fr_dialogs_03_05.json` (300 entrées, tutoiement, accents, placeholders / glossaire).
- Batch ACRS dialogs agents CryptChat EN→FR (lots 06–09) : `work/acrs_batches/fr_dialogs_06_09.json` (321 entrées, tutoiement, accents, placeholders / glossaire).
- Batch ACRS lobby topics/spam EN→FR (`_en_topics_00`–`02`) : `work/acrs_batches/fr_topics.json` (299 entrées, tutoiement, accents, spam/RP argotique, placeholders / glossaire ; DOS Coin & The Game préservés).

## P2

- PDF Contestants : lieux, métiers, couleurs, ADDITIONAL INFO traduits (2026-07-21) ; noms / coords / MAC / IP / téléphones conservés.
- **Compat Steam documentée** : BuildID `24303741` (AppID 3869850) pour pack v1.2.5 — `docs/STEAM_COMPAT.md`.
- Overlay Steam officiel : non modifiable sans Steamworks ; fichier local steam_settings mis à jour pour usage perso.
- Entrées `ui_fr.csv` sans FString correspondante (Apply, Yes/No génériques, etc.) : **ne peuvent pas** être injectées telles quelles.

## Glossaire

Voir `work/glossary.json`.
