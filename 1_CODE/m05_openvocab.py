"""
m05_openvocab.py - work-plan item for 23.11: do open-vocabulary detectors (YOLO-World, YOLOE) find obstacles that
standard YOLO (80 COCO classes) cannot - e-scooters and baby strollers - and how do they do on people / bikes / cars?
(Obstacle classes are needed next semester for the obstacle map and path planning.)

Run from 1_CODE:  python m05_openvocab.py [EVERY_SECONDS]     (default 2)
Clips: 3_EVIDENCE/2026-11-22/*.mp4 (new, never used for tuning). No hand labels yet, so:
  * person / bicycle / car / motorcycle: compared with a big COCO model (YOLO11l at 1280 px) = REFERENCE (estimate)
  * scooter / stroller: no COCO class, no reference -> every detection is saved as a crop for a by-eye check
Output: M05_data/results/openvocab_22.11/  (summary.md, per_class.csv, crops_<model>.jpg, side_by_side_*.jpg)
"""
import csv
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from m05 import iou

HERE = Path(__file__).resolve().parent
CLIPS = HERE.parent / "3_EVIDENCE" / "2026-11-22"
OUT = HERE.parent / "M05_data" / "results" / "openvocab_22.11"
PROMPTS = ["person", "bicycle", "car", "motorcycle", "electric scooter", "baby stroller"]
COCO = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle"}
SHARED = ["person", "bicycle", "car", "motorcycle"]          # classes the reference can check
NEW = ["electric scooter", "baby stroller"]                  # classes only open-vocabulary models have
CONF = 0.25
BLACK = 20
COLOURS = {"person": (255, 120, 40), "bicycle": (0, 200, 255), "car": (60, 220, 60), "motorcycle": (200, 0, 200),
           "electric scooter": (0, 0, 255), "baby stroller": (255, 0, 255)}


def load():
    from ultralytics import YOLO, YOLOWorld, YOLOE
    ref = YOLO(str(HERE / "yolo11l.pt"))
    models = {"yolo11n (COCO)": YOLO(str(HERE / "yolo11n.pt"))}
    w = YOLOWorld("yolov8s-worldv2.pt")
    w.set_classes(PROMPTS)
    models["YOLO-World v2 s"] = w
    e = YOLOE("yoloe-11s-seg.pt")
    e.set_classes(PROMPTS)
    models["YOLOE-11s"] = e
    return ref, models


def detect(name, model, img, **kw):
    """-> list of (class name, box, conf)"""
    if name.startswith("yolo11"):
        r = model(img, classes=list(COCO), verbose=False, **kw)[0]
        names = COCO
    else:
        r = model(img, verbose=False, **kw)[0]
        names = {i: p for i, p in enumerate(PROMPTS)}
    out = []
    for b, c, f in zip(r.boxes.xyxy.cpu().numpy().tolist(), r.boxes.cls.cpu().numpy().astype(int).tolist(),
                       r.boxes.conf.cpu().numpy().tolist()):
        if c in names:
            out.append((names[c], b, f))
    return out


def draw(img, dets, title):
    im = img.copy()
    for cl, (x1, y1, x2, y2), f in dets:
        col = COLOURS[cl]
        cv2.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), col, 2)
        cv2.putText(im, f"{cl} {f:.2f}", (int(x1), max(14, int(y1) - 4)), 0, 0.5, col, 2)
    cv2.rectangle(im, (0, 0), (im.shape[1], 34), (20, 20, 20), -1)
    cv2.putText(im, title, (8, 25), 0, 0.8, (255, 255, 255), 2)
    return im


