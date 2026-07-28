# Assemble release/azerty_runtime for the Full beginner pack.
# Sources (first match wins for UE4SS core):
#   1) $env:WTTG3_AZERTY_UE4SS  (folder with dwmapi.dll + ue4ss\)
#   2) Desktop "WTTG3 AZERTY Rebind*" Win64 (if present)
#   3) tools/UE4SS (+ optional tools/UE4SS-exp)
param(
    [string]$LocRoot = (Split-Path $PSScriptRoot -Parent)
)
$ErrorActionPreference = "Stop"
$dst = Join-Path $LocRoot "release\azerty_runtime"
$core = Join-Path $dst "ue4ss_core"

function Find-Ue4ssWin64 {
    if ($env:WTTG3_AZERTY_UE4SS -and (Test-Path $env:WTTG3_AZERTY_UE4SS)) {
        return $env:WTTG3_AZERTY_UE4SS
    }
    $desk = Get-ChildItem "$env:USERPROFILE\Desktop" -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "WTTG3 AZERTY Rebind*" } |
        Select-Object -First 1
    if ($desk) {
        $p = Join-Path $desk.FullName "WTTGSD\Binaries\Win64"
        if ((Test-Path (Join-Path $p "dwmapi.dll")) -and (Test-Path (Join-Path $p "ue4ss\UE4SS.dll"))) {
            return $p
        }
    }
    $tools = Join-Path $LocRoot "tools\UE4SS"
    if (Test-Path (Join-Path $tools "UE4SS.dll")) { return $tools }
    return $null
}

$src = Find-Ue4ssWin64
if (-not $src) { throw "UE4SS introuvable (Desktop AZERTY Rebind ou tools\UE4SS)." }

Write-Host "UE4SS source : $src"
New-Item -ItemType Directory -Force -Path $core | Out-Null

$dwmapi = Join-Path $src "dwmapi.dll"
if (-not (Test-Path $dwmapi)) { $dwmapi = Join-Path $src "..\dwmapi.dll" }
if (Test-Path $dwmapi) {
    Copy-Item $dwmapi (Join-Path $core "dwmapi.dll") -Force
} else {
    throw "dwmapi.dll manquant"
}

$ue4ssDir = if (Test-Path (Join-Path $src "ue4ss\UE4SS.dll")) { Join-Path $src "ue4ss" } else { $src }
Copy-Item (Join-Path $ue4ssDir "UE4SS.dll") (Join-Path $core "UE4SS.dll") -Force
if (Test-Path (Join-Path $ue4ssDir "UE4SS-settings.ini")) {
    Copy-Item (Join-Path $ue4ssDir "UE4SS-settings.ini") (Join-Path $core "UE4SS-settings.ini") -Force
}
if (Test-Path (Join-Path $ue4ssDir "LICENSE")) {
    Copy-Item (Join-Path $ue4ssDir "LICENSE") (Join-Path $core "LICENSE") -Force
}
$sig = Join-Path $ue4ssDir "UE4SS_Signatures"
if (Test-Path $sig) {
    $sigDst = Join-Path $core "UE4SS_Signatures"
    if (Test-Path $sigDst) { Remove-Item $sigDst -Recurse -Force }
    Copy-Item $sig $sigDst -Recurse -Force
}

# Preserve our Mods/AzertyRemap + mods.txt if already authored under release/azerty_runtime
$modsKeep = Join-Path $core "Mods"
New-Item -ItemType Directory -Force -Path $modsKeep | Out-Null
# Refresh Keybinds/shared from source if present
foreach ($m in @("Keybinds", "shared")) {
    $ms = Join-Path $ue4ssDir "Mods\$m"
    if (-not (Test-Path $ms)) { $ms = Join-Path $LocRoot "tools\UE4SS\Mods\$m" }
    if (Test-Path $ms) {
        $md = Join-Path $modsKeep $m
        if (Test-Path $md) { Remove-Item $md -Recurse -Force }
        Copy-Item $ms $md -Recurse -Force
    }
}

if (-not (Test-Path (Join-Path $modsKeep "AzertyRemap\Scripts\main.lua"))) {
    throw "AzertyRemap Scripts manquants - creer release\azerty_runtime\ue4ss_core\Mods\AzertyRemap d'abord"
}
if (-not (Test-Path (Join-Path $modsKeep "mods.txt"))) {
    throw "mods.txt manquant dans ue4ss_core\Mods"
}

# AHK portable
$ahkDst = Join-Path $dst "AutoHotkey64.exe"
if (-not (Test-Path $ahkDst)) {
    $tmp = Join-Path $env:TEMP "ahk_v2_dl"
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $zip = Join-Path $tmp "ahk.zip"
    Invoke-WebRequest -Uri "https://www.autohotkey.com/download/ahk-v2.zip" -OutFile $zip -UseBasicParsing -TimeoutSec 120
    Expand-Archive $zip -DestinationPath (Join-Path $tmp "out") -Force
    $exe = Get-ChildItem (Join-Path $tmp "out") -Recurse -Filter "AutoHotkey64.exe" | Select-Object -First 1
    if (-not $exe) { throw "AutoHotkey64.exe introuvable dans ahk-v2.zip" }
    Copy-Item $exe.FullName $ahkDst -Force
}

foreach ($req in @("WTTG3-Menu-Touches.ahk", "WTTG3-AZERTY-Menu.cmd", "ATTRIBUTION.txt")) {
    if (-not (Test-Path (Join-Path $dst $req))) {
        throw "Fichier manquant dans release\azerty_runtime : $req"
    }
}

Write-Host "OK azerty_runtime : $dst"
Get-ChildItem $dst -Recurse -File | Select-Object FullName, Length | Format-Table -AutoSize
