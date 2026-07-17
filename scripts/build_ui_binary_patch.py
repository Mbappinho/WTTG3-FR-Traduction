# -*- coding: utf-8 -*-
"""
Patch UI/dialog FStrings — SAME BYTE LENGTH only (safe for WidgetBlueprints).

Changing FString length in WBP_* shifts binary data → Bad name index / fatal.
DataAssets can update SerialSize, but widgets cannot without UAssetGUI+usmap.

Policy: full French words when they fit; otherwise best synonym of same length;
shorter FR is space-padded (no letter clipping).

Scope: UI/Widgets + Data/DataAssets/Agents (not WebSites).
"""
from __future__ import annotations

import csv
import shutil
import struct
import subprocess
from pathlib import Path

from game_paths import ROOT, paks_dir

LEGACY_CONTENT = ROOT / "source" / "legacy_ui" / "WTTGSD" / "Content"
PATCHED_CONTENT = ROOT / "build" / "legacy_patched" / "WTTGSD" / "Content"
PAKS_GAME = None  # resolved lazily via paks_dir()
RETOC = ROOT / "tools" / "retoc" / "retoc.exe"
MAP_CSV = ROOT / "work" / "uexp_patch_fr.csv"
MOD_BASE = "WTTGSD-Windows_FR_P"

COPY_PREFIXES = (
    "UI\\Widgets",
    "Data\\DataAssets\\Agents",
)

