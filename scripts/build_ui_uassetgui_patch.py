# -*- coding: utf-8 -*-
"""
Full-length FR UI patch via UAssetGUI JSON + usmap (variable FString length).

Pipeline per asset:
  tojson (VER_UE5_6 + Mappings.usmap)
  -> patch RawExport base64 FStrings
  -> update SerialSize / SerialOffset
  -> fromjson
  -> retoc to-zen
"""
from __future__ import annotations

import base64
import csv
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from game_paths import ROOT, paks_dir

# Prefer Steam extract when present (Desktop extract ≠ Steam cook → Bad export index)
_LEGACY_STEAM = ROOT / "source" / "legacy_ui_steam" / "WTTGSD" / "Content"
_LEGACY_DESKTOP = ROOT / "source" / "legacy_ui" / "WTTGSD" / "Content"
LEGACY = _LEGACY_STEAM if _LEGACY_STEAM.exists() else _LEGACY_DESKTOP
STAGED = ROOT / "build" / "uassetgui_patched" / "WTTGSD" / "Content"
JSON_DIR = ROOT / "build" / "uassetgui_json"
RETOC = ROOT / "tools" / "retoc" / "retoc.exe"
UASSETGUI = ROOT / "tools" / "UAssetGUI" / "UAssetGUI.exe"
USMAP = ROOT / "source" / "Mappings.usmap"
MAP_CSV = ROOT / "work" / "uexp_patch_fr.csv"
MOD_BASE = "WTTGSD-Windows_FR_P"
ENGINE = "VER_UE5_6"

COPY_PREFIXES = (
    "UI\\Widgets",
    "Data\\DataAssets\\Agents",
    "Data\\DataAssets\\Products",
    "Data\\DataAssets\\PlayerItems",
    "Data\\DataAssets\\SimonThoughts",
    "Data\\DataAssets\\ChoiceTrees",
    "Data\\DataAssets\\Difficulty",
    "Data\\DataAssets\\ACRS",
    "Data\\DataTables",
    "BluePrints\\Cinema",
    "BluePrints\\Pawns",
    "BluePrints\\GameActors",
    "BluePrints\\PawnSwitchers",
    "BluePrints\\PlayerItems",
)

# Previously excluded when overlaying Desktop extract onto Steam.
# With Steam-matched legacy_ui_steam, Settings/Pause can be patched again.
EXCLUDE_FROM_PAK: set[str] = set()

# Extra ACRS / CryptChat maps (generated): work/acrs_cryptchat_fr.json
EXTRA_MAP = ROOT / "work" / "acrs_cryptchat_fr.json"


# File-relative paths must stay EN (game loads RawFiles/PDFS/<path>)
_ASSET_PATH_RE = re.compile(r"^[A-Za-z0-9_./\\-]+\.(html|css|js|jpg|jpeg|png|gif|fetch)$")


def _load_extra_raw() -> dict[str, str]:
    if not EXTRA_MAP.exists():
        return {}
    try:
        data = json.loads(EXTRA_MAP.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out: dict[str, str] = {}
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, str):
            continue
        # Never rewrite asset/file paths (e.g. Threats/index.html -> Menaces/...)
        out[k] = k if _ASSET_PATH_RE.match(k) else v
    return out


