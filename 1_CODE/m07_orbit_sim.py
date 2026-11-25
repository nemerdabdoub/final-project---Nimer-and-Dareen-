"""
m07_orbit_sim.py - Project 3760: top-down SIMULATOR for the curved "orbit" track around the user (notebook item 13).

Why: sim_drone.py replays a clip, so it can only simulate turning (yaw). An orbit also needs SIDEWAYS motion, which a clip
cannot show. This sim models the geometry from above instead: the user walks, the drone gets the same stick commands the real
one would (forward / right / yaw_cw in -1..1), with the command delay and limits, and draws the curved track it flies.

The controller only uses what the real drone can measure from the camera:
  * bearing of the user in the picture (box centre)  -> yaw keeps her centred (+ feed-forward while orbiting)
  * distance from the box height (noisy, ~5%)         -> forward keeps the orbit radius
  * orbit = constant sideways speed                    -> the drone circles her while facing her
  * SUN mode: orbit until the sun is BEHIND the drone (fixes the backlight problem of 25.11: turban looked black), then hold.
States: FOLLOW (hold distance, face her) / ORBIT / SUN-FIX / LOST (she left the view -> stop moving, turn toward last bearing).

Run (in 1_CODE):
  python m07_orbit_sim.py                         window, user standing still, press O to orbit, S for sun mode
  python m07_orbit_sim.py --walk line             user walks back and forth   (--walk still | line | random)
  python m07_orbit_sim.py --mode sun --sun 200    start in sun mode, sun at 200 deg (0 = east/right, 90 = north/up)
  python m07_orbit_sim.py --seconds 60 --no-window --mode orbit   headless test -> numbers only
Keys: O orbit on/off · S sun-fix · D change orbit direction · W change walk · +/- radius · SPACE pause · Q quit
Same timing settings as sim_drone.py: set SIM_DELAY=0.25 (command delay, s), SIM_YAW_RATE=90 (deg/s at full stick).
Output: ../3_EVIDENCE/m07_orbit_sim/<time>_<mode>.csv + summary printed (radius error, centring error, % time in view).
Limits: flat ground, no wind, no obstacles, ideal attitude; checks LOGIC, signs and timing - not real flight.
"""
import argparse
import csv
import math
import os
import random
import time
from collections import deque

import numpy as np

HFOV = 118.0                                   # DJI Neo camera, deg (same as sim_drone.py)
V_MAX = 2.0                                    # m/s at full stick (forward / sideways) - replace by field numbers
DT = 1 / 60                                    # world step, s
CTRL_HZ = 15                                   # detector + controller rate (field: 11m ~18 FPS on battery)


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class World:
    def __init__(self, walk, radius, sun_deg, delay, yaw_rate, seed=1):
        self.rng = random.Random(seed)
        self.walk = walk
        self.user = np.array([0.0, 0.0])
        self.user_dir = 0.0
        self.drone = np.array([-radius, 0.0])   # start west of her, facing east (toward her)
        self.theta = 0.0                         # drone heading, math angle (CCW from +x)
        self.delay, self.yaw_rate = delay, yaw_rate
        self.cmds = deque([(0.0, (0.0, 0.0, 0.0))])
        self.t = 0.0
        self.sun = math.radians(sun_deg)         # direction FROM her TOWARD the sun
        self.trail_d, self.trail_u = deque(maxlen=1500), deque(maxlen=1500)

    def send(self, fwd, right, yaw_cw):
        c = tuple(float(np.clip(v, -1, 1)) for v in (fwd, right, yaw_cw))
        self.cmds.append((self.t + self.delay, c))

    def step(self):
        while len(self.cmds) > 1 and self.cmds[1][0] <= self.t:
            self.cmds.popleft()
        fwd, right, yaw_cw = self.cmds[0][1]
        f = np.array([math.cos(self.theta), math.sin(self.theta)])
        r = np.array([math.sin(self.theta), -math.cos(self.theta)])
        self.drone += (f * fwd + r * right) * V_MAX * DT
        self.theta = wrap(self.theta - math.radians(yaw_cw * self.yaw_rate) * DT)
        # user motion
        if self.walk == "line":
            v = 0.8 * (1 if (self.t % 20) < 10 else -1)
            self.user += np.array([v, 0.0]) * DT
        elif self.walk == "random":
            self.user_dir += self.rng.gauss(0, 0.6) * math.sqrt(DT)
            self.user += 0.7 * np.array([math.cos(self.user_dir), math.sin(self.user_dir)]) * DT
        self.t += DT
        if int(self.t / DT) % 4 == 0:
            self.trail_d.append(self.drone.copy())
            self.trail_u.append(self.user.copy())

    # what the camera would measure (with noise), or None if she is out of the picture
    def measure(self):
        d = self.user - self.drone
        rng = float(np.hypot(*d))
        bearing = wrap(math.atan2(d[1], d[0]) - self.theta)         # + = she is LEFT of centre
        if abs(math.degrees(bearing)) > HFOV / 2 or rng > 15 or rng < 0.5:
            return None
        return (bearing + math.radians(self.rng.gauss(0, 1.0)),
                rng * (1 + self.rng.gauss(0, 0.05)))

    def around_angle(self):                    # where the drone sits around her (CCW angle)
        d = self.drone - self.user
        return math.atan2(d[1], d[0])


