# -*- coding: utf-8 -*-
"""Build French localization deliverables for WTTG3 (PDF + achievements + UI CSV)."""
from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path

from game_paths import ROOT, game_root

GAME = game_root()
PDF_SRC = ROOT / "backup" / "PDFS"
PDF_BUILD = ROOT / "build" / "pdfs"


ACH_TR = {
    "Debt Settled": ("Dettes réglées", "Terminer le jeu en difficulté Normal"),
    "God Gamer": ("God Gamer", "Terminer le jeu en difficulté 1337"),
    "Tanner’s Pet": ("Chouchou de Tanner", "Rester une heure dans la scène de crime de Tanner"),
    "Tanner's Pet": ("Chouchou de Tanner", "Rester une heure dans la scène de crime de Tanner"),
    "Tanner’s Good Girl": (
        "Bonne fille de Tanner",
        "Rester 10 heures cumulées dans la scène de crime de Tanner",
    ),
    "Tanner's Good Girl": (
        "Bonne fille de Tanner",
        "Rester 10 heures cumulées dans la scène de crime de Tanner",
    ),
    "Bad Breath": ("Mauvaise haleine", "Tu l'as cherché"),
    "Ronald’s Approval": ("Approbation de Ronald", "Terminer le tutoriel"),
    "Ronald's Approval": ("Approbation de Ronald", "Terminer le tutoriel"),
    "Ronald’s Vengeance": ("Vengeance de Ronald", "Agacer Ronald"),
    "Ronald's Vengeance": ("Vengeance de Ronald", "Agacer Ronald"),
    "Juiced": ("Juiced", "Obtenir le jackpot maximum sur Merramun"),
    "Bad Luck": ("Pas de chance", "Subir une perte maximale sur Merramun"),
    "Agent 67": (
        "Agent 67",
        "Éliminer tous les autres joueurs via services de hitman en une seule partie",
    ),
    "Stacked": ("Stacked", "Contrer 100 hacks Stack Pusher"),
    "QWERTY": ("QWERTY", "Contrer 100 hacks KernalCompiler"),
    " Fast Fingers": (" Doigts rapides", "Contrer 100 hacks MEMDeallacator"),
    "Fast Fingers": ("Doigts rapides", "Contrer 100 hacks MEMDeallacator"),
    "You Are Human": ("Tu es humain", "Contrer 100 hacks TOKEN9"),
    "Stick Shift": ("Stick Shift", "Contrer 100 hacks ShiftSeq"),
    "Breacher": ("Breacher", "Pirater 50 machines virtuelles"),
    "Movie Night": ("Soirée cinéma", "Vendre 50 vidéos DarkNet"),
    "Shopping Spree": (
        "Folle journée shopping",
        "Acheter tous les objets DarkDrop en une seule partie",
    ),
    "Blackhat": (
        "Blackhat",
        "Ne perdre aucun hack dans une partie sans utiliser de NOPSleds",
    ),
    "NOPE": ("NOPE", "Utiliser 50 NOP Sleds"),
    "JESTER": ("JESTER", "Se faire tuer par Lucas d'une certaine façon"),
    "Good Boy": ("Bon garçon", "Lui obéir 10 fois"),
    "Heisenberg": ("Heisenberg", "Acheter 250 Krystal Kings"),
    "Cardiac Arrest": ("Arrêt cardiaque", "Pousser jusqu'à la limite"),
    "Track Star": (
        "As de la course",
        "Fuir le Breather jusqu'en sécurité sans aide supplémentaire",
    ),
    "Paranoid": (
        "Parano",
        "Avoir 4 détecteurs de mouvement et 4 Go Cams tout en possédant des AID Pods",
    ),
    "Yoink": ("Yoink", "Voler 5 000 DOS aux autres joueurs dans The Game"),
}


UI_TR = {
    "Enter Desk": "S'asseoir au bureau",
    "[TAB] Inventory": "[TAB] Inventaire",
    "[SHIFT] Run": "[SHIFT] Courir",
    "[W,A,S,D] Move": "[Z,Q,S,D] Se déplacer",
    "Yes": "Oui",
    "No": "Non",
    "Cancel": "Annuler",
    "Start": "Démarrer",
    "Play": "Jouer",
    "Settings": "Paramètres",
    "Close": "Fermer",
    "Apply": "Appliquer",
    "Exit": "Quitter",
    "Next": "Suivant",
    "Confirm": "Confirmer",
    "Take": "Prendre",
    "Accept": "Accepter",
    "Submit": "Envoyer",
    "Options": "Options",
    "Disconnect": "Déconnecter",
    "Continue": "Continuer",
    "Connect": "Connecter",
    "Back": "Retour",
    "Run": "Courir",
    "Retry": "Réessayer",
    "Skip": "Passer",
    "Hide": "Se cacher",
    "Pause": "Pause",
    "Open": "Ouvrir",
    "Previous": "Précédent",
    "RESUME": "REPRENDRE",
    "Resume": "Reprendre",
    "Install": "Installer",
    "Decline": "Refuser",
    "Quit": "Quitter",
    "no": "non",
    "yes": "oui",
    "take": "prendre",
}


