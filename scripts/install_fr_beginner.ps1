# Install French patch for WTTG3 (beginner-friendly).
param(
    [string]$GameRoot = "",
    [switch]$SkipGitHubUpdate
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "beginner_common.ps1")

function Remove-AzertyRuntime([string]$GameRoot) {
    $win64 = Join-Path $GameRoot "WTTGSD\Binaries\Win64"
    $dwmapi = Join-Path $win64 "dwmapi.dll"
    $dwmapiOff = Join-Path $win64 "dwmapi.dll.off"
    if (Test-Path -LiteralPath $dwmapi) {
        # Prefer rename to .off (same as dump workflow) so Steam verify is less noisy
        if (Test-Path -LiteralPath $dwmapiOff) { Remove-Item -LiteralPath $dwmapiOff -Force }
        Rename-Item -LiteralPath $dwmapi -NewName "dwmapi.dll.off" -Force
        Write-Host "  UE4SS desactive (dwmapi.dll -> .off)"
    }
    $azertyMod = Join-Path $win64 "ue4ss\Mods\AzertyRemap"
    if (Test-Path -LiteralPath $azertyMod) {
        Remove-Item -LiteralPath $azertyMod -Recurse -Force
        Write-Host "  Mod AzertyRemap retire"
    }
    foreach ($name in @("WTTG3-Menu-Touches.ahk", "WTTG3-Menu.ini", "AutoHotkey64.exe", "WTTG3-AZERTY-Menu.cmd")) {
        $p = Join-Path $GameRoot $name
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Force
            Write-Host ("  Retire : {0}" -f $name)
        }
    }
}

function Install-AzertyRuntime([string]$GameRoot, [string]$PackRoot) {
    $src = Join-Path $PackRoot "fichiers\azerty_runtime"
    if (-not (Test-Path -LiteralPath $src)) {
        Write-Host "WARN: fichiers\azerty_runtime absent — pak AZERTY seul (pas de mini-jeux)." -ForegroundColor Yellow
        return
    }
    $win64 = Join-Path $GameRoot "WTTGSD\Binaries\Win64"
    if (-not (Test-Path -LiteralPath $win64)) {
        throw "Binaries Win64 introuvable : $win64"
    }

    # UE4SS core (dwmapi proxy + ue4ss folder)
    $ue4ssSrc = Join-Path $src "ue4ss_core"
    if (Test-Path -LiteralPath $ue4ssSrc) {
        $dwmapiSrc = Join-Path $ue4ssSrc "dwmapi.dll"
        if (Test-Path -LiteralPath $dwmapiSrc) {
            $off = Join-Path $win64 "dwmapi.dll.off"
            if (Test-Path -LiteralPath $off) { Remove-Item -LiteralPath $off -Force }
            Copy-Item $dwmapiSrc (Join-Path $win64 "dwmapi.dll") -Force
        }
        $ue4ssDst = Join-Path $win64 "ue4ss"
        New-Item -ItemType Directory -Force -Path $ue4ssDst | Out-Null
        # Copy settings + DLL if present
        foreach ($name in @("UE4SS.dll", "UE4SS-settings.ini", "LICENSE")) {
            $f = Join-Path $ue4ssSrc $name
            if (Test-Path -LiteralPath $f) { Copy-Item $f (Join-Path $ue4ssDst $name) -Force }
        }
        $sigSrc = Join-Path $ue4ssSrc "UE4SS_Signatures"
        if (Test-Path -LiteralPath $sigSrc) {
            $sigDst = Join-Path $ue4ssDst "UE4SS_Signatures"
            if (Test-Path $sigDst) { Remove-Item $sigDst -Recurse -Force }
            Copy-Item $sigSrc $sigDst -Recurse -Force
        }
        $modsSrc = Join-Path $ue4ssSrc "Mods"
        $modsDst = Join-Path $ue4ssDst "Mods"
        New-Item -ItemType Directory -Force -Path $modsDst | Out-Null
        # Keybinds + shared stubs + our AzertyRemap + mods.txt
        if (Test-Path -LiteralPath $modsSrc) {
            Copy-Item (Join-Path $modsSrc "*") $modsDst -Recurse -Force
        }
        Write-Host "  UE4SS deploye (dwmapi.dll + ue4ss)"
    }

    # Overlay AHK + portable interpreter at game root
    foreach ($name in @("WTTG3-Menu-Touches.ahk", "AutoHotkey64.exe", "WTTG3-AZERTY-Menu.cmd", "WTTG3-Menu.ini")) {
        $f = Join-Path $src $name
        if (Test-Path -LiteralPath $f) {
            Copy-Item $f (Join-Path $GameRoot $name) -Force
        }
    }
    Write-Host "  Menu mini-jeux AHK deploye (racine du jeu)"
    Write-Host "  Note: antivirus peut signaler dwmapi.dll (injecteur UE4SS)." -ForegroundColor Yellow
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
                # Old script still in memory — hand off to synced installer (one INSTALLER.bat click).
                Restart-InstallScriptAfterPackUpdate $pack $game
            }
        } else {
            # Backward compat if an ancient beginner_common is somehow mixed
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

    # Optional AZERTY: pak IMC + UE4SS/AHK runtime for hack minigames
    $azertyGlob = Join-Path $paksSrc "WTTGSD-Windows_FR_AZERTY_P.*"
    $azertyFiles = @(Get-ChildItem $azertyGlob -ErrorAction SilentlyContinue)
    Get-ChildItem (Join-Path $paksDst "WTTGSD-Windows_FR_AZERTY_P.*") -ErrorAction SilentlyContinue |
        Remove-Item -Force
    # Always clear previous AZERTY runtime when (re)installing; re-enable only if user says O
    Write-Host "Nettoyage runtime AZERTY precedent (si present)..."
    Remove-AzertyRuntime $game

    if ($azertyFiles.Count -gt 0 -or (Test-Path (Join-Path $pack "fichiers\azerty_runtime"))) {
        Write-Host ""
        Write-Host "Option clavier AZERTY (ZQSD) :" -ForegroundColor Cyan
        Write-Host "  - Pak : deplacement / ShiftSEQ (Enhanced Input)"
        Write-Host "  - Runtime UE4SS + AutoHotkey : mini-jeux hack (MemDealloc, StackPusher, ...)"
        Write-Host "  Windows reste en AZERTY. KernalCompiler (saisie) non remappe."
        Write-Host "  Antivirus peut signaler dwmapi.dll (injecteur). Desinstaller = DESINSTALLER ou N."
        $azerty = Read-Host "Activer remap AZERTY complet (pak + mini-jeux) ? (O/N)"
        if ($azerty -match '^[oOyY]') {
            if ($azertyFiles.Count -gt 0) {
                Write-Host "Copie du mod AZERTY (FR_AZERTY_P)..."
                Copy-Item $azertyGlob -Destination $paksDst -Force
            }
            Write-Host "Deploiement runtime AZERTY (UE4SS + menu mini-jeux)..."
            Install-AzertyRuntime $game $pack
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
