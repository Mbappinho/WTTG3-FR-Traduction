# Restore original English PDFS from backup
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
$pdfSrc = Join-Path $LocRoot "backup\PDFS"
$pdfDst = Join-Path $GameRoot "WTTGSD\Content\RawFiles\PDFS"
$achSrc = Join-Path $LocRoot "source\achievements_en.json"
$achDst = Join-Path $GameRoot "Engine\Binaries\ThirdParty\Steamworks\Steamv157\Win64\steam_settings\achievements.json"

Copy-Item -Path (Join-Path $pdfSrc "*") -Destination $pdfDst -Recurse -Force
if ((Test-Path $achSrc) -and (Test-Path (Split-Path $achDst -Parent))) {
  Copy-Item $achSrc $achDst -Force
}
Write-Host "Restored English PDFS (+ achievements if present)."
