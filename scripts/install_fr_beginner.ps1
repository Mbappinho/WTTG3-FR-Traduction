# Install French patch for WTTG3 (beginner-friendly).
param(
    [string]$GameRoot = "",
    [switch]$SkipGitHubUpdate
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "beginner_common.ps1")

# Cleanup leftovers from withdrawn v1.6.0 UE4SS/AHK injector (fatal errors).
#
# dwmapi.dll n'est desactive que si le VIEIL injecteur AZERTY est reconnu
# (ue4ss\Mods\AzertyRemap present). Sinon on conserve UE4SS du joueur
# (ex. sous-titres cinematiques) — courtesy fix from PR #1 (iPresing).
function Remove-AzertyRuntimeLeftovers([string]$GameRoot) {
    $win64 = Join-Path $GameRoot "WTTGSD\Binaries\Win64"
    $dwmapi = Join-Path $win64 "dwmapi.dll"
    $dwmapiOff = Join-Path $win64 "dwmapi.dll.off"
    $azertyMod = Join-Path $win64 "ue4ss\Mods\AzertyRemap"
    $vieilInjecteur = Test-Path -LiteralPath $azertyMod

    if ((Test-Path -LiteralPath $dwmapi) -and $vieilInjecteur) {
        if (Test-Path -LiteralPath $dwmapiOff) { Remove-Item -LiteralPath $dwmapiOff -Force }
        Rename-Item -LiteralPath $dwmapi -NewName "dwmapi.dll.off" -Force
        Write-Host "  Ancien injecteur AZERTY desactive (dwmapi.dll -> .off)"
    }
    elseif (Test-Path -LiteralPath $dwmapi) {
        Write-Host "  UE4SS present et conserve (aucun injecteur AZERTY detecte)"
    }
    if ($vieilInjecteur) {
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

function Install-SubtitlesRuntime([string]$GameRoot, [string]$PackRoot) {
    $src = Join-Path $PackRoot "fichiers\subtitles_runtime"
    if (-not (Test-Path -LiteralPath $src)) {
        Write-Host "WARN: fichiers\subtitles_runtime absent — sous-titres non disponibles dans ce pack." -ForegroundColor Yellow
        return
    }
    $win64 = Join-Path $GameRoot "WTTGSD\Binaries\Win64"
    if (-not (Test-Path -LiteralPath $win64)) {
        throw "Binaries Win64 introuvable : $win64"
    }

    $ue4ssSrc = Join-Path $src "ue4ss_core"
    if (-not (Test-Path -LiteralPath $ue4ssSrc)) {
        throw "ue4ss_core manquant dans subtitles_runtime"
    }

    # Nettoyer un ancien layout « flat » (UE4SS.dll a la racine Win64) qui
    # double-charge / casse le scan avec le proxy moderne nested ue4ss/.
    foreach ($stale in @(
            (Join-Path $win64 "UE4SS.dll"),
            (Join-Path $win64 "UE4SS-settings.ini"),
            (Join-Path $win64 "UE4SS.log"),
            (Join-Path $win64 "override.txt")
        )) {
        if (Test-Path -LiteralPath $stale) { Remove-Item -LiteralPath $stale -Force }
    }
    foreach ($staleDir in @("Mods", "UE4SS_Signatures")) {
        $p = Join-Path $win64 $staleDir
        if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force }
    }

    $ue4ssDst = Join-Path $win64 "ue4ss"
    $existingNested = Test-Path -LiteralPath (Join-Path $ue4ssDst "UE4SS.dll")
    $dwmapiSrc = Join-Path $ue4ssSrc "dwmapi.dll"
    $dwmapiDst = Join-Path $win64 "dwmapi.dll"
    $dwmapiOff = Join-Path $win64 "dwmapi.dll.off"

    if ($existingNested) {
        Write-Host "  UE4SS existant detecte — on ajoute SousTitresFR (DLL / settings / autres mods conserves)."
        New-Item -ItemType Directory -Force -Path $ue4ssDst | Out-Null

        if (Test-Path -LiteralPath $dwmapiDst) {
            Write-Host "  Proxy dwmapi existant conserve."
        } elseif (Test-Path -LiteralPath $dwmapiOff) {
            Rename-Item -LiteralPath $dwmapiOff -NewName "dwmapi.dll" -Force
            Write-Host "  Proxy dwmapi reactive (.off -> .dll)"
        } elseif (Test-Path -LiteralPath $dwmapiSrc) {
            Copy-Item $dwmapiSrc $dwmapiDst -Force
            Write-Host "  Proxy dwmapi installe (aucun proxy present)."
        } else {
            Write-Host "WARN: dwmapi.dll manquant dans le pack et aucun proxy sur le jeu." -ForegroundColor Yellow
        }

        $sigSrcFile = Join-Path $ue4ssSrc "UE4SS_Signatures\StaticConstructObject.lua"
        if (Test-Path -LiteralPath $sigSrcFile) {
            $sigDir = Join-Path $ue4ssDst "UE4SS_Signatures"
            New-Item -ItemType Directory -Force -Path $sigDir | Out-Null
            $sigDstFile = Join-Path $sigDir "StaticConstructObject.lua"
            $sigBak = Join-Path $sigDir "StaticConstructObject.lua.bak-wttg3fr"
            if ((Test-Path -LiteralPath $sigDstFile) -and -not (Test-Path -LiteralPath $sigBak)) {
                Copy-Item $sigDstFile $sigBak -Force
            }
            Copy-Item $sigSrcFile $sigDstFile -Force
            Write-Host "  Signature StaticConstructObject installee (requise pour ce jeu)."
        }
    } else {
        if (Test-Path -LiteralPath $dwmapiSrc) {
            if (Test-Path -LiteralPath $dwmapiOff) { Remove-Item -LiteralPath $dwmapiOff -Force }
            Copy-Item $dwmapiSrc $dwmapiDst -Force
        } else {
            Write-Host "WARN: dwmapi.dll manquant dans le pack — lance scripts\build_subtitles_runtime.ps1" -ForegroundColor Yellow
        }

        New-Item -ItemType Directory -Force -Path $ue4ssDst | Out-Null
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
        if (Test-Path -LiteralPath $modsSrc) {
            Copy-Item (Join-Path $modsSrc "*") $modsDst -Recurse -Force
        }
    }

    $modSrc = Join-Path $ue4ssSrc "Mods\SousTitresFR"
    $modDst = Join-Path $ue4ssDst "Mods\SousTitresFR"
    if (Test-Path -LiteralPath $modSrc) {
        New-Item -ItemType Directory -Force -Path (Split-Path $modDst -Parent) | Out-Null
        if (Test-Path -LiteralPath $modDst) { Remove-Item -LiteralPath $modDst -Recurse -Force }
        Copy-Item $modSrc $modDst -Recurse -Force
    }

    $az = Join-Path $ue4ssDst "Mods\AzertyRemap"
    if (Test-Path -LiteralPath $az) {
        Remove-Item -LiteralPath $az -Recurse -Force
    }

    $modsTxt = Join-Path $ue4ssDst "Mods\mods.txt"
    Set-Ue4ssModLine $modsTxt "SousTitresFR" "1"

    $en = Join-Path $modDst "enabled.txt"
    if (Test-Path (Split-Path $en -Parent)) {
        Set-Content -Path $en -Value "1" -Encoding ASCII -NoNewline
    }

    if ($existingNested) {
        Write-Host "  SousTitresFR fusionne dans l'UE4SS existant."
    } else {
        Write-Host "  Sous-titres UE4SS deployes (dwmapi + SousTitresFR)"
    }
    Write-Host "  Note: antivirus peut signaler dwmapi.dll (injecteur)." -ForegroundColor Yellow
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

    # Always strip withdrawn AZERTY injector if present (v1.6.0)
    Write-Host "Nettoyage ancien injecteur AZERTY (si present)..."
    Remove-AzertyRuntimeLeftovers $game

    # Optional AZERTY: pak IMC only
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

    # Optional cinematic subtitles (UE4SS) — off by default.
    # Do not strip SousTitresFR before the prompt: a previous O then N must
    # also disable dwmapi when no other custom UE4SS mod remains.
    $hasSubtitles = Test-Path (Join-Path $pack "fichiers\subtitles_runtime\ue4ss_core\Mods\SousTitresFR\Scripts\main.lua")
    if ($hasSubtitles) {
        Write-Host ""
        Write-Host "Option sous-titres cinematiques (UE4SS) :" -ForegroundColor Cyan
        Write-Host "  Affiche en FR les voix (Wade, Simon, Cletus, …) — le jeu n'a aucun sous-titre natif."
        Write-Host "  Independant du pak FR ; utilise un injecteur (dwmapi.dll)."
        Write-Host "  Antivirus peut signaler dwmapi. Pas active par defaut."
        Write-Host "  Credit : contribution iPresing (PR #1)."
        Write-Host "  Si un UE4SS est deja la : on ajoute SousTitresFR sans ecraser tes autres mods."
        Write-Host "  N (y compris apres un O precedent) : retire SousTitresFR et coupe dwmapi"
        Write-Host "    s'il ne reste aucun autre mod UE4SS."
        $subs = Read-Host "Activer les sous-titres cinematiques ? (O/N)"
        if ($subs -match '^[oOyY]') {
            Write-Host "Deploiement sous-titres (UE4SS + SousTitresFR)..."
            Install-SubtitlesRuntime $game $pack
        } else {
            Write-Host "Sous-titres non installes."
            Disable-PackSubtitles $game
        }
    } else {
        Write-Host "Pack sans runtime sous-titres — nettoyage d'un eventuel SousTitresFR precedent..."
        Disable-PackSubtitles $game
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