def main():
    every = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    OUT.mkdir(parents=True, exist_ok=True)
    ref, models = load()
    stats = {m: {c: [0, 0] for c in SHARED} for m in models}   # [matched ref boxes, extra boxes]
    refn = {c: 0 for c in SHARED}
    newn = {m: {c: 0 for c in NEW} for m in models}
    times = {m: [] for m in models}
    crops = {m: [] for m in models}
    scenes = []                                                 # (score, frame, dets per model) for side-by-side
    for clip in sorted(CLIPS.glob("*.mp4")):
        cap = cv2.VideoCapture(str(clip))
        fps, n = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, int(round(fps * every)))
        for fi in range(0, n, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
            ok, img = cap.read()
            if not ok:
                break
            if img.mean() < BLACK:
                continue
            tag = f"{clip.stem[:6]} {fi / fps:.0f}s"
            gt = detect("yolo11l", ref, img, imgsz=1280, conf=0.35)
            for c in SHARED:
                refn[c] += sum(1 for g in gt if g[0] == c)
            per = {}
            for m, model in models.items():
                t0 = time.perf_counter()
                d = detect(m, model, img, conf=CONF)
                times[m].append(time.perf_counter() - t0)
                per[m] = d
                for c in SHARED:
                    G = [g[1] for g in gt if g[0] == c]
                    used = set()
                    for _, b, _ in [x for x in d if x[0] == c]:
                        best = max(((iou(b, g), i) for i, g in enumerate(G) if i not in used), default=(0, -1))
                        if best[0] >= 0.5:
                            used.add(best[1])
                            stats[m][c][0] += 1
                        else:
                            stats[m][c][1] += 1
                for cl, (x1, y1, x2, y2), f in d:
                    if cl in NEW:
                        newn[m][cl] += 1
                        if len(crops[m]) < 48:
                            p = int(0.2 * max(x2 - x1, y2 - y1))
                            cr = img[max(0, int(y1) - p):int(y2) + p, max(0, int(x1) - p):int(x2) + p]
                            if cr.size:
                                t = cv2.resize(cr, (200, 200))
                                cv2.putText(t, f"{cl.split()[-1]} {f:.2f}", (4, 18), 0, 0.5, (0, 255, 255), 2)
                                cv2.putText(t, tag, (4, 192), 0, 0.45, (0, 255, 255), 1)
                                crops[m].append(t)
            busy = len(set(g[0] for g in gt)) * 10 + len(gt)
            scenes.append((busy, tag, img, per))
        cap.release()

    for m in models:                                             # crop grids for the by-eye check
        tiles = crops[m]
        if tiles:
            while len(tiles) % 8:
                tiles.append(np.zeros_like(tiles[0]))
            g = np.vstack([np.hstack(tiles[i:i + 8]) for i in range(0, len(tiles), 8)])
            cv2.imwrite(str(OUT / f"crops_{m.split()[0]}.jpg"), g, [cv2.IMWRITE_JPEG_QUALITY, 80])
    scenes.sort(key=lambda s: -s[0])                             # busiest frames, spread over the clips
    picked, seen = [], set()
    for s in scenes:
        if s[1][:6] + str(int(s[1].split()[1][:-1]) // 30) not in seen:
            picked.append(s)
            seen.add(s[1][:6] + str(int(s[1].split()[1][:-1]) // 30))
        if len(picked) == 4:
            break
    for k, (_, tag, img, per) in enumerate(picked):
        panels = [draw(img, per[m], f"{m}  ({tag})") for m in models]
        small = [cv2.resize(p, (p.shape[1] * 2 // 3, p.shape[0] * 2 // 3)) for p in panels]
        cv2.imwrite(str(OUT / f"side_by_side_{k + 1}.jpg"), np.vstack(small), [cv2.IMWRITE_JPEG_QUALITY, 82])

    lines = [f"# Open-vocabulary check on the 22.11 clips ({len(scenes)} frames, one every {every:g} s)",
             "Reference for the COCO classes = YOLO11l at 1280 px (estimate, not hand labels).", "",
             "| model | ms/frame | " + " | ".join(f"{c}: found % (extra)" for c in SHARED) + " | " +
             " | ".join(f"{c} boxes" for c in NEW) + " |",
             "|---" * (2 + len(SHARED) + len(NEW)) + "|"]
    rows = []
    for m in models:
        cells = []
        for c in SHARED:
            hit, extra = stats[m][c]
            cells.append(f"{100 * hit / refn[c]:.0f}% ({extra})" if refn[c] else f"- ({extra})")
        new = [str(newn[m][c]) if not m.startswith("yolo11") else "no class" for c in NEW]
        ms = 1000 * float(np.mean(times[m][1:] or times[m]))
        lines.append(f"| {m} | {ms:.0f} | " + " | ".join(cells) + " | " + " | ".join(new) + " |")
        rows.append([m, f"{ms:.0f}"] + [stats[m][c][0] for c in SHARED] + [stats[m][c][1] for c in SHARED] +
                    [newn[m][c] for c in NEW])
    lines.append("")
    lines.append("Reference counts: " + ", ".join(f"{c} {refn[c]}" for c in SHARED))
    lines.append("Scooter / stroller boxes must be checked by eye in crops_<model>.jpg (no reference exists).")
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    with open(OUT / "per_class.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "ms_per_frame"] + [f"{c}_found" for c in SHARED] + [f"{c}_extra" for c in SHARED] +
                   [f"{c}_boxes" for c in NEW] + [])
        w.writerow(["reference yolo11l@1280", ""] + [refn[c] for c in SHARED] + [""] * (len(SHARED) + len(NEW)))
        w.writerows(rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
