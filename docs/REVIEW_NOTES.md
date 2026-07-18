# Relecture humaine — notes

## P0 (fait, à revalider in-game)

- PDF VirtMesh / Hacks / Threats : traduits ; noms techniques (INJ3KT-R, K3RN3LC0MP1L3R, sujets) **conservés**.
- Labels Contestants (PLAYER NAME, LOCATION, etc.).
- Achievements (27) dans `work/achievements_fr.json`.
- **Accents UI** : dict `RAW` avec accents ; patch en FString **UTF-16** (pas cp1252 — les glyphes disparaissaient in-game).
- **Boutons / HUD interaction** : `BUY`→ACHETER ; DARE Confirm/Connect/Checkout ; `Hide`→Se cacher ; portes Open/Close/Lock/Unlock ; Turn On/Off ; Peep, Repair, Attempt Defusal, Enter Panic Mode, Head To Work (`BluePrints\GameActors`).
- **HUD mouvement** (`Move`/`Run`/`Inventory`/`Pick Up`/`Crouch`) : **confirmé non patchable** — labels dérivés des noms `IA_Default_*` (Enhanced Input), pas de FString. CSV annotés `unpatchable_inputaction`. Pas de rename IA (casse les références IMC).

## P1

- Messages spam chat DOS Coin : traduits dans `ui_fr.csv` (ton argotique volontaire).
- Lot MT ACRS/CryptChat (~1200) : accents / style encore perfectibles (hors passe accents UI).

## P2

- Textes libres Contestants (ADDITIONAL INFO, couleurs de cheveux, métiers) : encore largement EN — faible priorité.
- Overlay Steam officiel : non modifiable sans Steamworks ; fichier local steam_settings mis à jour pour usage perso.
- Entrées `ui_fr.csv` sans FString correspondante (Apply, Yes/No génériques, etc.) : **ne peuvent pas** être injectées telles quelles.

## Glossaire

Voir `work/glossary.json`.
