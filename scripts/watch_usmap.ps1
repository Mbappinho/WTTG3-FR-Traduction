param(
  [int]$TimeoutSec = 300
)
# Launch game + poll for Mappings.usmap. Requires Generate click in UE4SS GUI.
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

if (Test-Path $usmap) {
  New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
  Copy-Item $usmap $dest -Force
  Write-Host "Already present -> $dest"
  exit 0
}

$proc = Get-Process -Name "WTTGSD-Win64-Shipping" -ErrorAction SilentlyContinue
if (-not $proc) {
  Write-Host "Starting game..."
  Start-Process -FilePath $exe -WorkingDirectory $win64
} else {
  Write-Host "Game already running."
}

$deadline = (Get-Date).AddSeconds($TimeoutSec)
while ((Get-Date) -lt $deadline) {
  if (Test-Path $usmap) {
    New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
    Copy-Item $usmap $dest -Force
    Write-Host "FOUND usmap -> $dest size=$((Get-Item $dest).Length)"
    exit 0
  }
  Start-Sleep -Seconds 3
}
Write-Host "Timeout waiting for usmap"
exit 2