# Ideal FR (may be longer than EN — will be fitted to exact EN byte length)
RAW: dict[str, str] = {
    # Main / pause — prefer complete synonyms that fit
    "Play": "Joue",
    "PLAY": "JOUE",
    "Continue": "Reprends",
    "Settings": "Options",
    "Exit": "Quit",
    "Resume": "Retour",
    "PAUSE": "PAUSE",
    "SETTINGS": "OPTIONS",
    "BACK": "RET.",
    "INVENTORY": "INVENTAIR",
    "CANCEL": "ANNULE",
    "Equip": "Equipe",
    "Flashlight": "Lampe",
    "Assign Quick Use": "Raccourci rapide",
    "Quit Game": "Quitter",
    "Quit to main menu": "Menu principal",
    "Graphics Settings": "Graphismes",
    "Audio Settings": "Audio",
    "Game Settings": "Jeu",
    "Mouse Sensitivity": "Sensibilite souris",
    "Show Tooltips": "Info-bulles",
    "Anti-aliasing": "Anticrenelage",
    "FPS Limit": "Limite FPS",
    "Resolution": "Resolution",
    "Window Mode": "Mode fenetre",
    "Global Illumination": "Illumination globale",
    "Post Processing": "Post-traitement",
    "Reflections": "Reflexions",
    "Resolution Scale": "Echelle resol.",
    "View Distance": "Distance vue",
    "Pause Music": "Musique pause",
    "Game Audio": "Audio jeu",
    "Title Music": "Musique titre",
    "Quality": "Qualite",
    "Effects": "Effets",
    "Shading": "Ombrage",
    "Shadows": "Ombres",
    "Textures": "Textures",
    "CUSTOM": "PERSO",
    "LOW": "BAS",
    "MID": "MOY",
    "HIGH": "HAUT",
    "EPIC": "EPIC",
    "NEAR": "PRES",
    "FAR": "LOIN",
    "Normal": "Normal",
    "OVERWRITE?": "ECRASER ?",
    "Select Your Difficulty:": "Choisissez la difficulte:",
    "This will overwrite your current save file.": "Ceci ecrasera votre sauvegarde actuelle.",
    "Are you sure?": "Confirmer ?",
    "Tanner's Crime Scene": "Scene de crime Tanner",
    "THANKS FOR PLAYING!": "MERCI D'AVOIR JOUE!",
    "PRESS [ESC] TO EXIT": "APPUYEZ [ESC] POUR QUITTER",
    "GAME DEVELOPERS": "DEVELOPPEURS",
    "PLAYTESTERS": "TESTEURS",
    "SPECIAL THANKS": "REMERCIEMENTS",
    "Created By": "Cree par",
    "WEB DEVELOPERS": "DEV WEB",
    "ANIMATION TEAM": "EQUIPE ANIM",
    "ENVIRONMENT TEAM": "EQUIPE ENV.",
    "UI/UX TEAM": "EQUIPE UI/UX",
    "AUDIO TEAM": "EQUIPE AUDIO",
    "CHARACTER ARTIST": "ARTISTE PERSO",
    "VOICE ACTORS": "COMEDIENS",
    "Associate Producer": "Producteur associe",
    "WRITERS": "AUTEURS",
    # HUD
    "Enter Computer": "Entrer ordi.",
    "NO CAMERAS DETECTED": "AUCUNE CAMERA DETECTEE",
    "CONNECTING": "CONNEXION",
    "ARMED": "ARME",
    "DISARMED": "DESARME",
    "STREAM": "FLUX",
    "OFFLINE": "OFFLINE",
    "Every time you are prompted, hold/release [SPACEBAR] to keep the ring between the bands": (
        "Quand demande, maintenez/relachez [ESPACE] pour garder l'anneau entre les bandes"
    ),
    # Desktop
    "DOSCoin Balance": "Solde DOSCoin",
    "YoloYen Balance": "Solde YoloYen",
    "Firewall Tier I": "Pare-feu Niv. I",
    "0 Hacks Blocked": "0 Hacks bloques",
    "Backdoor Hacks": "Hacks backdoor",
    "Network Status": "Etat reseau",
    "Signal Booster Strength": "Force amplificateur",
    "Quick Switch To Virtual Desktop": "Bureau virtuel rapide",
    "Quick Switch To Desktop": "Bureau rapide",
    "Key Finding": "Cles a trouver",
    "Name Goes Here": "Nom ici",
    "STARTING UP": "DEMARRAGE",
    "SHUTTING DOWN": "ARRET...",
    "NOP Sleds": "NOP Sleds",
    # Apps / chat UI
    "A.C.R.S - Anon Chat Relay Service": "A.C.R.S - Relais chat anonyme",
    "Not Enough Rep - Required Rep Level 3": "Rep insuffisante - Niveau requis 3",
    "Not Enough Rep To Message This User": "Pas assez de rep pour ce user",
    "This user has blocked you.": "Cet user vous a bloque.",
    "You seem to be offline...": "Tu sembles hors ligne...",
    "User Offline...": "User hors ligne",
    "SEND DOS COIN": "ENVOYER DOS",
    "PING SENT": "PING ENVOYE",
    "PINGS DISABLED": "PINGS OFF",
    "User Info:": "Infos user:",
    " SYSTEM CLEARED CHAT": " SYSTEME A VIDE LE CHAT",
    "Internet Connection Lost": "Connexion internet perdue",
    "Source Code Viewer": "Visionneuse code source",
    "Fetch URL...": "URL Fetch...",
    "Enter Fetch URL...": "Entrer URL Fetch...",
    "Enter Dealer ID": "ID vendeur",
    "Invalid Dealer ID": "ID vendeur invalide",
    "Order Submitted": "Commande envoyee",
    "Confirm Order": "Confirmer cmd",
    "Order in progress": "Commande en cours",
    "Active Order Detected": "Commande active detectee",
    "Dealer will share details directly": "Le vendeur enverra les details",
    "Sessions are temporary.": "Sessions temporaires.",
    "Access expires after order is placed.": "Acces expire apres commande.",
    "Authorized Vendor Access": "Acces vendeur autorise",
    "Proceed with this order?": "Confirmer cette commande ?",
    "Est. Delivery:": "Livraison est.:",
    "RETURN HOME": "RETOUR",
    "GO BACK": "RETOUR",
    "EXCHANGE": "ECHANGE",
    "Exchange Processing": "Echange en cours",
    "Estimated waiting time:": "Temps d'attente estime:",
    "Gas Fee:": "Frais gas:",
    "1 DOS Coin = 1.00 YoloYen": "1 DOS Coin = 1.00 YoloYen",
    "Time Remaining: 230 seconds": "Temps restant: 230 secondes",
    "Access to hacker agents": "Acces agents hackers",
    "Access to hitman": "Acces tueur a gages",
    "FOUND VIDEO FILE": "FICHIER VIDEO TROUVE",
    "Create Valid Auth Token": "Creer jeton auth valide",
    "Launching Counter Measures...": "Lancement contre-mesures...",
    "-- INCOMING HACK [SOURCE] DETECTED --": "-- HACK ENTRANT [SOURCE] DETECTE --",
    "> CORRUPTED MEMORY BLOCKS:": "> BLOCS MEMOIRE CORROMPUS:",
    "Website Name": "Nom du site",
    "INJECTING": "INJECTION",
    "VALIDATING": "VALIDATION",
    "TOTAL": "TOTAL",
    "Dealer ID:": "ID vendeur:",
    "Dealer ID": "ID vendeur",
    # Key Finding tutorial
    "A.N.N. is a special web browser that can connect to the Dark Net.": (
        "A.N.N. est un navigateur special qui peut joindre le Dark Net."
    ),
    "A.N.N. can be found on every computer you enter through VirtMesh.": (
        "A.N.N. est sur chaque ordi auquel vous entrez via VirtMesh."
    ),
    "Access to Dark Net websites is gained through a Wiki page, which will have several links to choose from.": (
        "L'acces aux sites Dark Net passe par une page Wiki, avec plusieurs liens au choix."
    ),
    "Important to note that a site may not be active at the time you to try visit it. If that happens try again after a few minutes. Certain sites are more secretive than others, reserving their active time to a shorter period within each hour.": (
        "Un site peut etre inactif quand vous essayez. Reessayez apres quelques minutes. Certains sont plus secrets et n'ouvrent que peu de temps chaque heure."
    ),
    "Your goal is to uncover all 8 keys.": "But: decouvrir les 8 cles.",
    "The 8 keys are spread out across multiple sites, accessible only through different Wiki pages, and hidden in one of three unique methods.": (
        "Les 8 cles sont sur plusieurs sites, via differentes Wiki, cachees selon 3 methodes."
    ),
    "Pro Tip: Copy text by using [CTRL + C] and paste text by using [CTRL + V]": (
        "Astuce: Copiez avec [CTRL + C] et collez avec [CTRL + V]"
    ),
    "Example key:": "Ex. de cle:",
    "First, keys can be hidden in plain sight. Keep your eyes peeled when looking over a page.": (
        "D'abord, les cles peuvent etre en plain vue. Fouillez bien chaque page."
    ),
    "Pro Tip: Resizing the A.N.N. browser can help your search": (
        "Astuce: Redimensionner A.N.N. aide la recherche"
    ),
    "Second, keys can be hidden inside an element on the page, only revealing themselves through a click. Look over every word, image, and any other elements, including the area surrounding them.": (
        "Ensuite, une cle peut etre dans un element: un clic la revele. Verifiez mots, images et zones autour."
    ),
    "When you click a key's location a sound will be played and its text will either be revealed somewhere on the page or a file will be downloaded onto your desktop with the information. Check both before moving on.": (
        "Un clic joue un son: le texte apparait sur la page ou un fichier est telecharge sur le bureau. Verifiez les deux."
    ),
    "Third, keys can be hidden within a webpage's source code. When searching a page be sure to open its source code and carefully look through it. ": (
        "Enfin, une cle peut etre dans le code source. Ouvrez-le et parcourez-le avec soin. "
    ),
    "After finding a key make sure you've copied it's index and key hash i.e. 1 - 2bfc88a4.": (
        "Apres une cle, copiez index + hash (ex: 1 - 2bfc88a4)."
    ),
    "You'll need both parts for it to be decrypted by an agent found in the ACRS chatroom. ": (
        "Il faut les deux parties pour qu'un agent ACRS la dechiffre. "
    ),
    "Each decrypted key moves you one step closer to winning The Game.": (
        "Chaque cle dechiffree vous rapproche de gagner The Game."
    ),
    "While searching for keys you may encounter Fetch URLs. These URLs direct to video files which ACRS users may have interest in buying, so save them if you come across one.": (
        "En cherchant des cles, vous pouvez trouver des URL Fetch. Ce sont des videos vendables sur ACRS: sauvegardez-les."
    ),
    "All Fetch URLs begin with file:// and finish with .fetch. Copy and paste them into the ShadowFetch application to see what its contents are, then download to later sell the video file.": (
        "Les URL Fetch commencent par file:// et finissent par .fetch. Collez-les dans ShadowFetch, puis telechargez pour vendre."
    ),
    # Ronald / agents
    "Ok, you know what todo!": "Ok, tu sais quoi faire!",
    "Hi I'm Ronald, the Game Master for tonight.": "Salut, je suis Ronald, Game Master ce soir.",
    "Courtesy of your friend Wade I'll be offering a bit of help.": (
        "Grace a Wade, je vais t'offrir un peu d'aide."
    ),
    "VirtMesh is a program you need to install. Without it you won't be able to get onto the Dark Net.": (
        "VirtMesh est un programme a installer. Sans lui, pas d'acces au Dark Net."
    ),
    "ShadowFetch will be your way to download instructions and general help documents. I'd use it if I were you.": (
        "ShadowFetch sert a telecharger guides et docs d'aide. Je l'utiliserais a ta place."
    ),
    "VirtMesh? ShadowFetch? What are you fucking talking about? how do I get those programs?!": (
        "VirtMesh? ShadowFetch? Tu parles de quoi putain? Comment j'ai ces programmes?!"
    ),
    "Open Dark Drop to download both VirtMesh and ShadowFetch.": (
        "Ouvre Dark Drop pour telecharger VirtMesh et ShadowFetch."
    ),
    "Oh, wait, that's right. Wade did tell me you have a gambling problem, and you probably have no DOSCoin. ": (
        "Ah oui, Wade m'a dit que tu joues trop, et que t'as surement pas de DOSCoin. "
    ),
    "Here is some DOS Coin to get you started.": "Voici du DOS Coin pour commencer.",
    "Ok, I got them installed. Now what?": "Ok, c'est installe. Et maintenant?",
    "Take this fetch link [VMFETCHURL] and put it into ShadowFetch to download a file onto your desktop. It'll breakdown how VirtMesh works.": (
        "Prends ce lien fetch [VMFETCHURL] et mets-le dans ShadowFetch. Le fichier explique VirtMesh."
    ),
    "Or you can open up VirtMesh and try to figure it out yourself.": (
        "Ou ouvre VirtMesh et essaye de comprendre tout seul."
    ),
    "Through VirtMesh hack, mount, then enter a computer. Once you get that done switch over to this desktop and I'll share a link to a Wiki Page that has all types of websites on it.": (
        "Via VirtMesh: hack, mount, puis entre dans un ordi. Reviens ici et je te donne un lien Wiki avec des sites."
    ),
    "If what I'm saying doesn't make sense download and look at that document from the fetch link above.": (
        "Si c'est flou, telecharge et lis le document du lien fetch ci-dessus."
    ),
    "Alright. If you're still connected to that computer I'd urge you to disconnect from it.": (
        "Bon. Si t'es encore connecte a cet ordi, deconnecte-toi vite."
    ),
    "Staying connected to a hacked computer will eventually lock you out of it permanently. From here the easiest way to disconnect would be opening up VirtMesh through the app icon, then double clicking the circle in the cen": (
        "Rester connecte a un ordi hacke finit par te bloquer pour de bon. Le plus simple: ouvre VirtMesh via l'icone, puis double-clique le cercle au cen"
    ),
    "ter of the screen to exit it.": "tre de l'ecran pour quitter. ",
    "Later on you'll be better off switching between multiple computers to avoid permanent lockouts.": (
        "Plus tard, alterne entre plusieurs ordis pour eviter les lockouts."
    ),
    "This is the first Wiki Page:": "Voici la 1ere page Wiki:",
    "Put that link into A.N.N. to access a bunch of different Dark Net websites.": (
        "Mets ce lien dans A.N.N. pour acceder a plein de sites Dark Net."
    ),
    "It's very important to know what you're looking for. I downloaded a guide onto your desktop, which breaks that down. I'd highly recommend checking that out before going onto the Dark Net.": (
        "Il faut savoir quoi chercher. J'ai mis un guide sur ton bureau. Lis-le avant d'aller sur le Dark Net."
    ),
    "I reached out to some people who will contact you soon in CryptChat with more information, but unlike me they'll charge you for it.": (
        "J'ai contacte des gens qui t'ecriront sur CryptChat, mais eux te feront payer."
    ),
    "ODDroot - Has information on hacks you'll face. ": "ODDroot - Infos sur les hacks a venir. ",
    "Goggin - Has information on the people who will be trying to kill you tonight.": (
        "Goggin - Infos sur ceux qui veulent te tuer ce soir."
    ),
    "After you've collected, then decrypted all 8 keys, send me the master key (each decrypted key placed in order by its index number, assembled together as a single key) to beat tonight's game. ": (
        "Quand tu as les 8 cles dechiffrees, envoie-moi la master key (cles dans l'ordre des index, assemblees) pour gagner. "
    ),
    "But let's be real.. You are more than likely dead as fuck lol. ": (
        "Mais soyons francs.. T'es probablement deja mort lol. "
    ),
    "I know who's coming for you tonight. Pay me [PRICE] DOS Coin and I'll link a file you can download off ShadowFetch that'll give you a fighting chance.": (
        "Je sais qui vient te chercher. Paie [PRICE] DOS Coin et je te file un lien ShadowFetch pour t'en sortir."
    ),
    "If you want information on the hacks you'll need to counter pay me [PRICE] DOS Coin and I'll link a file you can download off ShadowFetch": (
        "Pour les infos sur les hacks a contrer, paie [PRICE] DOS Coin et je te file un lien ShadowFetch"
    ),
    "Was that a tip? Doesn't matter if it wasn't you're not getting that back.": (
        "C'etait un pourboire? Peu importe, tu le recuperes pas."
    ),
    "It's still [PRICE] DOS Coin to get the file. Send it all in a single payment or you get nothing.": (
        "C'est toujours [PRICE] DOS Coin. Envoie tout d'un coup ou tu n'as rien."
    ),
    "Stop typing, just give me the DOS Coin and you will get what you want.": (
        "Arrete d'ecrire, donne le DOS Coin et tu auras ce que tu veux."
    ),
    "Okay, thanks. Here's the link: ": "Ok, merci. Voici le lien: ",
    "Put that into ShadowFetch to download your file. I'm out of here.. Later": (
        "Mets ca dans ShadowFetch pour telecharger. Je me casse.. A+"
    ),
}


