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

### Pack Full (recommande)
`INSTALLER.bat` propose **Activer les sous-titres cinematiques ? (O/N)** — desactive par defaut.
Repondre **O** deploie `SousTitresFR`. S’il n’y a pas d’UE4SS, le pack installe le runtime
(experimental-latest). S’il y en a déjà un (layout `ue4ss\`) : **merge** — DLL, settings et
autres mods conservés ; `mods.txt` reçoit `SousTitresFR : 1` ; signature
`StaticConstructObject` posée (backup `.bak-wttg3fr` si un fichier existait).
Le proxy `dwmapi` n’est copié que s’il est absent (un `.off` est réactivé).

### Manuel
Layout **nested** (obligatoire avec le proxy actuel) :

```
WTTGSD\Binaries\Win64\
  dwmapi.dll          ← proxy seulement
  ue4ss\
    UE4SS.dll
    UE4SS-settings.ini
    UE4SS_Signatures\StaticConstructObject.lua
    Mods\SousTitresFR\...
```

Rebuild local des DLL : `powershell -File scripts\build_subtitles_runtime.ps1`  
(necessite `tools\UE4SS` = **experimental-latest**, pas le zip v3.0.1 de fevrier 2024).

Le mod est liste dans `mods.txt` (`SousTitresFR : 1`) et a un `enabled.txt` non vide.

Nexus : pas d'injecteur dans le zip drop-in — utiliser le pack Full.

## Depannage (log qui ne bouge pas / F9 mort)

Si `ue4ss\UE4SS.log` ne se met pas a jour au lancement, **UE4SS ne s'injecte pas**.

Cause (assets 1.7.0 remplaces) : le `dwmapi.dll` / `UE4SS.dll` **v3.0.1 (fev 2024)** ne chargeait
plus correctement le layout `ue4ss\` sur ce jeu (chemin avec espaces). Contre-mesure :
**UE4SS experimental-latest** (proxy nested-aware, scan GUObjectArray OK sur UE5.6).

Controle rapide :

1. Fermer le jeu, supprimer `ue4ss\UE4SS.log`, relancer 20 s.
2. Le fichier doit reapparaitre avec `PS scan successful` puis `Starting Lua mod 'SousTitresFR'`.
3. En jeu : **F9** = ligne d'essai 10 s (bas d'ecran).

Ne pas laisser un `UE4SS.dll` a la racine de `Win64` en plus du dossier `ue4ss\`
(double install → scan casse). L'installeur Full nettoie ces restes.

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

**Sous-titres N après un O** (relancer INSTALLER) : retire `SousTitresFR` et
coupe `dwmapi` s'il ne reste aucun autre mod custom (Keybinds/shared ignorés).
Un UE4SS tiers avec d'autres mods n'est pas éteint.

**Sous-titres O sur un UE4SS déjà présent** : merge uniquement `SousTitresFR` +
ligne `mods.txt` + signature SCO. Pas d'écrasement de `UE4SS.dll` / `mods.txt`
complet / autres dossiers Mods.
