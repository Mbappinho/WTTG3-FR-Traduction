# -*- coding: utf-8 -*-
"""
Optional AZERTY keyboard remap via Enhanced Input IMC NameMap rewrite.

QWERTY letter key FNames -> AZERTY letters for the same physical positions:
  W -> Z, A <-> Q, Z -> W (if present). Other keys unchanged.

Pipeline:
  tojson (VER_UE5_6 + Mappings.usmap)
  -> rewrite NameMap single-letter key names
  -> fromjson
  -> retoc to-zen  => WTTGSD-Windows_FR_AZERTY_P
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from game_paths import ROOT, paks_dir

_LEGACY_STEAM = ROOT / "source" / "legacy_ui_steam" / "WTTGSD" / "Content"
_LEGACY_DESKTOP = ROOT / "source" / "legacy_ui" / "WTTGSD" / "Content"
LEGACY = _LEGACY_STEAM if _LEGACY_STEAM.exists() else _LEGACY_DESKTOP

STAGED = ROOT / "build" / "azerty_imc_patched" / "WTTGSD" / "Content"
JSON_DIR = ROOT / "build" / "azerty_imc_json"
RETOC = ROOT / "tools" / "retoc" / "retoc.exe"
UASSETGUI = ROOT / "tools" / "UAssetGUI" / "UAssetGUI.exe"
USMAP = ROOT / "source" / "Mappings.usmap"
MOD_BASE = "WTTGSD-Windows_FR_AZERTY_P"
ENGINE = "VER_UE5_6"

# Same physical finger positions as QWERTY binds, labeled for AZERTY.
AZERTY_LETTER_MAP: dict[str, str] = {
    "W": "Z",
    "A": "Q",
    "Q": "A",
    "Z": "W",
}

_LETTER = re.compile(r"^[A-Z]$")


def run_gui(args: list[str]) -> None:
    r = subprocess.run(
        [str(UASSETGUI), *args],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"UAssetGUI failed {args[:3]}: {r.stderr or r.stdout}")


def remap_namemap(names: list) -> tuple[list, list[tuple[str, str]]]:
    """Apply AZERTY permutation to single-letter NameMap entries only."""
    changes: list[tuple[str, str]] = []
    # Two-pass: collect targets first to detect collisions among remapped slots.
    indices: list[int] = []
    olds: list[str] = []
    news: list[str] = []
    for i, n in enumerate(names):
        if not isinstance(n, str) or not _LETTER.fullmatch(n):
            continue
        if n not in AZERTY_LETTER_MAP:
            continue
        new = AZERTY_LETTER_MAP[n]
        if new == n:
            continue
        indices.append(i)
        olds.append(n)
        news.append(new)

    if not indices:
        return names, changes

    # Collision: two remapped indices must not land on the same final name
    # unless they came from a clean permutation of distinct letters.
    if len(set(news)) != len(news):
        raise RuntimeError(f"AZERTY NameMap collision after remap: {list(zip(olds, news))}")

    # Also refuse if a remapped letter would overwrite an unmapped letter slot
    # that is not itself being remapped away.
    unmapped_letters = {
        n
        for j, n in enumerate(names)
        if isinstance(n, str) and _LETTER.fullmatch(n) and j not in indices
    }
    for new in news:
        if new in unmapped_letters:
            raise RuntimeError(
                f"AZERTY remap would collide with unmapped NameMap letter {new!r}"
            )

    out = list(names)
    for i, old, new in zip(indices, olds, news):
        out[i] = new
        changes.append((old, new))
    return out, changes


def process_imc(src_uasset: Path) -> list[tuple[str, str]]:
    rel = src_uasset.relative_to(LEGACY)
    dst_uasset = STAGED / rel
    dst_uasset.parent.mkdir(parents=True, exist_ok=True)
    json_path = JSON_DIR / rel.with_suffix(".json")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    run_gui(["tojson", str(src_uasset), str(json_path), ENGINE, str(USMAP)])
    if not json_path.exists():
        raise RuntimeError(f"tojson produced no file: {json_path}")

    asset = json.loads(json_path.read_text(encoding="utf-8"))
    names = asset.get("NameMap")
    if not isinstance(names, list):
        raise RuntimeError(f"No NameMap in {rel}")

    new_names, changes = remap_namemap(names)
    if not changes:
        # Still stage untouched so pak layout is complete if we only pack changed —
        # skip copy: we only include remapped IMCs in the pak.
        return []

    asset["NameMap"] = new_names
    json_path.write_text(json.dumps(asset, ensure_ascii=False, indent=2), encoding="utf-8")
    run_gui(["fromjson", str(json_path), str(dst_uasset), str(USMAP)])
    if not dst_uasset.exists():
        raise RuntimeError(f"fromjson produced no uasset: {dst_uasset}")
    return changes


def stage_and_patch() -> dict[str, list[tuple[str, str]]]:
    if STAGED.parent.exists():
        shutil.rmtree(STAGED.parent)
    if JSON_DIR.exists():
        shutil.rmtree(JSON_DIR)
    STAGED.mkdir(parents=True)
    JSON_DIR.mkdir(parents=True)

    imcs = sorted((LEGACY / "Input").rglob("IMC_*.uasset"))
    if not imcs:
        raise RuntimeError(f"No IMC_*.uasset under {LEGACY / 'Input'}")

    results: dict[str, list[tuple[str, str]]] = {}
    for src in imcs:
        rel = str(src.relative_to(LEGACY)).replace("\\", "/")
        changes = process_imc(src)
        if changes:
            results[rel] = changes
            print(f"  {rel}: " + ", ".join(f"{a}->{b}" for a, b in changes))
        else:
            print(f"  {rel}: (no letter remap)")
    return results


def verify_staged_namemaps(results: dict[str, list[tuple[str, str]]]) -> None:
    """Re-tojson staged assets and assert expected letters are present."""
    for rel, changes in results.items():
        ua = STAGED / Path(rel.replace("/", "\\"))
        tmp = JSON_DIR / "_verify" / Path(rel).with_suffix(".json")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        run_gui(["tojson", str(ua), str(tmp), ENGINE, str(USMAP)])
        names = json.loads(tmp.read_text(encoding="utf-8")).get("NameMap") or []
        letters = {n for n in names if isinstance(n, str) and _LETTER.fullmatch(n)}
        for old, new in changes:
            if new not in letters:
                raise RuntimeError(f"{rel}: expected {new!r} in NameMap after remap, got {sorted(letters)}")
            # Old letter may still appear if it was the destination of another swap (A<->Q).
            if old not in AZERTY_LETTER_MAP.values() and old in letters and old != new:
                # e.g. W->Z: W should be gone unless something else maps to W
                mapped_to_old = any(b == old for _, b in changes)
                if not mapped_to_old and old in letters:
                    raise RuntimeError(f"{rel}: {old!r} still in NameMap after remap to {new!r}")
        print(f"  verify OK {rel}: letters={sorted(letters)}")


def pack_and_apply() -> None:
    out_dir = ROOT / "build" / "pak"
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob(f"{MOD_BASE}*"):
        p.unlink()
    zen = out_dir / f"{MOD_BASE}.utoc"
    # Same as build_ui_uassetgui_patch: pass .../WTTGSD (parent of Content)
    cmd = [str(RETOC), "to-zen", "--version", "UE5_6", str(STAGED.parent), str(zen)]
    print("Running", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    print((r.stdout or "")[-1500:])
    print((r.stderr or "")[-1500:])
    if r.returncode != 0:
        raise RuntimeError("to-zen failed")
    # Optional install into local game paks if path configured
    try:
        paks_game = paks_dir()
    except SystemExit:
        print("WARN: game path not set — pak left in build/pak only")
        return
    for p in list(paks_game.glob(f"{MOD_BASE}*")):
        p.unlink()
    for p in out_dir.glob(f"{MOD_BASE}*"):
        shutil.copy2(p, paks_game / p.name)
        print("Copied", p.name, "->", paks_game)


def main() -> None:
    if not USMAP.exists():
        print("Missing", USMAP, file=sys.stderr)
        sys.exit(1)
    if not UASSETGUI.exists():
        print("Missing", UASSETGUI, file=sys.stderr)
        sys.exit(1)
    if not RETOC.exists():
        print("Missing", RETOC, file=sys.stderr)
        sys.exit(1)
    print(f"LEGACY={LEGACY}")
    if not LEGACY.exists():
        raise SystemExit(f"Legacy Content missing: {LEGACY}")

    print("Patching IMC NameMaps (AZERTY)...")
    results = stage_and_patch()
    if not results:
        raise RuntimeError("No IMC NameMap letters remapped — unexpected")
    print(f"assets_remapped={len(results)}")
    print("Verifying staged NameMaps...")
    verify_staged_namemaps(results)
    pack_and_apply()
    print("done — AZERTY IMC mod packed as", MOD_BASE)


if __name__ == "__main__":
    main()
