"""
countdown.py - a BIG full-screen countdown on the laptop, then runs a drone script (for testing alone: walk into place first).
  python countdown.py 45 m06_follow.py --live --dry --seconds 120
"""
import os
import subprocess
import sys
import time

import cv2
import numpy as np

n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
rest = sys.argv[2:]
win = "COUNTDOWN - get into place"
cv2.namedWindow(win, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
end = time.time() + n
while True:
    left = int(round(end - time.time()))
    if left <= 0:
        break
    img = np.zeros((1080, 1920, 3), np.uint8)
    img[:] = (0, 120, 0) if left > 10 else (0, 140, 255)
    cv2.putText(img, str(left), (560 if left >= 10 else 760, 760), cv2.FONT_HERSHEY_SIMPLEX, 22, (255, 255, 255), 60)
    cv2.putText(img, "turban on - stand 2-3 m in front of the drone", (300, 980), cv2.FONT_HERSHEY_SIMPLEX, 1.8,
                (255, 255, 255), 4)
    cv2.imshow(win, img)
    if cv2.waitKey(100) & 0xFF == 27:
        sys.exit("cancelled")
img = np.zeros((1080, 1920, 3), np.uint8)
cv2.putText(img, "GO - starting (about 30 s to load)", (220, 560), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 8)
cv2.imshow(win, img)
cv2.waitKey(1500)
cv2.destroyAllWindows()
if rest:
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, "run_with_adb.py"), *rest], cwd=here)
