# Assemble a beginner pack under release\
# -Distribution Full  : zip GitHub (INSTALLER.bat + backup PDF EN)
# -Distribution Nexus : zip Nexus drop-in (pas de .bat/.ps1, structure WTTGSD/...)
param(
    [string]$LocRoot = (Split-Path $PSScriptRoot -Parent),
    [ValidateSet("Full", "Nexus")]
    [string]$Distribution = "Full"
)

$ErrorActionPreference = "Stop"
$outName = if ($Distribution -eq "Nexus") { "WTTG3-FR-Beginner-Nexus" } else { "WTTG3-FR-Beginner" }
$out = Join-Path $LocRoot "release\$outName"
$pakSrc = Join-Path $LocRoot "build\pak"
$pdfFr = Join-Path $LocRoot "build\pdfs"
$pdfEn = Join-Path $LocRoot "backup\PDFS"
$achFr = Join-Path $LocRoot "build\achievements_fr.json"
$achEn = Join-Path $LocRoot "source\achievements_en.json"

if (-not (Test-Path (Join-Path $pakSrc "WTTGSD-Windows_FR_P.ucas"))) {
    throw "Mod FR manquant dans build\pak - lance d'abord build_ui_uassetgui_patch.py"
}
$azertyPak = Join-Path $pakSrc "WTTGSD-Windows_FR_AZERTY_P.ucas"
$hasAzerty = Test-Path $azertyPak
if (-not $hasAzerty) {
    Write-Host "WARN: pak AZERTY absent (build\pak\WTTGSD-Windows_FR_AZERTY_P.*) — lance build_azerty_imc_patch.py pour l'option ZQSD." -ForegroundColor Yellow
}
$azertyRuntime = Join-Path $LocRoot "release\azerty_runtime"
$hasAzertyRuntime = Test-Path (Join-Path $azertyRuntime "ue4ss_core\Mods\AzertyRemap\Scripts\main.lua")
if ($Distribution -eq "Full" -and -not $hasAzertyRuntime) {
    Write-Host "WARN: release\azerty_runtime incomplet — lance scripts\build_azerty_runtime.ps1 pour mini-jeux." -ForegroundColor Yellow
}
if ($Distribution -eq "Full" -and $hasAzertyRuntime -and -not (Test-Path (Join-Path $azertyRuntime "AutoHotkey64.exe"))) {
    Write-Host "WARN: AutoHotkey64.exe manquant — lance scripts\build_azerty_runtime.ps1" -ForegroundColor Yellow
    $hasAzertyRuntime = $false
}
if (-not (Test-Path $pdfFr)) { throw "PDF FR manquants : build\pdfs" }
if ($Distribution -eq "Full" -and -not (Test-Path $pdfEn)) {
    throw "Backup PDF EN manquant : backup\PDFS"
}

if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Force -Path $out | Out-Null

$steamTarget = Join-Path $LocRoot "release\steam_target.json"
if (-not (Test-Path $steamTarget)) {
    throw "steam_target.json manquant : release\steam_target.json (BuildID Steam du pack)"
}

