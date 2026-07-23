# Relecture humaine — notes

## P0 (fait, à revalider in-game)

- PDF VirtMesh / Hacks / Threats : traduits ; noms techniques (INJ3KT-R, K3RN3LC0MP1L3R, sujets) **conservés**.
- **Intro Simon Zhao** : texte EN dans texture `AptLoadingScreen` (1064×810 BGRA). **Patché FR** dans `FR_P` (2026-07-21). Note : `TitleLogoA/B` = logo W3LCM3, pas l’intro.
- Settings restants : `Master Audio`, `Browser & Files` / Resolution / FPS / GPU Acceleration / Requires Restart.
- **Difficulté** : bullets Normal+ — maj `24359942` a retiré `Experimental` ; clé à 2 lignes remappée (`Same as Normal` / `Perma Death`).
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
- **UI v1.2.6** : titre Tanner raccourci (`Scène crime Tanner`) + page costumes ; skip ciné ; BitHit ; participants ; `SEND`→`ENVOYER` ; `Default`→`Défaut` ; `BUY` déjà mappé.
- **v1.2.7+** : `Enter Desk` dual — `BP_BlankPawnSwitcher` → `S'asseoir au bureau` ; desk→écran → `Sur bureau` (aussi override **Maps/Motel.uexp**, sinon le niveau force l’EN).
- **v1.2.8** : BitHit `Wallet`→`Solde` (anti-overflow) ; `230 Seconds`→`230 sec.` ; gaps DarkDrop `INSTALLING`/`INSTALLED!`/`OWNED` **absents des FStrings** cookées (probablement runtime/C++).
- **v1.4** : rebuild post-MAJ Steam (BuildID `24327711`) ; pack Nexus **drop-in** sans `.bat`/`.ps1` (évite quarantaine « suspicious files »).
- **HUD / système (lot post-v1.4, rebuild local)** : `Next Rep Level:` ; `[CONNECTING]` ; `Online` (Title Case, FString) ; `Uploading...` ; `Processing` ; `Status:` / `Total:` / `Items:` / `ETA:` / `QTY` / `Qty: 99` ; popup rep `<Bold>…</> Sent <XP>…</> Rep` ; BitHit `DOS Coin For … YoloYen` ; tip settings PDF/pages web. Voir `work/competitor_gap_analysis/README.md`.
- **v1.4.1** : lot map `pay up` / `Payment???` / `Upload to \r\nX` / `Price` / `2 - 4 mins` ; **auto-update GitHub** dans `INSTALLER.bat` (Full) via `steam_target.json` + zip release.
- **v1.4.2** : saluts ACRS Difficulty + Tier 1 hacker for hire ; gaps Online/Rep exe documentés.
- **Doc release** : templates `LIREMOI_*` + `RELEASE_NOTES_TEMPLATE.md` — install / maj auto (Full) / manuel / Nexus a tenir a jour a chaque upload.
- **v1.5.0** : rebuild post-MAJ Steam BuildID `24359942` ; **11 labels rôles** CryptChat dans `WBP_CryptChatMessageTab` (Hacker, Doxeur, Dealer, Courtier de tueurs, …) ; dialogue Ronald wrap-up + ligne `4AM Tonight` ; `GAME MASTER` (AgentTag). Rapport : `work/maj_24359942/RAPPORT.md`.
- **v1.5.1** : Normal+ 2 bullets (sans Experimental) ; tooltip résolution navigateur combiné ; DAREDash footer Sessions/Access + **catalogue Drugs** ; accents clé employé.
- **Audit concurrent UE4SS** : ~213 EN absents de nos maps dont ~151 Wiki (exclus volontaires) ; **1** EN=FR (`47.56 / Min`, déjà chez nous) ; **1** oubli flagrant (dialogue NOPSled quasi non traduit). Pas de gap HUD massif de leur côté.
- **v1.2.9 / v1.3** : intro Simon via texture `AptLoadingScreen` FR ; PDF Hacks comportement vanilla (trad FR seule) ; essais TEST HACK mis de côté. v1.3 = même pack, tag version public.
- **Gaps runtime** : DarkDrop `OWNED`/`INSTALLING`/`INSTALLED!` ; ShadowFetch prompts download ; simulation `ONLINE` (ALL CAPS, absent du cook) / `AFK` / `MINED` / `Using …` ; BitHit `15 Seconds` dynamique (seul le défaut `230 Seconds` est patchable).
- **ACRS panneau user (confirmé exe, BuildID `24327711`)** : `Online` / `Offline` et `Not Enough Rep - Required Rep Level %d` sont des littéraux **C++** dans `WTTGSD-Win64-Shipping.exe` (à côté de `PingPress` / `UserNameClickAction`). Le `FR_P` patch bien les FString défaut du widget (`En ligne`, `Pas assez…`) mais le runtime les **écrase**. Pas corrigeable via pak seul (il faudrait patch exe ou UE4SS). Ne pas confondre avec `ONLINE` simulation.

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
- **Compat Steam documentée** : BuildID `24303741` (AppID 3869850) pour pack v1.2.7 — `docs/STEAM_COMPAT.md`.
- Overlay Steam officiel : non modifiable sans Steamworks ; fichier local steam_settings mis à jour pour usage perso.
- Entrées `ui_fr.csv` sans FString correspondante (Apply, Yes/No génériques, etc.) : **ne peuvent pas** être injectées telles quelles.

## Glossaire

Voir `work/glossary.json`.
