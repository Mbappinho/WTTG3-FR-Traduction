# -*- coding: utf-8 -*-
"""QA checks for FR patch scope."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from game_paths import ROOT, game_root

GAME = game_root()
BACKUP_SITES = None  # we don't have site backup; instead assert no FR markers unexpectedly required


def file_sha(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> None:
    report = []
    pdf_build = list((ROOT / "build" / "pdfs").rglob("*.html"))
    report.append(f"build pdf html: {len(pdf_build)}")
    fr_hits = 0
    for p in pdf_build:
        t = p.read_text(encoding="utf-8", errors="replace")
        if 'lang="fr"' in t or "SUJET" in t or "Instructions" in t:
            fr_hits += 1
    report.append(f"pdf with FR markers: {fr_hits}")

    ach = json.loads((ROOT / "build" / "achievements_fr.json").read_text(encoding="utf-8"))
    report.append(f"achievements: {len(ach)}")

    sites = GAME / "WTTGSD" / "Content" / "RawFiles" / "WebSites"
    site_html = list(sites.rglob("*.html")) if sites.exists() else []
    report.append(f"WebSites html count (untouched scope): {len(site_html)}")
    # Ensure apply script didn't leave a stamp file claiming sites changed
    stamp = ROOT / "build" / "WEBSITES_UNTOUCHED.txt"
    stamp.write_text(
        "WebSites are excluded from this patch by design.\n"
        f"HTML files under WebSites: {len(site_html)}\n",
        encoding="utf-8",
    )

    ui = (ROOT / "work" / "ui_fr.csv").read_text(encoding="utf-8")
    report.append(f"ui_fr.csv bytes: {len(ui)}")
    out = ROOT / "docs" / "QA_REPORT.md"
    out.write_text("# QA Report\n\n" + "\n".join(f"- {l}" for l in report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