def enc(s: str) -> bytes:
    return s.encode("cp1252", errors="replace")


def fit_bytes(en: str, fr: str) -> bytes:
    """Exact same cp1252 length as EN (pad spaces / truncate)."""
    eb, fb = enc(en), enc(fr)
    if len(fb) < len(eb):
        return fb + (b" " * (len(eb) - len(fb)))
    return fb[: len(eb)]


def fstring_pattern_from_body(body_no_null: bytes) -> bytes:
    body = body_no_null + b"\x00"
    return struct.pack("<I", len(body)) + body


def replace_fstrings(data: bytes, pairs: list[tuple[str, bytes]]) -> tuple[bytes, int]:
    pairs = sorted(pairs, key=lambda x: len(x[0]), reverse=True)
    n = 0
    out = data
    for en, fr_body in pairs:
        src = fstring_pattern_from_body(enc(en))
        dst = fstring_pattern_from_body(fr_body)
        assert len(src) == len(dst)
        c = out.count(src)
        if c:
            out = out.replace(src, dst)
            n += c
    return out, n


def should_copy(rel: Path) -> bool:
    s = str(rel).replace("/", "\\")
    return any(s == p or s.startswith(p + "\\") for p in COPY_PREFIXES)


def build_pairs() -> list[tuple[str, bytes]]:
    pairs = []
    rows = []
    for en, fr in RAW.items():
        body = fit_bytes(en, fr)
        pairs.append((en, body))
        rows.append([en, body.decode("cp1252", errors="replace"), len(en), len(body)])
    with MAP_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "translation", "len_en", "len_fr"])
        w.writerows(rows)
    return pairs


