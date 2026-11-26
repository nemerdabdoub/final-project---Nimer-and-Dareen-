"""
twin.py - Project 3760: DIGITAL TWIN of our DJI Neo for tuning the follow controller WITHOUT flying (25.11).

What it is: a recorded hover clip (the drone still, the user walking) is played FRAME BY FRAME (same frames every run =
fair comparisons). The twin shows only a window of the wide picture (VIEW = 60% of the width); the controller's commands
move that window like the real drone would turn / slide, using a drone model measured in the field:
  * delay      DELAY s between a command and its effect in the picture (25.11: ~0.5 s total loop, 2 samples)
  * turn rate  YAW_RATE deg/s at full yaw stick, with a first-order lag TAU s (speeds up / slows down, not instant)
  * sideways   SIDE_RATE deg-equivalent/s at full side stick (approximation: a slide also shifts the picture)
  * battery    BATT_DRAIN % per minute (25.11 automatic run: 50 -> 34 % in ~3 min)
Then the SAME follow logic as the real flights (m06_follow: Follower + Controller) runs on the window.

Score per run: % of frames FOLLOWING (user locked), mean |off-centre|, oscillation (yaw sign flips per minute),
% of frames the user is even in the window. Use it to COMPARE settings; confirm the best one with one real flight.

  python twin.py --video ..\\3_EVIDENCE\\2026-11-25\\164955_recording_walk_60s.mp4 --max-yaw 0.3
  python twin.py --video ... --sweep          (tries several settings, prints a table, saves twin_results.csv)
  python twin.py --video ... --labels ..\\M05_data\\test_22.11\\labels --seconds 0 --sweep-acc   (accuracy sweep, 26.11)
  python twin.py --video ... --labels ... --seconds 0 --colour --sweep-trackers   (all 6 trackers vs hand labels)
  options: --model yolo11m.pt  --imgsz 800  --turban wide  --clothes-thr 0.40  --colour
  options: --k-yaw 0.6  --predict  --no-search  --side  --delay 0.5  --yaw-rate 90  --tau 0.3  --seconds 60  --show
Limits (honest): people in the clip do not react to the drone; sideways / forward motion is only approximated; numbers
are for comparing settings, not exact predictions. Validate: same settings as a real run -> similar "in view %".
"""
import argparse
import csv
import sys
from collections import deque
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m05
import m06_follow as F
from user_score import user_scores, body_crop, colour_feat, colour_similarity
import numpy as np

HFOV, VIEW = 118.0, 0.60
TURBAN_RANGES = {"default": [((165, 110, 70), (179, 255, 255))],
                 # 26.11: measured on session 1 (tuning clip): head covering hue 168-187 (wraps to 0-7)
                 "wide": [((165, 110, 70), (179, 255, 255)), ((0, 110, 70), (7, 255, 255))]}
OUT = Path(__file__).resolve().parent.parent / "3_EVIDENCE" / "twin"


class NeoModel:
    """delayed, lagged turn (and slide) of the virtual camera window"""

    def __init__(self, W, delay, yaw_rate, tau, side_rate, dt):
        self.W, self.vw = W, int(W * VIEW)
        self.off = (W - self.vw) / 2.0
        self.ppd = W / HFOV
        self.q = deque([(0.0, 0.0)] * max(1, int(round(delay / dt))))
        self.rate = 0.0
        self.yaw_rate, self.tau, self.side_rate, self.dt = yaw_rate, tau, side_rate, dt
        self.heading = 0.0

    def step(self, yaw, side):
        self.q.append((yaw, side))
        y, s = self.q.popleft()                       # command from DELAY seconds ago
        target = y * self.yaw_rate + s * self.side_rate
        self.rate += (target - self.rate) * min(1.0, self.dt / max(self.tau, 1e-3))
        deg = self.rate * self.dt
        self.heading += deg
        self.off = min(max(0.0, self.off + deg * self.ppd), self.W - self.vw)

    def view(self, frame):
        H = frame.shape[0]
        x = int(self.off)
        return cv2.resize(frame[:, x:x + self.vw], (self.W, H))