if ($Distribution -eq "Nexus") {
    # Drop-in: unzip into the Steam game root (folder that contains WTTGSD).
    # No .bat / .ps1 — avoids Nexus "suspicious files" quarantine.
    $pakDst = Join-Path $out "WTTGSD\Content\Paks"
    $pdfDst = Join-Path $out "WTTGSD\Content\RawFiles\PDFS"
    New-Item -ItemType Directory -Force -Path $pakDst | Out-Null
    New-Item -ItemType Directory -Force -Path $pdfDst | Out-Null
    Copy-Item (Join-Path $pakSrc "WTTGSD-Windows_FR_P.*") $pakDst -Force
    Copy-Item (Join-Path $pdfFr "*") $pdfDst -Recurse -Force
    Copy-Item $steamTarget (Join-Path $out "steam_target.json") -Force
    Copy-Item $steamTarget (Join-Path $pakDst "WTTGSD-Windows_FR_P.steam_target.json") -Force

    # Optional AZERTY: not in default Paks (would force remap). Drop-in folder + LIREMOI.
    if ($hasAzerty) {
        $azertyOpt = Join-Path $out "optionnel_azerty"
        New-Item -ItemType Directory -Force -Path $azertyOpt | Out-Null
        Copy-Item (Join-Path $pakSrc "WTTGSD-Windows_FR_AZERTY_P.*") $azertyOpt -Force
        $azertyReadme = @(
            "Option AZERTY (ZQSD) — Welcome to the Game III FR (Nexus)",
            "",
            "Par defaut ce pack Nexus n'active PAS le remap clavier.",
            "Pour avancer avec Z / gauche avec Q (Windows reste en AZERTY) :",
            "  1. Copie tous les fichiers WTTGSD-Windows_FR_AZERTY_P.*",
            "     de ce dossier vers :",
            "     <dossier du jeu>\WTTGSD\Content\Paks\",
            "  2. Relance le jeu.",
            "",
            "Pour desactiver : supprime WTTGSD-Windows_FR_AZERTY_P.* dans Paks.",
            "La saisie texte (chat) n'est pas modifiee.",
            "",
            "MINI-JEUX DE HACK (MemDealloc, etc.) :",
            "  Non inclus sur Nexus (injecteur UE4SS / AutoHotkey).",
            "  Utilise le pack GitHub Full (INSTALLER.bat) pour AZERTY complet."
        ) -join "`r`n"
        Set-Content -Path (Join-Path $azertyOpt "LIREMOI_AZERTY.txt") -Value $azertyReadme -Encoding UTF8
    }
} else {
    New-Item -ItemType Directory -Force -Path (Join-Path $out "fichiers\paks") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $out "fichiers\pdfs") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $out "scripts") | Out-Null

    Copy-Item (Join-Path $pakSrc "WTTGSD-Windows_FR_P.*") (Join-Path $out "fichiers\paks") -Force
    if ($hasAzerty) {
        Copy-Item (Join-Path $pakSrc "WTTGSD-Windows_FR_AZERTY_P.*") (Join-Path $out "fichiers\paks") -Force
    }
    if ($hasAzertyRuntime) {
        $rtDst = Join-Path $out "fichiers\azerty_runtime"
        New-Item -ItemType Directory -Force -Path $rtDst | Out-Null
        Copy-Item (Join-Path $azertyRuntime "*") $rtDst -Recurse -Force
    }
    Copy-Item (Join-Path $pdfFr "*") (Join-Path $out "fichiers\pdfs") -Recurse -Force

    New-Item -ItemType Directory -Force -Path (Join-Path $out "fichiers\pdfs_en_backup") | Out-Null
    Copy-Item (Join-Path $pdfEn "*") (Join-Path $out "fichiers\pdfs_en_backup") -Recurse -Force
    if (Test-Path $achFr) { Copy-Item $achFr (Join-Path $out "fichiers\achievements_fr.json") -Force }
    if (Test-Path $achEn) { Copy-Item $achEn (Join-Path $out "fichiers\achievements_en.json") -Force }

    Copy-Item $steamTarget (Join-Path $out "fichiers\steam_target.json") -Force
    # Copie aussi sous le glob FR_P.* pour que l'installeur (meme ancien) pose un stamp version dans Paks/
    Copy-Item $steamTarget (Join-Path $out "fichiers\paks\WTTGSD-Windows_FR_P.steam_target.json") -Force

    Copy-Item (Join-Path $LocRoot "scripts\beginner_common.ps1") (Join-Path $out "scripts") -Force
    Copy-Item (Join-Path $LocRoot "scripts\install_fr_beginner.ps1") (Join-Path $out "scripts") -Force
    Copy-Item (Join-Path $LocRoot "scripts\uninstall_fr_beginner.ps1") (Join-Path $out "scripts") -Force

    # Keep the console open if PowerShell fails to parse/start (double-click UX).
    $installerBat = @(
        "@echo off",
        "chcp 65001 >nul",
        'cd /d "%~dp0"',
        'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_fr_beginner.ps1"',
        "if errorlevel 1 (",
        "  echo.",
        "  echo Echec de l'installateur. Relis le message ci-dessus.",
        "  pause",
        ")"
    ) -join "`r`n"
    Set-Content -Path (Join-Path $out "INSTALLER.bat") -Value $installerBat -Encoding ASCII

    $uninstallerBat = @(
        "@echo off",
        "chcp 65001 >nul",
        'cd /d "%~dp0"',
        'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uninstall_fr_beginner.ps1"',
        "if errorlevel 1 (",
        "  echo.",
        "  echo Echec de la desinstallation. Relis le message ci-dessus.",
        "  pause",
        ")"
    ) -join "`r`n"
    Set-Content -Path (Join-Path $out "DESINSTALLER.bat") -Value $uninstallerBat -Encoding ASCII
}

$readmePath = if ($Distribution -eq "Nexus") {
    Join-Path $LocRoot "release\LIREMOI_NEXUS_TEMPLATE.txt"
} else {
    Join-Path $LocRoot "release\LIREMOI_BEGINNER_TEMPLATE.txt"
}
if (-not (Test-Path $readmePath)) {
    throw "Template LIREMOI manquant : $readmePath"
}
Copy-Item $readmePath (Join-Path $out "LIREMOI.txt") -Force

Write-Host "Pack pret ($Distribution) : $out"
if ($Distribution -eq "Nexus") {
    Write-Host "Zip Nexus recommande : release\WTTG3-FR-Traduction-Nexus.zip (drop-in, sans scripts)"
} else {
    Write-Host "Tu peux zipper ce dossier et le donner a quelqu'un."
}
Get-ChildItem $out | Select-Object Name, Length
