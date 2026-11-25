"""
session.py - Project 3760: ALL tracking-milestone (7.12) flight tests in ONE go, one video, one log, guided on screen.

Nimer only presses SPACE = next step (each step WAITS for SPACE before anything moves = our permission rule), Esc = end.
T = take off, L = land (DJI Fly buttons, like record_video.py). FORCE_LAND.bat and the battery stop (<= 30%) work all the time.
The screen shows for every step: what the PILOT does, what the USER does, and a timer.

Steps:  READY -> STOP TEST -> TURN TEST -> FOLLOW TEST -> SIDE TEST -> FROM ABOVE -> DELAY TEST -> TURN SPEED TEST -> END
  python run_with_adb.py session.py                (GPU python; model yolo11n; max yaw 0.2)
  python run_with_adb.py session.py --model yolo11m.pt
  Simulator check (no drone): set DRONE_SIM=<video>, add --auto-advance (presses SPACE by itself)
Output: 3_EVIDENCE/m06_tracking/session_<time>.mp4 (everything, 25 fps real time) + session_<time>.csv (step column).
"""
import argparse
import csv
import os
import sys
import threading
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m05
import m06_follow as F
from user_score import user_scores
from command_delay_test import small_grey, shift_px

OUT = Path(__file__).resolve().parent.parent / "3_EVIDENCE" / "m06_tracking"
VIDEO_FPS = 25

# (name, mode, seconds, PILOT text, USER text)   mode: HOVER / TURN / FOLLOW / SIDE / ABOVE / DELAY / SPEED
STEPS = [
    ("READY", "HOVER", 0, "Take off (T or by hand), hover 1.5 m facing the user 4 m away. Then SPACE.",
     "Turban on, stand 4 m in front of the drone, face it."),
    ("STOP TEST", "HOVER", 0, "Hover ~1 m. Double-click FORCE_LAND.bat -> drone must land. Take off again, hover, SPACE.",
     "Stay back 3 m."),
    ("TURN TEST", "TURN", 40, "Phone in hand. Drone only TURNS. Esc = stop.",
     "Walk slowly in an ARC around the drone (same distance), stop sometimes."),
    ("FOLLOW TEST", "FOLLOW", 60, "Phone in hand. Drone turns + moves forward/back. Esc = stop.",
     "Walk slowly anywhere: away, closer, diagonal. 60 s."),
    ("SIDE TEST", "SIDE", 40, "Phone in hand. Drone also slides sideways. Esc = stop.",
     "Step slowly sideways left, stop, right, stop."),
    ("FROM ABOVE", "ABOVE", 40, "First climb by hand to 3.5-4 m, THEN SPACE. Camera tilts down by itself.",
     "Walk slowly, turn your back 3 times."),
    ("DELAY TEST", "DELAY", 0, "Hover 1.5 m, point at a still scene. Drone turns by itself 10 times.",
     "Step OUT of the picture, stay still."),
    ("TURN SPEED TEST", "SPEED", 0, "Hover. Drone turns by itself at 3 speeds.",
     "Stay out of the picture."),
    ("END", "HOVER", 0, "Land (L or by hand). Then Esc to save.", "Done - thank you!"),
]