# Full French — free length (ASCII ANSI / accents UTF-16)
RAW: dict[str, str] = {
    "Play": "Jouer",
    "PLAY": "JOUER",
    "Continue": "Continuer",
    "Settings": "Paramètres",
    "Exit": "Quitter",
    "Resume": "Reprendre",
    "PAUSE": "PAUSE",
    "SETTINGS": "PARAMÈTRES",
    "BACK": "RETOUR",
    "INVENTORY": "INVENTAIRE",
    "CANCEL": "ANNULER",
    "Confirm": "Confirmer",
    "Connect": "Connecter",
    "Checkout": "Commander",
    "Hide": "Se cacher",
    # RMB / leave prompts (Hide, Panic, Peep, Desk, Monitor)
    "[RMB] - Exit": "[Clic droit] - Quitter",
    "[RMB] Exit": "[Clic droit] Quitter",
    "[RMB] Get Up From Desk": "[Clic droit] Se lever du bureau",
    "[RMB] Leave Computer": "[Clic droit] Quitter l'ordinateur",
    "Exit To VertMesh": "Passer à VirtMesh",
    # HUD / interaction prompts (GameActors + tooltips)
    "Open": "Ouvrir",
    "Close": "Fermer",
    "Unlock": "Déverrouiller",
    "Lock": "Verrouiller",
    "Turn On": "Allumer",
    "Turn Off": "Éteindre",
    "Turn On Computer": "Allumer l'ordinateur",
    "Peep": "Regarder",
    "Repair": "Réparer",
    "Attempt Defusal": "Tenter désamorçage",
    "Enter Panic Mode": "Mode panique",
    "Enter Desk": "S'asseoir au bureau",
    "Head To Work": "Aller au travail",
    "Equip": "Équiper",
    "Flashlight": "Lampe torche",
    "Assign Quick Use": "Assigner raccourci",
    "Quit Game": "Quitter le jeu",
    "Quit to main menu": "Retour au menu principal",
    "Graphics Settings": "Paramètres graphiques",
    "Audio Settings": "Paramètres audio",
    "Game Settings": "Paramètres de jeu",
    "Mouse Sensitivity": "Sensibilité de la souris",
    "Show Tooltips": "Afficher les info-bulles",
    "Anti-aliasing": "Anticrénelage",
    "FPS Limit": "Limite FPS",
    "Resolution": "Résolution",
    "Window Mode": "Mode fenêtre",
    "Global Illumination": "Illumination globale",
    "Post Processing": "Post-traitement",
    "Reflections": "Réflexions",
    "Resolution Scale": "Échelle de résolution",
    "View Distance": "Distance d'affichage",
    "Pause Music": "Musique en pause",
    "Game Audio": "Audio du jeu",
    "Title Music": "Musique du titre",
    "Master Audio": "Audio principal",
    "Browser & Files": "Navigateur et fichiers",
    "Browser Resolution": "Résolution navigateur",
    "Browser FPS": "FPS navigateur",
    "GPU Acceleration": "Accélération GPU",
    "(Requires Restart)": "(Redémarrage requis)",
    "Pick Up": "Ramasser",
    "Quality": "Qualité",
    "Effects": "Effets",
    "Shading": "Ombrage",
    "Shadows": "Ombres",
    "Textures": "Textures",
    "CUSTOM": "PERSONNALISÉ",
    "LOW": "BAS",
    "MID": "MOYEN",
    "HIGH": "HAUT",
    "EPIC": "EPIC",
    "NEAR": "PRÈS",
    "FAR": "LOIN",
    "Normal": "Normal",
    "OVERWRITE?": "ÉCRASER ?",
    "Select Your Difficulty:": "Choisissez votre difficulté :",
    "This will overwrite your current save file.": "Ceci écrasera votre sauvegarde actuelle.",
    "Are you sure?": "Êtes-vous sûr ?",
    "Tanner's Crime Scene": "Scène de crime de Tanner",
    "THANKS FOR PLAYING!": "MERCI D'AVOIR JOUÉ !",
    "PRESS [ESC] TO EXIT": "APPUYEZ SUR [ESC] POUR QUITTER",
    "GAME DEVELOPERS": "DÉVELOPPEURS",
    "PLAYTESTERS": "TESTEURS",
    "SPECIAL THANKS": "REMERCIEMENTS",
    "Created By": "Créé par",
    "WEB DEVELOPERS": "DÉVELOPPEURS WEB",
    "ANIMATION TEAM": "ÉQUIPE ANIMATION",
    "ENVIRONMENT TEAM": "ÉQUIPE ENVIRONNEMENT",
    "UI/UX TEAM": "ÉQUIPE UI/UX",
    "AUDIO TEAM": "ÉQUIPE AUDIO",
    "CHARACTER ARTIST": "ARTISTE PERSONNAGES",
    "VOICE ACTORS": "COMÉDIENS VOIX",
    "Associate Producer": "Producteur associé",
    "WRITERS": "AUTEURS",
    "Enter Computer": "Entrer dans l'ordinateur",
    "NO CAMERAS DETECTED": "AUCUNE CAMÉRA DÉTECTÉE",
    "CONNECTING": "CONNEXION",
    "ARMED": "ARMÉ",
    "DISARMED": "DÉSARMÉ",
    "STREAM": "FLUX",
    "OFFLINE": "HORS LIGNE",
    "Every time you are prompted, hold/release [SPACEBAR] to keep the ring between the bands": (
        "Quand on vous le demande, maintenez/relâchez [ESPACE] pour garder l'anneau entre les bandes"
    ),
    "DOSCoin Balance": "Solde DOSCoin",
    "YoloYen Balance": "Solde YoloYen",
    "Firewall Tier I": "Pare-feu niveau I",
    "0 Hacks Blocked": "0 hacks bloqués",
    "Backdoor Hacks": "Hacks backdoor",
    "Network Status": "État du réseau",
    "Signal Booster Strength": "Force de l'amplificateur",
    "Quick Switch To Virtual Desktop": "Basculer vers le bureau virtuel",
    "Quick Switch To Desktop": "Basculer vers le bureau",
    "Key Finding": "Recherche de clés",
    "Name Goes Here": "Nom ici",
    "STARTING UP": "DÉMARRAGE",
    "SHUTTING DOWN": "ARRÊT EN COURS",
    "A.C.R.S - Anon Chat Relay Service": "A.C.R.S - Relais de chat anonyme",
    "Not Enough Rep - Required Rep Level 3": "Pas assez de rep - Niveau requis : 3",
    "Not Enough Rep To Message This User": "Pas assez de rep pour écrire à cet utilisateur",
    "This user has blocked you.": "Cet utilisateur vous a bloqué.",
    "You seem to be offline...": "Tu sembles être hors ligne...",
    "User Offline...": "Utilisateur hors ligne...",
    "SEND DOS COIN": "ENVOYER DOS COIN",
    "PING SENT": "PING ENVOYÉ",
    "PINGS DISABLED": "PINGS DÉSACTIVÉS",
    "User Info:": "Infos utilisateur :",
    " SYSTEM CLEARED CHAT": " LE SYSTÈME A VIDÉ LE CHAT",
    "Internet Connection Lost": "Connexion internet perdue",
    "Source Code Viewer": "Visionneuse de code source",
    "Fetch URL...": "URL Fetch...",
    "Enter Fetch URL...": "Entrer l'URL Fetch...",
    "Enter Dealer ID": "Entrer l'ID vendeur",
    "Invalid Dealer ID": "ID vendeur invalide",
    "Order Submitted": "Commande envoyée",
    "Confirm Order": "Confirmer la commande",
    "Order in progress": "Commande en cours",
    "Active Order Detected": "Commande active détectée",
    "Dealer will share details directly": "Le vendeur enverra les détails directement",
    "Sessions are temporary.": "Les sessions sont temporaires.",
    "Access expires after order is placed.": "L'accès expire après la commande.",
    "Authorized Vendor Access": "Accès vendeur autorisé",
    "Proceed with this order?": "Confirmer cette commande ?",
    "Est. Delivery:": "Livraison estimée :",
    "RETURN HOME": "RETOUR ACCUEIL",
    "GO BACK": "RETOUR",
    "EXCHANGE": "ÉCHANGER",
    "Exchange Processing": "Échange en cours",
    "Estimated waiting time:": "Temps d'attente estimé :",
    "Gas Fee:": "Frais de gas :",
    "Time Remaining: 230 seconds": "Temps restant : 230 secondes",
    "Access to hacker agents": "Accès aux agents hackers",
    "Access to hitman": "Accès au tueur à gages",
    "FOUND VIDEO FILE": "FICHIER VIDÉO TROUVÉ",
    "Create Valid Auth Token": "Créer un jeton d'auth valide",
    "Launching Counter Measures...": "Lancement des contre-mesures...",
    "-- INCOMING HACK [SOURCE] DETECTED --": "-- HACK ENTRANT [SOURCE] DÉTECTÉ --",
    "> CORRUPTED MEMORY BLOCKS:": "> BLOCS MÉMOIRE CORROMPUS :",
    "Website Name": "Nom du site",
    "INJECTING": "INJECTION",
    "VALIDATING": "VALIDATION",
    "Dealer ID:": "ID vendeur :",
    "Dealer ID": "ID vendeur",
    # Key Finding — blocs FString combines (\\r\\n\\r\\n)
    "A.N.N. is a special web browser that can connect to the Dark Net.\r\n\r\nA.N.N. can be found on every computer you enter through VirtMesh.": (
        "A.N.N. est un navigateur spécial capable de se connecter au Dark Net.\r\n\r\n"
        "A.N.N. se trouve sur chaque ordinateur auquel vous accédez via VirtMesh."
    ),
    "Access to Dark Net websites is gained through a Wiki page, which will have several links to choose from.\r\n\r\nImportant to note that a site may not be active at the time you to try visit it. If that happens try again after a few minutes. Certain sites are more secretive than others, reserving their active time to a shorter period within each hour.": (
        "L'accès aux sites du Dark Net se fait via une page Wiki, avec plusieurs liens au choix.\r\n\r\n"
        "Un site peut être inactif au moment où vous essayez d'y accéder. Dans ce cas, réessayez après quelques minutes. "
        "Certains sites sont plus secrets et ne restent actifs que peu de temps chaque heure."
    ),
    "Your goal is to uncover all 8 keys.\r\n\r\nThe 8 keys are spread out across multiple sites, accessible only through different Wiki pages, and hidden in one of three unique methods.\r\n\r\nPro Tip: Copy text by using [CTRL + C] and paste text by using [CTRL + V]\r\n": (
        "Votre but est de découvrir les 8 clés.\r\n\r\n"
        "Les 8 clés sont réparties sur plusieurs sites, accessibles via différentes pages Wiki, et cachées selon l'une des trois méthodes.\r\n\r\n"
        "Astuce : copiez le texte avec [CTRL + C] et collez avec [CTRL + V]\r\n"
    ),
    "First, keys can be hidden in plain sight. Keep your eyes peeled when looking over a page.\r\n\r\nPro Tip: Resizing the A.N.N. browser can help your search": (
        "D'abord, les clés peuvent être cachées au vu de tous. Fouillez chaque page attentivement.\r\n\r\n"
        "Astuce : redimensionner le navigateur A.N.N. peut aider votre recherche"
    ),
    "Second, keys can be hidden inside an element on the page, only revealing themselves through a click. Look over every word, image, and any other elements, including the area surrounding them.\r\n\r\nWhen you click a key's location a sound will be played and its text will either be revealed somewhere on the page or a file will be downloaded onto your desktop with the information. Check both before moving on.": (
        "Ensuite, une clé peut être cachée dans un element de la page et ne se révéler qu'au clic. Verifiez chaque mot, image et zone autour.\r\n\r\n"
        "Quand vous cliquez sur l'emplacement d'une cle, un son est joué et le texte apparait sur la page, ou un fichier est téléchargé sur votre bureau. Verifiez les deux avant de continuer."
    ),
    "Third, keys can be hidden within a webpage's source code. When searching a page be sure to open its source code and carefully look through it. ": (
        "Enfin, une clé peut être cachée dans le code source d'une page. Ouvrez le code source et parcourez-le attentivement. "
    ),
    "After finding a key make sure you've copied it's index and key hash i.e. 1 - 2bfc88a4.\r\nYou'll need both parts for it to be decrypted by an agent found in the ACRS chatroom. \r\n\r\nEach decrypted key moves you one step closer to winning The Game.": (
        "Après avoir trouvé une clé, copiez son index et son hash, par exemple : 1 - 2bfc88a4.\r\n"
        "Il vous faut les deux parties pour qu'un agent du salon ACRS puisse la déchiffrer. \r\n\r\n"
        "Chaque clé déchiffrée vous rapproche d'une victoire dans The Game."
    ),
    "While searching for keys you may encounter Fetch URLs. These URLs direct to video files which ACRS users may have interest in buying, so save them if you come across one.\r\n\r\nAll Fetch URLs begin with file:// and finish with .fetch. Copy and paste them into the ShadowFetch application to see what its contents are, then download to later sell the video file.": (
        "En cherchant des clés, vous pouvez croiser des URL Fetch. Ce sont des fichiers video que des utilisateurs ACRS peuvent vouloir acheter : sauvegardez-les.\r\n\r\n"
        "Toutes les URL Fetch commencent par file:// et finissent par .fetch. Collez-les dans ShadowFetch pour voir le contenu, puis téléchargez pour revendre la video."
    ),
    "Example key:": "Exemple de clé :",
    "Ok, you know what todo!": "Ok, tu sais quoi faire !",
    "Hi I'm Ronald, the Game Master for tonight.": "Salut, je suis Ronald, le Game Master de ce soir.",
    "Courtesy of your friend Wade I'll be offering a bit of help.": (
        "Grâce à ton ami Wade, je vais t'offrir un peu d'aide."
    ),
    "VirtMesh is a program you need to install. Without it you won't be able to get onto the Dark Net.": (
        "VirtMesh est un programme à installer. Sans lui, tu ne pourras pas accéder au Dark Net."
    ),
    "ShadowFetch will be your way to download instructions and general help documents. I'd use it if I were you.": (
        "ShadowFetch te servira à télécharger des instructions et des documents d'aide. A ta place, je l'utiliserais."
    ),
    "VirtMesh? ShadowFetch? What are you fucking talking about? how do I get those programs?!": (
        "VirtMesh ? ShadowFetch ? Tu parles de quoi putain ? Comment j'obtiens ces programmes ?!"
    ),
    "Open Dark Drop to download both VirtMesh and ShadowFetch.": (
        "Ouvre Dark Drop pour télécharger VirtMesh et ShadowFetch."
    ),
    "Oh, wait, that's right. Wade did tell me you have a gambling problem, and you probably have no DOSCoin. ": (
        "Ah oui, c'est vrai. Wade m'a dit que tu as un problème de jeu, et que tu n'as probablement pas de DOSCoin. "
    ),
    "Here is some DOS Coin to get you started.": "Voici un peu de DOS Coin pour commencer.",
    "Ok, I got them installed. Now what?": "Ok, c'est installé. Et maintenant ?",
    "Take this fetch link [VMFETCHURL] and put it into ShadowFetch to download a file onto your desktop. It'll breakdown how VirtMesh works.": (
        "Prends ce lien ShadowFetch [VMFETCHURL] et mets-le dans ShadowFetch pour télécharger un fichier sur ton bureau. "
        "Ça explique comment VirtMesh fonctionne."
    ),
    "Or you can open up VirtMesh and try to figure it out yourself.": (
        "Ou tu peux ouvrir VirtMesh et essayer de comprendre par toi-même."
    ),
    "Through VirtMesh hack, mount, then enter a computer. Once you get that done switch over to this desktop and I'll share a link to a Wiki Page that has all types of websites on it.": (
        "Via VirtMesh : pirater, monter, puis entre dans un ordinateur. Une fois fait, reviens sur ce bureau "
        "et je te partagerai un lien vers une page Wiki avec toutes sortes de sites."
    ),
    "If what I'm saying doesn't make sense download and look at that document from the fetch link above.": (
        "Si ce que je dis n'est pas clair, télécharge et lis le document du lien ShadowFetch ci-dessus."
    ),
    # Ronald wrap-up — FStrings combines exactes (une seule chaine par asset)
    "Alright. If you're still connected to that computer I'd urge you to disconnect from it.\r\n\r\nStaying connected to a hacked computer will eventually lock you out of it permanently. From here the easiest way to disconnect would be opening up VirtMesh through the app icon, then double clicking the circle in the center of the screen to exit it.\r\n\r\nLater on you'll be better off switching between multiple computers to avoid permanent lockouts.": (
        "Bon. Si tu es encore connecté à cet ordinateur, je te conseille fortement de te déconnecter.\r\n\r\n"
        "Rester connecté à un ordinateur piraté finit par t'en exclure définitivement. Le plus simple ici : "
        "ouvre VirtMesh via l'icône de l'appli, puis double-clique le cercle au centre de l'écran pour en sortir.\r\n\r\n"
        "Plus tard, tu auras intérêt à alterner entre plusieurs ordinateurs pour éviter les blocages définitifs."
    ),
    "This is the first Wiki Page:\r\n[WIKI]\r\n\r\nPut that link into A.N.N. to access a bunch of different Dark Net websites.": (
        "Voici la première page Wiki :\r\n[WIKI]\r\n\r\n"
        "Mets ce lien dans A.N.N. pour accéder à plein de sites du Dark Net."
    ),
    "It's very important to know what you're looking for. I downloaded a guide onto your desktop, which breaks that down. I'd highly recommend checking that out before going onto the Dark Net.": (
        "Il est très important de savoir ce que tu cherches. J'ai téléchargé un guide sur ton bureau qui explique tout. "
        "Je te conseille fortement de le lire avant d'aller sur le Dark Net."
    ),
    "I reached out to some people who will contact you soon in CryptChat with more information, but unlike me they'll charge you for it.\r\n\r\nODDroot - Has information on hacks you'll face. \r\n\r\nGoggin - Has information on the people who will be trying to kill you tonight.\r\n\r\nAfter you've collected, then decrypted all 8 keys, send me the master key (each decrypted key placed in order by its index number, assembled together as a single key) to beat tonight's game. \r\n\r\nBut let's be real.. You are more than likely dead as fuck lol. \r\n\r\nGood luck! ": (
        "J'ai contacté des gens qui vont bientôt t'écrire sur CryptChat avec plus d'infos, mais contrairement à moi ils te feront payer.\r\n\r\n"
        "ODDroot - A des infos sur les hacks que tu vas croiser. \r\n\r\n"
        "Goggin - A des infos sur les gens qui vont essayer de te tuer ce soir.\r\n\r\n"
        "Une fois que t'as collecté puis déchiffré les 8 clés, envoie-moi la master key "
        "(chaque clé déchiffrée dans l'ordre de son index, assemblées en une seule clé) pour finir la partie de ce soir. \r\n\r\n"
        "Mais soyons réalistes.. T'es très probablement déjà mort lol. \r\n\r\n"
        "Bonne chance ! "
    ),
    "I know who's coming for you tonight. Pay me [PRICE] DOS Coin and I'll link a file you can download off ShadowFetch that'll give you a fighting chance.": (
        "Je sais qui vient te chercher ce soir. Paie-moi [PRICE] DOS Coin et je te file un lien ShadowFetch qui te donnera une chance de t'en sortir."
    ),
    "If you want information on the hacks you'll need to counter pay me [PRICE] DOS Coin and I'll link a file you can download off ShadowFetch": (
        "Si tu veux des infos sur les hacks a contrer, paie-moi [PRICE] DOS Coin et je te file un lien à télécharger sur ShadowFetch"
    ),
    "Was that a tip? Doesn't matter if it wasn't you're not getting that back.": (
        "C'était un pourboire ? Peu importe, tu ne récupères pas ca."
    ),
    "It's still [PRICE] DOS Coin to get the file. Send it all in a single payment or you get nothing.": (
        "C'est toujours [PRICE] DOS Coin pour le fichier. Envoie tout en un seul paiement ou tu n'as rien."
    ),
    "Stop typing, just give me the DOS Coin and you will get what you want.": (
        "Arrête d'écrire, donne-moi juste le DOS Coin et tu auras ce que tu veux."
    ),
    # PlayerPaid — une seule FString avec [LINK]
    "Okay, thanks. Here's the link: \r\n[LINK]\r\n\r\nPut that into ShadowFetch to download your file. I'm out of here.. Later": (
        "Ok, merci. Voici le lien : \r\n[LINK]\r\n\r\n"
        "Mets ça dans ShadowFetch pour télécharger ton fichier. Je me casse.. A plus"
    ),
    # VirtMesh app (UI/Widgets/Computer/VM)
    "Mount": "MONTER",
    "Unmount": "DÉMONTER",
    "MINE": "MINER",
    "UNMINE": "DÉMINER",
    "HACK": "PIRATER",
    "Enter": "Entrer",
    "[EXIT]": "[QUITTER]",
    "[MOUNTING]": "[MONTAGE]",
    "47.56 / Min": "47.56 / min",
    # DarkDrop / Products
    "BUY": "ACHETER",
    "VirtMesh": "VirtMesh",
    "ShadowFetch": "ShadowFetch",
    "Trying to browse the Dark Net? This software is your one stop *secure solution. Access a web of virtual machines that can be hacked for Dark Net browsing or converted into DOS Coin crypto miners!\r\n\r\n*Virtual machine access can be lost if connection is overstayed.": (
        "Tu veux surfer sur le Dark Net ? Ce logiciel est ta *solution sécurisée. Accède à un réseau de machines virtuelles "
        "a pirater pour le Dark Net, ou convertis-les en mineurs de crypto DOS Coin !\r\n\r\n"
        "*L'accès à une machine virtuelle peut être perdu si tu restes connecte trop longtemps."
    ),
    "Looking to download contents from .fetch URLs found on the Dark Net? This program has you covered.": (
        "Tu veux télécharger le contenu des URL .fetch trouvées sur le Dark Net ? Ce programme est fait pour ça."
    ),
    "ACRS": "ACRS",
    "Install and chat with strangers! Anon Chat Relay Server is the premiere application to communicate with all types of people. Ping users to privately buy and sell goods or services through CryptChat.": (
        "Installe et discute avec des inconnus ! Anon Chat Relay Server est l'appli de référence pour parler a tout le monde. "
        "Pingue des utilisateurs pour acheter ou vendre en privé via CryptChat."
    ),
    "AID Pods": "AID Pods",
    "In-ear headphones which increase the audible range of all sounds. Particularly useful for those who have security concerns.\r\n\r\nPress [R] to power on / off.": (
        "Écouteurs intra-auriculaires qui augmentent la portée audible de tous les sons. Utile si tu as des soucis de sécurité.\r\n\r\n"
        "Appuie sur [R] pour allumer / éteindre."
    ),
    "Backdoor Hack": "Hack backdoor",
    "Want a way to get back at those pesky hackers?! The Backdoor Hack is what you need! Defeating a hack will steal DOS Coin from the hacker! Each time you're hacked one will be auto-consumed.": (
        "Envie de te venger de ces satânés hackers ?! Le Hack backdoor est ce qu'il te faut ! "
        "Battre un hack vole des DOS Coin au hacker ! A chaque hack subi, un exemplaire est consommé automatiquement."
    ),
    "Want a way to get back at those pesky hackers?! Then the Backdoor Hack is what you need! Each time you are hacked, it will auto consume, if you defeat the hack you will steal DOS Coin from the hacker!": (
        "Envie de te venger de ces satânés hackers ?! Le Hack backdoor est ce qu'il te faut ! "
        "A chaque hack subi il se consomme ; si tu gagnes, tu voles des DOS Coin au hacker !"
    ),
    "DAREDash": "DAREDash",
    "Convenient app to purchase drugs off the Dark Net. Quickly access drug dealer inventories, make a selection, then order for delivery.": (
        "Appli pratique pour acheter de la drogue sur le Dark Net. Accède vite aux stocks des dealers, choisis, puis commande en livraison."
    ),
    "Firewall Tier I": "Pare-feu niveau I",
    "Firewall Tier II": "Pare-feu niveau II",
    "Firewall Tier III": "Pare-feu niveau III",
    "Firewall Tier IV": "Pare-feu niveau IV",
    "Firewall Tier V": "Pare-feu niveau V",
    "Passively prevents incoming hacks with a 20% success rate. Can be turned on / off by clicking on the taskbar icon and checking / unchecking the box.": (
        "Bloque passivement les hacks entrants avec 20% de réussite. Active / désactive via l'icone de la barre des taches."
    ),
    "Increases passive defense against incoming hacks to a 40% success rate.": (
        "Passe la défense passive contre les hacks entrants a 40% de réussite."
    ),
    "Increases passive defense against incoming hacks to a 60% success rate.": (
        "Passe la défense passive contre les hacks entrants a 60% de réussite."
    ),
    "Increases passive defense against incoming hacks to a 80% success rate.": (
        "Passe la défense passive contre les hacks entrants a 80% de réussite."
    ),
    "Increases passive defense against incoming hacks to a 98% success rate.": (
        "Passe la défense passive contre les hacks entrants a 98% de réussite."
    ),
    "GO CAM": "GO CAM",
    "Portable battery-powered camera that can be attached to a surface and viewed remotely through the SecCam application. All placed cameras auto-sync to SecCam.": (
        "Caméra portable à piles, à fixer sur une surface et à consulter a distance via SecCam. Toutes les caméras placées se synchronisent avec SecCam."
    ),
    "Portable battery-powered camera that can be attached to a surface and viewed remotely through the SecCam application. All placed cameras auto-sync to the SecCam application.": (
        "Caméra portable à piles, à fixer sur une surface et à consulter a distance via SecCam. Toutes les caméras placées se synchronisent avec SecCam."
    ),
    "Key Cue": "Key Cue",
    "Key Cue Plus": "Key Cue Plus",
    "Want extra help to find key hashes? When loaded onto a website that contains one there will be a small key icon visible near the top right of A.N.N. browser.": (
        "Besoin d'aide pour trouver les hash de clés ? Sur un site qui en contient une, une petite icône clé apparait en haut a droite du navigateur A.N.N."
    ),
    "Interested in gaining more help with key hashes? When loaded onto the specific website page which contains one the key icon near the top right of A.N.N. browser will change from white to a gold color.": (
        "Envie d'encore plus d'aide pour les hash de clés ? Sur la page exacte qui en contient une, l'icône clé en haut a droite d'A.N.N. passe du blanc au doré."
    ),
    "Motion Alert": "Alerte mouvement",
    "Software that provides visual & audio notifications when a placed motion sensor is triggered. Perfect for the person who's focused on other tasks when unexpected motion arrives.\r\n\r\nClicking on the motion alert taskbar icon will reveal the named location and status of all placed motion sensors.": (
        "Logiciel qui envoie des alertes visuelles et sonores quand un détecteur de mouvement placé se déclenche. Idéal quand tu es concentré ailleurs.\r\n\r\n"
        "Clique l'icone d'alerte dans la barre des taches pour voir le lieu et l'état de tous les détecteurs placés."
    ),
    "Motion Sensor": "Détecteur de mouvement",
    "Portable battery-powered sensor that detects nearby motion. Requires separate purchase of Motion Alert to receive visual and sound based notifications on your computer when a sensor is triggered.": (
        "Capteur portable à piles qui detecte le mouvement à proximité. Nécessite l'achat separe d'Alerte mouvement pour les notifications sur ton PC."
    ),
    "NOP Sled": "NOP Sled",
    "Want to skip an incoming hack? The NOP Sled is your answer! Upon activation you'll immediately break free. (Backdoor Hacks are not consumed).\r\n\r\nPress [Middle Mouse Button] during a hack to activate.": (
        "Envie de zapper un hack entrant ? Le NOP Sled est la réponse ! A l'activation tu te libères tout de suite. (Les Hacks backdoor ne sont pas consommés).\r\n\r\n"
        "Appuie sur [Clic molette] pendant un hack pour l'activer."
    ),
    "Find yourself in a hack you don't want to deal with? Then the NOPSled is what you want! By simply pressing the middle mouse button you break free from the hack!(Does not consume any Backdoors)": (
        "Coincé dans un hack dont tu ne veux pas ? Le NOPSled est fait pour toi ! Un clic molette et tu te libères ! (Ne consomme aucun Backdoor)"
    ),
    "Ringonome": "Ringonome",
    "Finger ring that provides a ticking noise once per second when activated. Great way to keep your counting consistent.\r\n\r\nPress [T] to power on / off.": (
        "Bague qui fait un tic une fois par seconde une fois activée. Pratique pour compter régulièrement.\r\n\r\n"
        "Appuie sur [T] pour allumer / éteindre."
    ),
    "SecCam": "SecCam",
    "Monitor your placed GO CAM camera feeds with this app. Navigate between cameras using the on-screen buttons or press [A] / [D].": (
        "Surveille tes flux GO CAM avec cette appli. Change de camera avec les boutons à l'écran ou [A] / [D]."
    ),
    "Signal Booster": "Amplificateur de signal",
    "Temporarily increase internet speed by placing this device in an *optimal location. View on-device section labled \"Signal Strength\" to see quality of speed boost.\r\n\r\n*Over time device may need to be moved to maintain full speed boost.": (
        "Augmente temporairement la vitesse internet en placant cet appareil a un endroit *optimal. "
        "Regarde la section \"Signal Strength\" sur l'appareil pour la qualité du boost.\r\n\r\n"
        "*Avec le temps, tu devras peut-être le deplacer pour garder le boost max."
    ),
    "Sig.Boost Monitor": "Moniteur amplif.",
    "Track your Signal Booster's internet speed increase through a desktop taskbar icon. The icon will display the current boost strength.": (
        "Suis le boost de vitesse de ton Amplificateur via une icône de barre des taches. L'icone affiche la force actuelle."
    ),
    "VM Cyrpto Miner": "Mineur crypto VM",
    "Purchase a *single-use script that turns a hacked computer in VirtMesh to a crypto miner for passive money generation.\r\n\r\n*Choosing to unmine a hacked computer will destroy the script. It can be mined again, but will require another script to do so.": (
        "Achete un script *à usage unique qui transforme un PC piraté dans VirtMesh en mineur crypto pour gagner passivement.\r\n\r\n"
        "*Déminer un PC détruit le script. Tu pourras reminer, mais il faudra un autre script."
    ),
    "VM Grid Tier II": "Grille VM niveau II",
    "VM Grid Tier III": "Grille VM niveau III",
    "Expand access within VirtMesh to higher quality computers, both in increased uptime before active connection is compromised and in crypto mining potential.": (
        "Élargit l'accès VirtMesh à des PC de meilleure qualité : plus d'uptime avant compromission et meilleur potentiel de minage."
    ),
    "Expand access within VirtMesh to highest quality computers, both in increased uptime before active connection is compromised and in crypto mining potential.": (
        "Élargit l'accès VirtMesh aux meilleurs PC : plus d'uptime avant compromission et meilleur potentiel de minage."
    ),
    "VM Mount Tier II": "Montage VM niveau II",
    "VM Mount Tier III": "Montage VM niveau III",
    "Increase maximum mounted computers in VirtMesh from 2 -> 4. Mounted computers can access A.N.N. web browser.": (
        "Passe le max de PC montés dans VirtMesh de 2 à 4. Les PC montés peuvent utiliser le navigateur A.N.N."
    ),
    "Increase maximum mounted computers in VirtMesh from 4 -> 6. Mounted computers can access A.N.N. web browser.": (
        "Passe le max de PC montés dans VirtMesh de 4 à 6. Les PC montés peuvent utiliser le navigateur A.N.N."
    ),
    # Inventaire / PlayerItems
    "Eviction Letter": "Lettre d'expulsion",
    "Just a letter from my dickhead landord telling me I am getting evicted. Don't have time to read it right now.": (
        "Juste une lettre de mon connard de proprio qui me dit que je me fais expulser. Pas le temps de la lire maintenant."
    ),
    "Flashlight": "Lampe torche",
    "High-powered handheld light.\r\n\r\nPress [F] to power on / off.": (
        "Lampe portative puissante.\r\n\r\nAppuie sur [F] pour allumer / éteindre."
    ),
    "[F] - Toggle Flash Light": "[F] - Allumer / éteindre la lampe",
    "[R] - Toggle AID Pods": "[R] - Allumer / éteindre les AID Pods",
    "[T] - Toggle Ringonome": "[T] - Allumer / éteindre le Ringonome",
    "Electrical Room Key": "Clé de la salle électrique",
    "This key unlocks the inner electrical room door.": "Cette clé ouvre la porte interieure de la salle électrique.",
    "Employee Key": "Clé employé",
    "This key unlocks the employee back doors.": "Cette clé ouvre les portes arrière reservees aux employes.",
    "Motel Master Key": "Passe-partout du motel",
    "This key locks / unlocks the motel room doors.": "Cette clé ferme / ouvre les portes des chambres du motel.",
    "Crank'd": "Crank'd",
    "Banned energy drink that claims to amplify your physical capabilities.\r\n\r\nI've heard stories of people having sudden heart attacks after consuming these drinks.": (
        "Boisson énergétique interdite qui prétend booster tes capacités physiques.\r\n\r\n"
        "J'ai entendu parler de gens qui font des crises cardiaques après en avoir bu."
    ),
    "Krystal King": "Krystal King",
    "Baggie of crushed methamphetamine.\r\n\r\nNo way I'm trying that shit.": (
        "Sachet de méthamphétamine écrasée.\r\n\r\nPas question que j'y touche."
    ),
    "Zannac": "Zannac",
    "Low-dosage prescription grade anxiety medication.\r\n\r\nTaking everything in the pill bottle will calm my nerves.": (
        "Anxiolytique de prescription à faible dose.\r\n\r\nAvaler tout le flacon devrait calmer mes nerfs."
    ),
    # Pensees Simon
    "I can't hold anymore of these...": "Je ne peux plus en tenir davantage...",
    "It's locked...": "C'est fermé à clé...",
    "Shit... I gotta get to work...": "Merde... Je dois aller bosser...",
    "I don't have the key...": "Je n'ai pas la clé...",
    "I have to stay calm...": "Je dois rester calme...",
    "I think he's gone...": "Je crois qu'il est parti...",
    "There is someone in there...": "Il y a quelqu'un là-dedans...",
    "This room is out of order...": "Cette chambre est hors service...",
    # ShadowFetch ChoiceTrees
    "./>Welcome to ShadowFetch": "./>Bienvenue sur ShadowFetch",
    "Error: No Connection Detected": "Erreur : aucune connexion détectée",
    "Error: No connection detected.": "Erreur : aucune connexion détectée.",
    "Enter the Fetch URL to verify the file...": "Entre l'URL Fetch pour vérifier le fichier...",
    "Enter the Fetch  URL to verify the file...": "Entre l'URL Fetch pour vérifier le fichier...",
    "Invalid Fetch URL - Enter A Valid Fetch URL!": "URL Fetch invalide - entre une URL Fetch valide !",
    "File downloaded successfully on your desktop!": "Fichier téléchargé avec succès sur ton bureau !",
    "Check your internet connection.": "Vérifie ta connexion internet.",
    # Difficulte
    "Must Complete Normal Mode": "Terminer le mode Normal d'abord",
    "- Perma Death\r\n- Good Luck": "- Mort permanente\r\n- Bonne chance",
    "- No Perma Death\r\n- Challenging": "- Pas de mort permanente\r\n- Difficile",
    "- Same as Normal \r\n- Perma Death\r\n- Experimental": (
        "- Identique au Normal\r\n- Mort permanente\r\n- Expérimental"
    ),
    # Cinema / messages hacker
    "I can't believe that fucking degenerate gambler won...": (
        "J'arrive pas a croire que ce putain de joueur dégénéré ait gagné..."
    ),
    "Pay off the rent he owes and make sure the payment's in his name. Keeping him in that shithole will make it easy to find him if we're given a reason": (
        "Paie le loyer qu'il doit et assure-toi que le paiement est à son nom. "
        "Le garder dans ce trou a rats facilitera de le retrouver si on a une raison"
    ),
    "Also, you can cut surveillance to focus on the big task. I assume you know what...": (
        "Aussi, tu peux couper la surveillance pour te concentrer sur la grosse tâche. Je suppose que tu vois ce que..."
    ),
    "Sure thing.": "Avec plaisir.",
    "Yeah, I'm already back on it.": "Ouais, j'y suis déjà remis.",
}


