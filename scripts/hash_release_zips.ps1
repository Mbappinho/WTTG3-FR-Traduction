# Write SHA256 sidecars for GitHub release assets (upload *.zip.sha256 next to the zips).
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
Write-Host "Joins les fichiers .sha256 aux assets de la GitHub Release (l'installeur Full les verifie)."
