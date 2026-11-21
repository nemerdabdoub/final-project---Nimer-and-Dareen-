"""
flight_test.py (v3.1) - Project 3493: tests of control from code. ONE question; the battery is read and logged by itself
(before the flight, and after the landing once the Take Off circle is back). Nothing is added while the drone flies.

  python flight_test.py dry      NO DRONE: the drone must be OFF. Shows where the code presses the phone screen
                                 (turn on Show taps + Pointer location, open a blank page such as Chrome about:blank).
  python flight_test.py hover    take off from code, hover 5 s, YOU land by hand
  python flight_test.py cycle    take off from code, hover 5 s, then LAND FROM CODE (hold Land, OK only if the pop-up shows)
  python flight_test.py moves [push] [seconds]   take off, six small moves (forward, back, right, left, rotate right, rotate left),
                                 then LAND FROM CODE. Starts gentle: push 0.1 for 0.4 s. Example of a bigger try:  moves 0.15 0.5
                                 (never above 0.4; raise it only if the moves are too small to see). Needs 1.5 m free in EVERY direction.
  python flight_test.py land     the drone is already hovering (you took off by hand): lands it from code
  python flight_test.py battery  NO FLIGHT: just reads the battery from DJI Fly's ring (drone on, app showing the ring) and saves the pictures

Needs a big open space (about 2.5 x 2.5 m clear) for everything except dry. Phone in your hand, DJI Fly in front,
Manual Control, 'Takeoff permitted'. STOP: Ctrl+C here (sticks released, the drone hovers), then hold Land on the phone.
Every step is written with its time to 3_EVIDENCE/<today's date>/<time>_flight_test_log.txt
"""
import os
import sys
import time
from drone_interface import Drone

try:
    from paths import evidence_dir, stamp
except ImportError:                      # running outside the organised folder
    def evidence_dir():
        return "."
    def stamp():
        return time.strftime("%H%M%S")

DEFLECT = 0.1         # stick push for the real moves (0-1). START SMALL: 0.1 for 0.4 s should move the drone only 10-20 cm
PULSE_S = 0.4         # how long each real move lasts (seconds)
PAUSE_S = 3.0         # rest between real moves
MAX_DEFLECT = 0.4     # the test refuses anything stronger
DRY_DEFLECT = 0.5     # bigger push for the dry run, so the finger is easy to see
DRY_PULSE_S = 2.0
LOG = os.path.join(evidence_dir(), f"{stamp()}_flight_test_log.txt")


def note(msg):
    print(msg)
    with open(LOG, "a", encoding="utf8") as f:
        f.write(time.strftime("%H:%M:%S  ") + msg + "\n")


def confirm(mode):
    print("\nCheck: big open space, nothing above, nobody close; phone in your hand; DJI Fly in front,")
    print("Manual Control, saying 'Takeoff permitted'; battery above 40% (the script reads it for the log).")
    if mode == "moves":
        print("MOVES: at least 1.5 m free in EVERY direction around the drone (walls, furniture, blanket, cables) and nothing above.")
    if input("Type YES to start: ").strip().upper() != "YES":
        sys.exit("Not started.")
    note(f"START  mode={mode}  DEFLECT={DEFLECT}  PULSE_S={PULSE_S}")


def hold(drone, seconds, **cmd):
    """Send the same stick push about 20 times a second, then release the sticks."""
    end = time.time() + seconds
    while time.time() < end:
        drone.send_speeds(**cmd)
        time.sleep(0.05)
    drone.stop()


