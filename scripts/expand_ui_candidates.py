# -*- coding: utf-8 -*-
import csv
import re
from pathlib import Path

src = Path(__file__).resolve().parents[1] / "source" / "game_locres_full.csv"
out = Path(__file__).resolve().parents[1] / "source" / "ui_candidates_en.csv"

deny = re.compile(
    r"(Ultra Dynamic|CinematicCamera|volumetric|material_function|UDW|UDS |"
    r"Path Tracer|Sequencer|PostProcess|groom|IMAX|Fog Density|Weather|"
    r"Movie Render|AmbientSound|CustomizableObject|SMessaging|Blueprint editor|"
    r"game module|CHECK_PUREVIRTUAL|Interchange|Niagara|Chaos|Slate|"
    r"Editor only|DEPRECATED)",
    re.I,
)
interest = re.compile(
    r"(desk|inventory|dos ?coin|hack|mount|mine|hide|run|move|debt|normal|"
    r"difficulty|tutorial|threat|firewall|continue|options|settings|quit|play|"
    r"save|load|pause|virtmesh|simon|tanner|ronald|chat|npc|upgrade|buy|sell|"
    r"enter|press|tab|shift|wasd|slot|casino|motel|key|hash|counter|"
    r"kidnap|breather|lucas|noir|cletus|tucker)",
    re.I,
)

rows = []
seen = set()
with src.open(encoding="utf-8", errors="replace", newline="") as f:
    for row in csv.DictReader(f):
        t = (row.get("source") or "").strip()
        k = (row.get("key") or "").strip()
        if not t or t in seen:
            continue
        if deny.search(t) or deny.search(k):
            continue
        if "<cf>" in t or "\n" in t:
            continue
        if len(t) < 3 or len(t) > 220:
            continue
        hashed = bool(re.fullmatch(r"[0-9A-F]{32}", k))
        if not hashed and not interest.search(t):
            continue
        if hashed and not interest.search(t) and not re.search(r"[a-z]", t):
            continue
        # keep hashed interesting OR any interesting
        if hashed or interest.search(t):
            if hashed and not interest.search(t):
                # keep short UI-like hashed strings
                if not (3 <= len(t) <= 60 and re.search(r"[A-Za-z]", t)):
                    continue
            seen.add(t)
            rows.append((k, t, "hashed" if hashed else "named"))

with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["key", "source", "kind", "translation", "notes"])
    for k, t, kind in rows:
        w.writerow([k, t, kind, "", ""])

print("candidates", len(rows))
for k, t, kind in rows:
    if interest.search(t):
        print(f"{kind}|{t[:140]}")
