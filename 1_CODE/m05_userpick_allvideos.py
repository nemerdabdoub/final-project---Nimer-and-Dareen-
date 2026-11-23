"""
m05_userpick_allvideos.py - "finding THE user" (Table B) for every method on ALL our videos so far, same rules everywhere.

Frame sets (one frame = one decision, no 1-second hold, exactly like Table B in m05.py):
  M05   20.11 clips, turban frames   : 132 frames, hand labels (3_EVIDENCE/m05_user_detection/labels_marker)
  NEW1  22.11 clip 143404 (ground)   : 1 frame / 2 s, user box marked by eye on YOLO11l boxes (user_gt_22.11.json)
  NEW2  22.11 clip 144943            : 1 frame / 2 s, user only in the first 10 s (ground), then 7-8 m over the car park
                                       (red cars, red dome, no user) -> mostly a false-alarm test
  (The 20 no-turban frames of 154124 are left out: no colour method can find a user without the turban.)

Methods: colour only; each detector alone (its guess = the biggest person); each detector + turban colour (hybrid).
Rules per frame: user in frame -> right (IoU >= 0.5 with the user box; colour: point inside it) / wrong / missed;
                 no user -> false alarm if anything is picked, else correct.
Output: M05_data/results/userpick_allvideos_22.11/  (table.md, counts.csv)
Run from 1_CODE:  python m05_userpick_allvideos.py
"""
import csv
import json
import time
from pathlib import Path

import cv2

import m05
from m05 import turban_mask, colour_only_user, hybrid_user, iou, read_labels, frames_in

HERE = Path(__file__).resolve().parent
EV = HERE.parent / "3_EVIDENCE" / "m05_user_detection"
OUT = HERE.parent / "M05_data" / "results" / "userpick_allvideos_22.11"
GT_NEW = OUT / "user_gt_22.11.json"
DETECTORS = ["yolo11n.pt", "yolo12n.pt", "yolo26n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11n_drone_gentle.pt"]


def framesets():
    sets = {"M05": []}
    for p in frames_in(EV / "frames"):
        g = read_labels(EV / "labels_marker", p, (1, 1))       # normalised; scaled when the image is read
        if g is not None:
            sets["M05"].append((p, "marker"))
    gt = json.loads(GT_NEW.read_text())
    sets["NEW1"] = [(EV / "newclips_22.11_frames" / n, gt[n]) for n in sorted(gt) if n.startswith("143404")]
    sets["NEW2"] = [(EV / "newclips_22.11_frames" / n, gt[n]) for n in sorted(gt) if n.startswith("144943")]
    return sets


def user_box(item, img):
    p, g = item
    if g == "marker":
        users = read_labels(EV / "labels_marker", p, img.shape)[0]
        return users[0] if users else None
    return g                                                   # [x1, y1, x2, y2] or None


def judge(u, box=None, point=None):
    if u is not None:
        if box is not None:
            return "right" if iou(box, u) >= m05.IOU_MATCH else "wrong"
        if point is not None:
            return "right" if u[0] <= point[0] <= u[2] and u[1] <= point[1] <= u[3] else "wrong"
        return "missed"
    return "alarm" if (box is not None or point is not None) else "none"


def main():
    from ultralytics import YOLO
    OUT.mkdir(parents=True, exist_ok=True)
    sets = framesets()
    cache = {}                                                 # image + user box per frame
    for s, items in sets.items():
        for it in items:
            img = cv2.imread(str(it[0]))
            cache[(s, str(it[0]))] = (img, user_box(it, img))
    results, speed = {}, {}                                    # (method, set) -> outcome counts

    def add(method, s, outcome):
        d = results.setdefault((method, s), {"right": 0, "wrong": 0, "missed": 0, "alarm": 0, "none": 0})
        d[outcome] += 1

    t = 0.0
    for (s, _), (img, u) in cache.items():
        t0 = time.perf_counter()
        pt = colour_only_user(turban_mask(img))
        t += time.perf_counter() - t0
        add("colour only", s, judge(u, point=pt))
    speed["colour only"] = 1000 * t / len(cache)
    for det in DETECTORS:
        model = YOLO(str(HERE / det))
        name = det.replace(".pt", "")
        model(next(iter(cache.values()))[0], verbose=False)
        t = 0.0
        for (s, _), (img, u) in cache.items():
            t0 = time.perf_counter()
            people = m05.people_of(model, img)
            pick = hybrid_user(turban_mask(img), people)
            t += time.perf_counter() - t0
            add(f"hybrid {name}", s, judge(u, box=pick))
            big = max(people, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])) if people else None
            add(f"{name} alone", s, judge(u, box=big))
        speed[f"hybrid {name}"] = speed[f"{name} alone"] = 1000 * t / len(cache)
        print("done", name, flush=True)

    methods = ["colour only"] + [f"{d.replace('.pt', '')} alone" for d in DETECTORS] + \
              [f"hybrid {d.replace('.pt', '')}" for d in DETECTORS]
    rows = []
    for m in methods:
        for s in list(sets) + ["ALL"]:
            d = {k: sum(results[(m, x)][k] for x in sets) for k in ("right", "wrong", "missed", "alarm", "none")} \
                if s == "ALL" else results[(m, s)]
            withu = d["right"] + d["wrong"] + d["missed"]
            without = d["alarm"] + d["none"]
            rows.append([m, s, withu, without, d["right"], d["wrong"], d["missed"], d["alarm"],
                         d["right"] + d["none"], round(speed[m], 1)])
    with open(OUT / "counts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "set", "frames with user", "frames without user", "right", "wrong person", "missed",
                    "false alarm", "frames correct", "ms/frame (whole method)"])
        w.writerows(rows)

    pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "-"
    lines = ["# Finding THE user on ALL our videos (same rules for every method)", "",
             "Sets: " + ", ".join(f"{s} = {len(v)} frames" for s, v in sets.items()) +
             ". Counts in counts.csv; % = count / frames.", ""]
    for s in list(sets) + ["ALL"]:
        R = [r for r in rows if r[1] == s]
        lines += [f"## {s}  (frames with the user: {R[0][2]}, without: {R[0][3]})", "",
                  "| method | user found | wrong person | missed | false alarm | frames correct | ms/frame |",
                  "|---|---|---|---|---|---|---|"]
        for r in R:
            _, _, wu, wo, right, wrong, missed, alarm, correct, ms = r
            lines.append(f"| {r[0]} | {pct(right, wu)} ({right}/{wu}) | {pct(wrong, wu)} ({wrong}) | {pct(missed, wu)} | "
                         f"{pct(alarm, wo)} ({alarm}/{wo}) | {pct(correct, wu + wo)} | {ms} |")
        lines.append("")
    (OUT / "table.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