CHAT_TR = {
    "Hello I am part of a pay-it-forward group, enabling users who are lacking funds to obtain the goods they desire. It doesn't cost any more than 10 DOS Coin to contribute. Can I count on you today to ma": (
        "Salut, je fais partie d'un groupe d'entraide qui aide ceux qui manquent de fonds à obtenir ce qu'ils veulent. "
        "Ça ne coûte pas plus de 10 DOS Coin. Je peux compter sur toi aujourd'hui ?"
    ),
}


# Phrase replacements applied to PDF HTML (order matters: longer first).
PDF_REPLACEMENTS: list[tuple[str, str]] = [
    ("Details provided in accordance with fair play standard", "Détails fournis conformément au standard de fair-play"),
    ("Simulate a test hack by clicking the button at the bottom.", "Simulez un hack test en cliquant sur le bouton en bas."),
    ("All Threats", "Toutes les menaces"),
    ("All Hacks", "Tous les hacks"),
    ("Quick links:", "Liens rapides :"),
    ("Breakdown", "Analyse"),
    ("Instructions", "Instructions"),
    ("SUBJECT: ", "SUJET : "),
    ("TEST HACK", "TESTER LE HACK"),
    ("The Kidnapper", "The Kidnapper"),
    ("The Breather", "The Breather"),
    # VirtMesh
    (
        "VirtMesh is your path onto the Dark Net. Hacking a computer here allows you to remotely access its Dark Net web browser application.",
        "VirtMesh est votre accès au Dark Net. Pirater un ordinateur ici permet d'accéder à distance à son navigateur Dark Net.",
    ),
    (
        "After opening VirtMesh a network web will expand before you.",
        "Après avoir ouvert VirtMesh, une toile réseau s'étend devant vous.",
    ),
    (
        "All unlocked nodes can be clicked <strong>[LMB]</strong> and hacked to gain remote access to another computer.",
        "Tous les nœuds déverrouillés peuvent être cliqués <strong>[Clic gauche]</strong> puis piratés pour obtenir un accès distant à un autre ordinateur.",
    ),
    (
        "Clicking HACK will open the INJ3KT-R tool.",
        "Cliquer sur HACK ouvre l'outil INJ3KT-R.",
    ),
    (
        "With INJ3KT-R you will be presented a flow grid like this:",
        "Avec INJ3KT-R, une grille de flux s'affiche comme ceci :",
    ),
    (
        "A successful INJ3KT-R injection requires a valid path from the marked start, on the top, to the marked goal, on the bottom.",
        "Une injection INJ3KT-R réussie exige un chemin valide du départ (en haut) jusqu'à l'objectif (en bas).",
    ),
    (
        "Each step along the path must <strong>alternate between tile colors</strong> and at some point must <strong>pass through every highlighted tile</strong> along the way.",
        "Chaque étape du chemin doit <strong>alterner les couleurs de tuiles</strong> et doit <strong>passer par chaque tuile surlignée</strong>.",
    ),
    (
        "Each tile can be clicked <strong>[LMB]</strong> to change its flow direction. Click the same tile multiple times to cycle through flow directions - Up, Right, Down, Left.",
        "Chaque tuile peut être cliquée <strong>[Clic gauche]</strong> pour changer la direction du flux. Cliquez plusieurs fois pour cycler : Haut, Droite, Bas, Gauche.",
    ),
    (
        "<strong>NOTE: Mistakes in your created path will cause failure, however you're only temporarily locked out of the targeted computer.</strong>",
        "<strong>NOTE : Une erreur dans le chemin provoque un échec, mais vous n'êtes verrouillé que temporairement hors de l'ordinateur cible.</strong>",
    ),
    (
        "Once hacked clicking the computer again will offer options to <strong>MOUNT</strong> or <strong>MINE</strong>.",
        "Une fois piraté, recliquer sur l'ordinateur propose <strong>MONTER</strong> ou <strong>MINER</strong>.",
    ),
    (
        "MOUNT - Use for Dark Net web browsing - UNMOUNT will restore mounting token",
        "MONTER - Pour naviguer sur le Dark Net - DÉMONTER restaure le jeton de montage",
    ),
    (
        "MINE - Use to passively mine cryptocurrency - UNMINE does not return mining token",
        "MINER - Pour miner passivement de la crypto - ARRÊTER LE MINAGE ne rend pas le jeton",
    ),
    (
        "After clicking MOUNT a token is consumed and the short mounting process begins. Once complete you can click the now mounted computer again to ENTER and use it for browsing the Dark Net.",
        "Après MONTER, un jeton est consommé et le montage démarre. Ensuite, recliquez sur l'ordinateur monté pour ENTRER et naviguer sur le Dark Net.",
    ),
    (
        "Available mount and mine tokens can be seen in the top right",
        "Les jetons de montage et de minage disponibles sont visibles en haut à droite",
    ),
    (
        "<strong>NOTE: Mount multiple computers and swap between them routinely to avoid losing access to one by overstaying your connection.</strong>",
        "<strong>NOTE : Montez plusieurs ordinateurs et alternez régulièrement pour éviter de perdre l'accès en restant trop longtemps connecté.</strong>",
    ),
    (
        "While using a mounted computer you can return to your main desktop or VirtMesh using the bottom right taskbar buttons. Hovering over either will tell you their purpose.",
        "Sur un ordinateur monté, revenez au bureau principal ou à VirtMesh via les boutons de la barre des tâches en bas à droite. Survolez-les pour voir leur rôle.",
    ),
    (
        "<strong>NOTE: Switching to your main desktop does not disconnect you from a mounted computer.</strong>",
        "<strong>NOTE : Passer au bureau principal ne vous déconnecte pas d'un ordinateur monté.</strong>",
    ),
    (
        "If you want to exit VirtMesh completely click the central circle twice.",
        "Pour quitter VirtMesh complètement, cliquez deux fois sur le cercle central.",
    ),
    # Threats - Noir
    (
        "This couple appears seemingly out of thin air. Preferring the dark, they are often together and demand you follow their rules.",
        "Ce couple apparaît comme de nulle part. Ils préfèrent l'obscurité, restent souvent ensemble et exigent que vous suiviez leurs règles.",
    ),
    (
        "Their pose will decide your next move. If you see, from left to right, the shorter woman, then the taller man - Shine a flashlight at them for a moment and turn away completely, <strong>count exactly to 10</strong>, then immediately turn back around to where they previously were.",
        "Leur pose décide de votre prochain geste. De gauche à droite : la femme plus petite puis l'homme plus grand — allumez une lampe un instant, détournez-vous complètement, <strong>comptez exactement jusqu'à 10</strong>, puis regardez immédiatement l'endroit où ils étaient.",
    ),
    (
        "See, from left to right, the taller man, then the shorter woman - Do nearly the same as above, but <strong>count exactly to 5</strong>.",
        "De gauche à droite : l'homme plus grand puis la femme plus petite — même procédure, mais <strong>comptez exactement jusqu'à 5</strong>.",
    ),
    (
        "Observing prey is something they both individually enjoy. Find yourself alone with either one and you must follow similar rules, but no longer need to count exact.<strong> Once you're close by only look away.</strong> After waiting a moment they'll disappear.",
        "Observer leur proie les amuse chacun. Seul face à l'un d'eux, suivez des règles similaires sans compter exactement. <strong>Une fois près, détournez seulement le regard.</strong> Après un moment, ils disparaissent.",
    ),
    # Tanner
    (
        "You are to be his next victim, but be thankful he likes to play.",
        "Vous serez sa prochaine victime — remerciez le fait qu'il aime jouer.",
    ),
    (
        "Always secure the area you're in, because if there's an easy way to you he'll take it.",
        "Sécurisez toujours la zone : s'il existe un accès facile jusqu'à vous, il le prendra.",
    ),
    (
        "At times acknowledging his presence can be enough to ruin his fun. Use what you have around to look him in the eyes and remove any dreams of ambush he may have had.",
        "Parfois, reconnaître sa présence suffit à gâcher son plaisir. Utilisez ce que vous avez pour le regarder dans les yeux et briser toute idée d'embuscade.",
    ),
    (
        "Equipped at your desk is a panic button. Pressing it will lock the front sliding doors shut, stopping anyone from entering... that is if you hit the button in time.",
        "Un bouton de panique est installé à votre bureau. Il verrouille les portes coulissantes avant et empêche quiconque d'entrer… si vous appuyez à temps.",
    ),
    # Tucker
    (
        "One of Wade's boys who's been put on to take some swings at you. The thrill of the hunt gets him going, be that luring his prey to a trap or setting the place off to see a scramble for safety.",
        "Un des gars de Wade chargé de s'occuper de vous. Le frisson de la chasse l'excite : attirer sa proie dans un piège ou semer le chaos pour voir tout le monde fuir.",
    ),
    (
        "Listen close when heading out to do repairs, with your back turned there may be someone over your shoulder. Hear strange noise? It's best to stay still for a moment before carrying on.",
        "Écoutez bien en sortant faire des réparations : dos tourné, quelqu'un peut être derrière vous. Bruit bizarre ? Restez immobile un instant avant de continuer.",
    ),
    (
        "This boy isn't all quiet though, from time to time you may hear an old tune. When heard caution is out the window and time is ticking. Search the motel's lot to find a door with the Ace of Spades playing card, then enter.",
        "Il n'est pas toujours silencieux : parfois une vieille mélodie retentit. Alors plus de prudence lente — le temps presse. Cherchez sur le parking du motel une porte avec l'As de pique, puis entrez.",
    ),
    (
        "Make it inside before the night turns quiet again and you'll survive.",
        "Entrez avant que la nuit redevienne silencieuse et vous survivrez.",
    ),
    # Cletus
    (
        "Another of Wade's boys with an itch for a fix.",
        "Un autre des gars de Wade, accro à sa dose.",
    ),
    (
        "There's only one way to be on this tweaker's good side and it's giving him with what he craves most, meth.",
        "Une seule façon de rester dans ses bons papiers : lui donner ce qu'il crave le plus, de la meth.",
    ),
    (
        "Once you pickup don't worry about finding him, he'll sniff you out when he's hungry for another hit, just have it on ya.",
        "Une fois récupérée, ne cherchez pas à le trouver : il vous flairera quand il voudra une autre dose. Ayez-la sur vous.",
    ),
    # Lucas
    (
        "All players in The Game have an assigned hitman standing by, waiting for the call to kill them. This one is yours.",
        "Chaque joueur de The Game a un hitman assigné, prêt à tuer sur appel. Celui-ci est le vôtre.",
    ),
    (
        "You won't know when the hitman is called upon, so secure yourself before that time comes. A trained killer is stealthy, sticking to the shadows and staying silent in most cases, little will tell you he's closing in unless you prepare.",
        "Vous ne saurez pas quand le hitman est appelé : sécurisez-vous avant. Un tueur entraîné est furtif, reste dans l'ombre et silencieux ; peu d'indices annoncent son approche sans préparation.",
    ),
    (
        "If you've noticed him, disguise where you're playing from. Turn off lights, keep doors locked, and locate a place you can hide inside.",
        "S'il est repéré, masquez votre position de jeu. Éteignez les lumières, verrouillez les portes, trouvez une cachette intérieure.",
    ),
    (
        "That anxiety condition of yours will make staying silent a challenge.",
        "Votre anxiété rendra le silence difficile.",
    ),
    # Kidnapper
    (
        "This trained trafficker knows of your location and has been instructed to capture if the opportunity arises while he's parked nearby.",
        "Ce trafiquant entraîné connaît votre position et a pour ordre de vous capturer si l'occasion se présente pendant qu'il est garé à proximité.",
    ),
    (
        "Stealth is a priority of his, so keep your back doors locked. If heading outside take a good look at the surrounding street area for his white van. See it and you'll have to wait for him to drive off.",
        "La furtivité est sa priorité : gardez les portes arrière verrouillées. Dehors, scrutez la rue pour son van blanc. S'il est là, attendez qu'il reparte.",
    ),
    (
        "Using your eyes alone will often not be enough to spot his vehicle's position. Secure yourself early, or question every time you walk outdoors.",
        "Les yeux seuls ne suffisent souvent pas à le repérer. Sécurisez-vous tôt, ou méfiez-vous à chaque sortie.",
    ),
    # Breather
    (
        "A troubled manic man may wait around your dead drop package location.",
        "Un homme maniaque et troublé peut attendre près de votre dead drop.",
    ),
    (
        "If he appears run away, back towards an area with others. Their presence, even if only assumed, will be enough for him to give up chase.",
        "S'il apparaît, fuyez vers une zone avec d'autres personnes. Leur présence, même supposée, suffit à le faire abandonner.",
    ),
    # Hacks generic / K3RN3L
    (
        "K3RN3LC0MP1L3R is revered in the cybersecurity community as trusted tool to contain and remove corrupted memory blocks before damage is done to the host system.",
        "K3RN3LC0MP1L3R est respecté en cybersécurité comme outil fiable pour contenir et retirer des blocs mémoire corrompus avant qu'ils n'endommagent le système hôte.",
    ),
    (
        "With K3RN3LC0MP1L3R you will be presented a corrupted memory block with lines of text like this:",
        "Avec K3RN3LC0MP1L3R, un bloc mémoire corrompu s'affiche avec des lignes de texte comme ceci :",
    ),
    (
        "Countering an attack with K3RN3LC0MP1L3R requires you type the highlighted line of text exactly as it's shown, then press <strong>[ENTER]</strong>.",
        "Contrer une attaque avec K3RN3LC0MP1L3R exige de taper exactement la ligne surlignée, puis d'appuyer sur <strong>[ENTRÉE]</strong>.",
    ),
    (
        "Entering the text correctly will move onto the next line in the series if there is one. After submitting the last line you'll block the attack.",
        "Un texte correct passe à la ligne suivante s'il y en a une. Après la dernière ligne, l'attaque est bloquée.",
    ),
    (
        "Mistakes will highlight in red for both the active line and your typed input. Resolve them by removing the characters with <strong>[BACKSPACE]</strong>.",
        "Les erreurs s'affichent en rouge sur la ligne active et votre saisie. Corrigez avec <strong>[RETOUR ARRIÈRE]</strong>.",
    ),
    (
        "<strong>NOTE: More difficult versions of this hack exist, which require you to counter multiple corrupted memory blocks, type code strings instead of text, or counter many corrupted memory blocks of code strings.</strong>",
        "<strong>NOTE : Des versions plus difficiles existent : plusieurs blocs mémoire, chaînes de code au lieu de texte, ou de nombreux blocs de chaînes de code.</strong>",
    ),
    (
        " The total number of corrupted memory blocks to remove can be seen in the bottom left corner.",
        " Le nombre total de blocs mémoire à retirer est visible en bas à gauche.",
    ),
    (
        "memDEALLOCATER began as an open source project with the intention of countering memory injection attacks. Through community collaboration it's become a security tool used worldwide throughout all technology running A.D.O.S.",
        "memDEALLOCATER a commencé en open source pour contrer les injections mémoire. Grâce à la communauté, c'est devenu un outil de sécurité mondial sur toute techno sous A.D.O.S.",
    ),
    (
        "With memDEALLOCATER you will be presented a block of memory like this:",
        "Avec memDEALLOCATER, un bloc mémoire s'affiche comme ceci :",
    ),
    (
        "Using memDEALLOCATER correctly requires you avoid red sections of memory by directing to the left, right, or skip, one line at a time.",
        "Bien utiliser memDEALLOCATER : évitez les sections rouges en allant à gauche, à droite, ou en sautant, une ligne à la fois.",
    ),
    (
        "Starting at the bottom and moving up, focus on the green sections of memory to determine what sequence of keys to press. Every key press moves the memory block down one line and a new line appears at the top.",
        "Du bas vers le haut, concentrez-vous sur les sections vertes pour choisir les touches. Chaque touche fait descendre le bloc d'une ligne ; une nouvelle ligne apparaît en haut.",
    ),
    (
        "It's fastest to look at the upcoming lines, than react to what the key hint tells you to press.",
        "Le plus rapide : anticiper les lignes à venir plutôt que de réagir à l'indice de touche.",
    ),
    ("Left section green -> <strong> Left - [A] / [◀]</strong>", "Section gauche verte -> <strong> Gauche - [Q] / [◀]</strong>"),
    ("Both sections green -> <strong> Skip - [SPACEBAR]</strong>", "Les deux sections vertes -> <strong> Sauter - [ESPACE]</strong>"),
    ("Right section green -> <strong>Right - [D] / [▶]</strong>", "Section droite verte -> <strong>Droite - [D] / [▶]</strong>"),
    (
        "Pressing correct keys will progress the bar at the top to full. While incorrect actions will remove progress. When full the hack will be blocked.",
        "Les bonnes touches remplissent la barre du haut. Les erreurs retirent de la progression. Pleine = hack bloqué.",
    ),
    (
        "<strong>NOTE: More difficult versions of this hack exist, which remove the key hint below the memory block and have harsher penalties for pressing the wrong key.</strong>",
        "<strong>NOTE : Des versions plus difficiles retirent l'indice de touche et punissent plus fort les mauvaises touches.</strong>",
    ),
    (
        "shiftSEQ is an endpoint security system that detects, then dispatches malicious code payloads. A user's connected network is simplified into a series of nodes that can be quickly navigated and defended.",
        "shiftSEQ est un système de sécurité endpoint qui détecte puis neutralise des payloads. Le réseau connecté est simplifié en nœuds à naviguer et défendre rapidement.",
    ),
    (
        "With shiftSEQ you will be presented a node network like this:",
        "Avec shiftSEQ, un réseau de nœuds s'affiche comme ceci :",
    ),
    (
        "Stopping an attack using shiftSEQ requires you to remove all infected nodes by navigating to each one and destroying it through repeated actions.",
        "Arrêter une attaque avec shiftSEQ : éliminez tous les nœuds infectés en y naviguant et en les détruisant par actions répétées.",
    ),
    (
        "You always begin inside the home node. While inside infected node attacks are blocked.",
        "Vous commencez toujours dans le nœud home. Dedans, les attaques de nœuds infectés sont bloquées.",
    ),
    (
        "If you're outside the home node when an attack reaches it your connection health will decrease. This is the only way to fail early. You can move freely through node attacks without issue.",
        "Hors du nœud home, si une attaque l'atteint, votre santé de connexion baisse. C'est le seul échec précoce. Vous pouvez traverser librement les attaques de nœuds.",
    ),
    (
        "Navigate onto infected nodes using <strong>[W] / [A] / [S] / [D]</strong>, then destroy them using <strong>[SPACEBAR]</strong>.",
        "Naviguez vers les nœuds infectés avec <strong>[Z] / [Q] / [S] / [D]</strong>, puis détruisez-les avec <strong>[ESPACE]</strong>.",
    ),
    ("<strong>[W] - Up</strong>", "<strong>[Z] - Haut</strong>"),
    ("<strong>[A] - Left</strong>", "<strong>[Q] - Gauche</strong>"),
    ("<strong>[S] - Down</strong>", "<strong>[S] - Bas</strong>"),
    ("<strong>[D] - Right</strong>", "<strong>[D] - Droite</strong>"),
    (
        "<strong>[SPACEBAR] - Attack infected node / Active restore (while inside home node)</strong>",
        "<strong>[ESPACE] - Attaquer le nœud infecté / Restauration active (dans le nœud home)</strong>",
    ),
    (
        "Once on top of an infected node press <strong>[SPACEBAR]</strong> repeatedly to decrease its health to zero. However note that you have limited resources and must return to the home node to recharge.",
        "Sur un nœud infecté, appuyez sur <strong>[ESPACE]</strong> plusieurs fois pour le réduire à zéro. Ressources limitées : revenez au nœud home pour recharger.",
    ),
    (
        "<strong>NOTE: Resources are measured via the battery symbol in the bottom right.</strong>",
        "<strong>NOTE : Les ressources sont indiquées par le symbole batterie en bas à droite.</strong>",
    ),
    (
        "Quickly recharge to full by pressing <strong>[SPACEBAR]</strong> when the expanding pulse overlaps the solid outline of the home node. Incorrect timing will temporarily disable all recharging.",
        "Rechargez vite en appuyant sur <strong>[ESPACE]</strong> quand l'impulsion chevauche le contour du nœud home. Un mauvais timing désactive temporairement la recharge.",
    ),
    (
        "<strong>NOTE: More difficult versions of this hack exist, which have faster and more frequent infected node attacks, unblocked attacks have a greater penalty to connection health, and the amount of infected nodes to destroy is increased.</strong>",
        "<strong>NOTE : Versions plus difficiles : attaques plus rapides/fréquentes, pénalité plus forte hors home, plus de nœuds infectés.</strong>",
    ),
    # stackPUSHER
    (
        "stackPUSHER is a security tool used to prevent stack overflow attacks. Developed by computer science major Tyler Draven in 2015, it's risen to become a leading security tool.",
        "stackPUSHER est un outil de sécurité contre les stack overflows. Développé par Tyler Draven (info) en 2015, il est devenu une référence.",
    ),
    (
        "With stackPUSHER you will be presented a stack grid like this:",
        "Avec stackPUSHER, une grille de pile s'affiche comme ceci :",
    ),
    (
        "Defend against a stack overflow attack with stackPUSHER by pushing all stack nodes:",
        "Défendez-vous d'un stack overflow avec stackPUSHER en poussant tous les nœuds stack :",
    ),
    ("Into the popper node:", "Dans le nœud popper :"),
    (
        "Stack nodes can <strong>ONLY</strong> be moved when activated by the pusher node:",
        "Les nœuds stack ne peuvent être déplacés <strong>QUE</strong> quand le nœud pusher les active :",
    ),
    (
        "You can move the pusher node anywhere on the grid by clicking <strong>[LMB]</strong> on it to activate, then clicking again <strong>[LMB]</strong> to place it. The same goes for stack nodes, click to pick up, then click to place down.",
        "Déplacez le pusher n'importe où : <strong>[Clic gauche]</strong> pour l'activer, puis encore pour le placer. Idem pour les nœuds stack : clic pour prendre, clic pour poser.",
    ),
    (
        "<strong>NOTE: A stack node is limited to moving within a 3x3 matrix surrounding the pusher node, example below:</strong>",
        "<strong>NOTE : Un nœud stack ne se déplace que dans une matrice 3x3 autour du pusher, exemple ci-dessous :</strong>",
    ),
    (
        "Strategic placement of the pusher node will make the process smooth and linear. Here is a demonstration of a successful stackPUSHER solve.",
        "Un placement stratégique du pusher rend le processus fluide. Voici une démonstration d'une résolution réussie.",
    ),
    (
        "<strong>NOTE: Avoid placing any nodes atop laughing skulls within the grid. Doing so will result in an immediate failure.</strong>",
        "<strong>NOTE : Ne placez aucun nœud sur les crânes rieurs de la grille. Sinon, échec immédiat.</strong>",
    ),
    # TOKENINE
    (
        "The TOKENINE service actively listens for unauthorized network traffic. If found the user is notified to manually validate any unknowns, but ignoring the alert will block it automatically. Unfortunately a recent exploit has the service doing the opposite, demanding validation to stop unknown access.",
        "Le service TOKENINE écoute le trafic réseau non autorisé. S'il en trouve, l'utilisateur doit valider manuellement ; ignorer l'alerte le bloque automatiquement. Un exploit récent inverse ce comportement : la validation est exigée pour stopper l'accès inconnu.",
    ),
    (
        "With TOKENINE you will be presented an auth token and its potential parts like this:",
        "Avec TOKENINE, un jeton d'auth et ses pièces potentielles s'affichent comme ceci :",
    ),
    (
        "Stopping an attack using TOKENINE requires you assemble an auth token which matches the one shown by clicking <strong>[LMB]</strong> on each piece.",
        "Arrêter une attaque TOKENINE : assemblez un jeton d'auth identique en cliquant <strong>[Clic gauche]</strong> sur chaque pièce.",
    ),
    (
        "<strong>NOTE: You can see how many pieces it will take to create the auth token shown via the squares underneath it.</strong> E.g. Image below shows the auth token requires two pieces to create.",
        "<strong>NOTE : Le nombre de pièces nécessaires est indiqué par les carrés sous le jeton.</strong> Ex. : l'image ci-dessous montre un jeton en deux pièces.",
    ),
    (
        "Once you choose a token piece it cannot be removed. When checked your assembled token will be erased if it's incorrect.",
        "Une pièce choisie ne peut plus être retirée. À la vérification, un jeton incorrect est effacé.",
    ),
    (
        "A failed match will require another attempt. A success will move onto the next token in the series if there is one.",
        "Un échec demande une nouvelle tentative. Un succès passe au jeton suivant s'il y en a un.",
    ),
    (
        "<strong>NOTE: There's limited time between token piece selections, and failing to choose will cause failure. Always select something, even if it's wrong, to avoid early failure.</strong>",
        "<strong>NOTE : Temps limité entre les sélections ; ne rien choisir provoque un échec. Sélectionnez toujours quelque chose, même faux, pour éviter l'échec précoce.</strong>",
    ),
    (
        "<strong>NOTE: More difficult versions of this hack exist, which require a greater number of auth tokens to be put together, visual glitches distort the auth token you must copy, and copying a token requires more pieces to assemble.</strong>",
        "<strong>NOTE : Versions plus difficiles : plus de jetons à assembler, glitches visuels sur le jeton à copier, et plus de pièces par jeton.</strong>",
    ),
]


