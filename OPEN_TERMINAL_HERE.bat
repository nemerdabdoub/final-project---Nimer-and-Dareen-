@echo off
set "ROOT=%~dp0"
cd /d "%ROOT%1_CODE"
title Drone project - terminal inside 1_CODE
echo You are inside: %cd%
echo.
echo Type for example:   python connection_test.py 1
echo Safety: phone in your hand, DJI Fly in Manual Control. Ctrl+C = stop, then hold Land on the phone.
echo.
cmd /k
