"""
m05_newclips_auto.py - quick M05 check on the NEW 22.11 clips (Medical Faculty, bike racks), never used for tuning.

No hand labels exist for these clips yet, so:
  * people / bikes: a much bigger model (YOLO11l at 1280 px) is the REFERENCE; the small models are compared
    with it (an ESTIMATE of detection rate, not a hand-labelled score).
  * the user (turban): every frame where colour-only or the hybrid says "user" is saved in a picture grid,
    so a person can check each pick by eye (wrong person / false alarm).

Run from 1_CODE:   python m05_newclips_auto.py [EVERY_SECONDS]      (default 1 = one frame per second)
Clips are read from 3_EVIDENCE/2026-11-22/. Results: M05_data/results/newclips_22.11/
"""
import csv
import sys
import time
from pathlib import Path

import cv2
import numpy as np

import m05
from m05 import turban_mask, colour_only_user, hybrid_user, iou

HERE = Path(__file__).resolve().parent
CLIPS = HERE.parent / "3_EVIDENCE" / "2026-11-22"
OUT = HERE.parent / "M05_data" / "results" / "newclips_22.11"
SMALL = ["yolo11n.pt", "yolo12n.pt", "yolo26n.pt", "yolo11n_drone_gentle.pt"]
REF = "yolo11l.pt"
REF_SIZE, REF_CONF = 1280, 0.35
CONF = 0.25
PERSON, BIKE_CLASSES = 0, (1, 3)          # COCO: 0 person, 1 bicycle, 3 motorcycle
BLACK = 20                                # mean brightness below this = "signal lost" screen


def boxes(model, img, **kw):
    r = model(img, classes=[0, 1, 3], verbose=False, **kw)[0]
    xy = r.boxes.xyxy.cpu().numpy().tolist()
    cl = r.boxes.cls.cpu().numpy().astype(int).tolist()
    cf = r.boxes.conf.cpu().numpy().tolist()
    return ([b for b, c in zip(xy, cl) if c == PERSON], [b for b, c in zip(xy, cl) if c in BIKE_CLASSES],
            [f for f, c in zip(cf, cl) if c == PERSON])


def greedy(pred, gt, thr=0.5):
    """-> set of matched gt indices, list of unmatched pred indices"""
    used, unmatched = set(), []
    for pi, p in enumerate(pred):
        best, bi = 0.0, -1
        for i, g in enumerate(gt):
            if i not in used and iou(p, g) > best:
                best, bi = iou(p, g), i
        if best >= thr:
            used.add(bi)
        else:
            unmatched.append(pi)
    return used, unmatched


def on_bike(person, bikes):
    """a rider: the person's lower half overlaps a bike box"""
    x1, y1, x2, y2 = person
    low = [x1, (y1 + y2) / 2, x2, y2]
    return any(iou(low, b) > 0.1 for b in bikes)


def grid(tiles, path, cols=6):
    if not tiles:
        return
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(str(path), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])


