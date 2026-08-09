# Sous-titres des cinématiques (composant optionnel)

Le jeu n'a **aucun** système de sous-titres : les voix de Wade, du propriétaire
et des poursuivants ne sont accompagnées d'aucun texte. Ce composant les
affiche, en français, sans toucher au moindre asset.

Il est indépendant du pak `FR_P` : c'est un mod Lua UE4SS et des fichiers
`.srt`. Une mise à jour Steam ne le casse pas — il n'y a rien à recuire.

| | |
|---|---|
| Emplacement | `release/subtitles_runtime/ue4ss_core/` |
| Couverture | 28 fichiers, 120 répliques |
| Voix | Wade (intro motel, 2 fins), le propriétaire, Cletus, Lucas, Myra, Tanner, Tucker, le Breather |
| Poids | ~80 Ko |

## Installation

Le contenu de `ue4ss_core/` va dans `WTTGSD\Binaries\Win64\ue4ss\`, à côté du
proxy `dwmapi.dll` d'UE4SS (non redistribué ici : `.gitignore` exclut `*.dll`).
Le fichier `enabled.txt` suffit à activer le mod, sans toucher `mods.txt`.

## Pourquoi pas un patch d'asset

Trois verrous, vérifiés un par un :

1. Le jeu n'a pas de système de sous-titres à alimenter.
2. Les paquets sont en sérialisation *unversioned* : la propriété `Subtitles`
   d'un `SoundWave` étant vide, elle n'est pas sérialisée, et l'ajouter
   demanderait de reconstruire l'en-tête avec le schéma exact de `USoundWave`.
3. `UEngine::bSubtitlesEnabled` est `transient` : ni `.ini` ni asset ne
   l'active.

D'où UE4SS, qui exécute du code et lève les trois d'un coup.

## Comment le mod fonctionne

- **Détection.** `NotifyOnNewObject("/Script/Engine.AudioComponent")` : le nom
  du son est lu **dès la création** du composant, et ceux qui portent une piste
  sont gardés à vue jusqu'à leur départ.
- **Affichage.** Un widget UMG bâti à l'exécution
  (`WidgetBlueprintLibrary:Create`, puis `WidgetTree` / `CanvasPanel` /
  `TextBlock`), ancré en bas de l'écran.
- **Minutage.** Horloge audio du moteur (`GetAudioTimeSeconds`), avec repli sur
  un compteur de boucle. La pause fige le sous-titre ; couper une scène
  l'efface.

Ajouter une voix ne demande que de déposer un `.srt` nommé d'après le
`SoundWave` : le script lit le dossier au démarrage.

## Pièges rencontrés, pour éviter de les repayer

- **Les HUD Blueprints n'implémentent pas `ReceiveDrawHUD`.** Le hook
  s'enregistre mais n'est jamais appelé, même quand un `AHUD` existe. Tout
  l'affichage du jeu passe par UMG : `AHUD:DrawText` est une impasse.
- **Le nom vu à l'exécution n'est pas celui du `SoundWave`.** L'intro passe par
  un MetaSound : on voit `MS_WadeIntro`, jamais `Wade_MotelIntro-Full`. Idem
  pour l'appartement (`MS_FinalNotice`, `MS_SimonA`…).
- **Le composant naît bien avant de jouer.** Celui de Wade appartient à
  `BP_WadeCinema` : il est créé au chargement du motel et ne démarre que deux
  minutes plus tard.
- **Un composant se déclare « en lecture » longtemps après la fin du son** —
  37 secondes observées pour une réplique d'une seconde. Une piste doit donc se
  terminer quand son texte est épuisé, pas quand le composant se tait.
- **Trois plantages, tous muets au journal**, diagnostiqués par
  `%LOCALAPPDATA%\WTTGSD\Saved\Crashes\*\CrashContext.runtime-xml` : appeler une
  UFunction hors du fil du jeu, passer une chaîne Lua là où un `FText` est
  attendu, et balayer tous les `AudioComponent` à chaque tour. `pcall` n'en
  rattrape aucun : ce sont des violations d'accès natives, pas des erreurs Lua.

## Signature `StaticConstructObject`

UE4SS résout huit repères sur neuf sur ce binaire et abandonne sur
`StaticConstructObject_Internal` (`Fatal Error: PS scan timed out`). La
signature fournie ici comble le trou.

**Elle diffère volontairement de celle d'`azerty_runtime`.** Sur le build Steam
`24463842`, la variante à jokers
(`4C 8B DC 55 53 41 56 49 8D AB ?? ?? ?? ?? …`) donne **24 correspondances**
dans `WTTGSD-Win64-Shipping.exe` ; UE4SS retient la première, qui se trouve être
la bonne — mais rien ne le garantit après une mise à jour. La variante
littérale utilisée ici n'en donne **qu'une**, au décalage `0x15e57a0`.

À revalider après chaque mise à jour Steam : le décalage bougera, et la
correspondance doit rester unique.

## Cohabitation avec l'installeur

`install_fr_beginner.ps1` et `uninstall_fr_beginner.ps1` désactivaient
`dwmapi.dll` sans condition, pour nettoyer l'injecteur AZERTY retiré en v1.6.1.
Cela neutralisait **tout** mod UE4SS installé par le joueur. Ils ne le font
désormais que si la signature du vieil injecteur est présente — le dossier
`ue4ss\Mods\AzertyRemap`.