CONTESTANT_LABELS = [
    ("TARGETED USER SYSTEM BREACHED - ", "SYSTÈME UTILISATEUR CIBLE COMPROMIS - "),
    ("(collection completed in", "(collecte terminée en"),
    ("seconds)", "secondes)"),
    ("####-----LOG START-----####", "####-----DÉBUT DU LOG-----####"),
    ("PLAYER NAME: ", "PSEUDO JOUEUR : "),
    ("REAL NAME: ", "NOM RÉEL : "),
    ("LOCATION:", "POSITION :"),
    ("AGE:", "ÂGE :"),
    ("HAIR:", "CHEVEUX :"),
    ("EYES:", "YEUX :"),
    ("HEIGHT:", "TAILLE :"),
    ("WEIGHT:", "POIDS :"),
    ("PHONE #:", "TÉL :"),
    ("JOB:", "EMPLOI :"),
    ("MAC ADDRESS:", "ADRESSE MAC :"),
    ("IP ADDRESS:", "ADRESSE IP :"),
    ("ADDITIONAL INFO:", "INFOS SUPPLÉMENTAIRES :"),
]


def build_achievements() -> None:
    src = json.loads((ROOT / "source" / "achievements_en.json").read_text(encoding="utf-8"))
    out = []
    for a in src:
        dn = a["displayName"]
        name, desc = ACH_TR.get(dn, ACH_TR.get(dn.strip(), (dn, a["description"])))
        b = dict(a)
        b["displayName"] = name
        b["description"] = desc
        b["displayName_en"] = dn
        b["description_en"] = a["description"]
        out.append(b)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    (ROOT / "work" / "achievements_fr.json").write_text(text, encoding="utf-8")
    (ROOT / "build" / "achievements_fr.json").write_text(text, encoding="utf-8")
    print(f"achievements: {len(out)}")


