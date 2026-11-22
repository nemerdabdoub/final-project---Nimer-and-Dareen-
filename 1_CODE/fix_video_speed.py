"""
fix_video_speed.py - Project 3493
The first version of connection_test.py saved demo.mp4 at 20 frames/s although about 50 mirror
frames/s were written, so the video plays in slow motion (about 2.5 times slower than real).
This script re-saves it with the correct speed:  demo.mp4  ->  demo_realtime.mp4
The original file is not changed.

Run in the project folder:   python fix_video_speed.py
Optional:                    python fix_video_speed.py demo.mp4 demo_realtime.mp4 60
                             (the last number = how many seconds the recording really lasted)
"""
import csv
import sys

import cv2

src = sys.argv[1] if len(sys.argv) > 1 else "demo.mp4"
dst = sys.argv[2] if len(sys.argv) > 2 else "demo_realtime.mp4"
if len(sys.argv) > 3:
    seconds = float(sys.argv[3])
else:
    # the recording lasted min(60 s, the length of the test) - the test length is in connection_log.csv
    try:
        with open("connection_log.csv") as f:
            rows = list(csv.reader(f))[1:]
        run = float(rows[-1][0])
    except Exception:
        run = 60.0
    seconds = min(60.0, run)

cap = cv2.VideoCapture(src)
if not cap.isOpened():
    sys.exit(f"Cannot open {src}")
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
old_fps = cap.get(cv2.CAP_PROP_FPS)
new_fps = n / seconds
print(f"{src}: {n} frames, saved at {old_fps:.0f} fps -> plays for {n / old_fps:.0f} s")
print(f"the recording really lasted about {seconds:.0f} s, so the true rate is {new_fps:.1f} fps")

out = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), new_fps, (w, h))
while True:
    ok, frame = cap.read()
    if not ok:
        break
    out.write(frame)
out.release()
cap.release()
print(f"saved {dst}: now plays for about {seconds:.0f} s, in real time")