def main():
    every = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    from ultralytics import YOLO
    OUT.mkdir(parents=True, exist_ok=True)
    small = {n: YOLO(str(HERE / n)) for n in SMALL}
    ref = YOLO(str(HERE / REF))
    rows, times = [], {n: [] for n in SMALL}
    picks, alarms = [], []                                    # picture tiles for the by-eye check
    for clip in sorted(CLIPS.glob("*.mp4")):
        cap = cv2.VideoCapture(str(clip))
        fps, n = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, int(round(fps * every)))
        print(f"{clip.name}: {n / fps:.0f} s, one frame every {every:g} s")
        for fi in range(0, n, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
            ok, img = cap.read()
            if not ok:
                break
            t = fi / fps
            row = {"clip": clip.stem[:6], "t_s": round(t, 1)}
            if img.mean() < BLACK:
                row["signal_lost"] = 1
                rows.append(row)
                continue
            row["signal_lost"] = 0
            H = img.shape[0]
            gp, gb, _ = boxes(ref, img, imgsz=REF_SIZE, conf=REF_CONF)
            big = [i for i, g in enumerate(gp) if g[3] - g[1] > m05.BIG_PERSON * H]
            riders = [i for i, g in enumerate(gp) if on_bike(g, gb)]
            row.update(ref_people=len(gp), ref_big=len(big), ref_riders=len(riders), ref_bikes=len(gb))
            for name, model in small.items():
                t0 = time.perf_counter()
                pp, pb, _ = boxes(model, img, conf=CONF)
                times[name].append(time.perf_counter() - t0)
                hit, extra = greedy(pp, gp)
                k = Path(name).stem
                bike_as_person = sum(1 for i in extra if any(iou(pp[i], b) > 0.3 for b in gb))
                row.update({f"{k}_tp": len(hit), f"{k}_fp": len(extra), f"{k}_big_tp": len(hit & set(big)),
                            f"{k}_rider_tp": len(hit & set(riders)), f"{k}_bikes": len(pb),
                            f"{k}_bike_as_person": bike_as_person})
                if name == "yolo11n.pt":
                    people11 = pp
            mask = turban_mask(img)
            c = colour_only_user(mask)
            u = hybrid_user(mask, people11)
            row["colour_user"] = int(c is not None)
            row["hybrid_user"] = int(u is not None)
            tag = f"{row['clip']} {t:.0f}s"
            if u is not None:
                x1, y1, x2, y2 = u
                pad = int(0.3 * (y2 - y1))
                crop = img[max(0, y1 - pad):y2 + pad, max(0, x1 - pad):x2 + pad]
                tile = cv2.resize(crop, (200, 300))
                cv2.putText(tile, tag, (4, 20), 0, 0.55, (0, 255, 255), 2)
                picks.append(tile)
            if c is not None and u is None:
                tile = img.copy()
                cv2.circle(tile, (int(c[0]), int(c[1])), 40, (0, 255, 255), 5)
                tile = cv2.resize(tile, (360, 203))
                cv2.putText(tile, tag + " colour only", (4, 20), 0, 0.55, (0, 255, 255), 2)
                alarms.append(tile)
            rows.append(row)
        cap.release()

    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("clip", "t_s", "signal_lost"), k))
    with open(OUT / "per_frame.csv", "w", newline="") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(rows)
    grid(picks, OUT / "hybrid_user_picks.jpg")
    grid(alarms, OUT / "colour_only_alarms.jpg", cols=4)

    # summary per clip and in total
    lines = []
    for clip in sorted({r["clip"] for r in rows}) + ["all"]:
        R = [r for r in rows if clip in ("all", r["clip"])]
        V = [r for r in R if not r["signal_lost"]]
        s = lambda k: sum(r.get(k, 0) for r in V)
        lines.append(f"\n## clip {clip}: {len(R)} frames, {len(R) - len(V)} signal lost, {len(V)} analysed")
        lines.append(f"reference ({REF} @ {REF_SIZE}px): {s('ref_people')} people, {s('ref_big')} big (> 1/4 height), "
                     f"{s('ref_riders')} on a bike, {s('ref_bikes')} bikes; frames with people: "
                     f"{sum(1 for r in V if r['ref_people'])}")
        lines.append("| model | agrees with reference: all % | big % | riders % | extra boxes (not in ref) | "
                     "extra on a bike | bikes found | ms/frame |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for name in SMALL:
            k = Path(name).stem
            pct = lambda a, b: f"{100 * a / b:.1f}" if b else "-"
            ms = 1000 * np.mean(times[name]) if times[name] else 0
            lines.append(f"| {k} | {pct(s(k + '_tp'), s('ref_people'))} | {pct(s(k + '_big_tp'), s('ref_big'))} | "
                         f"{pct(s(k + '_rider_tp'), s('ref_riders'))} | {s(k + '_fp')} | {s(k + '_bike_as_person')} | "
                         f"{s(k + '_bikes')} / {s('ref_bikes')} | {ms:.0f} |")
        lines.append(f"turban: colour-only says 'user' in {s('colour_user')} frames, hybrid in {s('hybrid_user')} "
                     f"frames (check each in hybrid_user_picks.jpg / colour_only_alarms.jpg)")
    text = "\n".join(lines)
    (OUT / "summary.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
