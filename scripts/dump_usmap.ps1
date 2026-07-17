# Dump Mappings.usmap for WTTG3 (required for full UI extraction)
# UE4SS must be installed next to WTTGSD-Win64-Shipping.exe
#
# Steps:
# 1. Run this script OR start the game manually from the Win64 folder
# 2. Wait until the main menu loads
# 3. Focus the UE4SS GUI window -> Dumpers tab -> "Generate .usmap file"
#    OR press Ctrl+Numpad6
# 4. Confirm Mappings.usmap appears next to the exe

$LocRoot = Split-Path $PSScriptRoot -Parent
$GameRoot = $env:WTTG3_GAME
if (-not $GameRoot) {
  $local = Join-Path $LocRoot "local_game_path.txt"
  if (Test-Path $local) { $GameRoot = (Get-Content $local -Raw).Trim().Trim('"') }
}
if (-not $GameRoot) { throw "Definis WTTG3_GAME ou cree local_game_path.txt" }

$win64 = Join-Path $GameRoot "WTTGSD\Binaries\Win64"
$exe = Join-Path $win64 "WTTGSD-Win64-Shipping.exe"
$usmap = Join-Path $win64 "Mappings.usmap"
$dest = Join-Path $LocRoot "source\Mappings.usmap"

if (-not (Test-Path (Join-Path $win64 "UE4SS.dll"))) {
  Write-Host "UE4SS missing. Re-copy from tools\UE4SS"
  exit 1
}

Write-Host "Launching game with UE4SS..."
Write-Host "After menu: Dumpers -> Generate .usmap  (or Ctrl+Numpad6)"
Start-Process -FileName $exe -WorkingDirectory $win64

Write-Host "Watching for $usmap ..."
for ($i = 0; $i -lt 180; $i++) {
  if (Test-Path $usmap) {
    New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
    Copy-Item $usmap $dest -Force
    Write-Host "FOUND usmap -> $dest size=$((Get-Item $dest).Length)"
    exit 0
  }
  Start-Sleep -Seconds 5
}
Write-Host "Timeout: usmap not created. Generate it manually in UE4SS then re-run."
exit 2