def build_ui_csv() -> None:
    src = ROOT / "source" / "ui_game_en.csv"
    out = ROOT / "work" / "ui_fr.csv"
    rows = []
    if src.exists():
        with src.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                en = row.get("source", "")
                fr = UI_TR.get(en)
                if fr is None:
                    # chat / long spam: light adaptive translation markers
                    if "DOS Coin" in en or "DOS COIN" in en:
                        fr = en  # keep EN spam tone for now; mark for review
                        notes = "P1_review_chat_spam"
                    else:
                        fr = en
                        notes = "needs_review"
                else:
                    notes = "translated"
                rows.append(
                    {
                        "key": row.get("key", ""),
                        "source": en,
                        "translation": fr,
                        "priority": row.get("priority", ""),
                        "notes": notes,
                    }
                )
    # ensure core UI present
    known_keys = {r["source"] for r in rows}
    for en, fr in UI_TR.items():
        if en not in known_keys:
            rows.append(
                {
                    "key": "",
                    "source": en,
                    "translation": fr,
                    "priority": "P0",
                    "notes": "translated",
                }
            )
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["key", "source", "translation", "priority", "notes"])
        w.writeheader()
        w.writerows(rows)
    print(f"ui_fr rows: {len(rows)}")


def translate_html(text: str, extra: list[tuple[str, str]] | None = None) -> str:
    reps = list(PDF_REPLACEMENTS)
    if extra:
        reps.extend(extra)
    # longer first
    reps.sort(key=lambda x: len(x[0]), reverse=True)
    for a, b in reps:
        text = text.replace(a, b)
    text = text.replace('lang="en"', 'lang="fr"', 1)
    return text


