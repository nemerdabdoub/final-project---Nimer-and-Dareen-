"""
drone_interface.py (v3) - Project 3493
Thin interface layer: the rest of our code talks ONLY to this class.
Switching drone (Neo / Pro / other) = rewriting this one file.

Backend: DJIneo.py from https://github.com/Penkov-D/DJI-Neo-to-PC
(controls the DJI Fly app on an Android phone through scrcpy + ADB).
Put this file in the same folder as DJIneo.py, scrcpy.py and settings.txt.

WHAT CHANGED IN v5.1 (battery) AND v5
  battery_percent() reads the DRONE battery from the ring in the top bar of DJI Fly: the length of the coloured arc is
  the percentage (checked on 5 of your screenshots: 45, 46, 45, 44, 71 all read correctly, within 1%). It only looks at
  a picture that is already in memory, so it never slows a take-off or a flight.
  v5:
  takeoff() now LOOKS AT THE SCREEN: it waits until DJI Fly shows the Take Off circle, presses, then checks that
  the joysticks appeared (= the drone is in the air); if not, it presses once more. It tells you what happened
  instead of failing silently (the first hover attempt on 7.11 did nothing).
  land() does the TWO-STEP landing of DJI Fly (short tap on the small Land button, then hold the big Land circle on the confirmation screen), taps OK only if the dark "safe to land?" pop-up appears, and then checks that the red STOP screen appeared = the landing really started (v5.3).
  Tested on the real drone: starting it, get_frame(), close(), take-off from code, landing from code (7.11).
  The screen checks (Take Off circle / joysticks / pop-up) were tested on saved screenshots of your phone.
"""
import time
import DJIneo


