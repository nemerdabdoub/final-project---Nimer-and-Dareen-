"""
m05_tweak_sweep.py - can a SIMPLE setting help YOLO11n find small / far people, without breaking the user pick or the speed?
Tries confidence cut-off x input size on all hand-labelled frames (the same 403 frames as m05_userpick_allvideos.py).
Run from 1_CODE:  python m05_tweak_sweep.py
Output: M05_data/results/tweak_sweep_23.11/sweep.md
"""
import time
from pathlib import Path

import m05
from m05 import turban_mask, hybrid_user
import m05_userpick_allvideos as A
import cv2

OUT = A.HERE.parent / "M05_data" / "results" / "tweak_sweep_23.11"
CONFS = [0.25, 0.20, 0.15]
SIZES = [640, 800, 960]


def main():
    from ultralytics import YOLO
    OUT.mkdir(parents=True, exist_ok=True)
    frames = []
    for s, items in A.framesets().items():
        for it in items:
            img = cv2.imread(str(it[0]))
            frames.append((img, A.user_box(it, img), A.all_people(it, img)))
    model = YOLO(str(A.HERE / "yolo11n.pt"))
    rows = []
    for size in SIZES:
        model(frames[0][0], imgsz=size, verbose=False)                # warm-up
        for conf in CONFS:
            tp = fp = fn = btp = bn = 0
            out = {"right": 0, "wrong": 0, "missed": 0, "alarm": 0, "none": 0}
            t = 0.0
            for img, u, gp in frames:
                t0 = time.perf_counter()
                r = model(img, classes=[0], conf=conf, imgsz=size, verbose=False)[0]
                people = r.boxes.xyxy.cpu().numpy().tolist()
                pick = hybrid_user(turban_mask(img), people)
                t += time.perf_counter() - t0
                a, b, c = m05.match(people, gp)
                big = [q for q in gp if q[3] - q[1] >= m05.BIG_PERSON * img.shape[0]]
                tp, fp, fn, btp, bn = tp + a, fp + b, fn + c, btp + m05.match(people, big)[0], bn + len(big)
                out[A.judge(u, box=pick)] += 1
            wu = out["right"] + out["wrong"] + out["missed"]
            wo = out["alarm"] + out["none"]
            ms = 1000 * t / len(frames)
            rows.append((size, conf, 100 * tp / (tp + fn), 100 * btp / bn, 100 * tp / (tp + fp), fp,
                         100 * out["right"] / wu, out["wrong"], out["alarm"], 100 * (out["right"] + out["none"]) / (wu + wo), ms))
            print(rows[-1], flush=True)
    lines = ["# YOLO11n simple tweaks: confidence cut-off x input size (403 hand-labelled frames, hybrid = + turban)", "",
             "| input px | cut-off | people found (all) | following distance | precision | wrong boxes | user found | wrong person | false alarm | frames correct | ms/frame | FPS |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        tag = " (current)" if r[0] == 640 and r[1] == 0.25 else ""
        lines.append(f"| {r[0]}{tag} | {r[1]:.2f} | {r[2]:.1f}% | {r[3]:.1f}% | {r[4]:.1f}% | {r[5]} | {r[6]:.1f}% | {r[7]} | {r[8]} | "
                     f"{r[9]:.1f}% | {r[10]:.0f} | {1000 / r[10]:.1f} |")
    (OUT / "sweep.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