def run(video, model, s):
    """one twin run with settings dict s -> score dict"""
    cap = cv2.VideoCapture(video)
    vfps = cap.get(cv2.CAP_PROP_FPS) or 25
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(s.get("start", 0) * vfps))
    step = max(1, round(vfps / s["rate_hz"]))
    dt = step / vfps
    ok, fr = cap.read()
    if not ok:
        raise RuntimeError(f"cannot read {video}")
    H, W = fr.shape[:2]
    neo = NeoModel(W, s["delay"], s["yaw_rate"], s["tau"], 40.0, dt)
    F.K_YAW = s["k_yaw"]
    F.SEARCH_YAW = 0.0 if s["no_search"] else 0.15
    m05.HEAD_PART = F.HEAD_DEFAULT
    m05.TURBAN_HSV = TURBAN_RANGES[s.get("turban", "default")]
    thr = s.get("clothes_thr", 0.45)
    fol = F.Follower()
    ctl = F.Controller(s["max_yaw"], False, s["predict"], s["delay"], s["yaw_rate"], use_side=s["side"])
    model.predictor = None                            # fresh tracker per run
    i, n, foll, inview, sum_x, flips, last_sign = 0, 0, 0, 0, 0.0, 0, 0
    enrol, tmpl = [], None
    log = []                                              # (frame index, window offset, window width, locked box)
    batt = s["battery"]
    lock_changes, prev_id = 0, None                       # times the locked user ID changes to another ID
    while ok and (not s["seconds"] or i / vfps < s["seconds"]):
        if i % step == 0:
            t = i / vfps
            v = neo.view(fr)
            r = model.track(v, persist=True, classes=[0], conf=m05.CONF, tracker=f"{s.get('tracker', 'botsort')}.yaml", verbose=False,
                            imgsz=s.get("imgsz", 640))[0]
            boxes = r.boxes.xyxy.cpu().numpy().astype(int).tolist()
            ids = r.boxes.id.cpu().numpy().astype(int).tolist() if r.boxes.id is not None else [None] * len(boxes)
            mask = m05.turban_mask(v)
            scores = user_scores(mask, boxes)
            colour_box = m05.hybrid_user(mask, boxes)
            if s.get("colour"):
                if len(enrol) < 5 and len(boxes) == 1:         # like the flight: learn the clothes when she is alone
                    c = body_crop(v, boxes[0])
                    if c is not None:
                        enrol.append(colour_feat(c))
                        tmpl = np.mean(enrol, 0).astype(np.float32)
                        if ids[0] is not None:
                            fol.user_id = ids[0]
                if tmpl is not None and boxes:
                    scores = [(ts + colour_similarity(tmpl, v, b)) / 2 for ts, b in zip(scores, boxes)]
                    kb = max(range(len(boxes)), key=lambda j: scores[j])
                    colour_box = boxes[kb] if scores[kb] >= thr else None
            box, state = fol.update(t, boxes, ids, colour_box, scores)
            if fol.user_id is not None:
                if prev_id is not None and fol.user_id != prev_id:
                    lock_changes += 1
                prev_id = fol.user_id
            batt -= s["drain"] * dt / 60
            if batt <= 30:
                state = "LOST"
            yaw, _ = ctl.step(box, state, W, H)
            side = ctl.side if state == "FOLLOWING" else 0.0
            if not (state == "FOLLOWING" or (state == "UNSURE" and yaw)):
                yaw, side = 0.0, 0.0
            log.append((i, neo.off, neo.vw, box if state == "FOLLOWING" else None))
            neo.step(yaw, side)
            n += 1
            if boxes:
                inview += 1
            if state == "FOLLOWING" and box is not None:
                foll += 1
                sum_x += abs(((box[0] + box[2]) / 2 - W / 2) / (W / 2))
            sg = (yaw > 0) - (yaw < 0)
            if sg and last_sign and sg != last_sign:
                flips += 1
            if sg:
                last_sign = sg
            if s.get("show"):
                F.draw(v, boxes, ids, box, state, fol.user_id, yaw, 0.0, s["rate_hz"], "DIGITAL TWIN", scores)
                cv2.imshow("digital twin", v)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
        ok, fr = cap.read()
        i += 1
    cap.release()
    if s.get("show"):
        cv2.destroyAllWindows()
    mins = max(1e-6, n * dt / 60)
    return {"following_%": round(100 * foll / max(1, n), 1), "mean_off_centre": round(sum_x / max(1, foll), 3),
            "people_in_view_%": round(100 * inview / max(1, n), 1), "yaw_flips_per_min": round(flips / mins, 1),
            "turned_deg": round(neo.heading, 0), "lock_changes": lock_changes, "frames": n, "_log": log, "_W": W}