class Drone:
    def __init__(self, settings_file="settings.txt", device=None):
        self._neo = DJIneo.DJIneo(device=device, settingsFile=settings_file)
        self._last_frame_time = None

    # ---- the drone battery, read from the ring in the top bar ---------------
    RING_CENTER = (758.0, 171.5)          # centre of the battery ring on this phone (1080 x 2280)
    RING_REGION = (112, 232, 690, 1030)   # top, bottom, left, right: ring + flight timer (saved as a small picture)

    def battery_crop(self, frame=None):
        """The small picture of the battery ring and the flight timer, or None."""
        frame = self.screen() if frame is None else frame
        if not self._screen_ok(frame):
            return None
        t, b, l, r = self.RING_REGION
        return frame[t:b, l:r].copy()

    def _ring_profile(self, frame):
        """For each degree around the ring (0 = top, clockwise): how coloured is the arc band (radius 27-34.5)?"""
        import math
        cx, cy = self.RING_CENTER
        prof = []
        for deg in range(360):
            th = math.radians(deg)
            best = 0
            for k in range(16):
                rad = 27 + 0.5 * k
                x = int(round(cx + rad * math.sin(th)))
                y = int(round(cy - rad * math.cos(th)))
                p = frame[y, x]
                best = max(best, int(p.max()) - int(p.min()))
            prof.append(best)
        return prof

    def battery_info(self, frame=None):
        """(percent or None, short text saying how it was read, or why not). Works on a picture already in memory (a few ms)."""
        frame = self.screen() if frame is None else frame
        if frame is None:
            return None, "no picture from the phone yet"
        if not self._screen_ok(frame):
            return None, f"the picture is too small ({frame.shape[1]}x{frame.shape[0]}, expected 1080x2280)"
        prof = sorted(self._ring_profile(frame))
        p95 = prof[int(0.95 * 359)]
        if p95 < 25:
            return None, f"no coloured ring found at the expected place (colour strength {p95}); is the ring on the screen?"
        thr = max(12, 0.4 * p95)
        coloured = [v > thr for v in self._ring_profile(frame)]
        if all(coloured):
            return 100, "full ring"
        count = sum(coloured)
        start = next((d for d in range(-15, 16) if coloured[d % 360]), None)
        if start is not None:                                        # normal case: one arc from the top, clockwise
            end = start
            while end < start + 360 and coloured[(end + 1) % 360]:
                end += 1
            if end - start + 1 >= count - 12:                        # the arc is one piece
                pct = round((end - 4.6) / 3.6)                       # fitted on 44, 45, 46 and 71 percent
                if 1 <= pct <= 100:
                    return pct, f"arc end {end} deg"
        pct = round((count - 12) / 3.6)                              # fallback: total coloured angle
        if 1 <= pct <= 100:
            return pct, f"estimated from the total coloured angle ({count} deg); check the picture"
        return None, f"the ring looks odd ({count} coloured degrees); check the picture"

    def battery_percent(self, frame=None):
        """Drone battery in percent, or None."""
        return self.battery_info(frame)[0]

    def describe_screen(self, frame=None):
        """A short human description of what DJI Fly is showing, for messages."""
        frame = self.screen() if frame is None else frame
        if not self._screen_ok(frame):
            return "no readable picture from the phone"
        if self.popup_visible(frame):
            return "the 'safe to land?' pop-up"
        if self.stop_screen_visible(frame):
            return "the red STOP (landing) screen"
        if self.land_confirm_visible(frame):
            return "the Land confirmation screen (tap 'Back' on the phone)"
        if self.on_ground_ready(frame):
            return "the ground screen with the Take Off circle"
        if self.in_flight_ui(frame):
            return "the in-flight screen with the joysticks (the drone seems to be in the air)"
        return "a screen I do not recognise (is DJI Fly in front, in Manual Control, with the drone connected?)"

    # ---- 1. take off / 2. land ------------------------------------------
    # ---- reading the screen: where are we in the app? --------------------
    GROUND_POINTS = ((440, 1447), (640, 1447), (539, 1560))   # inside the white Take Off circle (brightness 255 on the ground)
    GROUND_OUTSIDE = ((250, 1447), (830, 1447))              # just outside the circle: the grey panel (242)
    FLIGHT_POINTS = ((150, 1519), (950, 1519))                # inside the two joystick circles (brightness about 220 in the air)

    def _patch(self, frame, x, y):
        return float(frame[y - 6:y + 7, x - 6:x + 7].mean())

    def _screen_ok(self, frame):
        return frame is not None and frame.shape[0] >= 1570 and frame.shape[1] >= 960

    def on_ground_ready(self, frame=None):
        """True: the Take Off circle is showing. False: it is not. None: the screen cannot be read."""
        frame = self.screen() if frame is None else frame
        if not self._screen_ok(frame):
            return None
        inside = all(self._patch(frame, x, y) >= 250 for x, y in self.GROUND_POINTS)
        outside = all(self._patch(frame, x, y) < 250 for x, y in self.GROUND_OUTSIDE)      # a plain white page must not count
        return inside and outside

    def in_flight_ui(self, frame=None):
        """True if both joysticks are on the screen (the drone is in the air). None: the screen cannot be read."""
        frame = self.screen() if frame is None else frame
        if not self._screen_ok(frame):
            return None
        return all(150 <= self._patch(frame, x, y) < 232 for x, y in self.FLIGHT_POINTS)

    # ---- 1. take off / 2. land ------------------------------------------
    def takeoff(self, wait_ready=10.0, verify=6.0, tries=2, log=None):
        """Wait for the Take Off circle (and SAY what the phone shows while waiting), press and hold it, check that the joysticks
        appear, retry once. Returns what happened."""
        self.stop()
        t0 = time.time()
        ready = self.on_ground_ready()
        while ready is None and time.time() - t0 < 3.0:            # no picture yet: give it up to 3 s
            time.sleep(0.3)
            ready = self.on_ground_ready()
        if ready is not None:
            last = 0.0
            while not ready and time.time() - t0 < wait_ready:
                if log is not None and time.time() - last >= 2.5:
                    log(f"waiting for the Take Off circle ... the phone shows: {self.describe_screen()}")
                    last = time.time()
                time.sleep(0.5)
                ready = self.on_ground_ready()
            if not ready:
                return ("NOT STARTED: DJI Fly is not showing the Take Off circle. The phone shows: " + self.describe_screen() +
                        ". Nothing was pressed. Fix the phone screen (Manual Control, 'Takeoff permitted') and run it again.")
        for attempt in range(1, tries + 1):
            self._neo.takeoff()                                    # press and hold the Take Off button (3 s)
            if ready is None:
                return "take-off button pressed (the screen could not be read, so it was not checked)"
            end = time.time() + verify
            while time.time() < end:
                time.sleep(0.4)
                if self.in_flight_ui():
                    return f"took off (attempt {attempt})"
        return f"NO TAKE-OFF SEEN after {tries} tries. The phone shows: {self.describe_screen()}. Check the app, or hold Take Off by hand."

    def _hold(self, x, y, seconds):
        dev = self._neo._device
        pid = self._neo._pointerID_general
        dev.touchDown(pid, x, y)
        end = time.time() + seconds
        while time.time() < end:
            dev.touchMove(pid, x, y)
            time.sleep(0.1)
        dev.touchUp(pid, x, y)

    # ---- the "safe to land?" pop-up -------------------------------------
    POPUP_POINTS = ((240, 1070), (300, 1345), (800, 1345))   # three spots inside the dark pop-up (text area, Cancel, OK)
    POPUP_MAX_BRIGHTNESS = 80                                 # pop-up about 37; normal screens 150-242

    def screen(self):
        """The whole phone screen as an image (BGR), or None."""
        return self._neo._device.getLastFrame()

    def popup_visible(self, frame=None):
        """True if the dark 'safe to land?' pop-up is on the screen."""
        frame = self.screen() if frame is None else frame
        if frame is None:
            return False
        h, w = frame.shape[:2]
        for x, y in self.POPUP_POINTS:
            if y + 7 > h or x + 7 > w:
                return False
            if float(frame[y - 6:y + 7, x - 6:x + 7].mean()) >= self.POPUP_MAX_BRIGHTNESS:
                return False
        return True

    STOP_POINTS = ((420, 1500), (660, 1500), (540, 1590))     # inside the red STOP circle of the landing screen

    def stop_screen_visible(self, frame=None):
        """True if the red STOP circle of the landing screen is showing (the landing has started). None: the screen cannot be read."""
        frame = self.screen() if frame is None else frame
        if not self._screen_ok(frame):
            return None
        for x, y in self.STOP_POINTS:
            b, g, r = (float(v) for v in frame[y - 6:y + 7, x - 6:x + 7].reshape(-1, 3).mean(0))   # frames are BGR
            if not (r > 70 and r > 2.5 * g and r > 2.5 * b):
                return False
        return True

    CONFIRM_OUTSIDE = ((250, 1322), (830, 1322))              # just outside the big circle: the grey panel
    CONFIRM_POINTS = ((440, 1322), (640, 1322), (540, 1420))   # inside the big white "Land" circle of the confirmation screen

    def land_confirm_visible(self, frame=None):
        """True if the confirmation screen is showing (big white Land circle, 'Tap and hold to land'). None: screen unreadable."""
        frame = self.screen() if frame is None else frame
        if not self._screen_ok(frame):
            return None
        inside = all(self._patch(frame, x, y) >= 252 for x, y in self.CONFIRM_POINTS)
        outside = all(self._patch(frame, x, y) < 250 for x, y in self.CONFIRM_OUTSIDE)
        return inside and outside

    def land(self, hold_big=3.0):
        """Landing in DJI Fly is TWO steps (seen on 7.11): 1) a short tap on the small Land button opens a confirmation screen
        with a big white Land circle; 2) press and HOLD that big circle. Then a pop-up 'Make sure landing area is safe' may
        appear: tap OK only if it does. Finally check that the red STOP screen (landing started) appeared.
        Returns a short text saying exactly what happened."""
        self.stop()
        s = self._neo._settings
        self._hold(int(s["LAND_X"]), int(s["LAND_Y"]), 0.3)                       # step 1: short tap
        readable, seen = True, False
        t_end = time.time() + 3.0
        while time.time() < t_end:
            time.sleep(0.3)
            c = self.land_confirm_visible()
            if c is None:
                readable = False
                time.sleep(1.0)
                break
            if c:
                seen = True
                break
        if readable and not seen:
            return "the Land confirmation screen did not appear after the tap - nothing else was pressed. Hold Land by hand"
        bx = int(s.get("LAND_HOLD_X", 540))
        by = int(s.get("LAND_HOLD_Y", 1322))
        self._hold(bx, by, hold_big)                                              # step 2: hold the big Land circle
        # now watch the screen closely (every 0.15 s, up to 8 s): at 0.6 m the whole descent lasts only 1-2 seconds
        popup_text, taps = "no pop-up seen", 0
        saw_stop = saw_ground = False
        unreadable = False
        t_end = time.time() + 8.0
        while time.time() < t_end:
            time.sleep(0.15)
            frame = self.screen()
            if not self._screen_ok(frame):
                unreadable = True
                break
            if taps < 2 and self.popup_visible(frame):
                ok = (s.get("LAND_OK_X"), s.get("LAND_OK_Y"))
                if ok[0] is None or ok[1] is None:
                    popup_text = "pop-up seen, but LAND_OK_X / LAND_OK_Y are missing in settings.txt - tap OK by hand"
                    break
                self._hold(int(ok[0]), int(ok[1]), 0.2)
                taps += 1
                popup_text = "pop-up seen, tapped OK" + (" (twice)" if taps == 2 else "")
                continue
            if self.stop_screen_visible(frame):
                saw_stop = True
                break
            if self.on_ground_ready(frame):                                       # the Take Off circle is back: already landed
                saw_ground = True
                break
        if unreadable:
            return popup_text + "; (the screen cannot be read, so the start of the landing was not checked)"
        if saw_stop:
            return popup_text + "; LANDING STARTED (STOP screen seen)"
        if saw_ground:
            return popup_text + "; LANDED already (the Take Off circle is back)"
        return popup_text + "; NO LANDING STARTED within 8 s - hold Land by hand now"

    # ---- 3. send speeds -------------------------------------------------
    def send_speeds(self, forward=0.0, right=0.0, up=0.0, yaw_cw=0.0):
        """All values -1..1 = virtual-stick deflection (NOT m/s).
        Keep them small (0.2-0.3) in early tests."""
        self._neo.move(yaw_cw, up, right, forward)   # DJIneo order: rcw, du, lr, bf

    def stop(self):
        """Release all sticks -> drone hovers in place."""
        self._neo.move(0.0, 0.0, 0.0, 0.0)

    # ---- 4. get frame ---------------------------------------------------
    def get_frame(self):
        """Latest video frame (numpy BGR image) or None if not ready."""
        frame = self._neo.getFrame()
        if frame is not None:
            self._last_frame_time = time.time()
        return frame

    # ---- 5. get state ---------------------------------------------------
    def get_state(self):
        """The lab library gives no telemetry (battery, altitude, position).
        For now we only report link health."""
        age = None if self._last_frame_time is None else time.time() - self._last_frame_time
        return {"last_frame_age_s": age}

    # ---- cleanup --------------------------------------------------------
    def close(self):
        try:
            self.stop()
        finally:
            self._neo.destroy()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ---- rehearsal on the computer (Nimer's "simulate first" idea, 25.11): set DRONE_SIM=<video> -> every script gets the
# simulated drone from sim_drone.py instead of the real one. Empty / unset = the real drone (nothing changes).
import os as _os
if _os.environ.get("DRONE_SIM"):
    from sim_drone import SimDrone as Drone  # noqa: F811,E402
