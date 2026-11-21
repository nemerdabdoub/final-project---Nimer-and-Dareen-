@echo off
set "ROOT=%~dp0"
cd /d "%ROOT%1_CODE"
echo ===== Python =====
python --version
echo.
echo ===== Python libraries =====
python -c "import numpy, cv2, av, keyboard; print('numpy, opencv, av, keyboard: OK')"
python -c "import ultralytics; print('ultralytics (YOLO): OK')"
echo.
echo ===== Phone (you should see a line ending with the word  device ) =====
adb devices
echo.
echo ===== settings.txt =====
type settings.txt
echo.
pause
