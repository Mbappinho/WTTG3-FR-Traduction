# Rapport maj Steam — BuildID `24359942`

Date : 2026-07-23  
Ancien pack : **v1.4.2** / BuildID **`24327711`**  
Nouveau jeu : BuildID **`24359942`** (manifest `3958003346115020289`)

## Verdict

| Question | Réponse |
|----------|---------|
| Rebuild `FR_P` obligatoire ? | **Oui** — cook changé (18 `.uexp` taille différente ; ancien FR_P = risque crash) |
| Nouvelles trads joueur ? | **Oui, limité** — 11 libellés de **rôles CryptChat** nouvellement en FString |
| Gros lot de dialogues EN oubliés ? | **Non** — pas de nouveaux dialogs agents / ACRS status détectés |
| Assets Title/Pause/ACRSApp | **Inchangés** en taille |

## Diff cook (extract vs `legacy_ui_steam_bak_24327711`)

- `.uexp` : old 7325 → new 7363  
- Changements de **taille** réels : **18** fichiers (le reste « added/removed » est surtout bruit de chemins / assets 3D)  
- Extract : `source/legacy_ui_steam` (7939 packages retoc OK)

### Critiques UI

| Asset | Delta taille | Impact trad |
|-------|--------------|-------------|
| Title / Pause / ACRSApp | 0 | OK |
| `WBP_CryptChatMessageTab` | **+1340** | **Nouveaux labels rôles** |
| `Maps/Motel` | +356 | Pas de nouvelle FString joueur |
| `Maps/HackerLair` | +867 | Tech / BP only |
| `Seq_Hacker_Ending` | +19050 | Noms composants ciné, pas de texte joueur |
| Difficulty `*Mode*` | +16…+38 | Aucune FString ajoutée/retirée |
| `RonaldTutorialWrapUp4` | +46 | Pas de delta FString détecté |

## Nouveautés à traduire (priorité)

### Bloquant — dialogue Ronald (clé cassée)
`RonaldTutorialWrapUp4` : insertion `\r\n\r\nYou have to 4AM Tonight to beat the game!!\r\n\r\n` → l’ancienne clé FString ne matche plus. **Remappée** (RAW + ACRS).

### Labels rôles CryptChat (`WBP_CryptChatMessageTab`)

Apparues **uniquement** dans `WBP_CryptChatMessageTab.uexp` (absentes du cook précédent) :

| EN | FR proposé |
|----|------------|
| Hacker | Hacker |
| Doxxer | Doxeur |
| Drug Dealer | Dealer |
| Game Master | Game Master |
| Hitman Broker | Courtier de tueurs |
| Informant | Informateur |
| Key Decryptor | Déchiffreur |
| Opponent | Adversaire |
| Site Seeker | Chercheur de sites |
| Video Seeker | Chercheur de vidéos |
| Wiki Seller | Vendeur Wiki |

### Agent tag
| EN | FR |
|----|-----|
| `GAME MASTER` (ALL CAPS, `WBP_CryptChatAgentTag`) | `GAME MASTER` |

### Autre (agents / follow-up)
- TOKENINE rename + `*LeetPhase*` / `DD_Leet_NOPSled` : mêmes FStrings → rebuild suffit
- Saluts Difficulty courts restants : optionnel (hors lot v1.4.2)

## Gaps connus (inchangés, hors FR_P)

- ACRS panneau user : `Online` / `Offline` / `Not Enough Rep - Required Rep Level %d` → **exe C++**
- DarkDrop `OWNED` / `INSTALLING` / `INSTALLED!` → runtime
- HUD Enhanced Input (`Move`/`Run`/…) → non patchable
- WikiHolders → exclus volontairement

## Artefacts

- `work/maj_24359942/summary.txt`
- `work/maj_24359942/top_size_changes.tsv`
- `work/maj_24359942/string_diffs_changed_assets.json`
- `work/maj_24359942/missing_en_candidates.md` (bruité : CVars / usernames / faux positifs)

## Suite

1. Injecter les 11 rôles dans la map UI  
2. Rebuild `FR_P` + deploy Steam  
3. Bump `steam_target.json` → BuildID `24359942` (version pack à décider : **1.5.0** recommandé)  
4. Packs + release GitHub/Nexus **après validation in-game**