def build_pdfs() -> None:
    if PDF_BUILD.exists():
        shutil.rmtree(PDF_BUILD)
    shutil.copytree(PDF_SRC, PDF_BUILD)
    count = 0
    for html in PDF_BUILD.rglob("*.html"):
        raw = html.read_text(encoding="utf-8", errors="replace")
        extra = CONTESTANT_LABELS if "Contestants" in str(html) else None
        html.write_text(translate_html(raw, extra), encoding="utf-8")
        count += 1
    print(f"pdf html translated: {count}")


def qa_placeholders() -> None:
    ui = ROOT / "work" / "ui_fr.csv"
    bad = []
    with ui.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            s, t = row["source"], row["translation"]
            for token in re.findall(r"\{[^}]+\}", s):
                if token not in t:
                    bad.append((row.get("key"), token, s[:60]))
    report = ROOT / "work" / "qa_placeholders.txt"
    report.write_text(
        "OK\n" if not bad else "\n".join(f"{k}|{tok}|{s}" for k, tok, s in bad),
        encoding="utf-8",
    )
    print(f"placeholder issues: {len(bad)}")


def main() -> None:
    build_achievements()
    build_ui_csv()
    build_pdfs()
    qa_placeholders()
    print("done")


if __name__ == "__main__":
    main()
