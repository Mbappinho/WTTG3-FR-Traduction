# Phase 1 — Findings (UI Unreal)

## Archives

| Fichier | Taille approx. | Rôle |
|---------|----------------|------|
| `WTTGSD-Windows.pak` | ~12 MB | Conteneur legacy |
| `WTTGSD-Windows.ucas` / `.utoc` | ~3 GB | **IoStore** (contenu principal) |
| `global.ucas` / `.utoc` | ~3 MB | Global IoStore |

## Localisation native

- **Aucun `Game.locres`** trouvé dans les archives.
- Locres présents : `Engine.locres`, `OnlineSubsystem*.locres` (moteur / online, pas le gameplay).
- Steam / jeu : **anglais uniquement**.
- Beaucoup d’assets UE5 **unversioned** → extraction StringTable/DataTable complète nécessite un fichier **`.usmap`** (mappings) encore absent.

## Strings jeu récupérées

Via UEExtractor (scan PAK/IoStore) :

- Inventaire brut : `source/game_locres_full.csv` (~53k lignes, surtout plugins moteur / Ultra Dynamic Sky).
- Inventaire filtré jeu : `source/ui_game_en.csv` (prompts HUD, chat spam DOS Coin, boutons génériques).
- Hash sidecar : `source/strings_raw.locreshashes`.

Exemples P0 confirmés : `Enter Desk`, `[TAB] Inventory`, `[SHIFT] Run`, `[W,A,S,D] Move`.

## Méthode de livraison UI

| Approche | Statut |
|----------|--------|
| Pak override IoStore `WTTGSD-Windows_FR_P.*` | **Viable** via patch binaire `.uexp` + `retoc to-zen` (UE5_6) — voir `scripts/build_ui_binary_patch.py` |
| Pak `Game/fr/*.locres` | Non applicable (pas de `Game.locres` source) |
| Édition uasset (UAssetGUI) | Bloquée sans `.usmap` |
| Overlay PDF + achievements | **Viable immédiatement** |

## Prochaine étape UI (hors livrable actuel)

1. Générer `.usmap` (Dumper-7 / UE4SS) sur `WTTGSD-Win64-Shipping.exe`.
2. Rouvrir IoStore dans FModel + mappings.
3. Extraire widgets / DataTables de dialogue.
4. Reconstruire un vrai patch `_P` ou remplacer les assets ciblés.
