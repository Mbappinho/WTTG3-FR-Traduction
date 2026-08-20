# Revue qualité traduction FR (in-game)

**Date :** 2026-08-20 · **Pack :** v1.7.1 · **Steam BuildID :** `24463842`  
**Statut :** les 27 findings (QA-001…QA-027) sont **corrigés** et **rebuild** (2026-08-20) : `build_translations.py` + `build_ui_uassetgui_patch.py` + `apply_patch.ps1`. Pak `FR_P` copié dans les Paks du jeu local. Overlay Steam `achievements.json` non posé (dossier `steam_settings` absent). Zip beginner **non** régénéré.

Export : [`work/translation_qa_findings.json`](../work/translation_qa_findings.json) · canvas : `traduction-qa.canvas.tsx`.

Hors scope : LIREMOI / INSTALLER / README ; WebSites Dark Net ; HUD `IA_Default_*` ; littéraux C++ exe ; templates zh/ja/ko.

## Verdict

La loc FR **tient** : ACRS/CryptChat (1419) est globalement propre (tutoiement salon, `déchiffrer` / `hash de clé`, placeholders `[PRICE]` `[LINK]` `[WIKI]` `[DEALERID]`), les chemins `Contestants/*.html` / `Threats/index.html` ne sont **pas** retraduits, les lots `work/acrs_batches/` suivent la map ACRS, les 120 sous-titres ont une voix de perso crédible.

Le **P0** (PDF Hacks en ZQSD vs mini-jeux WASD) est corrigé dans `PDF_REPLACEMENTS` : les PDF indiquent maintenant `[W]/[A]/[S]/[D]`. Les P1/P2 listés ci-dessous sont appliqués dans RAW, ACRS, PDF, SRT, succès et intro PNG.

| Sévérité | n | Statut sources |
|----------|---|----------------|
| P0 | 1 | Corrigé (WASD dans les PDF Hacks) |
| P1 | 12 | Corrigés |
| P2 | 14 | Corrigés (titres succès memes EN **conservés** volontairement) |

## Inventaire (sources de vérité)

RAW **gagne** sur `acrs_cryptchat_fr.json` en cas de collision (14 clés en commun).

| Corpus | Volume | Fichier |
|--------|--------|---------|
| UI / HUD / items / Ronald (RAW) | 364 | [`scripts/build_ui_uassetgui_patch.py`](../scripts/build_ui_uassetgui_patch.py) |
| ACRS + CryptChat | 1419 | [`work/acrs_cryptchat_fr.json`](../work/acrs_cryptchat_fr.json) |
| FStrings mergées shippées | 1769 | `uexp_patch_fr.csv` généré au build |
| PDF phrases | 101 + 64 Contestants | [`scripts/build_translations.py`](../scripts/build_translations.py) |
| Succès | 27 × (nom + desc) | [`work/achievements_fr.json`](../work/achievements_fr.json) (`ACH_TR`) |
| Sous-titres | 28 fichiers / 120 répliques | `release/subtitles_runtime/.../SousTitres/` |
| Intro Simon | 1 paragraphe | [`work/simon_intro_texture/make_fr_png.py`](../work/simon_intro_texture/make_fr_png.py) → `AptLoadingScreen_FR.png` |
| Overrides `Enter Desk` | 3 | `Sur bureau` (desk→écran / Motel) |

**Non injectés** (ne pas relire comme vérité jeu) : [`work/ui_fr.csv`](../work/ui_fr.csv), [`work/ui_gameplay_fr.csv`](../work/ui_gameplay_fr.csv) (`translated_prefix` tronqué — les versions shippées ACRS sont complètes).

## QA mécanique (100 %)

Script rejouable : `python work/translation_qa_scan.py` (heuristiques ; beaucoup de faux positifs). Les findings retenus sont dans le JSON, pas dans un dump brut.

| Check | Résultat |
|-------|----------|
| Placeholders `[PRICE]` `[LINK]` `[SITE]` `[VIDEO]` `[TARGET]` `[DEALERID]` `[WIKI]` `[VMFETCHURL]` | OK sur le shippé |
| Chemins `*.html` | Identité EN=FR (garde-fou 404) |
| `\r\n` Ronald wrap-up / Key Finding | Conservés |
| EN=FR longs | Bruit (hashes, JFIF, `FUCKYOU`, chemins) |
| Faux positifs placeholders | `[RMB]`→`[Clic droit]`, `[ESPACE]`, `[QUITTER]` : **volontaires** |