def text_lines(img, lines, y0, colour, scale=0.75):
    y = y0
    for t in lines:
        cv2.putText(img, t, (12, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 5)
        cv2.putText(img, t, (12, y), cv2.FONT_HERSHEY_SIMPLEX, scale, colour, 2)
        y += int(34 * scale / 0.75)


def wrap(t, n=70):
    words, out, cur = t.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="yolo11n.pt")
    ap.add_argument("--max-yaw", type=float, default=0.2)
    ap.add_argument("--auto-advance", action="store_true", help="simulator test only: SPACE pressed by itself")
    ap.add_argument("--auto", action="store_true",
                    help="AUTOMATIC: 10 s countdown -> take off -> climb to ~1.5 m -> TURN -> FOLLOW -> SIDE -> land")
    ap.add_argument("--fast", type=float, default=1.0, help="simulator test only: multiply step times (0.2 = 5x shorter)")
    a = ap.parse_args()
    import lap  # noqa: F401
    m05.HEAD_PART = F.HEAD_DEFAULT
    model = m05.load_model(a.model)
    from drone_interface import Drone
    drone = Drone().__enter__()
    real = not os.environ.get("DRONE_SIM")
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    vpath, cpath = OUT / f"session_{stamp}.mp4", OUT / f"session_{stamp}.csv"
    writer, written, t0 = None, 0, time.perf_counter()
    rows, events = [], []
    step, running, step_t0 = 0, False, None
    fol, ctl = F.Follower(), None
    fps, t_prev, n = 0.0, time.perf_counter(), 0
    drone_batt, low_batt = "", False
    pulses, pend = [], None                    # automatic turns: [(t_start, yaw, seconds, label)], delay watch
    busy = {"txt": ""}

    def bg(fn, label):
        def run():
            busy["txt"] = label + " ..."
            try:
                r = fn()
                busy["txt"] = f"{label}: {r}"[:60]
            except Exception as e:
                busy["txt"] = f"{label} failed: {e}"[:60]
        threading.Thread(target=run, daemon=True).start()

    def start_step(k):
        nonlocal running, step_t0, fol, ctl, pulses
        name, mode = STEPS[k][0], STEPS[k][1]
        running, step_t0 = True, time.perf_counter()
        fol = F.Follower()
        ctl = F.Controller(a.max_yaw, mode in ("FOLLOW", "SIDE"), use_side=(mode == "SIDE"))
        pulses = []
        now = time.perf_counter()
        if mode == "ABOVE" and real:
            import gimbal
            bg(lambda: (gimbal.tilt_to(-30), "camera at -30 deg")[1], "tilt")
        if mode == "DELAY":
            pulses = [(now + 2 + 3 * i, 0.3 if i % 2 == 0 else -0.3, 0.6, f"delay {i + 1}") for i in range(10)]
        if mode == "SPEED":
            pulses = [(now + 2 + 5 * i, s if i % 2 == 0 else -s, 2.0, f"speed {s}") for i, s in
                      enumerate([0.2, 0.2, 0.3, 0.3, 0.4, 0.4])]
        events.append((round(now - t0, 2), f"START {name}"))
        print(f"\n=== {name} started ===")

    def end_step():
        nonlocal running, step
        name, mode = STEPS[step][0], STEPS[step][1]
        drone.stop()
        if mode == "ABOVE" and real:
            import gimbal
            bg(lambda: (gimbal.tilt_to(0), "camera level")[1], "tilt")
        events.append((round(time.perf_counter() - t0, 2), f"END {name}"))
        print(f"=== {name} finished ===")
        running = False
        step = min(step + 1, len(STEPS) - 1)

    AUTO_STEPS = [i for i, st in enumerate(STEPS) if st[0] in ("TURN TEST", "FOLLOW TEST", "SIDE TEST")]
    auto = {"phase": "countdown" if a.auto else None, "t": time.perf_counter(), "k": 0, "done": False}

    def auto_bg(fn, label):
        auto["done"] = False

        def run():
            busy["txt"] = label + " ..."
            try:
                r = fn()
                busy["txt"] = f"{label}: {r}"[:60]
            except Exception as e:
                busy["txt"] = f"{label} failed: {e}"[:60]
            auto["done"] = True
        threading.Thread(target=run, daemon=True).start()

    print("SESSION: SPACE = start / next step, Esc = end, T = take off, L = land.")
    try:
        while True:
            fr = drone.get_frame()
            if fr is None:
                time.sleep(0.01)
                continue
            fr = fr.copy()
            now = time.perf_counter()
            t = now - t0
            H, W = fr.shape[:2]
            name, mode, secs, pilot, user = STEPS[step]
            r = model.track(fr, persist=True, classes=[0], conf=m05.CONF, tracker="botsort.yaml", verbose=False)[0]
            boxes = r.boxes.xyxy.cpu().numpy().astype(int).tolist()
            ids = r.boxes.id.cpu().numpy().astype(int).tolist() if r.boxes.id is not None else [None] * len(boxes)
            mask = m05.turban_mask(fr)
            scores = user_scores(mask, boxes)
            box, state = fol.update(t, boxes, ids, m05.hybrid_user(mask, boxes), scores)
            if real and n % 30 == 0:
                try:
                    pb = drone.battery_percent()
                    if pb is not None:
                        drone_batt = pb
                        if pb <= F.LOW_BATTERY and not low_batt:
                            low_batt = True
                            print(f"  !!! DRONE BATTERY {pb}% - LAND NOW !!!")
                except Exception:
                    pass
            yaw = fwd = side = 0.0
            if running and not low_batt:
                if mode in ("TURN", "FOLLOW", "SIDE", "ABOVE"):
                    yaw, fwd = ctl.step(box, state, W, H)
                    side = ctl.side
                    if state == "FOLLOWING":
                        drone.send_speeds(forward=fwd, right=side, yaw_cw=yaw)
                    else:
                        drone.stop()
                elif mode in ("DELAY", "SPEED"):
                    act = [p for p in pulses if p[0] <= now < p[0] + p[2]]
                    if act:
                        yaw = act[0][1]
                        drone.send_speeds(yaw_cw=yaw)
                        if pend is None and mode == "DELAY" and now - act[0][0] < 0.05:
                            pend = (act[0], small_grey(fr))
                    else:
                        drone.stop()
                    if pend is not None:
                        dx, resp = shift_px(pend[1], small_grey(fr))
                        if abs(dx) >= 3 and resp > 0.05:
                            ms = round((now - pend[0][0]) * 1000)
                            events.append((round(t, 2), f"{pend[0][3]}: shift {dx:+.1f}px after {ms} ms"))
                            print(f"  {pend[0][3]}: picture shifted {dx:+.1f} px after {ms} ms")
                            pend = None
                        elif now - pend[0][0] > 1.5:
                            pend = None
                    if pulses and now > pulses[-1][0] + pulses[-1][2] + 1.5:
                        end_step()
                if running and secs and now - step_t0 >= secs * a.fast:
                    end_step()
            elif low_batt:
                drone.stop()
            fps = 0.9 * fps + 0.1 / max(1e-3, now - t_prev) if n else 0.0
            t_prev = now
            rows.append([round(t, 2), name, int(running), state, fol.user_id if box is not None else "",
                         *(box or ["", "", "", ""]), round(yaw, 3), round(fwd, 3), round(side, 3), round(fps, 1), drone_batt])
            # ---- picture: boxes + guidance
            F.draw(fr, boxes, ids, box, state if not low_batt else "LOW_BATTERY", fol.user_id, yaw, fwd, fps,
                   f"SESSION {step + 1}/{len(STEPS)}: {name}  {'RUNNING' if running else 'press SPACE to start'}"
                   + (f"  {max(0, secs - (now - step_t0)):.0f}s left" if running and secs else ""), scores)
            text_lines(fr, ["PILOT: " + l if i == 0 else "       " + l for i, l in enumerate(wrap(pilot))], 100, (0, 255, 255))
            text_lines(fr, ["USER: " + l if i == 0 else "      " + l for i, l in enumerate(wrap(user))], 200, (255, 255, 255))
            if busy["txt"]:
                text_lines(fr, [busy["txt"]], H - 60, (255, 200, 0), 0.6)
            if writer is None:
                writer = cv2.VideoWriter(str(vpath), cv2.VideoWriter_fourcc(*"mp4v"), VIDEO_FPS, (W, H))
            if fr.shape[:2] == (H, W):
                while written < int(t * VIDEO_FPS) + 1:
                    writer.write(fr)
                    written += 1
            if auto["phase"]:                                  # ---- AUTOMATIC sequence
                el = now - auto["t"]
                ph = auto["phase"]
                if ph == "countdown":
                    msg = f"AUTO: TAKE OFF IN {max(0, 10 - el):.0f} s  (Esc = cancel)"
                    if el >= 10:
                        events.append((round(t, 2), "AUTO take off"))
                        auto_bg(lambda: drone.takeoff(log=print), "take off")
                        auto.update(phase="takeoff", t=now)
                elif ph == "takeoff":
                    msg = "AUTO: taking off ..."
                    if auto["done"]:
                        auto.update(phase="climb", t=now)
                elif ph == "climb":
                    msg = "AUTO: climbing to ~1.5 m ..."
                    drone.send_speeds(up=0.3)
                    if el >= 1.5:
                        drone.stop()
                        auto.update(phase="gap", t=now)
                elif ph == "gap":
                    nxt = STEPS[AUTO_STEPS[auto["k"]]][0]
                    msg = f"AUTO: NEXT {nxt} in {max(0, 5 - el):.0f} s - user get ready"
                    if el >= 5:
                        step = AUTO_STEPS[auto["k"]]
                        start_step(step)
                        auto.update(phase="run", t=now)
                elif ph == "run":
                    msg = f"AUTO: {STEPS[step][0]} running"
                    if not running:
                        auto["k"] += 1
                        if auto["k"] < len(AUTO_STEPS):
                            auto.update(phase="gap", t=now)
                        else:
                            events.append((round(t, 2), "AUTO land"))
                            auto_bg(drone.land, "land")
                            auto.update(phase="landing", t=now)
                elif ph == "landing":
                    msg = "AUTO: landing ..." if not auto["done"] else "AUTO: done - press Esc to save"
                text_lines(fr, [msg], H // 2, (0, 255, 0), 1.0)
            cv2.imshow("SESSION - SPACE = next step, Esc = end, T = take off, L = land", fr)
            key = cv2.waitKey(1) & 0xFF
            if a.auto_advance and not a.auto and not running and now - (step_t0 or t0) > 3 and step < len(STEPS) - 1:
                key = 32
            if key == 27:
                break
            if key == 32 and not auto["phase"]:            # in AUTO mode SPACE does nothing (the sequence runs itself)
                if running:
                    end_step()
                elif step < len(STEPS) - 1 or name != "END":
                    if mode == "HOVER":                 # READY / STOP TEST: nothing moves -> SPACE just moves on
                        events.append((round(t, 2), f"DONE {name}"))
                        step = min(step + 1, len(STEPS) - 1)
                        step_t0 = now
                    else:
                        start_step(step)
            if key in (ord("t"), ord("T")):
                bg(lambda: drone.takeoff(log=print), "take off")
            if key in (ord("l"), ord("L")):
                bg(drone.land, "land")
            n += 1
    except KeyboardInterrupt:
        print("\nStopped with Ctrl+C.")
    finally:
        drone.stop()
        drone.__exit__(None, None, None)
        cv2.destroyAllWindows()
        if writer is not None:
            writer.release()
        with open(cpath, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time_s", "step", "running", "state", "user_id", "x1", "y1", "x2", "y2", "yaw", "forward", "side",
                        "fps", "drone_battery_pct"])
            w.writerows(rows)
            w.writerow([])
            w.writerow(["EVENTS"])
            w.writerows(events)
        print(f"\nSaved: {vpath}\n       {cpath}")
        for e in events:
            print("  ", e)


if __name__ == "__main__":
    main()
