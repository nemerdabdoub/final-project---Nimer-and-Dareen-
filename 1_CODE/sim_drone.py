"""
sim_drone.py - Project 3760: a SIMULATED drone for rehearsing on the computer (Nimer's idea: "simulate first, like Vivado").

Same methods as drone_interface.Drone (get_frame, send_speeds, stop, takeoff, land, close, with-block), so EVERY script
runs unchanged. Switch it on with one environment variable (cmd):
    set DRONE_SIM=..\\3_EVIDENCE\\2026-11-22\\143404_recording_session1.mp4
    %GPU% m06_follow.py --live --dry --seconds 30          (any script: record_video, command_delay_test, m06_follow ...)
    set DRONE_SIM=                                          (back to the real drone)

What it simulates:
  * camera: plays the recorded clip in real time (looping) and shows only a narrower window of it (VIEW = 60% of the width)
  * yaw: send_speeds(yaw_cw=...) slides that window left/right = the drone turning (virtual yaw), with
      - a command delay  SIM_DELAY  (s, default 0.25)  - replace by the field-day B3 number
      - a turning speed  SIM_YAW_RATE (deg/s at full stick, default 90) - replace by the B3b numbers
      - the camera width ~118 deg -> pixels per degree
    yaw_cw > 0 = turn right (clockwise seen from above) -> the scene moves LEFT in the picture.
  * take-off / land: only print (nothing flies). forward/back/up/right: logged, not simulated (the clip cannot zoom).
Limits: the people in the clip don't react to the drone; it checks LOGIC, signs, crashes and timing - not real flight.
"""
import os
import threading
import time
from collections import deque

import cv2

HFOV = 118.0                                    # DJI Neo camera, degrees (spec, approx.)
VIEW = 0.60                                     # simulated view = 60% of the recorded width


class SimDrone:
    def __init__(self, *args, **kwargs):
        self.path = os.environ.get("DRONE_SIM", "")
        self.cap = cv2.VideoCapture(self.path)
        if not self.cap.isOpened():
            raise RuntimeError(f"DRONE_SIM: cannot open video {self.path!r}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self.W = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.H = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.delay = float(os.environ.get("SIM_DELAY", 0.25))
        self.rate = float(os.environ.get("SIM_YAW_RATE", 90.0))
        self.ppd = self.W / HFOV
        self.vw = int(self.W * VIEW)
        self.offset = (self.W - self.vw) / 2.0      # left edge of the simulated view
        self.cmds = deque([(0.0, 0.0)])             # (time it takes effect, yaw stick)
        self.yaw_now, self.t_last, self.t0 = 0.0, time.perf_counter(), time.perf_counter()
        self.lock = threading.Lock()
        self.log = []                               # (time, yaw stick sent)
        self.heading = 0.0                          # simulated degrees turned (+ = right)
        print(f"[SIM] simulated drone on {os.path.basename(self.path)}: delay {self.delay}s, "
              f"yaw {self.rate} deg/s at full stick, view {VIEW:.0%} of {HFOV} deg")

    # ---- with-block, like the real Drone
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.cap.release()
        print(f"[SIM] closed; total simulated turn {self.heading:+.0f} deg, {len(self.log)} commands")

    # ---- motion
    def _advance(self):
        now = time.perf_counter()
        with self.lock:
            while len(self.cmds) > 1 and self.cmds[1][0] <= now:
                self.cmds.popleft()
            self.yaw_now = self.cmds[0][1]
            dt, self.t_last = now - self.t_last, now
        deg = self.yaw_now * self.rate * dt
        self.heading += deg
        self.offset = min(max(0.0, self.offset + deg * self.ppd), self.W - self.vw)

    # same FORCE LAND path as drone_interface.Drone, so /force_land can be rehearsed on the computer
    _force_landed = False

    def _check_force_land(self):
        from force_land import requested, clear, report
        if self._force_landed:
            return True
        if not requested():
            return False
        self._force_landed = True
        clear()
        print("\n!!! [SIM] FORCE LAND requested - releasing sticks and landing !!!", flush=True)
        with self.lock:
            self.cmds.append((time.perf_counter() + self.delay, 0.0))
        report(self.land())
        return True

    def send_speeds(self, forward=0.0, right=0.0, up=0.0, yaw_cw=0.0):
        if self._check_force_land():
            return
        t = time.perf_counter()
        with self.lock:
            self.cmds.append((t + self.delay, float(yaw_cw)))
        self.log.append((round(t - self.t0, 3), float(yaw_cw)))

    def stop(self):
        self.send_speeds()

    def move(self, *a):
        pass

    # ---- camera
    def get_frame(self):
        self._check_force_land()
        self._advance()
        k = int((time.perf_counter() - self.t0) * self.fps) % self.n
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, k)
        ok, fr = self.cap.read()
        if not ok:
            return None
        x = int(self.offset)
        view = fr[:, x:x + self.vw]
        return cv2.resize(view, (self.W, self.H))

    # ---- take-off / landing (print only)
    def takeoff(self, *a, **k):
        print("[SIM] take-off (simulated, nothing flies)")
        return "SIM take-off ok"

    def land(self, *a, **k):
        print("[SIM] landing (simulated)")
        return "SIM landing ok"

    def get_state(self):
        return {"sim": True, "heading": self.heading}

    def battery_percent(self, frame=None):
        return None
