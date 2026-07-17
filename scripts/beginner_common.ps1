# Shared helpers for beginner install / uninstall (French prompts).
$ErrorActionPreference = "Stop"

function Write-Title([string]$Text) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $Text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Pause-Exit([int]$Code = 0) {
    Write-Host ""
    Write-Host "Appuie sur Entree pour fermer..."
    [void][System.Console]::ReadLine()
    exit $Code
}

function Test-GameLooksValid([string]$Root) {
    if (-not $Root) { return $false }
    $paks = Join-Path $Root "WTTGSD\Content\Paks"
    $exe = Join-Path $Root "WTTGSD\Binaries\Win64\WTTGSD-Win64-Shipping.exe"
    return (Test-Path $paks) -and (Test-Path $exe)
}

function Find-CandidateGameRoots {
    $candidates = New-Object System.Collections.Generic.List[string]
    $add = {
        param($p)
        if ($p -and (Test-Path $p) -and (Test-GameLooksValid $p) -and -not $candidates.Contains($p)) {
            $candidates.Add($p) | Out-Null
        }
    }

    $steamRoots = @(
        "${env:ProgramFiles(x86)}\Steam\steamapps\common",
        "$env:ProgramFiles\Steam\steamapps\common",
        "D:\SteamLibrary\steamapps\common",
        "E:\SteamLibrary\steamapps\common"
    )
    foreach ($lib in $steamRoots) {
        if (-not (Test-Path $lib)) { continue }
        Get-ChildItem $lib -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $name = $_.Name
            if ($name -match "Welcome|WTTG|Game.?III") {
                & $add $_.FullName
                & $add (Join-Path $_.FullName "game")
            }
        }
    }
    return $candidates
}

function Select-GameRoot {
    Write-Title "Dossier du jeu"
    $found = @(Find-CandidateGameRoots)
    if ($found.Count -gt 0) {
        Write-Host "Dossiers detectes :"
        for ($i = 0; $i -lt $found.Count; $i++) {
            Write-Host ("  [{0}] {1}" -f ($i + 1), $found[$i])
        }
        Write-Host "  [M] Entrer le chemin a la main"
        Write-Host ""
        $choice = Read-Host "Choix"
        if ($choice -match '^\d+$') {
            $idx = [int]$choice - 1
            if ($idx -ge 0 -and $idx -lt $found.Count) { return $found[$idx] }
        }
    } else {
        Write-Host "Aucun dossier de jeu detecte automatiquement."
        Write-Host ""
    }

    Write-Host "Exemple Steam :"
    Write-Host '  C:\Program Files (x86)\Steam\steamapps\common\Welcome to the Game III'
    Write-Host "Exemple crack / copie locale :"
    Write-Host '  C:\Users\...\Welcome.to.the.Game.III\game'
    Write-Host ""
    $manual = Read-Host "Chemin complet du dossier du jeu"
    $manual = $manual.Trim().Trim('"')
    if (-not (Test-GameLooksValid $manual)) {
        throw "Ce dossier ne ressemble pas a WTTG3 (Paks / exe introuvables) : $manual"
    }
    return $manual
}

function Assert-GameClosed {
    $procs = Get-Process -Name "WTTGSD-Win64-Shipping" -ErrorAction SilentlyContinue
    if ($procs) {
        Write-Host "Le jeu est encore ouvert. Ferme-le puis relance cet outil." -ForegroundColor Yellow
        throw "Jeu ouvert (WTTGSD-Win64-Shipping)"
    }
}

function Get-PackRoot {
    # When scripts live inside release\WTTG3-FR-Beginner\scripts
    $packFromScripts = Resolve-Path (Join-Path $PSScriptRoot "..") -ErrorAction SilentlyContinue
    if ($packFromScripts -and (Test-Path (Join-Path $packFromScripts "fichiers\paks"))) {
        return $packFromScripts.Path
    }
    # Dev fallback: repo\release\WTTG3-FR-Beginner
    $repo = Resolve-Path (Join-Path $PSScriptRoot "..") -ErrorAction SilentlyContinue
    if ($repo) {
        $release = Join-Path $repo.Path "release\WTTG3-FR-Beginner"
        if (Test-Path (Join-Path $release "fichiers\paks")) { return $release }
    }
    throw "Pack introuvable. Lance d'abord : scripts\build_beginner_pack.ps1"
}
