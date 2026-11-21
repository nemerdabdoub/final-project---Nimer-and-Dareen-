"""
connection_test.py - Project 3493, milestone 19.10 ("stable connection for 10 minutes")
The drone stays ON THE GROUND (or hovering, flown by hand) - this script never moves it.

What it does:
  * shows the live video from the drone on the laptop
  * logs every second: frames received, FPS, longest gap between frames
  * saves a log (.csv) and the first minute as a video (.mp4) into 3_EVIDENCE/<today's date>/ - nothing is overwritten
  * prints a summary at the end -> numbers for Gabi

Stop early: click the video window and press Q (English keyboard) or Esc,
or press Ctrl+C in the terminal - the summary is printed either way.
Shorter test: python connection_test.py 3   (= 3 minutes, e.g. to avoid overheating)
"""
import csv
import os
import sys
import time
import cv2
from drone_interface import Drone
from paths import evidence_dir, stamp

TEST_SECONDS = (float(sys.argv[1]) if len(sys.argv) > 1 else 10) * 60   # minutes from the command line, default 10
RECORD_SECONDS = 60             # how much of the test to save as demo video
VIDEO_FPS = 25                  # the saved video is written at this rate, so it plays in real time
GAP_ALERT_S = 1.0               # a gap longer than this counts as a "drop"

EV, STAMP = evidence_dir(), stamp()
LOG_PATH = os.path.join(EV, f"{STAMP}_connection_test_log.csv")
VIDEO_PATH = os.path.join(EV, f"{STAMP}_connection_test_video.mp4")

with Drone() as drone, open(LOG_PATH, "w", newline="") as f:
    log = csv.writer(f)
    log.writerow(["t_s", "frames_this_second", "fps", "max_gap_s"])

    start = time.time()
    last_frame_t = start
    sec_start, sec_frames, max_gap = start, 0, 0.0
    total_frames, drops, worst_gap = 0, 0, 0.0
    writer = None
    written = 0
    last_sig = None
    loops = 0

    try:
      while time.time() - start < TEST_SECONDS:
          frame = drone.get_frame()
          now = time.time()
          loops += 1
          # a frame counts as NEW only if its content changed (the library may hand back
          # the same picture many times; a coarse grid of pixels is enough to tell)
          sig = None if frame is None else hash(frame[::8, ::8].tobytes())
          if sig is not None and sig != last_sig:
              gap = now - last_frame_t
              max_gap = max(max_gap, gap)
              worst_gap = max(worst_gap, gap)
              if gap > GAP_ALERT_S:
                  drops += 1
              last_frame_t, last_sig = now, sig
              sec_frames += 1
              total_frames += 1

              if now - start < RECORD_SECONDS:
                  if writer is None:
                      h, w = frame.shape[:2]
                      writer = cv2.VideoWriter(VIDEO_PATH, cv2.VideoWriter_fourcc(*"mp4v"), VIDEO_FPS, (w, h))
                  # keep the video in REAL TIME: write the picture as many times as needed so that
                  # (frames written) = (seconds passed) x VIDEO_FPS, whatever the speed of this loop
                  target = int((now - start) * VIDEO_FPS) + 1
                  while written < target:
                      writer.write(frame)
                      written += 1

              shown = frame.copy()
              cv2.putText(shown, f"t={now - start:5.0f}s  frames={total_frames}", (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
              cv2.imshow("drone view", shown)

          key = cv2.waitKey(1) & 0xFF
          if key in (ord("q"), ord("Q"), 27):      # Q or Esc
              break

          if now - sec_start >= 1.0:
              log.writerow([round(now - start, 1), sec_frames, round(sec_frames / (now - sec_start), 1), round(max_gap, 3)])
              sec_start, sec_frames, max_gap = now, 0, 0.0

    except KeyboardInterrupt:
        print("\nStopped with Ctrl+C")
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    duration = time.time() - start
    print("\n===== SUMMARY =====")
    print(f"duration:        {duration / 60:.1f} min")
    print(f"average FPS:     {total_frames / duration:.1f}   (new frames only)")
    print(f"loop rate:       {loops / duration:.1f} reads/s (for reference)")
    print(f"worst gap:       {worst_gap:.2f} s")
    print(f"drops (> {GAP_ALERT_S}s):  {drops}")
    print(f"log:   {LOG_PATH}")
    print(f"video: {VIDEO_PATH}")