def register_battery(d, label):
    """Read the drone battery from the ring in DJI Fly and save a small picture of it. A few milliseconds; nothing is pressed."""
    try:
        t0 = time.time()
        while d.screen() is None and time.time() - t0 < 4.0:        # the first picture can take a moment to arrive
            time.sleep(0.2)
        values, why = [], ""
        for _ in range(3):
            pct, why = d.battery_info()
            if pct is not None:
                values.append(pct)
            time.sleep(0.15)
        crop = d.battery_crop()
        if crop is not None:
            import cv2
            cv2.imwrite(os.path.join(evidence_dir(), f"{stamp()}_battery_{label}.png"), crop)
        if values:
            pct = sorted(values)[len(values) // 2]
            note(f"battery {label}: {pct}%  ({why}; picture saved, check it)")
            return pct
        note(f"battery {label}: could not be read - {why}")
        save_screen(d, f"screen_for_battery_{label}")                  # the whole screen, so the reason can be found
        return None
    except Exception as e:                                           # the log must never stop a flight
        note(f"(battery {label}: could not be registered: {e})")
        return None


def wait_until_landed(d, timeout=120, t_start=None):
    """Poll the screen (twice a second, nothing is pressed) until the Take Off circle is back = landed, then register the battery."""
    note("waiting for the landing: the script ends by itself (Ctrl+C to skip)")
    t0 = time.time() if t_start is None else t_start
    deadline = time.time() + timeout
    seen = 0
    while time.time() < deadline:
        ready = d.on_ground_ready()
        if ready is None:
            note("(the screen cannot be read, so the landing is not detected)")
            return None
        seen = seen + 1 if ready else 0
        if seen >= 3:                                       # the Take Off circle has been back for 1.5 s
            secs = time.time() - t0 - 1.0
            when = "after the start of the landing" if t_start is not None else "after 'NOW LAND BY HAND'"
            note(f"LANDED: the Take Off circle is back (about {secs:.0f} s {when})")
            time.sleep(2.0)
            register_battery(d, "after")
            return secs
        time.sleep(0.5)
    note(f"landing not detected within {timeout} s")
    register_battery(d, "after")
    return None


def took_off(result):
    return result.startswith("took off") or result.startswith("take-off button pressed")


def save_screen(d, label):
    try:
        import cv2
        frame = d.screen()
        if frame is not None:
            path = os.path.join(evidence_dir(), f"{stamp()}_{label}.png")
            cv2.imwrite(path, frame)
            note("screen saved: " + path)
    except Exception as e:                                   # a missing picture must never stop a flight test
        note(f"(could not save the screen picture: {e})")


def dry_run():
    print("\nDRY RUN - nothing can fly, but the phone gets REAL touches.")
    print("Phone: Developer options > 'Show taps' and 'Pointer location' ON; open a BLANK page (Chrome, about:blank), NOT DJI Fly.")
    if input("Type OFF when the drone is switched off and the phone shows a blank page: ").strip().upper() != "OFF":
        sys.exit("Not started.")
    with Drone() as d:
        s = d._neo._settings
        R = int(s["JOYSTICK_RADIUS"])
        lx, ly, rx, ry = (int(s[k]) for k in ("JOYSTICK_LEFT_X", "JOYSTICK_LEFT_Y", "JOYSTICK_RIGHT_X", "JOYSTICK_RIGHT_Y"))
        o = int(DRY_DEFLECT * R)
        steps = [("forward",      "RIGHT stick", (rx, ry - o), dict(forward=DRY_DEFLECT)),
                 ("backward",     "RIGHT stick", (rx, ry + o), dict(forward=-DRY_DEFLECT)),
                 ("right",        "RIGHT stick", (rx + o, ry), dict(right=DRY_DEFLECT)),
                 ("left",         "RIGHT stick", (rx - o, ry), dict(right=-DRY_DEFLECT)),
                 ("rotate right", "LEFT stick",  (lx + o, ly), dict(yaw_cw=DRY_DEFLECT)),
                 ("rotate left",  "LEFT stick",  (lx - o, ly), dict(yaw_cw=-DRY_DEFLECT)),
                 ("up",           "LEFT stick",  (lx, ly - o), dict(up=DRY_DEFLECT)),
                 ("down",         "LEFT stick",  (lx, ly + o), dict(up=-DRY_DEFLECT))]
        note(f"DRY RUN START  radius={R}  deflection={DRY_DEFLECT}")
        try:
            for name, stick, (ex, ey), cmd in steps:
                note(f"move: {name:12s} expected finger on the {stick} at X={ex}, Y={ey}")
                hold(d, DRY_PULSE_S, **cmd)
                time.sleep(2)
            note(f"take-off button: press and hold 3 s, expected at X={int(s['TAKEOFF_X'])}, Y={int(s['TAKEOFF_Y'])}")
            d._neo.takeoff()                      # only a touch: the drone is off
            time.sleep(2)
            note(f"Land button: press and hold 2.5 s, expected at X={int(s['LAND_X'])}, Y={int(s['LAND_Y'])}")
            d._hold(int(s["LAND_X"]), int(s["LAND_Y"]), 2.5)
        except KeyboardInterrupt:
            d.stop()
            note("STOPPED with Ctrl+C")
        note("DRY RUN END - compare each touch with the numbers above (screenshot: SCREENSHOT.bat dry_pointer)")


def main(mode, args=()):
    global DEFLECT, PULSE_S
    if mode == "moves":
        try:
            if len(args) >= 1:
                DEFLECT = float(args[0])
            if len(args) >= 2:
                PULSE_S = float(args[1])
        except ValueError:
            sys.exit("Use: python flight_test.py moves [push 0-0.4] [seconds], for example: moves 0.15 0.5")
        if not (0 < DEFLECT <= MAX_DEFLECT) or not (0 < PULSE_S <= 1.5):
            sys.exit(f"The push must be between 0 and {MAX_DEFLECT} and the time between 0 and 1.5 s.")
    if mode == "dry":
        dry_run()
        return
    if mode == "battery":
        with Drone() as d:
            note("BATTERY CHECK (no flight): the drone must be on and DJI Fly must show the battery ring")
            register_battery(d, "check")
            save_screen(d, "screen_for_battery_check")
        return
    if mode not in ("hover", "cycle", "moves", "land"):
        sys.exit("Use: dry | hover | cycle | moves | land | battery")
    confirm(mode)
    with Drone() as d:
        register_battery(d, "before")
        try:
            if mode == "land":
                print("The drone must be hovering. Landing from code in 2 seconds (Ctrl+C = stop)...")
                time.sleep(2)
                note("land from code: hold Land, then look for the pop-up")
                t_press = time.time()
                result = d.land()
                note("land() says: " + result)
                save_screen(d, "screen_after_land_press")
                if "NO LANDING STARTED" in result:
                    note("THE LANDING FROM CODE DID NOT START WITHIN 8 SECONDS. Hold Land on the phone yourself, now.")
                else:
                    note("WATCH THE DRONE. If it is not landing within 4 seconds: hold Land / tap OK by hand.")
                wait_until_landed(d, t_start=t_press)
                return
            print("Taking off in 3 seconds (Ctrl+C = stop). If nothing seems to happen, wait about 10 s: the script says what the phone shows.")
            time.sleep(3)
            note("take-off from code ...")
            result = d.takeoff(log=note)
            note("take-off: " + result)
            if result.startswith("NOT STARTED") or result.startswith("NO TAKE-OFF"):
                save_screen(d, "screen_not_ready")
            if not took_off(result):
                note("Nothing flew. Fix what the message says, then run the command again.")
                return
            note("hovering - 5 s to settle")
            time.sleep(5)
            if mode == "moves":
                for name, cmd in (("forward", dict(forward=DEFLECT)), ("backward", dict(forward=-DEFLECT)),
                                  ("right", dict(right=DEFLECT)), ("left", dict(right=-DEFLECT)),
                                  ("rotate right", dict(yaw_cw=DEFLECT)), ("rotate left", dict(yaw_cw=-DEFLECT))):
                    note(f"move: {name}")
                    hold(d, PULSE_S, **cmd)
                    time.sleep(PAUSE_S)
            if mode in ("cycle", "moves"):
                note("landing from code: tap Land, hold the big Land circle, OK only if the pop-up shows")
                t_press = time.time()
                result = d.land()
                note("land() says: " + result)
                save_screen(d, "screen_after_land_press")
                if "NO LANDING STARTED" in result:
                    note("THE LANDING FROM CODE DID NOT START WITHIN 8 SECONDS. Hold Land on the phone yourself, now.")
                else:
                    note("WATCH THE DRONE. If it is not landing within 4 seconds: hold Land / tap OK by hand.")
                wait_until_landed(d, t_start=t_press)
            else:
                note("NOW LAND BY HAND: hold Land on the phone until it is down.")
                wait_until_landed(d)
        except KeyboardInterrupt:
            d.stop()
            note("STOPPED with Ctrl+C - sticks released. If the drone is in the air it hovers: LAND IT BY HAND NOW (hold Land).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "", tuple(sys.argv[2:]))
