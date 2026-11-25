---
description: Pre-flight check before taking off (read only; never moves the drone)
---
Run from the repo root: `python 1_CODE/preflight.py`

Show the result to the user as a short list with ✅ (OK), ❌ (FAIL) and ⚠️ (WARN), then the "by hand" items as tick boxes.

- If it ends with READY: tell the user it is ready, and that THEY start the flight: `cd 1_CODE` then `python run_with_adb.py record_video.py`
  (or the script they planned), press **T** to take off; with no stick input the drone hovers; **L** = land; emergency = thumb on the
  phone or double-click `FORCE_LAND.bat`. Do NOT start a take-off yourself.
- If it ends with NOT READY: list only what failed and how to fix each item, and say clearly: do not fly yet.
