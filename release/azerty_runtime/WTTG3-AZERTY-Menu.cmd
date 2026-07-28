@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "AutoHotkey64.exe" (
  echo AutoHotkey64.exe manquant a cote de ce .cmd
  pause
  exit /b 1
)
if not exist "WTTG3-Menu-Touches.ahk" (
  echo WTTG3-Menu-Touches.ahk manquant
  pause
  exit /b 1
)
start "" "%~dp0AutoHotkey64.exe" "%~dp0WTTG3-Menu-Touches.ahk"
