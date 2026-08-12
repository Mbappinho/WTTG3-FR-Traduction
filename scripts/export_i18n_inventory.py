# -*- coding: utf-8 -*-
"""
Export the current FR-perimeter English inventory for multi-language translation.

Outputs under work/i18n_export/:
  - en_master.json / en_master.csv  (full catalog)
  - batches/*.json                  (split for Qwen / parallel langs)
  - templates/{locale}.json         (empty translation shells)
  - QWEN_PROMPT.md                  (instructions for translators/models)

Locales: zh-CN, zh-TW, ja, ko
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work" / "i18n_export"
LOCALES = ("zh-CN", "zh-TW", "ja", "ko")
# ~1500 JSON lines/batch (250 entries ≈ 3200 lines → ~115 entries ≈ 1500 lines)
BATCH_SIZE = 115

_ASSET_PATH_RE = re.compile(r"^[A-Za-z0-9_./\\-]+\.(html|css|js|jpg|jpeg|png|gif|fetch)$")


def _load_raw_from_build_script() -> dict[str, str]:
    src = (ROOT / "scripts" / "build_ui_uassetgui_patch.py").read_text(encoding="utf-8")
    start = src.index("RAW: dict[str, str] = {")
    i = src.index("{", start)
    depth = 0
    end = None
    for j, c in enumerate(src[i:], i):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = j + 1
                break
    if end is None:
        raise RuntimeError("Could not parse RAW dict")
    ns: dict = {}
    exec("RAW = " + src[i:end], ns)
    return dict(ns["RAW"])


def _load_pair_overrides() -> list[dict]:
    # Keep in sync with build_ui_uassetgui_patch.PAIR_OVERRIDES_BY_ASSET + MAP_FSTRING_PATCHES
    rows = []
    for asset, mapping in {
        "BluePrints\\PawnSwitchers\\BP_DeskToMonitor": {"Enter Desk": "Sur bureau"},
        "Blueprints\\PawnSwitchers\\BP_DeskToMonitor": {"Enter Desk": "Sur bureau"},
    }.items():
        for en, fr in mapping.items():
            rows.append(
                {
                    "id": f"override::{asset}::{en}",
                    "category": "ui_override",
                    "en": en,
                    "fr_reference": fr,
                    "asset": asset.replace("\\", "/"),
                    "notes": "Context override — same EN key, different meaning than default Enter Desk",
                }
            )
    rows.append(
        {
            "id": "map::Maps/Motel.uexp::Enter Desk",
            "category": "map_fstring",
            "en": "Enter Desk",
            "fr_reference": "Sur bureau",
            "asset": "Maps/Motel.uexp",
            "notes": "Same-length ASCII preferred for map embeds; FR uses Sur bureau",
        }
    )
    return rows


def _load_acrs() -> dict[str, str]:
    p = ROOT / "work" / "acrs_cryptchat_fr.json"
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}


def _load_pdf_replacements() -> list[tuple[str, str]]:
    src = (ROOT / "scripts" / "build_translations.py").read_text(encoding="utf-8")
    # Prefer the value bracket after "= [" — not the type subscript in list[tuple[...]]
    marker = "PDF_REPLACEMENTS"
    start = src.index(marker)
    eq = src.index("=", start)
    i = src.index("[", eq)
    depth = 0
    end = None
    for j, c in enumerate(src[i:], i):
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = j + 1
                break
    if end is None:
        raise RuntimeError("Could not parse PDF_REPLACEMENTS")
    ns: dict = {}
    exec("PDF_REPLACEMENTS = " + src[i:end], ns)
    out = list(ns["PDF_REPLACEMENTS"])
    bad = [x for x in out if not (isinstance(x, tuple) and len(x) == 2)]
    if bad:
        raise RuntimeError(f"Invalid PDF_REPLACEMENTS entries: {bad[:3]!r}")
    return out


def _load_achievements() -> list[dict]:
    p = ROOT / "work" / "achievements_fr.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    rows = []
    for a in data:
        name = a.get("name", "")
        if a.get("displayName_en"):
            rows.append(
                {
                    "id": f"ach::{name}::displayName",
                    "category": "achievement",
                    "en": a["displayName_en"],
                    "fr_reference": a.get("displayName", ""),
                    "asset": name,
                    "notes": "Steam achievement display name (local overlay)",
                }
            )
        if a.get("description_en"):
            rows.append(
                {
                    "id": f"ach::{name}::description",
                    "category": "achievement",
                    "en": a["description_en"],
                    "fr_reference": a.get("description", ""),
                    "asset": name,
                    "notes": "Steam achievement description (local overlay)",
                }
            )
    return rows


def _load_glossary() -> dict:
    p = ROOT / "work" / "glossary.json"
    if not p.exists():
        return {"preserve": [], "preferred": {}, "rules": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _do_not_translate(en: str, glossary: dict) -> tuple[bool, str]:
    if _ASSET_PATH_RE.match(en.strip()):
        return True, "file_path"
    if en in set(glossary.get("preserve") or []):
        return True, "glossary_preserve"
    # Identity FR often means keep EN
    return False, ""


def build_catalog() -> list[dict]:
    glossary = _load_glossary()
    raw = _load_raw_from_build_script()
    acrs = _load_acrs()
    pdf = _load_pdf_replacements()

    rows: list[dict] = []
    seen: set[str] = set()

    def add(
        en: str,
        *,
        category: str,
        fr: str = "",
        asset: str = "",
        notes: str = "",
        id_suffix: str = "",
    ) -> None:
        key_id = id_suffix or f"{category}::{en}"
        if key_id in seen:
            return
        seen.add(key_id)
        dnt, why = _do_not_translate(en, glossary)
        # If FR kept identity on purpose for preserve terms
        if fr and fr == en and en in set(glossary.get("preserve") or []):
            dnt, why = True, "glossary_preserve"
        row = {
            "id": key_id,
            "category": category,
            "en": en,
            "fr_reference": fr,
            "asset": asset,
            "do_not_translate": dnt,
            "dnt_reason": why,
            "notes": notes,
            "translations": {loc: (en if dnt else "") for loc in LOCALES},
        }
        rows.append(row)

    for en, fr in raw.items():
        add(en, category="ui_raw", fr=fr)

    for en, fr in acrs.items():
        # skip if already in RAW (RAW wins in build)
        if en in raw:
            continue
        add(en, category="acrs_cryptchat", fr=fr)

    for en, fr in pdf:
        add(en, category="pdf_html", fr=fr, notes="Phrase replace in RawFiles/PDFS HTML")

    for ov in _load_pair_overrides():
        key_id = ov["id"]
        if key_id in seen:
            continue
        seen.add(key_id)
        en = ov["en"]
        dnt, why = _do_not_translate(en, glossary)
        rows.append(
            {
                "id": key_id,
                "category": ov["category"],
                "en": en,
                "fr_reference": ov.get("fr_reference", ""),
                "asset": ov.get("asset", ""),
                "do_not_translate": dnt,
                "dnt_reason": why,
                "notes": ov.get("notes", ""),
                "translations": {loc: (en if dnt else "") for loc in LOCALES},
            }
        )

    for ach in _load_achievements():
        key_id = ach["id"]
        if key_id in seen:
            continue
        seen.add(key_id)
        en = ach["en"]
        dnt, why = _do_not_translate(en, glossary)
        rows.append(
            {
                **ach,
                "do_not_translate": dnt,
                "dnt_reason": why,
                "translations": {loc: (en if dnt else "") for loc in LOCALES},
            }
        )

    # Stable sort: category then id
    rows.sort(key=lambda r: (r["category"], r["id"]))
    return rows


def write_outputs(rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    batches_dir = OUT / "batches"
    templates_dir = OUT / "templates"
    if batches_dir.exists():
        for p in batches_dir.glob("*"):
            p.unlink()
    batches_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)

    meta = {
        "game": "Welcome to the Game III",
        "steam_appid": "3869850",
        "perimeter": "same_as_current_FR_pack",
        "locales": list(LOCALES),
        "packs": {
            "zh-CN": "WTTGSD-Windows_ZHCN_P",
            "zh-TW": "WTTGSD-Windows_ZHTW_P",
            "ja": "WTTGSD-Windows_JA_P",
            "ko": "WTTGSD-Windows_KO_P",
        },
        "entry_count": len(rows),
        "translatable_count": sum(1 for r in rows if not r["do_not_translate"]),
        "do_not_translate_count": sum(1 for r in rows if r["do_not_translate"]),
        "categories": sorted({r["category"] for r in rows}),
        "excluded_from_this_export": [
            "RawFiles/WebSites (voluntary EN)",
            "Audio / voice",
            "Enhanced Input HUD labels (Move/Run/Inventory)",
            "C++ exe literals that override widgets",
            "AptLoadingScreen texture intro (separate image pipeline)",
        ],
        "source_build_reference": "FR pack pipeline (build_ui_uassetgui_patch + build_translations + achievements)",
    }

    master = {"meta": meta, "entries": rows}
    (OUT / "en_master.json").write_text(
        json.dumps(master, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Flat CSV for spreadsheet / Qwen paste
    csv_path = OUT / "en_master.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
                "category",
                "en",
                "fr_reference",
                "do_not_translate",
                "dnt_reason",
                "asset",
                "notes",
                "zh-CN",
                "zh-TW",
                "ja",
                "ko",
            ]
        )
        for r in rows:
            tr = r["translations"]
            w.writerow(
                [
                    r["id"],
                    r["category"],
                    r["en"],
                    r["fr_reference"],
                    "1" if r["do_not_translate"] else "0",
                    r.get("dnt_reason", ""),
                    r.get("asset", ""),
                    r.get("notes", ""),
                    tr.get("zh-CN", ""),
                    tr.get("zh-TW", ""),
                    tr.get("ja", ""),
                    tr.get("ko", ""),
                ]
            )

    # Batches: only translatable rows, for model work
    todo = [r for r in rows if not r["do_not_translate"]]
    for i in range(0, len(todo), BATCH_SIZE):
        chunk = todo[i : i + BATCH_SIZE]
        batch = {
            "batch_index": i // BATCH_SIZE,
            "batch_size": len(chunk),
            "locales": list(LOCALES),
            "instruction": "Fill translations[locale] for each entry. Keep placeholders and \\r\\n exact. Leave do_not_translate entries alone (none in batches).",
            "entries": [
                {
                    "id": r["id"],
                    "category": r["category"],
                    "en": r["en"],
                    "fr_reference": r["fr_reference"],
                    "notes": r.get("notes", ""),
                    "translations": {loc: "" for loc in LOCALES},
                }
                for r in chunk
            ],
        }
        (batches_dir / f"batch_{i // BATCH_SIZE:03d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # Per-locale empty template (id -> translation)
    for loc in LOCALES:
        tpl = {
            "locale": loc,
            "pack_mod_base": meta["packs"][loc],
            "entries": {
                r["id"]: (r["en"] if r["do_not_translate"] else "") for r in rows
            },
        }
        (templates_dir / f"{loc}.json").write_text(
            json.dumps(tpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # Manifest for returning filled work
    (OUT / "RETURN_FORMAT.md").write_text(
        """# Format de retour (traductions)

