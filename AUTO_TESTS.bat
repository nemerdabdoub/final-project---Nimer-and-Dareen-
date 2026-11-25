@echo off
rem AUTO TESTS: 10 s countdown -> take off -> climb ~1.5 m -> TURN (40 s) -> FOLLOW (60 s) -> SIDE (40 s) -> land.
rem Esc in the window = stop (hover). FORCE_LAND.bat works any time. Phone in hand. User 4 m in front, turban on.
cd /d "%~dp01_CODE"
set DRONE_SIM=
"C:\Users\LORENenvs\gpu\Scripts\python.exe" run_with_adb.py session.py --auto
pause
