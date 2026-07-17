# -*- coding: utf-8 -*-
import csv
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "work" / "ui_fr.csv"

CHAT = {
    "Hello I am part of a pay-it-forward group, enabling users who are lacking funds to obtain the goods they desire. It doesn't cost any more than 10 DOS Coin to contribute. Can I count on you today to ma":
        "Salut, je fais partie d'un groupe d'entraide qui aide ceux sans fonds à obtenir ce qu'ils veulent. Ça ne coûte pas plus de 10 DOS Coin. Je peux compter sur toi aujourd'hui ?",
    "the feds are closing in on me so I'm giving away the shit I have before they seize it all. You are promised to get something worth at least 300 DOS Coin if you contribute 50 to my offshore legal fund.":
        "Les feds me collent aux basques, je brade tout avant la saisie. Tu es assuré d'avoir au moins 300 DOS Coin de valeur si tu verses 50 à mon fonds juridique offshore.",
    "!!!!---!!!! MONEY MAKING OPPORTUNITY !!!!---!!!! A SMALL INVESTMENT OF 500 DOS Coin CAN EARN YOU 200% RETURNS IN ONLY 10 MINUTES!!!! CONTACT FOR ADDITIONAL DETAILS":
        "!!!!---!!!! OPPORTUNITÉ DE FRIC !!!!---!!!! UN PETIT INVESTISSEMENT DE 500 DOS Coin PEUT TE RAPPORTER 200% EN 10 MINUTES!!!! CONTACTE POUR PLUS DE DÉTAILS",
    "Requesting participants for our computer based survey system. Simply download our software and run it, then copy and paste the results in our private chat. Free to join, Payment of 50 DOS Coin on comp":
        "On cherche des participants pour notre enquête ordi. Télécharge le soft, lance-le, colle les résultats en MP. Gratuit, paiement 50 DOS Coin à la fin.",
    "$$$ GET YOUR $$$ MONEY UP $$$ 150% CASH BACK ON PURCHASE REAL $$$ MINIMUM 400 DOS COIN $$$":
        "$$$ FAIS GONFLER TON FRIC $$$ 150% CASHBACK SUR ACHAT RÉEL $$$ MINIMUM 400 DOS COIN $$$",
    "!!!! MYSTERY BOX GIVEAWAY ALERT !!!! Tickets to join the giveaway cost only 20 DOS Coin / Ticket. !!!! MYSTERY BOX GIVEAWAY ALERT !!!!":
        "!!!! ALERTE MYSTERY BOX !!!! Les tickets coûtent seulement 20 DOS Coin. !!!! ALERTE MYSTERY BOX !!!!",
    "$$$$ EZ MONEY $$$$ SEND 20 DOS Coin -> WAIT ... -> GET 50 DOS Coin. SIMPLE. GO NOW!":
        "$$$$ FRIC FACILE $$$$ ENVOIE 20 DOS Coin -> ATTENDS ... -> REÇOIS 50 DOS Coin. SIMPLE. GO!",
    "I joined this chat because a friend told me it was filled with people selling fucked up stuff, but apparently I need DOS Coin to buy anything?":
        "J'ai rejoint ce chat parce qu'un pote m'a dit que ça vendait de la merde chelou, mais il faut des DOS Coin pour acheter quoi que ce soit ?",
    "hey im trying to impress this girl in another chat. can somebody here let me borrow 1000 DOS Coin? ill give it back after. she just thinks i have a lot of money cause i told her that. im serious":
        "hey j'essaie d'impressionner une meuf dans un autre chat. quelqu'un peut me prêter 1000 DOS Coin ? je rembourse après. elle croit que je suis riche parce que je lui ai dit. sérieux",
    "LAST CHANCE! Roll the dice by entering to win 3000 DOS Coin! Be the 36th participant to win! One entry per user. 50 DOS Coin to enter.":
        "DERNIÈRE CHANCE! Tente de gagner 3000 DOS Coin! Sois le 36e participant! Une inscription / user. 50 DOS Coin pour entrer.",
    "GET    REP    QUICK    WITH     REPMAXX.EXE     THIS PROGRAM HOOKS INTO THE BACKEND OF ANY CHAT ROOM AND ALLOWS YOU TO CHANGE THE NUMBERS TO WHATEVER YOU WANT. NEED 100 REP? TYPE IT IN AND CLICK ONE B":
        "BOOSTE TA REP AVEC REPMAXX.EXE — LE PROGRAMME SE BRANCHE AU BACKEND DE N'IMPORTE QUEL CHAT ET CHANGE LES CHIFFRES COMME TU VEUX. BESOIN DE 100 REP? TAPE ET CLIQUE",
    "LAST WEEK I GAVE ONE OF YOU 50000 DOS COIN TO SEE WHAT WOULD HAPPEN. WELL TONIGHT IM UPPING THOSE NUMBERS TO 100000 DOS COIN! DETAILS WILL BE SUPPLIED THROUGH PRIVATE MESSAGE. DO NOT DELAY.":
        "LA SEMAINE DERNIÈRE J'AI DONNÉ 50000 DOS COIN À L'UN D'ENTRE VOUS. CE SOIR JE PASSE À 100000 DOS COIN! DÉTAILS EN MP. NE TARDEZ PAS.",
    "Secure a DOS Coin loan in seconds. A small fee to confirm the funds can transfer our ONLY requirement.":
        "Obtiens un prêt en DOS Coin en quelques secondes. Un petit frais pour confirmer le transfert est NOTRE SEULE exigence.",
}

rows = []
with p.open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        src = row["source"]
        # match by prefix for truncated sources
        for en, fr in CHAT.items():
            if src == en or (len(src) > 40 and en.startswith(src[:40])):
                row["translation"] = fr
                row["notes"] = "translated_chat_P1"
                break
        rows.append(row)

with p.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["key", "source", "translation", "priority", "notes"])
    w.writeheader()
    w.writerows(rows)

print("updated", sum(1 for r in rows if r["notes"] == "translated_chat_P1"))