## Option A — CSV (recommandé si Excel / Sheets)
1. Ouvre `en_master.csv` (UTF-8 BOM).
2. Remplis les colonnes `zh-CN`, `zh-TW`, `ja`, `ko`.
3. Ne modifie **pas** la colonne `en` ni `id`.
4. Si `do_not_translate=1`, laisse la traduction = `en` (ou vide, on forcera l'identité).
5. Renvoie le CSV rempli.

## Option B — Batches JSON (recommandé pour Qwen)
1. Traduis `batches/batch_XXX.json` (un lot à la fois).
2. Remplis `entries[].translations` pour les 4 locales **en parallèle**.
3. Renvoie tous les `batch_XXX.filled.json` (même structure).

## Option C — Templates par langue
1. Remplis `templates/zh-CN.json` etc. (`entries[id] = texte traduit`).
2. Renvoie les 4 fichiers.

Après réception : rebuild de 4 packs séparés
`WTTGSD-Windows_ZHCN_P` / `_ZHTW_P` / `_JA_P` / `_KO_P`.
""",
        encoding="utf-8",
    )

    glossary = _load_glossary()
    preserve = glossary.get("preserve") or []
    rules = glossary.get("rules") or []
    prompt = f"""# Prompt Qwen / modèle — WTTG3 multi-langues

Tu traduis des chaînes du jeu *Welcome to the Game III* (horreur / darknet / PC sim).

## Locales à remplir EN PARALLÈLE pour chaque entrée
- `zh-CN` : chinois simplifié (大陆)
- `zh-TW` : chinois traditionnel (台灣用字 / 用語)
- `ja` : japonais
- `ko` : coréen

## Règles strictes
1. Ne change JAMAIS les placeholders : `[PRICE]` `[LINK]` `[SITE]` `[VIDEO]` `[TARGET]` `[DEALERID]` `[WIKI]` `[SOURCE]` `[VMFETCHURL]` et balises `<Bold>…</>` `<XP>…</>`.
2. Préserve exactement `\\r\\n` et la casse des fragments techniques.
3. Ne traduis PAS les chemins fichiers (`Threats/index.html`, `*.js`, `*.css`, …).
4. Noms / apps à préserver (liste) : {", ".join(preserve[:40])}{"…" if len(preserve) > 40 else ""}
5. UI courte : boutons / titres → rester concis (éviter overflow).
6. Ton : horreur / underground ; tutoiement type chat pour ACRS/CryptChat (adapter au naturel de chaque langue).
7. `fr_reference` = aide de sens (qualité FR), pas une source à calquer mot à mot.
8. Si `do_not_translate` : recopier `en` tel quel.

## Format de sortie
JSON identique au batch d'entrée, avec `translations` remplies pour les 4 locales.

## Référence règles FR (esprit)
{chr(10).join("- " + r for r in rules)}
"""
    (OUT / "QWEN_PROMPT.md").write_text(prompt, encoding="utf-8")

    # Stats sidecar
    by_cat: dict[str, int] = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    (OUT / "summary.json").write_text(
        json.dumps(
            {
                **meta,
                "by_category": by_cat,
                "batch_count": (len(todo) + BATCH_SIZE - 1) // BATCH_SIZE,
                "batch_size": BATCH_SIZE,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    rows = build_catalog()
    write_outputs(rows)
    todo = sum(1 for r in rows if not r["do_not_translate"])
    print(f"Wrote {OUT}")
    print(f"entries={len(rows)} translatable={todo} dnt={len(rows) - todo}")
    print(f"batches={(todo + BATCH_SIZE - 1) // BATCH_SIZE} x {BATCH_SIZE}")


if __name__ == "__main__":
    main()
