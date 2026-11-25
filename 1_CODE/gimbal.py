"""
gimbal.py - Project 3760: tilt the DJI Neo camera (1-axis gimbal) from the laptop, through ADB drags on DJI Fly.

Found 25.11 with the drone on the table (A3b): in DJI Fly's camera view there is a handle ( ^ = v ) on the LEFT of the live
picture. Dragging it UP tilts the camera up, DOWN tilts it down; the angle shows on a scale while dragging (green dot at 0).
  * range: -90 deg (straight down) ... about +50 deg (up)
  * about 11.4 phone pixels of drag per degree (portrait screen 1080 x 2280, handle at x=55, y=536)
  * the angle is NOT read back by code yet -> tilt_to() first drives to the -90 stop (always the same), then up by a known
    number of degrees. tilt_by() moves relative to wherever it is.
NOTE: measured in the PORTRAIT layout of DJI Fly. If the flight screen is in LANDSCAPE, the handle moves (left side, middle
height) -> re-measure (python gimbal.py calibrate) before using it in flight.
REMOVE THE GIMBAL GUARD before tilting.

  python gimbal.py to -30      camera to -30 deg (looking down 30 deg, e.g. "from above" filming)
  python gimbal.py by 10       10 deg further up (negative = down)
  python gimbal.py level       back to 0 deg
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ADB = os.path.join(HERE, "adb.exe")
HANDLE_X, HANDLE_Y = 55, 536        # portrait layout, phone pixels
PX_PER_DEG = 11.4
MAX_DRAG = 285                      # one drag at a time (stays on the screen)
MIN_DEG, MAX_DEG = -90, 50


def _drag(dy, ms=1500):
    """dy < 0 = drag up = camera up"""
    subprocess.run([ADB, "shell", "input", "swipe", str(HANDLE_X), str(HANDLE_Y), str(HANDLE_X), str(int(HANDLE_Y + dy)),
                    str(ms)], check=True)
    time.sleep(0.3)


def tilt_by(deg):
    """move the camera deg degrees (+ up, - down), relative"""
    px = -deg * PX_PER_DEG
    while abs(px) > 1:
        step = max(-MAX_DRAG, min(MAX_DRAG, px))
        _drag(step)
        px -= step


def tilt_to(deg):
    """absolute: to the -90 stop first, then up to deg"""
    deg = max(MIN_DEG, min(MAX_DEG, deg))
    for _ in range(5):                    # 5 x 25 deg > 140 deg = surely at the bottom stop
        _drag(MAX_DRAG)
    tilt_by(deg - MIN_DEG)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "to":
        tilt_to(float(a[1]))
    elif a[0] == "by":
        tilt_by(float(a[1]))
    elif a[0] == "level":
        tilt_to(0)
    else:
        sys.exit(__doc__)
    print("done")