class Controller:
    """Same logic would run on the real drone: input = (bearing, distance) from the detector, output = sticks."""
    def __init__(self, radius, mode, direction, orbit_speed=0.8):
        self.R, self.mode, self.dir, self.v_t = radius, mode, direction, orbit_speed
        self.last_bearing, self.state, self.lost_since = 0.0, "FOLLOW", None

    def __call__(self, meas, world, now):
        if meas is None:
            if self.lost_since is None:
                self.lost_since = now
            self.state = "LOST"
            # stop moving, turn slowly toward where she was last seen
            return 0.0, 0.0, -0.3 * math.copysign(1, self.last_bearing)
        self.lost_since = None
        b, rng = meas
        self.last_bearing = b
        fwd = float(np.clip(0.6 * (rng - self.R), -0.6, 0.6))
        yaw = -1.8 * b / math.radians(world.yaw_rate)              # P on bearing (stick units)
        right = 0.0
        self.state = "FOLLOW"
        orbit_dir = 0
        if self.mode == "orbit":
            orbit_dir = self.dir
        elif self.mode == "sun":
            err = wrap(world.sun - world.around_angle())           # sun behind drone = drone on the sun side of her
            if abs(math.degrees(err)) > 8:
                orbit_dir = 1 if err > 0 else -1
                self.state = "SUN-FIX"
            else:
                self.state = "SUN OK"
        if orbit_dir and abs(rng - self.R) < 1.5:                  # only orbit at about the right distance
            right = orbit_dir * self.v_t / V_MAX
            ff = math.degrees(self.v_t / max(rng, 0.5)) / world.yaw_rate
            yaw += -orbit_dir * ff                                 # feed-forward: keep facing her while sliding
            if self.state == "FOLLOW":
                self.state = "ORBIT"
        return fwd, right, float(np.clip(yaw, -1, 1))