## Corrections appliquées (2026-08-20)

### P0

- **QA-001** — PDF `shiftSEQ` / `memDEALLOCATER` : `[W]/[A]/[S]/[D]` et `[A]` gauche (plus de ZQSD). Le pak AZERTY remap le **monde**, pas les mini-jeux.

### P1

- **QA-002** — Accents RAW (DarkDrop, Key Finding, cinéma, extras).
- **QA-003** — Tutoiement joueur partout (menus, overwrite save, Key Finding, PDF). Lobby ACRS « vous » (salle) inchangé.
- **QA-004** — PDF `UNMINE` → `DÉMINER`.
- **QA-005–007** — PDF : plus de `crave` ; Tanner « tant mieux : il aime jouer » ; Noir « surgit de nulle part ».
- **QA-008** — « permettra de le retrouver » ; `trou à rats`.
- **QA-009** — Lobby : « On te promet un truc… ».
- **QA-010** — Intro : « on vient te réclamer la mise… » (`AptLoadingScreen_FR.png` régénéré).
- **QA-011** — Wade SRT : « Je vais te faire gagner du temps ».
- **QA-012** — Ronald : « Tu as jusqu'à 4 h du mat' ce soir… » (RAW + ACRS + lots).
- **QA-013** — `satanés` (plus `satânés`).

### P2

- **QA-014** — `RESET VIEW` → `RÉINIT.`
- **QA-015** — fiche Boost : « Force du signal ».
- **QA-016** — espace retiré devant `Doigts rapides` ; titres memes EN **gardés** (God Gamer, Juiced…).
- **QA-017** — descriptions succès : `K3RN3LC0MP1L3R` / `memDEALLOCATER` / `stackPUSHER` ; Agent 67 = tueur à gages.
- **QA-018** — `Peep` → `Guetter`.
- **QA-019** — `pay-it-forward` → groupe d'entraide ; Gatekeep / Hell yeah laissés (registre salon).
- **QA-020** — Wade : `parieur` ; cues 14–15 recoupées (`En échange` sur une cue). Full + Full_FX.
- **QA-021** — Tanner SRT : « Je te zyeute ! »
- **QA-022** — PDF : `nœud central` / `planque`.
- **QA-023** — Contestants `LIEU :`
- **QA-024** — BitHit `Frais réseau :`
- **QA-025** — stackPUSHER : 2e `<strong>[Clic gauche]</strong>`
- **QA-026** — lots ACRS alignés (`page Wiki` ; extras RAW).
- **QA-027** — « Quoi de neuf les enfoirés ? »

## Ce qui est bon (ne pas « recasser »)

- Dialogues agents CryptChat : tutoiement, glossaire `hash de clé` / `déchiffrer` / `backdoor` EN, placeholders.
- Spam lobby : argot volontaire, vouvoiement de salle OK.
- SRT Cletus / Lucas / Breather / proprio : registre perso.
- Dual `Enter Desk` : `S'asseoir au bureau` vs `Sur bureau`.
- DarkDrop titres courts anti-overflow.
- Identité volontaire : `TEST HACK`, `The Kidnapper`, `The Game`, `Key Cue`, `Krystal King`.
- `[RMB]`→`[Clic droit]`, `[ESPACE]`, `[QUITTER]` : libellés de touches, pas des binds WASD.
- Mini-jeux restent **WASD** même avec pak AZERTY (monde = ZQSD).

## Rebuild (fait 2026-08-20)

```powershell
python scripts\build_translations.py
python scripts\build_ui_uassetgui_patch.py
powershell -ExecutionPolicy Bypass -File scripts\apply_patch.ps1
```

Résultat : 1293 assets, 2825 remplacements FString ; intro `AptLoadingScreen` FR ; `MainTitle` Jouer/Continuer OK ; PDF Hacks WASD copiés dans le jeu.

Les `.srt` Wade/Tanner étaient déjà à jour dans `release/subtitles_runtime` (pas de recuit pak). Pour un zip de release : `scripts\build_beginner_pack.ps1` (pas lancé ici).
