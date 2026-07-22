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

    # ...\steamapps\common\<Game> -> ...\steamapps\appmanifest_*.acf
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

# --- Auto-update from GitHub Releases (Full pack only) ---

$script:Wttg3FrGitHubRepo = "Mbappinho/WTTG3-FR-Traduction"
$script:Wttg3FrZipAsset = "WTTG3-FR-Traduction.zip"
$script:Wttg3FrTargetAsset = "steam_target.json"

function ConvertTo-PackVersion([string]$Raw) {
    if (-not $Raw) { return [version]"0.0.0" }
    $v = $Raw.Trim().TrimStart("v", "V")
    if ($v -notmatch '^\d+(\.\d+){0,3}$') { return [version]"0.0.0" }
    # Normalize 1.4 -> 1.4.0 for [version]
    $parts = $v.Split(".")
    while ($parts.Count -lt 2) { $parts += "0" }
    try { return [version]($parts -join ".") } catch { return [version]"0.0.0" }
}

function Get-GitHubLatestReleaseInfo {
    $uri = "https://api.github.com/repos/$script:Wttg3FrGitHubRepo/releases/latest"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $rel = Invoke-RestMethod -Uri $uri -Headers @{
            "User-Agent" = "WTTG3-FR-Installer"
            "Accept"     = "application/vnd.github+json"
        } -TimeoutSec 30
        return $rel
    } catch {
        return $null
    }
}

function Find-ReleaseAssetUrl($Release, [string]$AssetName) {
    if (-not $Release -or -not $Release.assets) { return $null }
    foreach ($a in $Release.assets) {
        if ([string]$a.name -eq $AssetName) { return [string]$a.browser_download_url }
    }
    return $null
}

function Get-RemoteSteamTarget($Release) {
    $url = Find-ReleaseAssetUrl $Release $script:Wttg3FrTargetAsset
    if (-not $url) { return $null }
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $tmp = Join-Path $env:TEMP ("wttg3_fr_steam_target_{0}.json" -f [guid]::NewGuid().ToString("N"))
        Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing -Headers @{ "User-Agent" = "WTTG3-FR-Installer" } -TimeoutSec 30
        $obj = Get-Content -Raw -Encoding UTF8 $tmp | ConvertFrom-Json
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
        return $obj
    } catch {
        return $null
    }
}

function Expand-FrPackZip([string]$ZipPath, [string]$DestDir) {
    if (Test-Path $DestDir) { Remove-Item $DestDir -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $DestDir)
    # Zip may contain files at root (LIREMOI, fichiers\, ...) or a single top folder
    if (Test-Path (Join-Path $DestDir "fichiers\paks")) { return $DestDir }
    $sub = Get-ChildItem $DestDir -Directory | Select-Object -First 1
    if ($sub -and (Test-Path (Join-Path $sub.FullName "fichiers\paks"))) { return $sub.FullName }
    throw "Zip telecharge invalide (fichiers\paks manquant)."
}

<#
.SYNOPSIS
  Optionally download the latest Full pack from GitHub if newer / better BuildID match.
.OUTPUTS
  New pack root path (may be same as input).
#>
function Update-PackFromGitHubIfNeeded([string]$PackRoot, [hashtable]$Compat) {
    Write-Host ""
    Write-Host "Mise a jour automatique (GitHub)" -ForegroundColor Cyan
    Write-Host ("  Repo : https://github.com/{0}/releases" -f $script:Wttg3FrGitHubRepo)

    $rel = Get-GitHubLatestReleaseInfo
    if (-not $rel) {
        Write-Host "  Impossible de joindre GitHub (hors ligne ?). On continue avec ce pack." -ForegroundColor Yellow
        return $PackRoot
    }

    $tag = [string]$rel.tag_name
    $remoteTarget = Get-RemoteSteamTarget $rel
    $remoteVerStr = if ($remoteTarget -and $remoteTarget.pack_version) { [string]$remoteTarget.pack_version } else { $tag.TrimStart("v", "V") }
    $remoteBuild = if ($remoteTarget) { [string]$remoteTarget.steam_buildid } else { $null }
    $localVer = ConvertTo-PackVersion $Compat.PackVersion
    $remoteVer = ConvertTo-PackVersion $remoteVerStr
    $playerBuild = $Compat.Installed

    Write-Host ("  Derniere release : {0} (pack v{1})" -f $tag, $remoteVerStr)
    if ($remoteBuild) {
        Write-Host ("  BuildID distant  : {0}" -f $remoteBuild)
    } else {
        Write-Host "  BuildID distant  : (pas de steam_target.json sur la release)"
    }

    $newer = $remoteVer -gt $localVer
    $betterMatch = $false
    if ($playerBuild -and $remoteBuild) {
        if ($Compat.Status -eq "Mismatch" -and $remoteBuild -eq $playerBuild) { $betterMatch = $true }
        if ($remoteBuild -eq $playerBuild -and $newer) { $betterMatch = $true }
    } elseif ($Compat.Status -eq "Mismatch" -and $newer) {
        $betterMatch = $true
    }

    if (-not $newer -and -not $betterMatch) {
        Write-Host "  Deja a jour (ou pas de meilleure release pour ton BuildID)." -ForegroundColor Green
        return $PackRoot
    }

    $reason = if ($betterMatch -and $Compat.Status -eq "Mismatch") {
        "Ce pack ne matche pas ton BuildID Steam ; une release GitHub semble meilleure."
    } elseif ($newer) {
        "Une version plus recente du pack FR est disponible."
    } else {
        "Une mise a jour est disponible."
    }
    Write-Host ""
    Write-Host $reason -ForegroundColor Yellow
    $ans = Read-Host "Telecharger et utiliser la derniere release GitHub ? (O/N)"
    if ($ans -notmatch '^[oOyY]') {
        Write-Host "  OK - on garde ce pack local."
        return $PackRoot
    }

    $zipUrl = Find-ReleaseAssetUrl $rel $script:Wttg3FrZipAsset
    if (-not $zipUrl) {
        Write-Host ("  Asset {0} introuvable sur la release. Abandon maj." -f $script:Wttg3FrZipAsset) -ForegroundColor Yellow
        return $PackRoot
    }

    $work = Join-Path $env:TEMP ("WTTG3-FR-update-" + [guid]::NewGuid().ToString("N"))
    $zipPath = Join-Path $work $script:Wttg3FrZipAsset
    New-Item -ItemType Directory -Force -Path $work | Out-Null
    try {
        Write-Host "  Telechargement..."
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing -Headers @{ "User-Agent" = "WTTG3-FR-Installer" } -TimeoutSec 600
        Write-Host "  Extraction..."
        $extractRoot = Join-Path $work "extracted"
        $newPack = Expand-FrPackZip $zipPath $extractRoot
        Write-Host ("  Pack distant pret : {0}" -f $newPack) -ForegroundColor Green
        return $newPack
    } catch {
        Write-Host ("  Echec maj auto : {0}" -f $_.Exception.Message) -ForegroundColor Yellow
        Write-Host "  On continue avec ce pack local."
        return $PackRoot
    }
}
