# Remove French patch for WTTG3 (beginner-friendly).
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "beginner_common.ps1")

try {
    Write-Title "WTTG3 - Retirer la traduction FR"
    Write-Host "Ferme le jeu avant de continuer."
    Write-Host "Cet outil supprime le mod FR et remet les PDF anglais."
    Write-Host ""

    Assert-GameClosed
    $pack = Get-PackRoot
    $game = Select-GameRoot

    $paksDst = Join-Path $game "WTTGSD\Content\Paks"
    $pdfSrc = Join-Path $pack "fichiers\pdfs_en_backup"
    $pdfDst = Join-Path $game "WTTGSD\Content\RawFiles\PDFS"

    Write-Host ""
    Write-Host "Desinstallation depuis :" -ForegroundColor Yellow
    Write-Host "  $game"
    Write-Host ""
    $ok = Read-Host "Confirmer ? (O/N)"
    if ($ok -notmatch '^[oOyY]') { throw "Annule." }

    Write-Host "Suppression du mod UI (FR_P)..."
    $mods = Get-ChildItem (Join-Path $paksDst "WTTGSD-Windows_FR_P.*") -ErrorAction SilentlyContinue
    if ($mods) {
        $mods | Remove-Item -Force
        Write-Host ("  Supprime : {0} fichier(s)" -f @($mods).Count)
    } else {
        Write-Host "  Aucun fichier FR_P trouve (deja retire ?)"
    }

    if (Test-Path $pdfSrc) {
        if (-not (Test-Path $pdfDst)) { throw "Dossier PDFS introuvable : $pdfDst" }
        Write-Host "Restauration des PDF anglais..."
        Copy-Item (Join-Path $pdfSrc "*") -Destination $pdfDst -Recurse -Force
    } else {
        Write-Host "Pas de backup PDF EN dans le pack - PDF laisses tels quels."
    }

    $achSrc = Join-Path $pack "fichiers\achievements_en.json"
    $achDst = Join-Path $game "Engine\Binaries\ThirdParty\Steamworks\Steamv157\Win64\steam_settings\achievements.json"
    if ((Test-Path $achSrc) -and (Test-Path (Split-Path $achDst -Parent))) {
        Write-Host "Restauration achievements EN..."
        Copy-Item $achSrc $achDst -Force
    }

    Write-Host ""
    Write-Host "OK - Traduction retiree. Le jeu devrait etre en anglais." -ForegroundColor Green
    Pause-Exit 0
}
catch {
    Write-Host ""
    Write-Host "ERREUR : $($_.Exception.Message)" -ForegroundColor Red
    Pause-Exit 1
}
