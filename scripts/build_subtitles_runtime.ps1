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
    $iniDst = Join-Path $core "UE4SS-settings.ini"
    Copy-Item (Join-Path $tools "UE4SS-settings.ini") $iniDst -Force
    # WTTG3 (UE5.6) : cache UObject off, pas de console debug (AllocConsole), version forcee
    $ini = Get-Content -Raw $iniDst
    $ini = $ini -replace '(?m)^bUseUObjectArrayCache\s*=\s*\w+', 'bUseUObjectArrayCache = false'
    $ini = $ini -replace '(?m)^ConsoleEnabled\s*=\s*\d+', 'ConsoleEnabled = 0'
    $ini = $ini -replace '(?m)^GuiConsoleEnabled\s*=\s*\d+', 'GuiConsoleEnabled = 0'
    $ini = $ini -replace '(?m)^GuiConsoleVisible\s*=\s*\d+', 'GuiConsoleVisible = 0'
    $ini = $ini -replace '(?m)^MajorVersion\s*=.*', 'MajorVersion = 5'
    $ini = $ini -replace '(?m)^MinorVersion\s*=.*', 'MinorVersion = 6'
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [IO.File]::WriteAllText($iniDst, $ini, $utf8)
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

# mods.txt : SousTitresFR explicite (+ enabled.txt en secours)
@"
CheatManagerEnablerMod : 0
ConsoleCommandsMod : 0
ConsoleEnablerMod : 0
SplitScreenMod : 0
LineTraceMod : 0
BPML_GenericFunctions : 0
BPModLoaderMod : 0
SousTitresFR : 1

; Built-in keybinds, do not move up!
Keybinds : 1
"@ | Set-Content -Path (Join-Path $modsKeep "mods.txt") -Encoding ASCII

# enabled.txt non vide (certains unzip Windows sautent les fichiers 0 octet)
Set-Content -Path (Join-Path $mod "enabled.txt") -Value "1" -Encoding ASCII -NoNewline

$attr = @(
    "Sous-titres cinematiques WTTG3 FR",
    "",
    "Mod Lua + .srt : contribution iPresing (PR #1).",
    "UE4SS (dwmapi.dll + UE4SS.dll) : https://github.com/UE4SS-RE/RE-UE4SS",
    "Build valide : experimental-latest (nested ue4ss/) - v3.0.1 ancien (fev 2024) casse sur ce jeu.",
    "Optionnel via INSTALLER.bat (O/N) - pas active par defaut.",
    "Voir docs/SOUS_TITRES.md"
) -join "`r`n"
Set-Content -Path (Join-Path $dst "ATTRIBUTION.txt") -Value $attr -Encoding UTF8

Write-Host "OK subtitles_runtime : $dst"
Write-Host ("  SousTitresFR srt : {0}" -f @(Get-ChildItem (Join-Path $mod "SousTitres") -Filter "*.srt").Count)
Write-Host ("  dwmapi+UE4SS : {0}" -f (Test-Path (Join-Path $core "dwmapi.dll")))
