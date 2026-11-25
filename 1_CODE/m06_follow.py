"""
m06_follow.py - Project 3760, M06: follow THE user - tracker + sticky ID + safety states + controller.

What it adds to m06_track.py:
  * STICKY ID: once the turban has chosen a track ID, we keep that ID. We switch to another ID only if the turban is
    seen on the NEW one for SWITCH_FRAMES processed frames in a row AND not on the current one (stops a red-shirt
    passer-by from stealing the user for one frame - the failure Nimer found on session 1).
  * SAFETY STATES:  FOLLOWING (user box this frame) -> controller output
                    UNSURE    (user not seen < LOST_AFTER s, or tracked > MAX_NO_TURBAN s without a turban) -> HOVER
                    LOST      (user not seen >= LOST_AFTER s) -> HOVER, pilot lands by hand
  * CONTROLLER (proportional): box centre -> yaw, box height -> forward/back (only with --forward).
    Dead band (no tiny moves), max stick, rate limit (no jerks). Values are stick deflection 0..1, not m/s.

Three ways to run (from 1_CODE; GPU env recommended):
  python m06_follow.py --video CLIP.mp4             OFFLINE on a recorded clip: shows what the drone WOULD do
  python m06_follow.py --live --dry                 LIVE camera from the drone, commands only shown, NOTHING sent
  python m06_follow.py --live                       LIVE, sends YAW only (drone turns to keep the user centred)
  python m06_follow.py --live --forward             LIVE, yaw + forward/back (only after yaw-only worked)
  options: --model yolo11m.pt (default yolo11n.pt)  --tracker botsort  --max-yaw 0.25  --seconds 60
  --colour   add the clothes colour to the user score (Nimer's idea; AUC 0.928 -> 0.978 on our frames).
             LIVE: the user stands ALONE, close, facing the drone -> press E (a few times) = "this is me" (enrolment).
             OFFLINE: enrols by itself on the first 5 frames with a clear turban (>= 0.8) and only one person.
             Until enrolled it works like without --colour (turban only).

SAFETY (live): drone already hovering at 1.5-2 m (take off by hand / T in record_video.py), phone in hand, DJI Fly in
Manual Control, open space. Esc in the window or Ctrl+C = sticks released (hover). Take over with the phone any time.
Output: 3_EVIDENCE/m06_tracking/<name>_follow.mp4 (+ _follow.csv: time, state, user id, box, yaw, forward, fps).
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m05                                    # turban colour, head check, hand filter, CONF
from user_score import user_scores, body_crop, colour_feat, colour_similarity   # identity score per box (0..1)

OUT = Path(__file__).resolve().parent.parent / "3_EVIDENCE" / "m06_tracking"
SWITCH_FRAMES = 3       # (old rule, --old-switch) turban on another ID this many frames in a row -> switch
# GUARDED SWITCH (default, 25.11 - Nimer's eye check: the red shirt held the lock 4-7 s while she was visible with 0.85-0.98):
SWITCH_SECONDS = 1.0    # the other person must look like the user for 1 s in a row ...
KEEP_MIN = 0.30         # ... AND our current user must look unlike the user (smoothed score < 0.30) or be out of view ...
SWITCH_MARGIN = 0.30    # ... AND the other must score clearly higher (by 0.30). Never switch while she is visible and scoring.
HEAD_DEFAULT = 0.20     # head area = top 20% of the box (anatomy: head ~1/8 of the body + turban); M05 used 35%
START_FRAMES = 2        # turban on the same ID this many frames in a row -> first lock
LOST_AFTER = 2.0        # s without the user -> LOST
MAX_NO_TURBAN = 10.0    # s of tracking without seeing the turban -> UNSURE (needs a re-confirm)
# controller
X_DEAD = 0.15           # |x error| below this -> no yaw
K_YAW = 0.5             # yaw stick per unit x error (x error -1..1)
TARGET_H = 0.45         # wanted user height / frame height (~3-4 m away)
H_DEAD = 0.08
K_FWD = 1.0
MAX_FWD = 0.15
RATE = 0.05             # max change of a stick value per processed frame
# --colour (Nimer's idea): user score = (turban + clothes colour similarity) / 2
COMBO_MIN = 0.55        # combined score needed to (re)confirm a person as the user (first value; tune on crossing clips)
ENROL_N = 5             # template = mean of up to 5 enrolment views
ENROL_AUTO_MIN = 0.8    # offline auto-enrolment: turban score >= 0.8 AND the only person in the picture


def clip(v, m):
    return max(-m, min(m, v))


class Follower:
    """Sticky-ID user choice + safety state. Feed it boxes, ids and the turban pick of one frame."""

    def __init__(self, guarded=True):
        self.user_id, self.cand, self.cand_n, self.cand_since = None, None, 0, None
        self.last_seen = self.last_turban = None
        self.switches = self.blocked = 0
        self.guarded = guarded
        self.ema = {}                                   # smoothed user score per track ID

    def update(self, t, boxes, ids, colour_box, scores=None):
        if scores is not None:
            for tid, sc in zip(ids, scores):
                if tid is not None:
                    self.ema[tid] = 0.7 * self.ema.get(tid, sc) + 0.3 * sc
        turban_id = None
        if colour_box is not None and boxes:
            k = max(range(len(boxes)), key=lambda j: m05.iou(boxes[j], colour_box))
            turban_id = ids[k]
        if turban_id is not None and turban_id == self.user_id:
            self.cand, self.cand_n, self.cand_since, self.last_turban = None, 0, None, t   # our user re-confirmed
        elif turban_id is not None:
            if turban_id == self.cand:
                self.cand_n += 1
            else:
                self.cand, self.cand_n, self.cand_since = turban_id, 1, t
            if self.user_id is None:
                ok = self.cand_n >= START_FRAMES
            elif not self.guarded:
                ok = self.cand_n >= SWITCH_FRAMES
            else:
                mine_visible = self.user_id in ids
                mine, theirs = self.ema.get(self.user_id, 0.0), self.ema.get(turban_id, 0.0)
                long_enough = t - self.cand_since >= SWITCH_SECONDS
                ok = long_enough and (not mine_visible or (mine < KEEP_MIN and theirs > mine + SWITCH_MARGIN))
                if long_enough and not ok:
                    self.blocked += 1                   # a switch the guard refused (she was visible and scoring)
            if ok:
                if self.user_id is not None:
                    self.switches += 1
                self.user_id, self.cand, self.cand_n, self.cand_since, self.last_turban = turban_id, None, 0, None, t
        else:
            self.cand, self.cand_n, self.cand_since = None, 0, None
        box = boxes[ids.index(self.user_id)] if self.user_id is not None and self.user_id in ids else None
        if box is not None:
            self.last_seen = t
            if self.last_turban is not None and t - self.last_turban > MAX_NO_TURBAN:
                return box, "UNSURE"
            return box, "FOLLOWING"
        if self.last_seen is None or t - self.last_seen >= LOST_AFTER:
            return None, "LOST"
        return None, "UNSURE"


class Controller:
    def __init__(self, max_yaw, use_forward):
        self.max_yaw, self.use_forward = max_yaw, use_forward
        self.yaw = self.fwd = 0.0

    def step(self, box, state, W, H):
        want_yaw = want_fwd = 0.0
        if state == "FOLLOWING" and box is not None:
            x1, y1, x2, y2 = box
            x_err = ((x1 + x2) / 2 - W / 2) / (W / 2)
            if abs(x_err) > X_DEAD:
                want_yaw = clip(K_YAW * x_err, self.max_yaw)
            h_err = TARGET_H - (y2 - y1) / H
            if self.use_forward and abs(h_err) > H_DEAD:
                want_fwd = clip(K_FWD * h_err, MAX_FWD)
        if state != "FOLLOWING":                    # safety: hover at once, no rate limit
            self.yaw = self.fwd = 0.0
        else:
            self.yaw += clip(want_yaw - self.yaw, RATE)
            self.fwd += clip(want_fwd - self.fwd, RATE)
        return round(self.yaw, 3), round(self.fwd, 3)


def draw(fr, boxes, ids, box, state, uid, yaw, fwd, fps, head, scores):
    """Box tags show the USER SCORE (is this our user? 0..1), not YOLO's detection confidence."""
    col = {"FOLLOWING": (0, 220, 0), "UNSURE": (0, 200, 255), "LOST": (0, 0, 255)}[state]
    for b, tid, sc in zip(boxes, ids, scores):
        if b != box:
            cv2.rectangle(fr, tuple(b[:2]), tuple(b[2:]), (255, 120, 0), 2)
            m05.label_box(fr, f"person {sc:.2f}", b[0], b[1], (255, 120, 0), 0.55)
    if box is not None:
        sc = scores[boxes.index(box)]
        cv2.rectangle(fr, tuple(box[:2]), tuple(box[2:]), col, 3)
        m05.label_box(fr, f"USER {sc:.2f} (id {uid})", box[0], box[1], col, 0.75)
    cv2.putText(fr, "tag number = user score (0 = not the user, 1 = surely the user)", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    H = fr.shape[0]
    cv2.putText(fr, head, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(fr, f"{state}   yaw {yaw:+.2f}  fwd {fwd:+.2f}   {fps:4.1f} FPS", (10, H - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, col, 2)


def main():
    ap = argparse.ArgumentParser(description="M06: follow THE user (sticky ID + states + controller)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--video", help="recorded clip (offline)")
    src.add_argument("--live", action="store_true", help="live drone camera")
    ap.add_argument("--dry", action="store_true", help="live: show commands, send nothing")
    ap.add_argument("--forward", action="store_true", help="also send forward/back (distance)")
    ap.add_argument("--model", default="yolo11n.pt")
    ap.add_argument("--tracker", default="botsort")
    ap.add_argument("--max-yaw", type=float, default=0.25)
    ap.add_argument("--seconds", type=float, default=0, help="stop after N s (0 = until Esc / end)")
    ap.add_argument("--colour", action="store_true", help="user score = turban + clothes colour (enrol with E)")
    ap.add_argument("--old-switch", action="store_true", help="old sticky rule (3 turban frames) instead of the guarded switch")
    ap.add_argument("--head", type=float, default=HEAD_DEFAULT, help="head area for the turban (0.20 default; M05 used 0.35)")
    a = ap.parse_args()
    try:
        import lap  # noqa: F401
    except ImportError:
        sys.exit("The tracker needs one extra package. Run:  python -m pip install lap   then start again.")

    model = m05.load_model(a.model)
    m05.HEAD_PART = a.head                                     # used by the hybrid pick and the user score
    fol, ctl = Follower(guarded=not a.old_switch), Controller(a.max_yaw, a.forward)
    OUT.mkdir(parents=True, exist_ok=True)
    name = ((Path(a.video).stem if a.video else time.strftime("live_%Y%m%d_%H%M%S")) + ("_colour" if a.colour else "")
            + ("_old" if a.old_switch else "") + (f"_head{int(a.head * 100)}" if a.head != HEAD_DEFAULT else ""))
    mode = "OFFLINE" if a.video else ("LIVE DRY (nothing sent)" if a.dry else "LIVE - SENDING " +
                                      ("yaw+forward" if a.forward else "yaw only"))
    head = (f"M06 follow  {a.model.replace('.pt', '')} + {a.tracker} + turban (head {a.head:.0%}"
            f"{', old switch' if a.old_switch else ', guarded switch'})   {mode}")
    print(head)
    drone = cap = None
    if a.video:
        cap = cv2.VideoCapture(a.video)
        if not cap.isOpened():
            sys.exit(f"Cannot open {a.video}")
        vfps = cap.get(cv2.CAP_PROP_FPS) or 25
    else:
        from drone_interface import Drone
        drone = Drone().__enter__()
    send = drone is not None and not a.dry
    writer, rows, n, t_start = None, [], 0, time.perf_counter()
    counts = {"FOLLOWING": 0, "UNSURE": 0, "LOST": 0}
    fps, t_prev = 0.0, time.perf_counter()
    try:                                                       # laptop battery in the log = clean, comparable speed results
        import psutil
    except ImportError:
        psutil = None
    batt, plugged = "", ""
    enrol = []                                                 # clothes-colour views of the user ("this is me")
    template = None
    want_enrol = False

    def enrol_view(fr, boxes, tscores, need_alone):
        """add one view of the user's clothes: the only person, or the clearest turban (>= 0.5)"""
        nonlocal template
        if not boxes:
            return False
        k = max(range(len(boxes)), key=lambda j: tscores[j])
        if need_alone and (len(boxes) != 1 or tscores[k] < ENROL_AUTO_MIN):
            return False
        if not need_alone and len(boxes) > 1 and tscores[k] < 0.5:
            return False
        c = body_crop(fr, boxes[k])
        if c is None:
            return False
        enrol.append(colour_feat(c))
        del enrol[:-ENROL_N]
        template = np.mean(enrol, 0).astype(np.float32)
        print(f"  enrolled view {len(enrol)} (t = {t:.1f} s)")
        return True

    try:
        while True:
            if cap is not None:
                ok, fr = cap.read()
                if not ok:
                    break
                t = n / vfps                                   # video time
            else:
                fr = drone.get_frame()
                if fr is None:
                    time.sleep(0.01)
                    continue
                fr = fr.copy()
                t = time.perf_counter() - t_start
            if a.seconds and t >= a.seconds:
                break
            H, W = fr.shape[:2]
            r = model.track(fr, persist=True, classes=[0], conf=m05.CONF, tracker=f"{a.tracker}.yaml", verbose=False)[0]
            boxes = r.boxes.xyxy.cpu().numpy().astype(int).tolist()
            ids = r.boxes.id.cpu().numpy().astype(int).tolist() if r.boxes.id is not None else [None] * len(boxes)
            mask = m05.turban_mask(fr)
            colour_box = m05.hybrid_user(mask, boxes)
            scores = user_scores(mask, boxes)                  # turban score per box
            if a.colour:
                if want_enrol or (cap is not None and len(enrol) < ENROL_N):
                    enrol_view(fr, boxes, scores, need_alone=cap is not None)
                    want_enrol = False
                if template is not None:                       # combined score decides who the user is
                    scores = [(ts + colour_similarity(template, fr, b)) / 2 for ts, b in zip(scores, boxes)]
                    k = max(range(len(boxes)), key=lambda j: scores[j]) if boxes else None
                    colour_box = boxes[k] if k is not None and scores[k] >= COMBO_MIN else None
            box, state = fol.update(t, boxes, ids, colour_box, scores)
            yaw, fwd = ctl.step(box, state, W, H)
            if send:
                if state == "FOLLOWING":
                    drone.send_speeds(forward=fwd, yaw_cw=yaw)
                else:
                    drone.stop()
            now = time.perf_counter()
            fps = 0.9 * fps + 0.1 / max(1e-3, now - t_prev) if n else 0.0
            t_prev = now
            counts[state] += 1
            if psutil is not None and n % 30 == 0:
                b = psutil.sensors_battery()
                if b is not None:
                    batt, plugged = b.percent, int(b.power_plugged)
            rows.append([round(t, 2), state, fol.user_id if box is not None else "", *(box or ["", "", "", ""]),
                         yaw, fwd, round(fps, 1), batt, plugged])
            tag = head + ("" if not a.colour else ("  + colour (enrolled)" if template is not None else
                                                   "  + colour: NOT enrolled - user alone in view, press E"))
            draw(fr, boxes, ids, box, state, fol.user_id, yaw, fwd, fps, tag, scores)
            if writer is None:
                writer = cv2.VideoWriter(str(OUT / f"{name}_follow.mp4"), cv2.VideoWriter_fourcc(*"mp4v"),
                                         vfps if cap is not None else 15, (W, H))
            writer.write(fr)
            n += 1
            if drone is not None:
                cv2.imshow("M06 follow (Esc = hover + stop)", fr)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    break
                if key in (ord("e"), ord("E")) and a.colour:
                    want_enrol = True
            elif n % 200 == 0:
                print(f"  {t:5.0f} s done ...")
    except KeyboardInterrupt:
        print("\nStopped with Ctrl+C.")
    finally:
        if drone is not None:
            drone.stop()
            drone.__exit__(None, None, None)
            cv2.destroyAllWindows()
        if cap is not None:
            cap.release()
        if writer is not None:
            writer.release()
    with open(OUT / f"{name}_follow.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "state", "user_id", "x1", "y1", "x2", "y2", "yaw", "forward", "fps",
                    "laptop_battery_pct", "plugged_in"])
        w.writerows(rows)
    tot = max(1, n)
    print(f"\n{n} frames: FOLLOWING {100 * counts['FOLLOWING'] / tot:.0f}%  UNSURE {100 * counts['UNSURE'] / tot:.0f}%  "
          f"LOST {100 * counts['LOST'] / tot:.0f}%   ID switches by turban: {fol.switches}"
          f"   switches refused by the guard: {fol.blocked}")
    print(f"Saved: {OUT / (name + '_follow.mp4')}  (+ .csv)")


if __name__ == "__main__":
    main()
