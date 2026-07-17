# -*- coding: utf-8 -*-
"""Clean player-facing strings and produce translated ui_gameplay_fr.csv."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "source" / "game_locres_full.csv"
out = ROOT / "work" / "ui_gameplay_fr.csv"

deny = re.compile(
    r"(Ultra Dynamic|CinematicCamera|volumetric|material_function|\bUDW\b|\bUDS\b|"
    r"Path Tracer|Sequencer|PostProcess|groom|IMAX|Fog |Weather|Movie Render|"
    r"AmbientSound|CustomizableObject|SMessaging|Blueprint|game module|"
    r"CHECK_PUREVIRTUAL|Interchange|Niagara|Chaos|Slate|Nanite|Keyframing|"
    r"Color_Mode|Project_Mode|Sky_Atmosphere|Simplified_Color|Cloud Movement|"
    r"Foliage Wind|Input Mapping|Input Action|Input Modifier|GrantAbility|"
    r"animation data|Normals were supposed|Desktop/Console|Asset Loading|"
    r"Filmic_Hacker|High Frequency Noise|Getting and Displaying Time)",
    re.I,
)

UI = {
    "Enter Desk": "S'asseoir au bureau",
    "[TAB] Inventory": "[TAB] Inventaire",
    "[SHIFT] Run": "[SHIFT] Courir",
    "[W,A,S,D] Move": "[Z,Q,S,D] Se déplacer",
    "File downloaded successfully on your desktop!": "Fichier téléchargé avec succès sur votre bureau !",
    "Enter the Fetch URL to verify the file...": "Entrez l'URL Fetch pour vérifier le fichier…",
    "Enter the Fetch  URL to verify the file...": "Entrez l'URL Fetch pour vérifier le fichier…",
    "Invalid Fetch URL - Enter A Valid Fetch URL!": "URL Fetch invalide — entrez une URL Fetch valide !",
    "Can't figure out how the hell I'm supposed to buy crap here": "J'arrive pas à comprendre comment on est censé acheter de la merde ici",
    "Tried to buy a little something but it says no wallet linked. How do I link it?": "J'ai voulu acheter un truc mais ça dit aucun wallet lié. Comment on lie ?",
    "Apparently I need to buy a list of websites from this chat to actually get somewhere on the dark net. This is the place to do that right?": "Apparemment il faut acheter une liste de sites dans ce chat pour avancer sur le dark net. C'est bien ici pour ça ?",
    "Do people actually talk to each other here or is it mostly about buying or selling?": "Les gens se parlent vraiment ici ou c'est surtout du buy/sell ?",
    "Are there any mods in this chat?": "Y a des modos dans ce chat ?",
    "How long do I have to wait before I can sell something?": "Je dois attendre combien de temps avant de pouvoir vendre un truc ?",
    "I was told this chat clears. What does that mean?": "On m'a dit que ce chat « clears ». Ça veut dire quoi ?",
    "Is there a general refund policy or is everyone here running their own business of sorts?": "Y a une politique de remboursement générale ou chacun gère sa boutique ?",
    "Please tell me there's a video or something out there explaining how this chatroom functions. I'm worried if I do wrong I'll get permabanned": "Dites-moi qu'il existe une vidéo qui explique comment marche ce chat. J'ai peur de me faire ban à vie si je fais une connerie",
    "Anyone know of another chat room that's focused on providing services only? I'm sick of the people using this place like it's a casual group": "Quelqu'un connaît un autre chat axé uniquement services ? Marre des gens qui traitent cet endroit comme un groupe casual",
    "Hey how can I easily figure out if a deal is good or not? Everyone seems to hide their prices behind a ping.": "Hey, comment savoir facilement si une offre est bonne ? Tout le monde cache les prix derrière un ping.",
    "This chat was out of control yesterday, it seems fine for now. Did the mods finally do something or what?": "Ce chat était hors de contrôle hier, ça a l'air mieux. Les modos ont enfin fait un truc ou quoi ?",
    "We can all agree that having people spam dumb shit is pointless for this chat, right? So why are repeated spammers allowed to be here???": "On est d'accord que le spam débile sert à rien ici, non ? Alors pourquoi les spammeurs récidivistes sont encore là ???",
    "I've been here the past couple days and haven't seen a single username I recognize. Is that normal? Anonymous thing or constant influx of ne": "Je suis là depuis quelques jours et je reconnais aucun pseudo. C'est normal ? Anonymat ou flux constant de nouveaux ?",
    "I'm getting personal threats from a user in here. Yeah, I know you can see this. Curious what moderation has to say about this type of behav": "Je reçois des menaces perso d'un user ici. Ouais, je sais que tu vois ça. Curieux de voir ce que la modo en dit.",
    "If you don't know what's going, how this chat works, are new here and can't shut up, just get the fuck out and go somewhere else. By staying": "Si tu piges rien, t'es nouveau et tu fermes pas ta gueule, casse-toi ailleurs. En restant",
    "It wasn't too difficult to find this chat, so I have to wonder if the users here are legit or feds trying to honeypot people into prison.": "Pas trop dur de trouver ce chat… je me demande si les users sont legit ou des feds en honeypot.",
    "A bunch of pings tonight have lead to obvious bot accounts. This might end up being my last night in chat if things don't turn around soon..": "Plein de pings ce soir mènent à des bots évidents. Peut-être ma dernière nuit ici si ça s'améliore pas…",
    "Can we get the people who post random shit out of here??? Like why do they even have the ability to talk if they're just mashing nonsense in": "On peut virer ceux qui postent de la merde au pif ??? Pourquoi ils peuvent parler s'ils tapent du nonsense",
    "I shared the link to this chat with my homie but his connection is getting blocked. Do I need to talk to someone about that or is it just a ": "J'ai partagé le lien à mon pote mais sa co est bloquée. Je dois parler à quelqu'un ou c'est juste un",
    "A person with authority in this chatroom needs to contact me immediately. There's a user who needs to be permanently removed for reasons I c": "Une personne d'autorité ici doit me contacter immédiatement. Y a un user à ban définitivement pour des raisons que j",
    "Requesting a moderator ban on another user. A dear friend of mine is having his work given away for free after selling it to a certain someo": "Je demande un ban modo. Un pote se fait redistribuer son taf gratuitement après l'avoir vendu à quelqu'un",
    "I always respond! I'm always active! ***Certified Dark Net Expert*** I'm your middle man. What you want I get! Quit waiting and contact me!": "Je réponds toujours ! Toujours actif ! ***Expert Dark Net certifié*** Je suis ton middleman. Ce que tu veux, je l'ai ! Arrête d'attendre, contacte-moi !",
    "Hypothetically would it within reason to have the people selling drugs here deliver them to a prison? If you know or think you know let me k": "Hypothétiquement, ce serait jouable que les dealers ici livrent en prison ? Si tu sais, dis-moi",
    "LOWEST PRICES ON THE MARKET GUARANTEED. FULFILLED THROUGH SYNDICATE CONNECTIONS OTHERS SIMPLY DO NOT HAVE. BEING A LARGE GROUP ALLOWS FOR WI": "LES PRIX LES PLUS BAS DU MARCHÉ GARANTIS. VIA DES CONNEXIONS SYNDICAT QUE LES AUTRES N'ONT PAS. GROS GROUPE = WI",
}

# reuse chat translations
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "translate_chat_ui", Path(__file__).with_name("translate_chat_ui.py")
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
UI.update(_mod.CHAT)

rows = []
seen = set()
with src.open(encoding="utf-8", errors="replace", newline="") as f:
    for row in csv.DictReader(f):
        t = (row.get("source") or "").strip()
        k = (row.get("key") or "").strip()
        if not t or t in seen:
            continue
        if deny.search(t):
            continue
        fr = None
        notes = "needs_review"
        if t in UI:
            fr = UI[t]
            notes = "translated"
        else:
            for en, tr in UI.items():
                if t == en or (len(t) >= 40 and en.startswith(t[:40])):
                    fr = tr
                    notes = "translated_prefix"
                    break
        # keep if translated or clearly gameplay chat/UI
        keep = fr is not None or any(
            x in t
            for x in (
                "DOS Coin",
                "DOS COIN",
                "Enter Desk",
                "Inventory",
                "chat",
                "Fetch URL",
                "desktop",
                "moderator",
                "Dark Net",
            )
        )
        if not keep:
            continue
        if fr is None:
            fr = t
        seen.add(t)
        rows.append({"key": k, "source": t, "translation": fr, "notes": notes})

with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["key", "source", "translation", "notes"])
    w.writeheader()
    w.writerows(rows)

print(f"rows={len(rows)} translated={sum(1 for r in rows if r['notes'].startswith('translated'))}")
