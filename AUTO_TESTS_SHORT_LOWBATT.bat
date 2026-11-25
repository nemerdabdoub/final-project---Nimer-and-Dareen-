@echo off
rem SHORT auto run for a LOW battery (about 3 min): take off -> FOLLOW (60 s) -> ORBIT (30 s) -> land.
rem Follow stops at 15% drone battery (normal: 30%). If DJI warns or starts landing by itself: let it land.
rem Esc = stop (hover). FORCE_LAND.bat works any time. Phone in hand.
cd /d "%~dp01_CODE"
set DRONE_SIM=
"C:\Users\LOREN\venvs\gpu\Scripts\python.exe" run_with_adb.py session.py --auto --low-battery 15 --only "FOLLOW TEST,ORBIT TEST"
pause
