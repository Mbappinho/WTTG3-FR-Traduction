# Apply WTTG3 FR patch (PDF + achievements). Does NOT touch WebSites.
param(
  [string]$GameRoot = $env:WTTG3_GAME,
  [string]$LocRoot = (Split-Path $PSScriptRoot -Parent)
)
if (-not $GameRoot) {
  $local = Join-Path $LocRoot "local_game_path.txt"
  if (Test-Path $local) { $GameRoot = (Get-Content $local -Raw).Trim().Trim('"') }
}
if (-not $GameRoot) { throw "Definis WTTG3_GAME ou cree local_game_path.txt" }

$ErrorActionPreference = "Stop"
$pdfSrc = Join-Path $LocRoot "build\pdfs"
$pdfDst = Join-Path $GameRoot "WTTGSD\Content\RawFiles\PDFS"
$achSrc = Join-Path $LocRoot "build\achievements_fr.json"
$achDst = Join-Path $GameRoot "Engine\Binaries\ThirdParty\Steamworks\Steamv157\Win64\steam_settings\achievements.json"

if (-not (Test-Path $pdfSrc)) { throw "Missing build\pdfs - run scripts/build_translations.py first" }
if (-not (Test-Path $pdfDst)) { throw "Missing game PDFS folder" }

Write-Host "Copying PDFS FR -> $pdfDst"
Copy-Item -Path (Join-Path $pdfSrc "*") -Destination $pdfDst -Recurse -Force

if ((Test-Path $achSrc) -and (Test-Path (Split-Path $achDst -Parent))) {
  Write-Host "Copying achievements FR -> $achDst"
  Copy-Item $achSrc $achDst -Force
} else {
  Write-Host "Skipping achievements overlay (path missing)"
}

Write-Host "Done. WebSites were NOT modified."
