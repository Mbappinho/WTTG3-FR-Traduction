# Write local SHA256 sidecars for the release zips (optional maintainer check).
# Do NOT upload *.zip.sha256 to GitHub Releases — players would not know which file to download.
# The Full installer verifies the zip via the GitHub API asset digest.
# Run AFTER Compress-Archive of the Full / Nexus packs.
param(
    [string]$LocRoot = (Split-Path $PSScriptRoot -Parent)
)
$ErrorActionPreference = "Stop"
$names = @(
    "WTTG3-FR-Traduction.zip",
    "WTTG3-FR-Traduction-Nexus.zip"
)
$any = $false
foreach ($name in $names) {
    $zip = Join-Path $LocRoot "release\$name"
    if (-not (Test-Path -LiteralPath $zip)) {
        Write-Host "SKIP: $name absent"
        continue
    }
    $hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
    $line = "$hash  $name"
    Set-Content -Path ($zip + ".sha256") -Value $line -Encoding ASCII
    Write-Host "$name"
    Write-Host "  SHA256 $hash"
    $any = $true
}
if (-not $any) {
    throw "Aucun zip release trouve. Cree d'abord WTTG3-FR-Traduction.zip / -Nexus.zip sous release\"
}
Write-Host "Hash local OK. Ne PAS uploader les .sha256 sur GitHub (les joueurs ne sauraient plus quel zip prendre)."
Write-Host "L'installeur Full utilise le digest SHA256 deja fourni par l'API GitHub sur le zip."