def stage_tree() -> None:
    if PATCHED_CONTENT.parent.exists():
        shutil.rmtree(PATCHED_CONTENT.parent)
    PATCHED_CONTENT.mkdir(parents=True)
    for src in LEGACY_CONTENT.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(LEGACY_CONTENT)
        if not should_copy(rel):
            continue
        if src.suffix.lower() not in {".uasset", ".uexp", ".ubulk", ".uptnl"}:
            continue
        dst = PATCHED_CONTENT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def patch_staged(pairs: list[tuple[str, bytes]]) -> tuple[int, int]:
    files_touched = 0
    replacements = 0
    for path in PATCHED_CONTENT.rglob("*.uexp"):
        original = path.read_bytes()
        data, n = replace_fstrings(original, pairs)
        if n:
            assert len(data) == len(original), path
            path.write_bytes(data)
            files_touched += 1
            replacements += n
    return files_touched, replacements


def pack_iostore() -> None:
    out_dir = ROOT / "build" / "pak"
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob(f"{MOD_BASE}*"):
        p.unlink()
    zen_out = out_dir / f"{MOD_BASE}.utoc"
    cmd = [
        str(RETOC),
        "to-zen",
        "--version",
        "UE5_6",
        str(PATCHED_CONTENT.parent),
        str(zen_out),
    ]
    print("Running:", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout[-1500:])
    if r.stderr:
        print(r.stderr[-1500:])
    if r.returncode != 0:
        raise RuntimeError(f"to-zen failed: {r.returncode}")


