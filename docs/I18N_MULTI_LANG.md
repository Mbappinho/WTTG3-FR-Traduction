# Multi-langues WTTG3 (zh-CN / zh-TW / ja / ko)

## Statut (2026-08-12) — export only

Le livrable public reste **FR uniquement**. Il n’y a **pas** de script
`import_i18n_*.py`, **pas** de packs ZH/JA/KO, **pas** de zip joueur hors FR.

L’export (`scripts/export_i18n_inventory.py` → `work/i18n_export/`) est un
inventaire figé du périmètre FR, prêt si on reprend le chantier. Tant que
l’import n’existe pas, ne pas annoncer de packs cibles comme s’ils étaient
en cours de build.

Cibles **éventuelles** (non livrées) :

| Locale | Mod IoStore | Pack joueur (cible) |
|--------|-------------|---------------------|
| `zh-CN` | `WTTGSD-Windows_ZHCN_P` | `WTTG3-ZH-CN-Traduction.zip` |
| `zh-TW` | `WTTGSD-Windows_ZHTW_P` | `WTTG3-ZH-TW-Traduction.zip` |
| `ja` | `WTTGSD-Windows_JA_P` | `WTTG3-JA-Traduction.zip` |
| `ko` | `WTTGSD-Windows_KO_P` | `WTTG3-KO-Traduction.zip` |

## Inventaire EN (export)

```powershell
python scripts\export_i18n_inventory.py
```

Sortie : [`work/i18n_export/`](../work/i18n_export/)

| Fichier | Usage |
|---------|--------|
| `en_master.csv` | Vue tableur (UTF-8 BOM) — colonnes `zh-CN` `zh-TW` `ja` `ko` |
| `en_master.json` | Catalog complet + méta |
| `batches/batch_XXX.json` | Lots ~115 entrées (~1500 lignes) pour le modèle |
| `QWEN_PROMPT.md` | Consignes à coller au modèle |
| `RETURN_FORMAT.md` | Comment nous renvoyer les fichiers |
| `templates/*.json` | Coquilles `id → traduction` par locale |

## Si on reprend (plus tard)

1. Exporter l’inventaire (`export_i18n_inventory.py`)
2. Traduire les batches / CSV
3. Déposer les fichiers remplis dans `work/i18n_import/`
4. **Écrire** `import_i18n_batches.py` (n’existe pas) puis rebuild 4 mods `_P`
5. Packs débutants séparés + même contrainte BuildID Steam que le FR

## Hors inventaire texte (mêmes limites FR)

- Sites web Dark Net
- Audio
- HUD Enhanced Input (`Move` / `Run` / …)
- Littéraux C++ exe
- Intro Simon = texture `AptLoadingScreen` (pipeline image séparée)

## Références

- Pipeline FR : `docs/INSTALL.md`, `docs/UI_PATCH_CRASH.md`
- Glossaire : `work/glossary.json`