def check_labels(log, W, video, labels):
    """compare the twin's locked box (mapped back to the full picture) with the hand-labelled user box"""
    stem = Path(video).stem
    cap = cv2.VideoCapture(video)
    Hh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    res = {"right": 0, "wrong": 0, "missed": 0, "user_outside_view": 0, "ok_none": 0, "false_pick": 0}
    for i, off, vw, box in log:
        lab = m05.read_labels(labels, Path(f"{stem}_{i:05d}.jpg"), (Hh, W))
        if lab is None:
            continue
        users = lab[0]
        full = None
        if box is not None:
            k = vw / W                                  # twin window -> full picture
            full = [off + box[0] * k, box[1], off + box[2] * k, box[3]]
        if users:
            u = users[0]
            cx = (u[0] + u[2]) / 2
            if not (off <= cx <= off + vw):
                res["user_outside_view"] += 1
            elif full is None:
                res["missed"] += 1
            elif m05.iou(full, u) >= 0.3:
                res["right"] += 1
            else:
                res["wrong"] += 1
        else:
            res["false_pick" if full is not None else "ok_none"] += 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--model", default="yolo11n.pt")
    ap.add_argument("--max-yaw", type=float, default=0.3)
    ap.add_argument("--k-yaw", type=float, default=0.6)
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--no-search", action="store_true")
    ap.add_argument("--side", action="store_true")
    ap.add_argument("--colour", action="store_true", help="learn the clothes when alone (like the flight fix)")
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--yaw-rate", type=float, default=90.0)
    ap.add_argument("--tau", type=float, default=0.3)
    ap.add_argument("--rate-hz", type=float, default=15.0, help="controller rate (real flights ~19 FPS)")
    ap.add_argument("--seconds", type=float, default=60)
    ap.add_argument("--start", type=float, default=0, help="start at this second of the clip (skip take-off)")
    ap.add_argument("--battery", type=float, default=100)
    ap.add_argument("--drain", type=float, default=5.0, help="battery %% per minute")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--turban", default="default", choices=list(TURBAN_RANGES))
    ap.add_argument("--clothes-thr", type=float, default=0.45)
    ap.add_argument("--sweep-acc", action="store_true", help="accuracy sweep: model, picture size, turban range, clothes threshold")
    ap.add_argument("--tracker", default="botsort", help="botsort bytetrack ocsort deepocsort fasttrack tracktrack")
    ap.add_argument("--sweep-trackers", action="store_true", help="all 6 Ultralytics trackers with the other settings fixed")
    ap.add_argument("--out", default="", help="CSV name in 3_EVIDENCE/twin")
    ap.add_argument("--labels", default="", help="hand-label folder (YOLO txt) -> count right / wrong person")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    import lap  # noqa: F401
    base = {k: getattr(a, k) for k in ("max_yaw", "k_yaw", "predict", "no_search", "side", "delay", "yaw_rate", "tau",
                                         "rate_hz", "seconds", "battery", "drain", "show", "start", "colour",
                                         "imgsz", "turban", "clothes_thr", "model", "tracker")}
    tries = [base]
    if a.sweep:
        tries = []
        for my in (0.2, 0.3, 0.4):
            for search in (False, True):
                tries.append(dict(base, max_yaw=my, no_search=not search, predict=False, show=False))
        tries.append(dict(base, max_yaw=0.3, no_search=False, predict=True, show=False))
        tries.append(dict(base, max_yaw=0.4, no_search=False, predict=True, show=False))
    if a.sweep_trackers:
        tries = [dict(base, show=False, tracker=t) for t in
                 ("botsort", "bytetrack", "ocsort", "deepocsort", "fasttrack", "tracktrack")]
    if a.sweep_acc:                                   # one change at a time from the flight setting, then combinations
        b = dict(base, show=False)
        tries = [dict(b, colour=False), dict(b, colour=True)]
        tries += [dict(b, colour=True, clothes_thr=t) for t in (0.40, 0.50)]
        tries += [dict(b, colour=True, turban="wide"), dict(b, colour=True, imgsz=800)]
        tries += [dict(b, colour=True, model="yolo11m.pt"), dict(b, colour=False, model="yolo11m.pt")]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for s in tries:
        model = m05.load_model(s["model"])               # fresh model = fresh tracker IDs each run
        sc = run(a.video, model, s)
        row = {"tracker": s["tracker"], "model": s["model"], "imgsz": s["imgsz"], "turban": s["turban"], "clothes_thr": s["clothes_thr"],
               "max_yaw": s["max_yaw"], "k_yaw": s["k_yaw"], "search": not s["no_search"], "predict": s["predict"],
               "side": s["side"], "colour": s.get("colour", False), **sc}
        log, Wd = row.pop("_log"), row.pop("_W")
        if a.labels:
            row.update(check_labels(log, Wd, a.video, a.labels))
        if a.labels:
            inv = row["right"] + row["wrong"] + row["missed"]
            row["right_%_in_view"] = round(100 * row["right"] / max(1, inv), 1)
        rows.append(row)
        print("  ".join(f"{k}={v}" for k, v in row.items()), flush=True)
    path = OUT / (a.out or ("twin_sweep.csv" if (a.sweep or a.sweep_acc or a.sweep_trackers) else "twin_run.csv"))
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("saved", path)


if __name__ == "__main__":
    main()
