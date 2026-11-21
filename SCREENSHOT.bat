@echo off
setlocal
set "ROOT=%~dp0"
set "NAME=%~1"
if "%NAME%"=="" set "NAME=screen"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "D=%%i"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format HHmmss"') do set "T=%%i"
set "OUT=%ROOT%3_EVIDENCE\%D%"
mkdir "%OUT%" 2>nul
"%ROOT%1_CODE\adb.exe" exec-out screencap -p > "%OUT%\%T%_%NAME%.png"
echo Saved: %OUT%\%T%_%NAME%.png
if "%~1"=="" pause
