# -*- coding: utf-8 -*-
"""Regenerate AptLoadingScreen FR — full wipe of EN text panel then redraw."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

src = Path(
    r"C:\Users\kaoth\Projects\WTTG3-FR-Loc\work\simon_intro_texture\candidates\AptLoadingScreen.png"
)
out_dir = Path(r"C:\Users\kaoth\Projects\WTTG3-FR-Loc\work\simon_intro_texture")
im = Image.open(src).convert("RGBA")
draw = ImageDraw.Draw(im)

# Full wipe of EN text area (starts ~x357; leave Simon on the left)
draw.rectangle((320, 240, 1064, 430), fill=(0, 0, 0, 255))

fr = (
    "Tu es Simon Zhao, un joueur pathologique qui fait les nuits "
    "dans un motel délabré. Pour nourrir ton addiction, tu as "
    "emprunté de l'argent à la mauvaise personne — et maintenant, "
    "on vient te collecter…"
)

font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 22)
text_left = 350
max_width = 690

words = fr.split()
lines: list[str] = []
cur = ""
for word in words:
    test = (cur + " " + word).strip()
    bbox = draw.textbbox((0, 0), test, font=font)
    if bbox[2] - bbox[0] <= max_width:
        cur = test
    else:
        if cur:
            lines.append(cur)
        cur = word
if cur:
    lines.append(cur)

line_h = 28
y0 = 275
for i, line in enumerate(lines):
    draw.text((text_left, y0 + i * line_h), line, font=font, fill=(235, 235, 235, 255))

out_png = out_dir / "AptLoadingScreen_FR.png"
im.save(out_png)
print("saved", out_png)
for L in lines:
    print(" ", L)
