# Assemble release/subtitles_runtime binaries for the Full beginner pack.
# Requires tracked content already present:
#   Mods/SousTitresFR (Lua + .srt + enabled.txt)
#   UE4SS_Signatures/StaticConstructObject.lua
# Copies UE4SS.dll + dwmapi.dll from tools/UE4SS (gitignored).
param(
    [string]$LocRoot = (Split-Path $PSScriptRoot -Parent)
)
$ErrorActionPreference = "Stop"
$dst = Join-Path $LocRoot "release\subtitles_runtime"
$core = Join-Path $dst "ue4ss_core"
$mod = Join-Path $core "Mods\SousTitresFR"

if (-not (Test-Path (Join-Path $mod "Scripts\main.lua"))) {
    throw "SousTitresFR manquant - checkout PR / release\subtitles_runtime d'abord"
}
if (-not (Test-Path (Join-Path $core "UE4SS_Signatures\StaticConstructObject.lua"))) {
    throw "StaticConstructObject.lua manquant dans subtitles_runtime"
}

$tools = Join-Path $LocRoot "tools\UE4SS"
if (-not (Test-Path (Join-Path $tools "UE4SS.dll"))) {
    throw "tools\UE4SS\UE4SS.dll introuvable"
}
$dwmapi = Join-Path $tools "dwmapi.dll"
if (-not (Test-Path $dwmapi)) {
    throw "tools\UE4SS\dwmapi.dll introuvable"
}

Copy-Item $dwmapi (Join-Path $core "dwmapi.dll") -Force
Copy-Item (Join-Path $tools "UE4SS.dll") (Join-Path $core "UE4SS.dll") -Force
if (Test-Path (Join-Path $tools "UE4SS-settings.ini")) {
    Copy-Item (Join-Path $tools "UE4SS-settings.ini") (Join-Path $core "UE4SS-settings.ini") -Force
}
if (Test-Path (Join-Path $tools "LICENSE")) {
    Copy-Item (Join-Path $tools "LICENSE") (Join-Path $core "LICENSE") -Force
}

$modsKeep = Join-Path $core "Mods"
New-Item -ItemType Directory -Force -Path $modsKeep | Out-Null
foreach ($m in @("Keybinds", "shared")) {
    $ms = Join-Path $tools "Mods\$m"
    if (Test-Path $ms) {
        $md = Join-Path $modsKeep $m
        if (Test-Path $md) { Remove-Item $md -Recurse -Force }
        Copy-Item $ms $md -Recurse -Force
    }
}

# mods.txt : pas d'AzertyRemap ; SousTitresFR via enabled.txt
@"
CheatManagerEnablerMod : 0
ConsoleCommandsMod : 0
ConsoleEnablerMod : 0
SplitScreenMod : 0
LineTraceMod : 0
BPML_GenericFunctions : 0
BPModLoaderMod : 0

; Built-in keybinds, do not move up!
Keybinds : 1
"@ | Set-Content -Path (Join-Path $modsKeep "mods.txt") -Encoding ASCII

$attr = @(
    "Sous-titres cinematiques WTTG3 FR",
    "",
    "Mod Lua + .srt : contribution iPresing (PR #1).",
    "UE4SS (dwmapi.dll + UE4SS.dll) : https://github.com/UE4SS-RE/RE-UE4SS",
    "Optionnel via INSTALLER.bat (O/N) - pas active par defaut.",
    "Voir docs/SOUS_TITRES.md"
) -join "`r`n"
Set-Content -Path (Join-Path $dst "ATTRIBUTION.txt") -Value $attr -Encoding UTF8

Write-Host "OK subtitles_runtime : $dst"
Write-Host ("  SousTitresFR srt : {0}" -f @(Get-ChildItem (Join-Path $mod "SousTitres") -Filter "*.srt").Count)
Write-Host ("  dwmapi+UE4SS : {0}" -f (Test-Path (Join-Path $core "dwmapi.dll")))
