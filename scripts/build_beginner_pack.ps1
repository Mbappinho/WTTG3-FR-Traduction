# Assemble a double-click beginner pack under release\WTTG3-FR-Beginner
param(
    [string]$LocRoot = (Split-Path $PSScriptRoot -Parent)
)

$ErrorActionPreference = "Stop"
$out = Join-Path $LocRoot "release\WTTG3-FR-Beginner"
$pakSrc = Join-Path $LocRoot "build\pak"
$pdfFr = Join-Path $LocRoot "build\pdfs"
$pdfEn = Join-Path $LocRoot "backup\PDFS"
$achFr = Join-Path $LocRoot "build\achievements_fr.json"
$achEn = Join-Path $LocRoot "source\achievements_en.json"

if (-not (Test-Path (Join-Path $pakSrc "WTTGSD-Windows_FR_P.ucas"))) {
    throw "Mod FR manquant dans build\pak - lance d'abord build_ui_uassetgui_patch.py"
}
if (-not (Test-Path $pdfFr)) { throw "PDF FR manquants : build\pdfs" }
if (-not (Test-Path $pdfEn)) { throw "Backup PDF EN manquant : backup\PDFS" }

if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $out "fichiers\paks") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $out "fichiers\pdfs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $out "fichiers\pdfs_en_backup") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $out "scripts") | Out-Null

Copy-Item (Join-Path $pakSrc "WTTGSD-Windows_FR_P.*") (Join-Path $out "fichiers\paks") -Force
Copy-Item (Join-Path $pdfFr "*") (Join-Path $out "fichiers\pdfs") -Recurse -Force
Copy-Item (Join-Path $pdfEn "*") (Join-Path $out "fichiers\pdfs_en_backup") -Recurse -Force

if (Test-Path $achFr) { Copy-Item $achFr (Join-Path $out "fichiers\achievements_fr.json") -Force }
if (Test-Path $achEn) { Copy-Item $achEn (Join-Path $out "fichiers\achievements_en.json") -Force }

$steamTarget = Join-Path $LocRoot "release\steam_target.json"
if (-not (Test-Path $steamTarget)) {
    throw "steam_target.json manquant : release\steam_target.json (BuildID Steam du pack)"
}
Copy-Item $steamTarget (Join-Path $out "fichiers\steam_target.json") -Force

Copy-Item (Join-Path $LocRoot "scripts\beginner_common.ps1") (Join-Path $out "scripts") -Force
Copy-Item (Join-Path $LocRoot "scripts\install_fr_beginner.ps1") (Join-Path $out "scripts") -Force
Copy-Item (Join-Path $LocRoot "scripts\uninstall_fr_beginner.ps1") (Join-Path $out "scripts") -Force

$installerBat = @(
    "@echo off",
    "chcp 65001 >nul",
    'cd /d "%~dp0"',
    'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_fr_beginner.ps1"'
) -join "`r`n"
Set-Content -Path (Join-Path $out "INSTALLER.bat") -Value $installerBat -Encoding ASCII

$uninstallerBat = @(
    "@echo off",
    "chcp 65001 >nul",
    'cd /d "%~dp0"',
    'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uninstall_fr_beginner.ps1"'
) -join "`r`n"
Set-Content -Path (Join-Path $out "DESINSTALLER.bat") -Value $uninstallerBat -Encoding ASCII

$readmePath = Join-Path $LocRoot "release\LIREMOI_BEGINNER_TEMPLATE.txt"
if (-not (Test-Path $readmePath)) {
    throw "Template LIREMOI manquant : release\LIREMOI_BEGINNER_TEMPLATE.txt"
}
Copy-Item $readmePath (Join-Path $out "LIREMOI.txt") -Force

Write-Host "Pack pret : $out"
Write-Host "Tu peux zipper ce dossier et le donner a quelqu'un."
Get-ChildItem $out | Select-Object Name, Length
