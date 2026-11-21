"""
latency_test.py - Project 3493
Measures (1) the REAL camera frame rate and (2) the DELAY of the video chain.
The drone stays on the ground - this script never moves it.

Setup (drone ON, on the desk; DJI Fly in Manual Control; phone connected by USB):
  Point the drone camera at the laptop screen, so it sees the big stopwatch window.
  Make the stopwatch digits fill most of the camera picture and keep the laptop screen bright.

Step 1:  python latency_test.py            (runs 20 seconds; python latency_test.py 30 = 30 s)
Step 2:  open the pictures in the folder it names at the end (inside 3_EVIDENCE/<today's date>/) and read
         the stopwatch number in each one
Step 3:  python latency_test.py calc       (uses the newest run; or: python latency_test.py calc latency_143015)
         (type the numbers you read; it prints the average delay)

How it works:
  * The laptop shows a stopwatch (milliseconds since the script started).
  * Every picture that arrives from the drone is compared with the previous one.
    The screen mirror can send the SAME camera picture several times (only tiny compression
    noise differs). A NEW camera frame changes many pixels (the stopwatch digits change).
    So: new camera frames per second = real camera frame rate.
  * 10 pictures are saved with the laptop time at which they ARRIVED.
    delay = arrival time - the time shown on the stopwatch inside the picture.
  Small error: the laptop screen itself adds about 15-30 ms (it does not draw instantly).
"""
import os
import sys
import time

import cv2
import numpy as np

from paths import EVIDENCE_ROOT, evidence_dir, stamp

FOLDER_PREFIX = "latency"
SECONDS = 20
N_SAVE = 10
SAVE_EVERY_MS = 1500
STRONG_PIXEL_DIFF = 40     # a pixel counts as "changed" if it differs by more than this
STRONG_MIN_PIXELS = 150    # a picture is a NEW CAMERA FRAME if at least this many pixels changed


def newest_folder():
    """The newest run folder (its name contains 'latency') that holds pictures, anywhere under 3_EVIDENCE."""
    best, best_t = None, 0
    for dirpath, _dirs, files in os.walk(EVIDENCE_ROOT):
        pics = [f for f in files if f.endswith(".png")]
        if pics and "latency" in os.path.basename(dirpath):
            t = max(os.path.getmtime(os.path.join(dirpath, f)) for f in pics)
            if t > best_t:
                best, best_t = dirpath, t
    return best


def calc(folder=None):
    folder = folder or newest_folder()
    if not folder or not os.path.isdir(folder):
        print("No folder with pictures found. Run step 1 first (the drone must be on).")
        return
    files = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
    if not files:
        print(f"No pictures in the folder '{folder}' - run step 1 first.")
        return
    print(f"Using the folder: {folder}\n")
    delays = []
    for f in files:
        recv = int(f.split("recv_")[1].split("ms")[0])
        txt = input(f"{f}\n   number shown on the stopwatch in this picture (empty = skip): ").strip()
        if not txt:
            continue
        shown = int(txt)
        delays.append(recv - shown)
        print(f"   delay = {recv} - {shown} = {recv - shown} ms")
    if delays:
        print("\n===== DELAY =====")
        print(f"folder: {folder}")
        print(f"pictures used: {len(delays)}")
        print(f"average delay: {sum(delays) / len(delays):.0f} ms")
        print(f"smallest / largest: {min(delays)} / {max(delays)} ms")
        print("(about 15-30 ms of it is the laptop screen itself)")


def main():
    from drone_interface import Drone   # imported here so 'calc' works without the drone

    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else SECONDS
    folder = os.path.join(evidence_dir(), f"{stamp()}_latency")   # a new folder for every run - nothing is ever deleted
    os.makedirs(folder, exist_ok=True)

    t0 = time.perf_counter()
    now_ms = lambda: (time.perf_counter() - t0) * 1000.0

    canvas = np.zeros((420, 1500, 3), np.uint8)
    last_sig, prev = None, None
    mirror_frames, cam_times, strongs = 0, [], []
    saved, next_save = 0, 2000.0

    with Drone() as drone:
        while now_ms() < seconds * 1000:
            ms = now_ms()
            shown = canvas.copy()
            cv2.putText(shown, f"{int(ms):07d}", (30, 330), cv2.FONT_HERSHEY_SIMPLEX, 9, (255, 255, 255), 18)
            cv2.imshow("STOPWATCH - point the drone camera here (Esc = stop)", shown)
            if cv2.waitKey(1) & 0xFF == 27:
                break

            frame = drone.get_frame()
            t_recv = now_ms()
            if frame is None:
                continue
            sig = hash(frame[::8, ::8].tobytes())
            if sig == last_sig:
                continue
            last_sig = sig
            mirror_frames += 1

            if prev is not None and prev.shape == frame.shape:
                strong = int((cv2.absdiff(frame, prev).max(axis=2) > STRONG_PIXEL_DIFF).sum())
                strongs.append(strong)
                if strong >= STRONG_MIN_PIXELS:
                    cam_times.append(t_recv)
            prev = frame

            if saved < N_SAVE and t_recv >= next_save:
                cv2.imwrite(os.path.join(folder, f"frame_{saved + 1:02d}_recv_{int(t_recv)}ms.png"), frame)
                saved += 1
                next_save += SAVE_EVERY_MS

    cv2.destroyAllWindows()
    duration = now_ms() / 1000.0
    print("\n===== RESULT =====")
    print(f"duration:                      {duration:.1f} s")
    print(f"mirror frames per second:      {mirror_frames / duration:.1f}")
    print(f"NEW CAMERA frames per second:  {len(cam_times) / duration:.1f}   <- the real camera rate")
    if len(cam_times) > 2:
        gaps = np.diff(cam_times)
        print(f"typical time between camera frames: {np.median(gaps):.0f} ms")
    if strongs:
        p = np.percentile(strongs, [10, 50, 90])
        print(f"changed pixels per picture (10/50/90 percent): {p[0]:.0f} / {p[1]:.0f} / {p[2]:.0f}")
        print("   a good measurement has two groups: tiny numbers (repeated pictures) and big numbers (new camera frames)")
    print(f"pictures saved in the folder '{folder}': {saved}")
    print(f"NEXT: open the folder (explorer {folder}), read the stopwatch in each picture, then run:")
    print(f'      python latency_test.py calc "{folder}"   (or just: python latency_test.py calc)')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calc":
        calc(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        main()
