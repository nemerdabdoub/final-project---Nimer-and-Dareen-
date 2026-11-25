@echo off
rem FORCE LAND: lands the drone through the running script (drone_interface checks 1_CODE\FORCE_LAND). Double-click.
cd /d "%~dp01_CODE"
python force_land.py
pause
