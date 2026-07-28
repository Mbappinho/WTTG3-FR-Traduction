# Install French patch for WTTG3 (beginner-friendly).
param(
    [string]$GameRoot = "",
    [switch]$SkipGitHubUpdate
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "beginner_common.ps1")

# Cleanup leftovers from withdrawn v1.6.0 UE4SS/AHK injector (fatal errors).
function Remove-AzertyRuntimeLeftovers([string]$GameRoot) {
    $win64 = Join-Path $GameRoot "WTTGSD\Binaries\Win64"
    $dwmapi = Join-Path $win64 "dwmapi.dll"
    $dwmapiOff = Join-Path $win64 "dwmapi.dll.off"
    if (Test-Path -LiteralPath $dwmapi) {
        if (Test-Path -LiteralPath $dwmapiOff) { Remove-Item -LiteralPath $dwmapiOff -Force }
        Rename-Item -LiteralPath $dwmapi -NewName "dwmapi.dll.off" -Force
        Write-Host "  Ancien injecteur desactive (dwmapi.dll -> .off)"
    }
    $azertyMod = Join-Path $win64 "ue4ss\Mods\AzertyRemap"
    if (Test-Path -LiteralPath $azertyMod) {
        Remove-Item -LiteralPath $azertyMod -Recurse -Force
        Write-Host "  Ancien mod AzertyRemap retire"
    }
    foreach ($name in @("WTTG3-Menu-Touches.ahk", "WTTG3-Menu.ini", "AutoHotkey64.exe", "WTTG3-AZERTY-Menu.cmd")) {
        $p = Join-Path $GameRoot $name
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Force
            Write-Host ("  Retire : {0}" -f $name)
        }
    }
}

try {
    Write-Title "WTTG3 - Installer la traduction FR"
    Write-Host "Ferme le jeu avant de continuer."
    Write-Host "Cet outil copie le mod FR + les PDF traduits."
    Write-Host "Les sites web Dark Net ne sont PAS modifies."
    Write-Host "Si une maj GitHub existe, l'installeur peut la telecharger."
    Write-Host ""

    Assert-GameClosed
    $pack = Get-PackRoot
    if ($GameRoot -and (Test-GameLooksValid $GameRoot)) {
        $game = $GameRoot.Trim().Trim('"')
        Write-Host "Dossier jeu (fourni) : $game"
    } else {
        $game = Select-GameRoot
    }

    $compat = Test-SteamBuildCompatibility $game $pack
    Show-SteamBuildCheck $compat

    if (-not $SkipGitHubUpdate) {
        $packVerBefore = [string]$compat.PackVersion
        $upd = Update-PackFromGitHubIfNeeded $pack $compat
        if ($upd -is [hashtable]) {
            $pack = [string]$upd.PackRoot
            if ($upd.Updated) {
                Restart-InstallScriptAfterPackUpdate $pack $game
            }
        } else {
            $pack = [string]$upd
        }
        $compat = Test-SteamBuildCompatibility $game $pack
        if ([string]$compat.PackVersion -ne $packVerBefore) {
            Show-SteamBuildCheck $compat
        }
    } else {
        Write-Host "Maj GitHub ignoree (-SkipGitHubUpdate)." -ForegroundColor DarkGray
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
    Write-InstalledPackStamp $game $pack

    # Always strip withdrawn injector if present (v1.6.0)
    Write-Host "Nettoyage ancien injecteur AZERTY (si present)..."
    Remove-AzertyRuntimeLeftovers $game

    # Optional AZERTY: pak IMC only (no UE4SS / AutoHotkey)
    $azertyGlob = Join-Path $paksSrc "WTTGSD-Windows_FR_AZERTY_P.*"
    $azertyFiles = @(Get-ChildItem $azertyGlob -ErrorAction SilentlyContinue)
    Get-ChildItem (Join-Path $paksDst "WTTGSD-Windows_FR_AZERTY_P.*") -ErrorAction SilentlyContinue |
        Remove-Item -Force

    if ($azertyFiles.Count -gt 0) {
        Write-Host ""
        Write-Host "Option clavier AZERTY (ZQSD) — pak uniquement :" -ForegroundColor Cyan
        Write-Host "  OK : deplacement monde avec ZQSD (Windows reste en AZERTY)."
        Write-Host "  Mini-jeux de hack (MemDealloc, ShiftSEQ, etc.) :" -ForegroundColor Yellow
        Write-Host "    le jeu lit toujours les touches W/A/S/D (pas patchable sans injecteur)."
        Write-Host "    → soit tu joues ces hacks avec les touches W/A (positions QWERTY),"
        Write-Host "    → soit tu refuses ce mod AZERTY (N) et tu gardes WASD partout."
        Write-Host "  La saisie texte (chat) n'est pas modifiee."
        $azerty = Read-Host "Activer remap AZERTY (ZQSD monde) ? (O/N)"
        if ($azerty -match '^[oOyY]') {
            Write-Host "Copie du mod AZERTY (FR_AZERTY_P)..."
            Copy-Item $azertyGlob -Destination $paksDst -Force
        } else {
            Write-Host "Remap AZERTY non installe (WASD / touches QWERTY)."
        }
    }

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