def _is_ascii(s: str) -> bool:
    return s.isascii()


def enc_ansi(s: str) -> bytes:
    """ASCII / legacy ANSI body (English sources and ASCII-only FR)."""
    return s.encode("ascii", errors="strict")


def enc_dialog(s: str) -> bytes:
    """DialogMessage payloads: UTF-8 so accents survive (not cp1252)."""
    return s.encode("utf-8")


def fstring_bytes(s: str) -> bytes:
    """
    Unreal FString wire format:
      - ASCII  -> positive length + ANSICHAR + NUL
      - accents -> negative length + UTF-16LE + NUL  (cp1252 made glyphs vanish in UI)
    """
    if _is_ascii(s):
        body = enc_ansi(s) + b"\x00"
        return struct.pack("<I", len(body)) + body
    encoded = s.encode("utf-16-le") + b"\x00\x00"
    return struct.pack("<i", -(len(encoded) // 2)) + encoded


def patch_dialog_blob(data: bytes, pairs: list[tuple[str, str]]) -> tuple[bytes, int]:
    """DialogMessageDataAsset: 04 05 <u32 leninclnull> <text>\\0 ..."""
    if len(data) < 7 or data[0:2] != b"\x04\x05":
        return data, 0
    ln = struct.unpack_from("<I", data, 2)[0]
    if ln < 2 or 6 + ln > len(data):
        return data, 0
    body = data[6 : 6 + ln]
    if not body.endswith(b"\x00"):
        return data, 0
    text = body[:-1]
    n = 0
    new_text = text
    for en, fr in pairs:
        eb, fb = enc_dialog(en), enc_dialog(fr)
        c = new_text.count(eb)
        if c:
            new_text = new_text.replace(eb, fb)
            n += c
    if n == 0:
        return data, 0
    new_body = new_text + b"\x00"
    out = data[:2] + struct.pack("<I", len(new_body)) + new_body + data[6 + ln :]
    return out, n


def patch_blob(data: bytes, pairs: list[tuple[str, str]]) -> tuple[bytes, int]:
    pairs = sorted(pairs, key=lambda x: len(x[0]), reverse=True)
    n = 0
    out = data
    # 1) Standard / combined FStrings (int32 len + chars + nul)
    for en, fr in pairs:
        src, dst = fstring_bytes(en), fstring_bytes(fr)
        c = out.count(src)
        if c:
            out = out.replace(src, dst)
            n += c
    # 2) Dialog assets
    out2, n2 = patch_dialog_blob(out, pairs)
    return out2, n + n2


def recalculate_offsets(asset: dict) -> None:
    indexed = [
        e for e in asset.get("Exports", []) if isinstance(e.get("SerialSize"), int) and e["SerialSize"] > 0
    ]
    if not indexed:
        return
    indexed.sort(key=lambda e: e.get("SerialOffset", 0))
    cur = indexed[0]["SerialOffset"]
    for e in indexed:
        e["SerialOffset"] = cur
        cur += e["SerialSize"]


def should_copy(rel: Path) -> bool:
    # Steam extract uses "Blueprints"; Desktop dump used "BluePrints".
    # Compare case-insensitively so GameActors/Pawns are not skipped on Steam.
    s = str(rel).replace("/", "\\")
    sl = s.lower()
    stem = s[: -len(rel.suffix)] if rel.suffix else s
    if any(stem.lower() == x.lower() for x in EXCLUDE_FROM_PAK):
        return False
    return any(sl == p.lower() or sl.startswith(p.lower() + "\\") for p in COPY_PREFIXES)


def run_gui(args: list[str]) -> None:
    r = subprocess.run(
        [str(UASSETGUI), *args],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"UAssetGUI failed {args[:3]}: {r.stderr or r.stdout}")


def process_asset(src_uasset: Path, pairs: list[tuple[str, str]]) -> int:
    rel = src_uasset.relative_to(LEGACY)
    dst_uasset = STAGED / rel
    dst_uasset.parent.mkdir(parents=True, exist_ok=True)
    json_path = JSON_DIR / rel.with_suffix(".json")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    run_gui(["tojson", str(src_uasset), str(json_path), ENGINE, str(USMAP)])
    if not json_path.exists():
        # fallback copy untouched
        shutil.copy2(src_uasset, dst_uasset)
        uexp = src_uasset.with_suffix(".uexp")
        if uexp.exists():
            shutil.copy2(uexp, dst_uasset.with_suffix(".uexp"))
        return 0

    asset = json.loads(json_path.read_text(encoding="utf-8"))
    total = 0
    for exp in asset.get("Exports", []):
        data_b64 = exp.get("Data")
        if not data_b64:
            continue
        raw = base64.b64decode(data_b64)
        new_raw, n = patch_blob(raw, pairs)
        if n:
            exp["Data"] = base64.b64encode(new_raw).decode("ascii")
            exp["SerialSize"] = len(new_raw)
            total += n
    if total:
        recalculate_offsets(asset)
        json_path.write_text(json.dumps(asset, ensure_ascii=False, indent=2), encoding="utf-8")
        run_gui(["fromjson", str(json_path), str(dst_uasset), str(USMAP)])
    else:
        shutil.copy2(src_uasset, dst_uasset)
        uexp = src_uasset.with_suffix(".uexp")
        if uexp.exists():
            shutil.copy2(uexp, dst_uasset.with_suffix(".uexp"))
        for ext in (".ubulk", ".uptnl"):
            sibling = src_uasset.with_suffix(ext)
            if sibling.exists():
                shutil.copy2(sibling, dst_uasset.with_suffix(ext))
    return total


def asset_needs_patch(ua: Path, pairs: list[tuple[str, str]]) -> bool:
    uexp = ua.with_suffix(".uexp")
    if not uexp.exists():
        return False
    data = uexp.read_bytes()
    for en, _ in pairs:
        if fstring_bytes(en) in data:
            return True
    return False


def stage_and_patch(pairs: list[tuple[str, str]]) -> tuple[int, int]:
    if STAGED.parent.exists():
        shutil.rmtree(STAGED.parent)
    if JSON_DIR.exists():
        shutil.rmtree(JSON_DIR)
    STAGED.mkdir(parents=True)
    JSON_DIR.mkdir(parents=True)

    uassets = [
        p
        for p in LEGACY.rglob("*.uasset")
        if should_copy(p.relative_to(LEGACY)) and asset_needs_patch(p, pairs)
    ]
    print(f"assets_with_text={len(uassets)} (excluded_settings={len(EXCLUDE_FROM_PAK)})")

    files = 0
    reps = 0
    for i, ua in enumerate(uassets, 1):
        try:
            n = process_asset(ua, pairs)
        except Exception as ex:
            print(f"FAIL {ua.relative_to(LEGACY)}: {ex}")
            rel = ua.relative_to(LEGACY)
            dst = STAGED / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ua, dst)
            for ext in (".uexp", ".ubulk", ".uptnl"):
                s = ua.with_suffix(ext)
                if s.exists():
                    shutil.copy2(s, dst.with_suffix(ext))
            continue
        if n:
            files += 1
            reps += n
            print(f"patched {ua.relative_to(LEGACY)} replacements={n}")
        if i % 20 == 0:
            print(f"progress {i}/{len(uassets)}")
    return files, reps


def write_map_csv() -> list[tuple[str, str]]:
    merged = dict(RAW)
    # Extra map overrides only when key not already hand-tuned in RAW
    for en, fr in _load_extra_raw().items():
        merged.setdefault(en, fr)
    pairs = list(merged.items())
    with MAP_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "translation", "len_en", "len_fr"])
        for en, fr in pairs:
            w.writerow([en, fr, len(en), len(fr)])
    return pairs