def draw(world, ctrl, meas, scale, size, paused, stats):
    import cv2
    img = np.full((size, size, 3), 248, np.uint8)
    c = world.user if world.walk != "still" else np.array([0.0, 0.0])
    def px(p):
        q = (p - c) * scale
        return int(size / 2 + q[0]), int(size / 2 - q[1])
    for m in range(-20, 21):                               # 1 m grid
        x = int(size / 2 + (m - (c[0] % 1)) * scale); y = int(size / 2 + (m - (-c[1] % 1)) * scale)
        cv2.line(img, (x, 0), (x, size), (232, 232, 236), 1); cv2.line(img, (0, y), (size, y), (232, 232, 236), 1)
    cv2.circle(img, px(world.user), int(ctrl.R * scale), (205, 205, 215), 1, cv2.LINE_AA)    # target orbit
    for tr, col in ((world.trail_u, (160, 110, 230)), (world.trail_d, (200, 120, 40))):
        pts = np.array([px(p) for p in tr], np.int32)
        if len(pts) > 1:
            cv2.polylines(img, [pts], False, col, 2, cv2.LINE_AA)
    # sun arrow (from her toward the sun)
    s = world.user + 3.2 * np.array([math.cos(world.sun), math.sin(world.sun)])
    cv2.arrowedLine(img, px(world.user), px(s), (0, 170, 240), 2, cv2.LINE_AA, tipLength=0.12)
    cv2.circle(img, px(s), 9, (0, 200, 255), -1, cv2.LINE_AA)
    # camera field of view wedge
    for a in (world.theta + math.radians(HFOV / 2), world.theta - math.radians(HFOV / 2)):
        e = world.drone + 4 * np.array([math.cos(a), math.sin(a)])
        cv2.line(img, px(world.drone), px(e), (190, 200, 190), 1, cv2.LINE_AA)
    # drone triangle
    f = np.array([math.cos(world.theta), math.sin(world.theta)]); r = np.array([f[1], -f[0]])
    tri = np.array([px(world.drone + 0.45 * f), px(world.drone - 0.3 * f + 0.25 * r), px(world.drone - 0.3 * f - 0.25 * r)], np.int32)
    cv2.fillPoly(img, [tri], (200, 90, 20), cv2.LINE_AA)
    cv2.circle(img, px(world.user), 8, (130, 60, 200), -1, cv2.LINE_AA)
    # camera strip: where she is in the picture
    bar_y = size - 34
    cv2.rectangle(img, (20, bar_y), (size - 20, bar_y + 16), (225, 225, 230), -1)
    cv2.line(img, (size // 2, bar_y - 3), (size // 2, bar_y + 19), (120, 120, 130), 1)
    if meas:
        u = int(size / 2 - (math.degrees(meas[0]) / (HFOV / 2)) * (size / 2 - 20))
        cv2.circle(img, (u, bar_y + 8), 7, (130, 60, 200), -1, cv2.LINE_AA)
    col = {"LOST": (40, 40, 210), "SUN-FIX": (0, 140, 230), "SUN OK": (40, 150, 60)}.get(ctrl.state, (60, 60, 60))
    lines = [f"{ctrl.state}{'  (PAUSED)' if paused else ''}",
             f"t {world.t:5.1f}s  walk {world.walk}  radius {ctrl.R:.1f} m  dir {'CCW' if ctrl.dir > 0 else 'CW'}",
             f"distance {np.hypot(*(world.user - world.drone)):.2f} m   in view {stats['inview']:.0%}",
             f"sun vs drone {abs(math.degrees(wrap(world.sun - world.around_angle()))):4.0f} deg"
             f"{'   BACKLIT' if abs(math.degrees(wrap(world.sun - world.around_angle()))) > 120 else ''}",
             "O orbit  S sun  D dir  W walk  +/- radius  SPACE pause  Q quit"]
    for i, t in enumerate(lines):
        cv2.putText(img, t, (16, 28 + 22 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.62 if i else 0.8, col if i == 0 else (50, 50, 60),
                    2 if i == 0 else 1, cv2.LINE_AA)
    cv2.putText(img, "camera view (her position)", (20, bar_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (90, 90, 100), 1, cv2.LINE_AA)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", default="follow", choices=["follow", "orbit", "sun"])
    ap.add_argument("--walk", default="still", choices=["still", "line", "random"])
    ap.add_argument("--radius", type=float, default=4.0)
    ap.add_argument("--sun", type=float, default=0.0, help="sun direction in deg (0 = right/east). Default 0 = backlit start")
    ap.add_argument("--dir", type=int, default=1, choices=[1, -1])
    ap.add_argument("--speed", type=float, default=0.8, help="orbit sideways speed, m/s")
    ap.add_argument("--seconds", type=float, default=0, help="stop after N s (0 = until Q)")
    ap.add_argument("--no-window", action="store_true")
    a = ap.parse_args()

    delay = float(os.environ.get("SIM_DELAY", 0.25)); yaw_rate = float(os.environ.get("SIM_YAW_RATE", 90.0))
    world = World(a.walk, a.radius, a.sun, delay, yaw_rate)
    ctrl = Controller(a.radius, a.mode, a.dir, a.speed)
    print(f"[SIM-ORBIT] mode {a.mode}, walk {a.walk}, radius {a.radius} m, delay {delay}s, yaw {yaw_rate} deg/s, "
          f"sun {a.sun} deg, control {CTRL_HZ} Hz")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "3_EVIDENCE", "m07_orbit_sim")
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, time.strftime("%Y%m%d_%H%M%S") + f"_{a.mode}_{a.walk}.csv")
    rows, paused, meas, n_in, n_all = [], False, None, 0, 0
    steps_per_ctrl = max(1, round(1 / (CTRL_HZ * DT)))
    show = not a.no_window
    if show:
        import cv2
        cv2.namedWindow("M07 orbit simulator", cv2.WINDOW_AUTOSIZE)
    k_step, t_wall = 0, time.perf_counter()
    while True:
        if not paused:
            if k_step % steps_per_ctrl == 0:
                meas = world.measure()
                world.send(*ctrl(meas, world, world.t))
                n_all += 1; n_in += meas is not None
                d = np.hypot(*(world.user - world.drone))
                rows.append([round(world.t, 2), ctrl.state, round(float(d), 3),
                             round(math.degrees(meas[0]), 2) if meas else "",
                             round(math.degrees(world.around_angle()), 1),
                             round(abs(math.degrees(wrap(world.sun - world.around_angle()))), 1)])
            world.step(); k_step += 1
        if a.seconds and world.t >= a.seconds:
            break
        if show and k_step % 2 == 0:
            img = draw(world, ctrl, meas, 55, 760, paused, {"inview": n_in / max(n_all, 1)})
            cv2.imshow("M07 orbit simulator", img)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27) or cv2.getWindowProperty("M07 orbit simulator", cv2.WND_PROP_VISIBLE) < 1:
                break
            if key == ord("o"): ctrl.mode = "follow" if ctrl.mode == "orbit" else "orbit"
            if key == ord("s"): ctrl.mode = "follow" if ctrl.mode == "sun" else "sun"
            if key == ord("d"): ctrl.dir *= -1
            if key == ord("w"):
                order = ["still", "line", "random"]; world.walk = order[(order.index(world.walk) + 1) % 3]
            if key in (ord("+"), ord("=")): ctrl.R = min(8.0, ctrl.R + 0.5)
            if key == ord("-"): ctrl.R = max(2.0, ctrl.R - 0.5)
            if key == ord(" "): paused = not paused
            # keep real time
            lag = world.t - (time.perf_counter() - t_wall)
            if lag > 0 and not paused:
                time.sleep(min(lag, 0.05))
            if paused:
                t_wall = time.perf_counter() - world.t
    if show:
        cv2.destroyAllWindows()

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "state", "distance_m", "bearing_deg", "drone_around_deg", "sun_vs_drone_deg"])
        w.writerows(rows)
    seen = [r for r in rows if r[3] != ""]
    if seen:
        rad_err = math.sqrt(sum((r[2] - ctrl.R) ** 2 for r in seen) / len(seen))
        cen_err = math.sqrt(sum(r[3] ** 2 for r in seen) / len(seen))
    else:
        rad_err = cen_err = float("nan")
    sun_ok = next((r[0] for r in rows if r[1] == "SUN OK"), None)
    print(f"[SIM-ORBIT] {world.t:.1f} s simulated | in view {n_in / max(n_all, 1):.1%} | radius error RMS {rad_err:.2f} m | "
          f"centring error RMS {cen_err:.1f} deg | sun fixed at {sun_ok if sun_ok is not None else '-'} s")
    print(f"[SIM-ORBIT] log: {os.path.normpath(out_csv)}")


if __name__ == "__main__":
    main()