def apply_to_game() -> None:
    out_dir = ROOT / "build" / "pak"
    paks_game = paks_dir()
    for p in list(paks_game.glob(f"{MOD_BASE}*")):
        p.unlink()
    for p in out_dir.glob(f"{MOD_BASE}*"):
        shutil.copy2(p, paks_game / p.name)
        print("Copied", p.name)


def verify() -> None:
    p = PATCHED_CONTENT / "UI" / "Widgets" / "Titles" / "WBP_MainTitleWidget.uexp"
    d = p.read_bytes()
    assert len(d) == (LEGACY_CONTENT / "UI" / "Widgets" / "Titles" / "WBP_MainTitleWidget.uexp").stat().st_size
    assert fstring_pattern_from_body(b"Joue") in d
    btn = PATCHED_CONTENT / "UI" / "Widgets" / "Titles" / "WBP_TitleMenuButton.uexp"
    bd = btn.read_bytes()
    assert len(bd) == (LEGACY_CONTENT / "UI" / "Widgets" / "Titles" / "WBP_TitleMenuButton.uexp").stat().st_size
    print("verify OK: same file sizes, Joue present")


def main() -> None:
    pairs = build_pairs()
    print(f"pairs={len(pairs)} (same-length only)")
    stage_tree()
    files_touched, replacements = patch_staged(pairs)
    print(f"files_touched={files_touched} replacements={replacements}")
    verify()
    pack_iostore()
    apply_to_game()
    print("done — v5 same-length (stable)")


if __name__ == "__main__":
    main()
