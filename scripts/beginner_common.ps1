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
        try {
            if (-not (Test-Path -LiteralPath $lib)) { continue }
        } catch { continue }
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
    Write-Host "Exemple dossier local :"
    Write-Host '  C:\Games\Welcome to the Game III'
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

function Get-SteamTarget([string]$PackRoot) {
    $path = Join-Path $PackRoot "fichiers\steam_target.json"
    if (-not (Test-Path $path)) { return $null }
    return (Get-Content -Raw -Encoding UTF8 $path | ConvertFrom-Json)
}

function Find-SteamAppManifest([string]$GameRoot, [string]$AppId) {
    if (-not $AppId) { $AppId = "3869850" }
    $name = "appmanifest_$AppId.acf"
    $candidates = New-Object System.Collections.Generic.List[string]

    # ...\steamapps\common\<Game> → ...\steamapps\appmanifest_*.acf
    try {
        $common = Split-Path -Parent $GameRoot
        $steamapps = Split-Path -Parent $common
        if ($steamapps) {
            $candidates.Add((Join-Path $steamapps $name)) | Out-Null
        }
    } catch {}

    foreach ($lib in @(
            "${env:ProgramFiles(x86)}\Steam\steamapps",
            "$env:ProgramFiles\Steam\steamapps",
            "C:\Steam\steamapps",
            "D:\SteamLibrary\steamapps",
            "E:\SteamLibrary\steamapps"
        )) {
        try {
            if ($lib -and (Test-Path -LiteralPath $lib)) {
                $candidates.Add((Join-Path $lib $name)) | Out-Null
            }
        } catch {}
    }

    foreach ($p in $candidates) {
        try {
            if ($p -and (Test-Path -LiteralPath $p)) { return $p }
        } catch {}
    }
    return $null
}

function Get-SteamBuildIdFromManifest([string]$ManifestPath) {
    if (-not $ManifestPath -or -not (Test-Path -LiteralPath $ManifestPath)) { return $null }
    $raw = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8
    $m = [regex]::Match($raw, '"buildid"\s+"(\d+)"')
    if ($m.Success) { return $m.Groups[1].Value }
    return $null
}

<#
.SYNOPSIS
  Compare installed Steam BuildID to pack target.
.OUTPUTS
  Hashtable: Status = Match | Mismatch | Unknown ; Installed ; Expected ; Manifest
#>
function Test-SteamBuildCompatibility([string]$GameRoot, [string]$PackRoot) {
    $target = Get-SteamTarget $PackRoot
    $expected = if ($target) { [string]$target.steam_buildid } else { $null }
    $appId = if ($target) { [string]$target.steam_appid } else { "3869850" }
    $packVer = if ($target) { [string]$target.pack_version } else { "?" }

    $manifest = Find-SteamAppManifest $GameRoot $appId
    $installed = Get-SteamBuildIdFromManifest $manifest

    $status = "Unknown"
    if ($expected -and $installed) {
        $status = if ($installed -eq $expected) { "Match" } else { "Mismatch" }
    }

    return @{
        Status     = $status
        Installed  = $installed
        Expected   = $expected
        Manifest   = $manifest
        PackVersion = $packVer
        AppId      = $appId
    }
}

function Show-SteamBuildCheck([hashtable]$Info) {
    Write-Host ""
    Write-Host "Compatibilite Steam (BuildID)" -ForegroundColor Cyan
    Write-Host ("  Pack FR          : v{0}" -f $Info.PackVersion)
    Write-Host ("  BuildID attendu  : {0}" -f $(if ($Info.Expected) { $Info.Expected } else { "(inconnu dans le pack)" }))
    Write-Host ("  BuildID detecte  : {0}" -f $(if ($Info.Installed) { $Info.Installed } else { "(introuvable - copie non Steam ?)" }))
    if ($Info.Manifest) {
        Write-Host ("  Manifest         : {0}" -f $Info.Manifest)
    }

    switch ($Info.Status) {
        "Match" {
            Write-Host ""
            Write-Host "OK - Version du jeu compatible avec ce pack." -ForegroundColor Green
        }
        "Mismatch" {
            Write-Host ""
            Write-Host "ATTENTION - BuildID different : ce pack peut CRASH au lancement." -ForegroundColor Yellow
            Write-Host "Telecharge une release FR rebuildee pour ta maj Steam, ou desinstalle si ca plante." -ForegroundColor Yellow
        }
        default {
            Write-Host ""
            Write-Host "INFO - Impossible de verifier le BuildID (pas de manifest Steam trouve)." -ForegroundColor Yellow
            Write-Host "Si ce n'est pas l'install Steam officielle, le risque de crash est plus eleve." -ForegroundColor Yellow
        }
    }
}
