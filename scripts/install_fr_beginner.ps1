# Install French patch for WTTG3 (beginner-friendly).
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "beginner_common.ps1")

try {
    Write-Title "WTTG3 - Installer la traduction FR"
    Write-Host "Ferme le jeu avant de continuer."
    Write-Host "Cet outil copie le mod FR + les PDF traduits."
    Write-Host "Les sites web Dark Net ne sont PAS modifies."
    Write-Host "Si une maj GitHub existe, l'installeur peut la telecharger."
    Write-Host ""

    Assert-GameClosed
    $pack = Get-PackRoot
    $game = Select-GameRoot

    $compat = Test-SteamBuildCompatibility $game $pack
    Show-SteamBuildCheck $compat

    $packBefore = $pack
    $pack = Update-PackFromGitHubIfNeeded $pack $compat
    if ($pack -ne $packBefore) {
        $compat = Test-SteamBuildCompatibility $game $pack
        Show-SteamBuildCheck $compat
    }

    if ($compat.Status -eq "Mismatch") {
        Write-Host ""
        $force = Read-Host "Installer QUAND MEME malgre le mauvais BuildID ? (O/N)"
        if ($force -notmatch '^[oOyY]') { throw "Annule - telecharge une release FR pour ton BuildID Steam." }
        Write-Host "Installation forcee (risque de crash)." -ForegroundColor Yellow
    } elseif ($compat.Status -eq "Unknown") {
        Write-Host ""
        $cont = Read-Host "Continuer sans verification BuildID ? (O/N)"
        if ($cont -notmatch '^[oOyY]') { throw "Annule." }
    }

    $paksSrc = Join-Path $pack "fichiers\paks"
    $paksDst = Join-Path $game "WTTGSD\Content\Paks"
    $pdfSrc = Join-Path $pack "fichiers\pdfs"
    $pdfDst = Join-Path $game "WTTGSD\Content\RawFiles\PDFS"

    if (-not (Test-Path $paksSrc)) { throw "Fichiers mod manquants : $paksSrc" }
    if (-not (Test-Path $paksDst)) { throw "Dossier Paks introuvable : $paksDst" }

    Write-Host ""
    Write-Host "Installation vers :" -ForegroundColor Green
    Write-Host "  $game"
    Write-Host ""
    $ok = Read-Host "Confirmer l'installation ? (O/N)"
    if ($ok -notmatch '^[oOyY]') { throw "Annule." }

    Write-Host "Copie du mod UI (FR_P)..."
    Copy-Item (Join-Path $paksSrc "WTTGSD-Windows_FR_P.*") -Destination $paksDst -Force

    if (Test-Path $pdfSrc) {
        if (-not (Test-Path $pdfDst)) { throw "Dossier PDFS introuvable : $pdfDst" }
        Write-Host "Copie des PDF FR..."
        Copy-Item (Join-Path $pdfSrc "*") -Destination $pdfDst -Recurse -Force
    }

    $achSrc = Join-Path $pack "fichiers\achievements_fr.json"
    $achDst = Join-Path $game "Engine\Binaries\ThirdParty\Steamworks\Steamv157\Win64\steam_settings\achievements.json"
    if ((Test-Path $achSrc) -and (Test-Path (Split-Path $achDst -Parent))) {
        Write-Host "Copie achievements FR (si present)..."
        Copy-Item $achSrc $achDst -Force
    }

    Write-Host ""
    Write-Host "OK - Traduction installee." -ForegroundColor Green
    Write-Host "Lance le jeu. Si bug : utilise DESINSTALLER.bat"
    Pause-Exit 0
}
catch {
    Write-Host ""
    Write-Host "ERREUR : $($_.Exception.Message)" -ForegroundColor Red
    Pause-Exit 1
}
