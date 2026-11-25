"""
command_delay_test.py - Project 3760, M06: how long from "laptop sends a stick command" to "the drone moves"?

Two measurements in one run:
  1. COMMAND DELAY (main, by eye): a second phone films the laptop screen AND the drone at 60 fps.
     On every key press the laptop screen flashes RED with the number of the press and the stopwatch.
     Later: count video frames from the red flash to the first visible turn of the drone (1 frame = 16.7 ms).
  2. LOOP DELAY (automatic): the script watches the drone's own camera picture. When the drone turns, the picture
     shifts. Time from the key press to the first clearly shifted picture = command delay + video delay (~256 ms).
     So command delay ~ loop delay - 256 ms (cross-check of 1).

Use (from 1_CODE; drone HOVERING at ~1.5 m, open space, phone in hand, DJI Fly in Manual Control):
  python command_delay_test.py            real test: Y = short yaw RIGHT, U = short yaw LEFT, Esc = quit
  python command_delay_test.py --dry      same window and logging, but NOTHING is sent (test on the ground first)
  Options: --deflect 0.3 (stick 0..1, keep small)   --pulse 0.6 (seconds the stick is held)
Wait ~3 s between presses (drone must be still). Do 10 presses (5 right, 5 left).

Saves 3_EVIDENCE/<today>/<time>_command_delay.csv: press number, direction, laptop time, stopwatch ms,
automatic loop delay in ms (empty if the picture never clearly shifted).
SAFETY: Ctrl+C or Esc = sticks released (hover). If anything looks wrong, take over with the phone and land by hand.
"""
import argparse
import csv
import os
import threading
import time

import cv2
import numpy as np

try:
    from paths import evidence_dir, stamp
except ImportError:                                            # fallback if paths.py is missing
    def evidence_dir():
        d = os.path.join("..", "3_EVIDENCE", time.strftime("%Y-%m-%d"))
        os.makedirs(d, exist_ok=True)
        return d

    def stamp():
        return time.strftime("%H%M%S")

SHIFT_THRESHOLD = 12.0      # mean grey-level change (0..255) that counts as "the picture moved"
WATCH_SECONDS = 1.5         # how long after a press to look for the shift


def small_grey(frame):
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = g.shape
    g = g[h // 6: h * 5 // 6, w // 6: w * 5 // 6]               # skip the DJI Fly buttons at the edges
    return cv2.resize(g, (160, 90)).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="send nothing (ground test)")
    ap.add_argument("--deflect", type=float, default=0.3)
    ap.add_argument("--pulse", type=float, default=0.6)
    a = ap.parse_args()

    path = os.path.join(evidence_dir(), f"{stamp()}_command_delay{'_dry' if a.dry else ''}.csv")
    rows, t0 = [], time.perf_counter()
    pending = None                       # [press_no, t_press, reference picture] while watching for the shift
    flash_until, press_no = 0.0, 0

    from drone_interface import Drone
    with Drone() as d:
        def pulse(yaw):
            if not a.dry:
                d.send_speeds(yaw_cw=yaw)
                time.sleep(a.pulse)
                d.stop()

        print(f"{'DRY RUN - nothing is sent. ' if a.dry else ''}Y = yaw right, U = yaw left, Esc = quit.")
        try:
            while True:
                frame = d.get_frame()
                now = time.perf_counter()
                ms = int((now - t0) * 1000)
                canvas = np.zeros((720, 1280, 3), np.uint8)
                if now < flash_until:
                    canvas[:] = (0, 0, 255)                         # RED flash = command sent
                cv2.putText(canvas, f"{ms:>8d} ms", (60, 260), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 12)
                cv2.putText(canvas, f"press #{press_no}", (60, 420), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 6)
                cv2.putText(canvas, "DRY RUN" if a.dry else "LIVE - Y right, U left, Esc quit",
                            (60, 650), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 3)
                if frame is not None:
                    canvas[20:200, 1060:1260] = cv2.resize(frame, (200, 180))
                    if pending is not None:
                        diff = float(np.abs(small_grey(frame) - pending[2]).mean())
                        if diff >= SHIFT_THRESHOLD:
                            rows[-1]["loop_delay_ms"] = round((now - pending[1]) * 1000)
                            print(f"  press #{pending[0]}: picture moved after {rows[-1]['loop_delay_ms']} ms")
                            pending = None
                        elif now - pending[1] > WATCH_SECONDS:
                            print(f"  press #{pending[0]}: no clear shift within {WATCH_SECONDS} s")
                            pending = None
                cv2.imshow("command delay test (film this screen + the drone at 60 fps)", canvas)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    break
                if key in (ord("y"), ord("Y"), ord("u"), ord("U")) and pending is None and frame is not None:
                    press_no += 1
                    right = key in (ord("y"), ord("Y"))
                    t_press = time.perf_counter()
                    rows.append({"press": press_no, "direction": "right" if right else "left",
                                 "laptop_time": time.strftime("%H:%M:%S"), "stopwatch_ms": int((t_press - t0) * 1000),
                                 "loop_delay_ms": ""})
                    pending = [press_no, t_press, small_grey(frame)]
                    flash_until = t_press + 0.25
                    threading.Thread(target=pulse, args=(a.deflect if right else -a.deflect,), daemon=True).start()
                    print(f"press #{press_no} ({rows[-1]['direction']}) at {rows[-1]['stopwatch_ms']} ms")
        except KeyboardInterrupt:
            print("\nStopped with Ctrl+C.")
        finally:
            d.stop()
            cv2.destroyAllWindows()

    if rows:
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        got = [r["loop_delay_ms"] for r in rows if r["loop_delay_ms"] != ""]
        print(f"\nSaved: {path}")
        if got:
            print(f"automatic loop delay: mean {np.mean(got):.0f} ms, min {min(got)}, max {max(got)} (n={len(got)})")
            print(f"-> command delay ~ {np.mean(got) - 256:.0f} ms (loop - video 256 ms); check with the 60 fps video")


if __name__ == "__main__":
    main()
