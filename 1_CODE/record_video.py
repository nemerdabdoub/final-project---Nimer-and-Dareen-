"""
record_video.py - Project 3760
Record the drone's camera to a video file, saved AUTOMATICALLY in 3_EVIDENCE/<today's date>/.
Made for the detection data shoot: aim with the live window, record the user and the obstacles.

  python record_video.py                 record until you press Esc (or Ctrl+C), then it saves
  python record_video.py 3               record 3 minutes, then stop and save
  python record_video.py 3 user_5m       record 3 min; the file is named ..._user_5m.mp4
  python record_video.py 0 bikes         record until Esc; the file is named ..._bikes.mp4

The video is written in REAL TIME (correct speed) whatever the screen-mirror rate.
Phone in DJI Fly showing the camera. Press Esc in the window, or Ctrl+C here, to stop and save.

Keys in the window (click the window first so it gets the keys):
  T = TAKE OFF   (DJI Fly must show the Take Off circle)
  L = LAND       (two-step landing of DJI Fly, checked on the screen)
  Esc = stop recording and save (does NOT land - if the drone is up, press L first, or land by hand)
Take-off and landing run in the background, so the video keeps recording while they happen.
SAFETY: phone in hand, DJI Fly in Manual Control, open space, battery > 40%. If anything looks wrong, land by hand.
"""
import os
import sys
import threading
import time

import cv2
from drone_interface import Drone

try:
    from paths import evidence_dir, stamp
except ImportError:                       # running outside the organised folder
    def evidence_dir():
        return "."
    def stamp():
        return time.strftime("%H%M%S")

VIDEO_FPS = 25                            # the saved video plays at this rate


class Commands:
    """Runs take-off / landing in a background thread so the recording loop never stops."""

    def __init__(self, drone):
        self.drone = drone
        self.busy = None                  # "TAKING OFF" / "LANDING" while running
        self.status = "T = take off   L = land   Esc = stop rec"

    def start(self, name):
        if self.busy:
            print(f"Ignored: still {self.busy.lower()} ...")
            return
        self.busy = "TAKING OFF" if name == "takeoff" else "LANDING"
        self.status = self.busy + " ..."
        print(f"\n[{time.strftime('%H:%M:%S')}] {self.busy} ...")
        threading.Thread(target=self._run, args=(name,), daemon=True).start()

    def _run(self, name):
        try:
            if name == "takeoff":
                result = self.drone.takeoff(log=print)
            else:
                result = self.drone.land()
        except Exception as e:            # never kill the recording because of a command
            result = f"ERROR: {e} - use the phone by hand"
        print(f"[{time.strftime('%H:%M:%S')}] {name}: {result}")
        self.status = f"{name}: {result}"[:70]
        self.busy = None


def main():
    minutes, label = 0.0, ""
    if len(sys.argv) > 1:
        try:
            minutes = float(sys.argv[1])
        except ValueError:
            label = sys.argv[1]
    if len(sys.argv) > 2:
        label = sys.argv[2]
    suffix = ("_" + label) if label else ""
    path = os.path.join(evidence_dir(), f"{stamp()}_recording{suffix}.mp4")

    with Drone() as d:
        cmd = Commands(d)
        writer, written, start, seen = None, 0, None, 0
        print("Starting the camera ...")
        try:
            while True:
                frame = d.get_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                now = time.time()
                if start is None:
                    start = now
                    h, w = frame.shape[:2]
                    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), VIDEO_FPS, (w, h))
                    print(f"Recording to: {path}")
                    print("Aim with the window. Keys in the window: T = take off, L = land, Esc = stop and save.")
                seen += 1
                target = int((now - start) * VIDEO_FPS) + 1     # keep frames written == seconds * fps (real time)
                while written < target:
                    writer.write(frame)
                    written += 1
                disp = frame.copy()
                cv2.putText(disp, f"REC {now - start:5.1f}s", (12, 34),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                cv2.putText(disp, cmd.status, (12, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.imshow("drone recording (T = take off, L = land, Esc = stop)", disp)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:                                   # Esc
                    break
                if key in (ord("t"), ord("T")):
                    cmd.start("takeoff")
                elif key in (ord("l"), ord("L")):
                    cmd.start("land")
                if minutes > 0 and now - start >= minutes * 60:
                    break
        except KeyboardInterrupt:
            print("\nStopped with Ctrl+C.")
        finally:
            if writer is not None:
                writer.release()
            cv2.destroyAllWindows()
            if start is not None:
                print(f"\nSaved: {path}")
                print(f"length about {time.time() - start:.0f} s, {written} frames at {VIDEO_FPS} fps")
            else:
                print("No frames were received - nothing saved. Is DJI Fly showing the camera?")


if __name__ == "__main__":
    main()