def pack_and_apply() -> None:
    out_dir = ROOT / "build" / "pak"
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob(f"{MOD_BASE}*"):
        p.unlink()
    zen = out_dir / f"{MOD_BASE}.utoc"
    cmd = [str(RETOC), "to-zen", "--version", "UE5_6", str(STAGED.parent), str(zen)]
    print("Running", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    print((r.stdout or "")[-1500:])
    print((r.stderr or "")[-1500:])
    if r.returncode != 0:
        raise RuntimeError("to-zen failed")
    paks_game = paks_dir()
    for p in list(paks_game.glob(f"{MOD_BASE}*")):
        p.unlink()
    for p in out_dir.glob(f"{MOD_BASE}*"):
        shutil.copy2(p, paks_game / p.name)
        print("Copied", p.name)


def verify_sample() -> None:
    p = STAGED / "UI" / "Widgets" / "Titles" / "WBP_MainTitleWidget.uexp"
    if not p.exists():
        raise RuntimeError("MainTitle missing after patch")
    d = p.read_bytes()
    if fstring_bytes("Jouer") not in d and b"Jouer" not in d:
        # may be only in button exports
        btn = STAGED / "UI" / "Widgets" / "Titles" / "WBP_TitleMenuButton.uexp"
        pass
    main = STAGED / "UI" / "Widgets" / "Titles" / "WBP_MainTitleWidget.uexp"
    data = main.read_bytes()
    print(
        "MainTitle size",
        len(data),
        "has Jouer",
        fstring_bytes("Jouer") in data or b"Jouer\x00" in data,
        "has Continuer",
        fstring_bytes("Continuer") in data or b"Continuer\x00" in data,
    )


def main() -> None:
    if not USMAP.exists():
        print("Missing", USMAP, file=sys.stderr)
        sys.exit(1)
    if not UASSETGUI.exists():
        print("Missing", UASSETGUI, file=sys.stderr)
        sys.exit(1)
    print(f"LEGACY={LEGACY}")
    if not LEGACY.exists():
        raise SystemExit(f"Legacy Content missing: {LEGACY}")
    pairs = write_map_csv()
    print(f"pairs={len(pairs)}")
    files, reps = stage_and_patch(pairs)
    print(f"files_patched={files} replacements={reps}")
    if reps == 0:
        raise RuntimeError("No replacements made")
    verify_sample()
    pack_and_apply()
    print("done — UAssetGUI free-length FR mod installed")


if __name__ == "__main__":
    main()
