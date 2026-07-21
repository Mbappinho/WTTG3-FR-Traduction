# Intro Simon Zhao — texture FR

## Source

Le texte EN n’est **pas** une FString. Il est peint dans :

`Images/UI/HUD/AptLoadingScreen` (1064×810, `PF_B8G8R8A8`)

(`TitleLogoA` / `TitleLogoB` = logo « W3LCM3 TO TH3 GAM3 », pas cette intro.)

## Fichiers

| Fichier | Rôle |
|---------|------|
| `candidates/AptLoadingScreen.png` | Export EN |
| `AptLoadingScreen_FR.png` | Version FR (source du patch) |
| `make_fr_png.py` | Régénère le PNG FR |
| `inject_apt_loading.py` | Inject BGRA standalone |
| `cooked/` | Copie uasset/uexp patchés |

## Pipeline

`scripts/build_ui_uassetgui_patch.py` → `stage_apt_loading_screen_fr()` après les patchs FString, avant `retoc to-zen`.
