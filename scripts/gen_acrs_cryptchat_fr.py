# -*- coding: utf-8 -*-
"""Generate work/acrs_cryptchat_fr.json from EN string lists + embedded maps."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
sys.path.insert(0, str(ROOT / "scripts"))
from build_ui_uassetgui_patch import RAW  # noqa: E402

UI = {
    "[#VelvetRoad]: Buy / Sell Decryption Services, Hitman Services, Drugs, Dark Net Files & Sites, +more": (
        "[#VelvetRoad]: Achat / vente services de dechiffrement, tueurs a gages, drogue, fichiers & sites Dark Net, +encore"
    ),
    "[#VelvetRoad] Read & Interact only - CHAT DISABLED": (
        "[#VelvetRoad] Lecture & interaction seulement - CHAT DESACTIVE"
    ),
    "PINGS DISABLED": "PINGS DESACTIVES",
    "A.C.R.S - Anon Chat Relay Service": "A.C.R.S - Relais de chat anonyme",
}

# Unique ACRS lobby status ads (agents)
STATUS = {
    "ARE YOU AN ADDICT? DO YOU NEED DRUGS? I SELL THEM. DRUGS WILL BE DELIVERED. PING FOR INFO.": (
        "T'ES ADDICT ? T'AS BESOIN DE DROGUE ? J'EN VENDS. LIVRAISON ASSUREE. PING POUR INFOS."
    ),
    "Are you bored looking through the same part of the dark net? Well then purchase [SITE] from me for and expand your browsing!": (
        "Marre de tourner en rond sur le meme coin du dark net ? Achete [SITE] chez moi et elargis tes recherches !"
    ),
    "Bored? Feel like getting fucked up? Ping my shit and buy some drugs off me": (
        "Ennuye ? Envie de te dechirer ? Pingue-moi et achete de la drogue"
    ),
    "Can anyone share a link to [SITE]. 1st come 1st serve. I have money": (
        "Quelqu'un peut partager un lien vers [SITE] ? Premier arrive, premier servi. J'ai du fric"
    ),
    "DO YOU LIKE MONEY? DO YOU USE THE DARK NET? I AM TRYING TO LOCATE THE WEBSITE: [SITE]. SEND LINK AND GET PAID REAL MONEY": (
        "T'AIMES L'ARGENT ? TU USES LE DARK NET ? JE CHERCHE LE SITE : [SITE]. ENVOIE LE LIEN ET SOIS PAYE"
    ),
    "DO YOU LIKE MONEY? DO YOU USE THE DARK NET? I AM TRYING TO LOCATE [VIDEO]. SEND AND GET PAID REAL MONEY": (
        "T'AIMES L'ARGENT ? TU USES LE DARK NET ? JE CHERCHE [VIDEO]. ENVOIE ET SOIS PAYE"
    ),
    "DRUGS? GET THE BEST SHIT ON THE MARKET. ping me": "DROGUE ? LE MEILLEUR TRUC DU MARCHE. pingue-moi",
    "Decrypt key hashes with my service in 3 steps. 1) Send key 2) Pay price 3) Receive decrypted key. Service cost dependent on encryption strength. Only select encryption styles are compatible with my skill set.": (
        "Dechiffre des hash de cles en 3 etapes. 1) Envoie la cle 2) Paie le prix 3) Recois la cle dechiffree. "
        "Tarif selon la force du chiffrement. Seuls certains types sont compatibles avec mon savoir-faire."
    ),
    "Decryption assistance available for a price. Convert encrypted key hashes into the plaintext form needed. Ping for more info.": (
        "Aide au dechiffrement contre paiement. Transforme les hash chiffres en texte clair. Ping pour plus d'infos."
    ),
    "Doxx the private details of your enemy to do greater harm down the road. Ping for info": (
        "Doxxe les infos privees de ton ennemi pour lui faire plus de mal ensuite. Ping pour infos"
    ),
    "Drugs, anyone? Send your pings to my inbox to look at what I have in stock.": (
        "De la drogue, quelqu'un ? Envoyez vos pings pour voir mon stock."
    ),
    "Eliminate competition with our service. Allow me to broker the deal and connect a hitman that will remove whomever you choose. Ping to learn more": (
        "Eliminez la concurrence avec notre service. Je courtage le deal et connecte un tueur qui retirera qui vous voulez. Ping pour en savoir plus"
    ),
    "Expose details of any player in The Game with my doxing service. Market rate price & high ratio of success.": (
        "Expose les details de n'importe quel joueur de The Game avec mon service de dox. Prix marche & fort taux de reussite."
    ),
    "Extending my doxing services here. Ping for rate": "J'etends mes services de dox ici. Ping pour le tarif",
    "For those browsing the dark net I'm hunting down [VIDEO]. if you got it I'm ready to pay.": (
        "Pour ceux qui trainent sur le dark net, je cherche [VIDEO]. Si t'as ca, je suis pret a payer."
    ),
    "For those browsing the dark net I'm hunting down the website - [SITE]. if you got a link to it I'm ready to pay.": (
        "Pour ceux qui trainent sur le dark net, je cherche le site - [SITE]. Si t'as un lien, je paie."
    ),
    "Give me the video [VIDEO] IMMEDIATELY! Ready to pay NOW!": (
        "File-moi la video [VIDEO] TOUT DE SUITE ! Pret a payer MAINTENANT !"
    ),
    "Give me the website link [SITE] IMMEDIATELY! Ready to pay NOW!": (
        "File-moi le lien du site [SITE] TOUT DE SUITE ! Pret a payer MAINTENANT !"
    ),
        "Got those hitmen ready to go. Care to take someone out permanently? Ping me": (
        "J'ai des tueurs prets a partir. Envie de faire disparaitre quelqu'un pour de bon ? Pingue-moi"
    ),
        "Hack others for a small price and cause a little chaos. Tier 3 hacker. Ping me": (
        "Hack les autres pour pas cher et seme un peu le chaos. Hacker tier 3. Pingue-moi"
    ),
    "Hacker ready to interrupt any of The Game players. Send a ping to see rates. Tier 1 hacking services.": (
        "Hacker pret a interrompre n'importe quel joueur de The Game. Envoie un ping pour les tarifs. Services hack tier 1."
    ),
    "Hacker ready to interrupt any of The Game players. Send a ping to see rates. Tier 2 hacking services.": (
        "Hacker pret a interrompre n'importe quel joueur de The Game. Envoie un ping pour les tarifs. Services hack tier 2."
    ),
    "Hacker ready to interrupt any of The Game players. Send a ping to see rates. Tier 3 hacking services.": (
        "Hacker pret a interrompre n'importe quel joueur de The Game. Envoie un ping pour les tarifs. Services hack tier 3."
    ),
    "Heading out soon if you want [SITE] now's the time to pick it up. Ping.": (
        "Je me casse bientot, si tu veux [SITE] c'est le moment. Ping."
    ),
    "Heading out soon if you want [SITE] now's the time to pick it up. Ping. ": (
        "Je me casse bientot, si tu veux [SITE] c'est le moment. Ping. "
    ),
    "Highly efficient key decryption service online. Quality key hash processing at a fraction of the expected time. Share key to receive pricing & confirmation of key's compatibility with service": (
        "Service de dechiffrement de cles ultra efficace en ligne. Traitement de hash de qualite en une fraction du temps attendu. "
        "Envoie la cle pour le tarif et la confirmation de compatibilite"
    ),
    "Highly efficient key decryption service online. Quality key hash processing at a fraction of the expected time. Share key to receive pricing & confirmation of key's compatibility with service\"": (
        "Service de dechiffrement de cles ultra efficace en ligne. Traitement de hash de qualite en une fraction du temps attendu. "
        "Envoie la cle pour le tarif et la confirmation de compatibilite\""
    ),
    "Highly qualified and prepared to dox whomever. Pay up and their info becomes my target.": (
        "Hautement qualifie et pret a doxer n'importe qui. Paie et leurs infos deviennent ma cible."
    ),
    "Hire me to doxx someone you despise. I don't judge, I only doxx.": (
        "Engage-moi pour doxer quelqu'un que tu detestes. Je juge pas, je doxe."
    ),
    "Hitmen for hire. Service available at market price. Ping now": (
        "Tueurs a gages. Service au prix du marche. Ping maintenant"
    ),
    "Hitmen on standby, waiting for your payment to deploy. Contact to coordinate a kill.": (
        "Tueurs en attente, prets des que tu paies. Contacte pour coordonner un kill."
    ),
    "Hitmen services are available. Flat rate disposal. Our team will arrange the specifics, you only need their private details. Additional info provided via PM": (
        "Services de tueurs dispo. Forfait liquidaton. Notre equipe gere les details, il te faut juste leurs infos privees. Suite en MP"
    ),
    "I can help you get one step closer to eliminating your enemy. Pay me to dox their details.": (
        "Je peux t'aider a te rapprocher d'eliminer ton ennemi. Paie-moi pour doxer ses infos."
    ),
    "I have [SITE]. No negotiating. Ping Me": "J'ai [SITE]. Pas de nego. Pingue-moi",
    "I need [VIDEO]. 1st come 1st serve. I have money": (
        "J'ai besoin de [VIDEO]. Premier arrive, premier servi. J'ai du fric"
    ),
    "I need a link for a site named [SITE]. I'll pay hella DOSCoin!": (
        "J'ai besoin d'un lien pour un site nomme [SITE]. Je paie un max de DOSCoin !"
    ),
    "I need a video file named [VIDEO]. I'll pay hella DOSCoin!": (
        "J'ai besoin d'un fichier video nomme [VIDEO]. Je paie un max de DOSCoin !"
    ),
    "I'm selling hacking services to any who contact me. All rates shown via private message. Tier 1 hacker.": (
        "Je vends des services de hack a qui me contacte. Tarifs en message prive. Hacker tier 1."
    ),
    "I'm selling hacking services to any who contact me. All rates shown via private message. Tier 2 hacker.": (
        "Je vends des services de hack a qui me contacte. Tarifs en message prive. Hacker tier 2."
    ),
    "I'm selling hacking services to any who contact me. All rates shown via private message. Tier 3 hacker.": (
        "Je vends des services de hack a qui me contacte. Tarifs en message prive. Hacker tier 3."
    ),
    "I've been holding off on sharing [SITE] with the rest of you fucks, but now seems like the right time to reveal. If you think you're ready then ping me.": (
        "J'ai garde [SITE] pour moi face a vous les enfoires, mais c'est le moment de reveler. Si t'es pret, pingue-moi."
    ),
    "If anyone can find [SITE] on the dark net net ping me and I'll pay for the URL": (
        "Si quelqu'un trouve [SITE] sur le dark net, pingue-moi et je paie l'URL"
    ),
    "If anyone can find [VIDEO] on the dark net net ping me and I'll pay for the file": (
        "Si quelqu'un trouve [VIDEO] sur le dark net, pingue-moi et je paie le fichier"
    ),
    "If you're in need of key decryption services I am who you seek. There are a number of encryption methods I can work with. Message me to learn if my services are of use to you.": (
        "Si tu as besoin de dechiffrement de cles, c'est moi qu'il te faut. Je gere plusieurs methodes. "
        "Ecris-moi pour savoir si je peux t'aider."
    ),
    "If you're looking for [SITE] I'm the guy who's got what you need.": (
        "Si tu cherches [SITE], c'est moi qui ai ce qu'il te faut."
    ),
    "Interrupt and steal money from Game players via my hacking services. Tier 1 hacker. Rates shown after ping.": (
        "Interromps et vole l'argent des joueurs de The Game via mes hacks. Hacker tier 1. Tarifs apres ping."
    ),
    "Interrupt and steal money from Game players via my hacking services. Tier 2 hacker. Rates shown after ping.": (
        "Interromps et vole l'argent des joueurs de The Game via mes hacks. Hacker tier 2. Tarifs apres ping."
    ),
    "Interrupt and steal money from Game players via my hacking services. Tier 3 hacker. Rates shown after ping.": (
        "Interromps et vole l'argent des joueurs de The Game via mes hacks. Hacker tier 3. Tarifs apres ping."
    ),
    "It's your lucky day [SITE] is up for grabs. You'd be an idiot if you didn't BUY NOW!": (
        "C'est ton jour de chance, [SITE] est dispo. T'es un idiot si tu n'ACHETES PAS MAINTENANT !"
    ),
    "Key decryption services available. Connect and quickly reveal that which lies locked behind encryption. Fair prices. Superior Service. Ping now!": (
        "Services de dechiffrement de cles dispo. Connecte-toi et revele vite ce qui est verrouille. Prix justes. Service top. Ping maintenant !"
    ),
    "Lab grade at street prices. Potent to the point you'll never forget who sold to you. Ping to reveal drug inventory": (
        "Qualite labo a prix de rue. Assez fort pour jamais oublier qui t'a vendu. Ping pour voir le stock"
    ),
    "Leap over your competition by killing them dead, so you can get ahead. Hitmen can be hired for less than you think. More details provided in private": (
        "Depasse la concurrence en les tuant pour de vrai. Des tueurs pour moins cher que tu crois. Details en prive"
    ),
    "Looking for [SITE]. The one that's live now. big money up for grabs": (
        "Je cherche [SITE]. Celui qui est en ligne maintenant. Gros fric a la cle"
    ),
    "Looking for [VIDEO]. The full one. big money up for grabs": (
        "Je cherche [VIDEO]. La version complete. Gros fric a la cle"
    ),
    "Looking to hack someone? Connect with me to make that happen. Tier 1 hacker.": (
        "Envie de hacker quelqu'un ? Connecte-toi avec moi. Hacker tier 1."
    ),
    "Looking to hack someone? Connect with me to make that happen. Tier 2 hacker.": (
        "Envie de hacker quelqu'un ? Connecte-toi avec moi. Hacker tier 2."
    ),
    "Looking to hack someone? Connect with me to make that happen. Tier 3 hacker.": (
        "Envie de hacker quelqu'un ? Connecte-toi avec moi. Hacker tier 3."
    ),
    "Multi-algorithm decryption service. Message to validate key hash and its encryption algorithm with the service's tools.": (
        "Service de dechiffrement multi-algo. Ecris pour valider le hash et son algo avec mes outils."
    ),
    "My suite of decryption tools are ready to be put to use. Simply share your key hash with me and I'll perform all the necessary steps to reveal its original form. Prices vary depending on key index. Contact for more info": (
        "Ma suite d'outils de dechiffrement est prete. Envoie-moi ton hash de cle et je fais le necessaire pour reveler la forme d'origine. "
        "Prix selon l'index de cle. Contacte pour plus d'infos"
    ),
    "My suite of decryption tools are ready to be put to use. Simply share your key hash with me and I'll perform all the necessary steps to reveal its original form. Prices vary depending on key index. Contact for more info\"": (
        "Ma suite d'outils de dechiffrement est prete. Envoie-moi ton hash de cle et je fais le necessaire pour reveler la forme d'origine. "
        "Prix selon l'index de cle. Contacte pour plus d'infos\""
    ),
    "Need to DOX Someone? Hit me up. ": "Besoin de DOXER quelqu'un ? MP-moi. ",
    "Offering hacking services. Tier 1 hacker. Fairly priced.": (
        "Services de hack. Hacker tier 1. Prix corrects."
    ),
    "Offering hacking services. Tier 2 hacker. Fairly priced.": (
        "Services de hack. Hacker tier 2. Prix corrects."
    ),
    "Offering hacking services. Tier 3 hacker. Fairly priced.": (
        "Services de hack. Hacker tier 3. Prix corrects."
    ),
    "Out there in need of [SITE]? Well I got the shit you need. Hit the ping, to get it.": (
        "Besoin de [SITE] ? J'ai ce qu'il te faut. Pingue pour l'avoir."
    ),
    "Professional doxxing for sale. Connect to reveal rates.": (
        "Dox professionnel a vendre. Connecte pour voir les tarifs."
    ),
    "Professional hacker offering services. Ping me to hack any player of The Game. Tier 1 hacker.": (
        "Hacker pro. Pingue-moi pour hacker n'importe quel joueur de The Game. Tier 1."
    ),
    "Professional hacker offering services. Ping me to hack any player of The Game. Tier 2 hacker.": (
        "Hacker pro. Pingue-moi pour hacker n'importe quel joueur de The Game. Tier 2."
    ),
    "Professional hacker offering services. Ping me to hack any player of The Game. Tier 3 hacker.": (
        "Hacker pro. Pingue-moi pour hacker n'importe quel joueur de The Game. Tier 3."
    ),
    "Purest drugs on the market. Get what you need from a dealer who cares about his product. Ping for details": (
        "La drogue la plus pure du marche. Chez un dealer qui soigne son produit. Ping pour details"
    ),
    "Quality hacker with several options for sale. Tier 1 hacker. Ping for info.": (
        "Hacker de qualite, plusieurs options. Tier 1. Ping pour infos."
    ),
    "Quality hacker with several options for sale. Tier 2 hacker. Ping for info.": (
        "Hacker de qualite, plusieurs options. Tier 2. Ping pour infos."
    ),
    "Quality hacker with several options for sale. Tier 3 hacker. Ping for info.": (
        "Hacker de qualite, plusieurs options. Tier 3. Ping pour infos."
    ),
    "Quit letting them mess with you. Doxx your opps. Rates shared following ping.": (
        "Arrete de te laisser marcher dessus. Doxxe tes rivaux. Tarifs apres ping."
    ),
    "Reveal a key hashes' actual contents with my decryption expertise. Market rate prices. Speedy transactions. Multi-machine computing. Connect for additional details.": (
        "Revele le contenu reel d'un hash de cle avec mon expertise. Prix du marche. Transactions rapides. Multi-machines. Connecte pour details."
    ),
    "Rivals are only relevant when living. Eliminate them quickly with one of our hitmen. Service cost and specifics shared in private": (
        "Les rivaux ne comptent que vivants. Eliminez-les vite avec un de nos tueurs. Cout et details en prive"
    ),
    "SELLING [SITE] | QUICK REPLIES, HIGH REP, EXPERT SELLER": (
        "VENDS [SITE] | REPONSES RAPIDES, HAUTE REP, VENDEUR EXPERT"
    ),
    "Selling Doxing Services - Get your doxing services": (
        "Vends services de dox - Prenez vos services de dox"
    ),
    "Selling hitmen services. Contact me to broker a deal": (
        "Vends services de tueurs. Contacte-moi pour un deal"
    ),
    "Selling key decryption services to those in need. A number of key index values are valid with my work flow. Reach out privately to learn pricing and compatibility.": (
        "Vends du dechiffrement de cles. Plusieurs index sont compatibles avec mon process. Ecris en prive pour tarifs et compatibilite."
    ),
    "Sick of searching for [SITE]. Willing to purchase the URL from someone. If I check it and it's not legit you DONT get paid.": (
        "Marre de chercher [SITE]. Pret a acheter l'URL. Si je verifie et c'est pas legit, tu es PAS paye."
    ),
    "Sick of searching for [VIDEO]. Willing to purchase it from someone. If I check it and it's not legit you DONT get paid.": (
        "Marre de chercher [VIDEO]. Pret a l'acheter. Si je verifie et c'est pas legit, tu es PAS paye."
    ),
    "Some problems have only one answer. Allow our professionally trained killers to take care of them permanently. Ping for more information.": (
        "Certains problemes n'ont qu'une reponse. Laissez nos tueurs pro s'en charger pour de bon. Ping pour plus d'infos."
    ),
    "Take your dark net adventure to the next level by accessing [SITE]. I'm waiting for your call.": (
        "Passe au niveau superieur sur le dark net avec [SITE]. J'attends ton appel."
    ),
    "There's way more dark net to explore! [SITE] has plenty to reveal. Ping me to get it.": (
        "Y a bien plus de dark net a explorer ! [SITE] a plein a reveler. Pingue-moi pour l'avoir."
    ),
    "Tier 3 hacker for hire. Fair rates. More details shared after ping.": (
        "Hacker tier 3 a louer. Tarifs justes. Details apres ping."
    ),
    "Various decryption strategies ready to execute. Supply key hash for service approval, then pay presented price to commence decryption.": (
        "Plusieurs strategies de dechiffrement pretes. Envoie le hash pour validation, puis paie le prix affiche pour lancer le dechiffrement."
    ),
    "Vast connected network of hitmen able to deploy at a rapid rate. Share the required personal information and an expert will be sent to execute. Additional specifics sent through PM": (
        "Vaste reseau de tueurs deployables vite. Envoie les infos perso requises et un expert part en mission. Details en MP"
    ),
    "Want some good shit? Looking is free, getting drugs delivered is gonna cost ya. Ping for the hook up": (
        "Envie de bon matos ? Regarder c'est gratuit, la livraison ca coute. Ping pour le contact"
    ),
        "You know what makes life more fun? Drugs. Buy some off me. Ping to see what I got": (
        "Tu sais ce qui rend la vie plus drole ? La drogue. Achete chez moi. Ping pour voir mon stock"
    ),
    "[SITE] information up for sale. Competitive price, ping for more details.": (
        "Infos [SITE] a vendre. Prix competitif, ping pour details."
    ),
    "[SITE] secret info for sale | this won't be around forever | act quick if you want to succeed |Ping me.": (
        "Infos secretes [SITE] a vendre | ca durera pas | agis vite si tu veux reussir |Pingue-moi."
    ),
    "are you a little druggie fiending for another hit? ping me. I deliver": (
        "t'es un petit drogue en manque d'une autre dose ? pingue-moi. Je livre"
    ),
    "first to send me a WORKING copy of [VIDEO] gets paid": (
        "le premier a m'envoyer une copie QUI MARCHE de [VIDEO] est paye"
    ),
    "first to share a WORKING link to [SITE] gets paid": (
        "le premier a partager un lien QUI MARCHE vers [SITE] est paye"
    ),
    "hello, I am in need of a link to a site called [SITE] RIGHT NOW! EZ money": (
        "salut, j'ai besoin d'un lien vers un site appele [SITE] TOUT DE SUITE ! argent facile"
    ),
    "hello, I am in need of a video called [VIDEO] RIGHT NOW! EZ money": (
        "salut, j'ai besoin d'une video appelee [VIDEO] TOUT DE SUITE ! argent facile"
    ),
    "hey anyone got a video file named [VIDEO]. Please.": (
        "hey quelqu'un a un fichier video nomme [VIDEO]. S'il vous plait."
    ),
    "hey anyone got a website URL for a site named [SITE]. Please": (
        "hey quelqu'un a une URL pour un site nomme [SITE]. S'il vous plait"
    ),
    "hey anyone got a website URL for a site named [SITE]. Please.": (
        "hey quelqu'un a une URL pour un site nomme [SITE]. S'il vous plait."
    ),
    "hook me up with a link to the live website [SITE] RIGHT NOW! mega DOSCoin available": (
        "file-moi un lien vers le site live [SITE] TOUT DE SUITE ! gros DOSCoin dispo"
    ),
    "hook me up with a video by the name of [VIDEO] RIGHT NOW! mega DOSCoin available": (
        "file-moi une video nommee [VIDEO] TOUT DE SUITE ! gros DOSCoin dispo"
    ),
    "looking 4 [SITE]. Has to be the active version of the site. I have a way to validate all URLs. After I'm sure it's real you'll receive a reward": (
        "cherche [SITE]. Doit etre la version active. J'ai un moyen de valider les URL. Une fois sur que c'est vrai, tu auras une recompense"
    ),
    "looking 4 [VIDEO]. Has to be the original. I have a way to validate, after I'm sure it's real you'll receive a reward": (
        "cherche [VIDEO]. Doit etre l'original. J'ai un moyen de valider ; une fois sur, tu auras une recompense"
    ),
    "my browser crashed before I could connect to [SITE] and now I can't find it anywhere. Will pay anyone who has a URL to share": (
        "mon navigateur a plante avant que je joigne [SITE] et je le retrouve nulle part. Je paie qui a une URL"
    ),
    "my browser crashed before I could finish downloading [VIDEO] and now I can't get it. Will pay anyone who has a copy": (
        "mon navigateur a plante avant la fin du telechargement de [VIDEO] et je l'ai plus. Je paie qui a une copie"
    ),
    "please send me the URL of [SITE], pretty please. After I connect myself and am sure this is precisely what I'm looking for you will be compensated": (
        "envoie-moi l'URL de [SITE], s'il te plait. Apres connexion et verification que c'est bien ca, tu seras paye"
    ),
    "please send me the file of [VIDEO] in full. After I screen it myself to confirm you will be compensated": (
        "envoie-moi le fichier [VIDEO] en entier. Apres verif de mon cote, tu seras paye"
    ),
    "someone PLEASE send me a copy of [VIDEO]. PLEASE. I respond in seconds and have my payment info ready": (
        "quelqu'un s'il VOUS PLAIT envoyez-moi une copie de [VIDEO]. SVP. Je reponds en secondes, paiement pret"
    ),
    "someone PLEASE send me a direct link to [SITE]. PLEASE. I respond in seconds and have my payment info ready": (
        "quelqu'un s'il VOUS PLAIT envoyez-moi un lien direct vers [SITE]. SVP. Je reponds en secondes, paiement pret"
    ),
    "surely there's someone out here that already has [VIDEO]. Pop that fucker over through chat and I'll pay ya back": (
        "y a forcement quelqu'un qui a deja [VIDEO]. Balance ce putain de fichier en chat et je te paie"
    ),
    "surely there's someone out here who already visited [SITE] on the dark net. Pop that URL fucker over through chat and I'll pay ya back": (
        "y a forcement quelqu'un qui a deja visite [SITE] sur le dark net. Balance cette putain d'URL en chat et je te paie"
    ),
    "want to escape, drift away for a bit, or just take the edge off? Ping me I have the drugs you need": (
        "envie de t'evader, flotter un peu, ou juste detendre ? Pingue-moi j'ai la drogue qu'il te faut"
    ),
    "would anyone be so kind as to send [VIDEO] my way? I have money to share for the one who does!": (
        "quelqu'un aurait la gentillesse de m'envoyer [VIDEO] ? J'ai du fric pour celui qui le fait !"
    ),
    "would anyone be so kind as to send a URL to [SITE] my way? I have money for the one who does!": (
        "quelqu'un aurait la gentillesse de m'envoyer une URL vers [SITE] ? J'ai du fric pour celui qui le fait !"
    ),
}


def deaccent_keep_placeholders(s: str) -> str:
    """Normalize FR accents to ASCII while keeping [PLACEHOLDERS]."""
    table = str.maketrans(
        {
            "à": "a",
            "â": "a",
            "ä": "a",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "î": "i",
            "ï": "i",
            "ô": "o",
            "ö": "o",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ç": "c",
            "À": "A",
            "Â": "A",
            "É": "E",
            "È": "E",
            "Ê": "E",
            "Î": "I",
            "Ô": "O",
            "Ù": "U",
            "Ç": "C",
            "œ": "oe",
            "Œ": "OE",
        }
    )
    return s.translate(table)


def load_chunk_maps() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted(WORK.glob("acrs_fr_chunk_*.json")):
        out.update(json.loads(p.read_text(encoding="utf-8")))
    return out


def main() -> None:
    en_all = json.loads((WORK / "acrs_cryptchat_en_strings.json").read_text(encoding="utf-8"))["strings"]
    merged = dict(UI)
    merged.update(STATUS)
    merged.update(load_chunk_maps())

    fr_map: dict[str, str] = {}
    missing: list[str] = []
    for en in en_all:
        if en in RAW:
            continue
        if en in merged:
            fr_map[en] = deaccent_keep_placeholders(merged[en])
        else:
            missing.append(en)

    out = WORK / "acrs_cryptchat_fr.json"
    out.write_text(json.dumps(fr_map, ensure_ascii=False, indent=1), encoding="utf-8")
    (WORK / "acrs_cryptchat_fr_missing.json").write_text(
        json.dumps(missing, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"wrote {out} entries={len(fr_map)} missing={len(missing)}")


if __name__ == "__main__":
    main()
