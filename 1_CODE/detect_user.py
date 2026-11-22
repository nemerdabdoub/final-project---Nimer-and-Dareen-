"""
detect_user.py - Project 3760, milestone 23.11 (user detection)

Runs THREE methods on a recorded drone video and compares them:
  A. colour only  : finds the red/purple turban colour anywhere in the frame
  B. YOLO only    : finds every PERSON (it cannot tell which one is the user)
  C. hybrid       : YOLO finds the people, the turban colour INSIDE a person's box picks the user

Usage (in 1_CODE, the video file can be anywhere):
  python detect_user.py VIDEO.mp4                       -> YOLO11n, every 5th frame
  python detect_user.py VIDEO.mp4 yolo11s.pt            -> another model
  python detect_user.py VIDEO.mp4 yolo11n.pt 3          -> every 3rd frame

Output (next to the video, in a folder named <video>_detect_<model>):
  annotated.mp4   the video with boxes: green = user (hybrid), blue = other people, red = colour-only blobs
  frames.csv      one row per analysed frame: what each method found, and the time it took
  summary.txt     the numbers for the table
  check/          50 sample frames with the boxes drawn, for you to check BY EYE which ones are right

First time only: python -m pip install ultralytics
(the first run downloads the model file, a few MB)
"""
import csv
import os
import sys
import time

import cv2
import numpy as np

# ---- the turban colour, in HSV (OpenCV: H 0-179). Red wraps around 0, purple-red sits near 160-179.
# Tune these if the turban is missed or the mural is caught: run once, look at check/, adjust.
# Measured on 20.11 footage: the turban sits at hue 170-179 (purple-red); the orange-red mural sits at 0-19
# and only 1% of it reaches 170-179. So only the purple-red end is used.
HSV_RANGES = [((165, 110, 70), (179, 255, 255))]
MIN_BLOB_AREA = 150          # colour-only: ignore specks smaller than this (pixels)
HEAD_PART = 0.35             # hybrid: look for the turban in the TOP 35% of each person box
MIN_HEAD_FRACTION = 0.03     # hybrid: at least 3% of that head area must be turban-coloured
CONTRAST = 2.0               # ... and at least 2x more than the background just beside the head


def colour_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    m = np.zeros(hsv.shape[:2], np.uint8)
    for lo, hi in HSV_RANGES:
        m |= cv2.inRange(hsv, np.array(lo), np.array(hi))
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))


def colour_blobs(mask):
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask)
    return [tuple(stats[i, :4]) for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= MIN_BLOB_AREA]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    video = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "yolo11n.pt"
    step = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    from ultralytics import YOLO
    model = YOLO(model_name)

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        sys.exit(f"Cannot open {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    base = os.path.splitext(os.path.basename(video))[0]
    out_dir = os.path.join(os.path.dirname(os.path.abspath(video)),
                           f"{base}_detect_{os.path.splitext(os.path.basename(model_name))[0]}")
    os.makedirs(os.path.join(out_dir, "check"), exist_ok=True)

    writer = None
    rows = []
    check_every = max(1, (total // step) // 50)
    idx = analysed = 0
    print(f"{video}: {total} frames; analysing every {step}th with {model_name} ...")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step:
            idx += 1
            continue
        # A. colour only
        t0 = time.time()
        mask = colour_mask(frame)
        blobs = colour_blobs(mask)
        t_colour = time.time() - t0
        # B. YOLO people (class 0 = person)
        t0 = time.time()
        res = model(frame, classes=[0], verbose=False)[0]
        t_yolo = time.time() - t0
        people = [tuple(map(int, b)) for b in res.boxes.xyxy.tolist()]
        # C. hybrid: the person whose head area holds the most turban colour
        best, best_frac = None, 0.0
        W = mask.shape[1]
        for (x1, y1, x2, y2) in people:
            hy2 = y1 + max(1, int((y2 - y1) * HEAD_PART))
            head = mask[max(0, y1):hy2, max(0, x1):x2]
            if not head.size:
                continue
            frac = float((head > 0).mean())
            sw = max(4, (x2 - x1) // 2)                       # strips just left and right of the head
            side = np.concatenate([mask[max(0, y1):hy2, max(0, x1 - sw):max(0, x1)].ravel(),
                                   mask[max(0, y1):hy2, min(W, x2):min(W, x2 + sw)].ravel()])
            side_frac = float((side > 0).mean()) if side.size else 0.0
            if frac >= CONTRAST * side_frac and frac > best_frac:
                best, best_frac = (x1, y1, x2, y2), frac
        user = best if best_frac >= MIN_HEAD_FRACTION else None

        # draw
        vis = frame.copy()
        for (x, y, w, h) in blobs:
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 1)
        for p in people:
            if p != user:
                cv2.rectangle(vis, p[:2], p[2:], (255, 120, 0), 2)
        if user:
            cv2.rectangle(vis, user[:2], user[2:], (0, 220, 0), 3)
            cv2.putText(vis, "USER", (user[0], max(20, user[1] - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 0), 2)
        cv2.putText(vis, f"people {len(people)}  colour blobs {len(blobs)}  user {'yes' if user else 'no'}",
                    (10, vis.shape[0] - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        if writer is None:
            h, w = vis.shape[:2]
            writer = cv2.VideoWriter(os.path.join(out_dir, "annotated.mp4"),
                                     cv2.VideoWriter_fourcc(*"mp4v"), fps / step, (w, h))
        writer.write(vis)
        if analysed % check_every == 0:
            cv2.imwrite(os.path.join(out_dir, "check", f"f{idx:05d}.jpg"), vis)
        rows.append([idx, round(idx / fps, 2), len(blobs), len(people), int(user is not None),
                     round(best_frac, 3), round(t_colour * 1000, 1), round(t_yolo * 1000, 1)])
        analysed += 1
        idx += 1
        if analysed % 20 == 0:
            print(f"  {analysed} frames analysed ...")
    cap.release()
    if writer:
        writer.release()

    with open(os.path.join(out_dir, "frames.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "time_s", "colour_blobs", "people", "user_found_hybrid",
                    "turban_fraction", "colour_ms", "yolo_ms"])
        w.writerows(rows)

    n = len(rows) or 1
    def mean(col):
        return sum(r[col] for r in rows) / n
    lines = [
        f"video: {video}",
        f"model: {model_name}   frames analysed: {len(rows)} (every {step}th)",
        f"colour only : frames with >=1 blob {sum(r[2] > 0 for r in rows) / n:.0%},"
        f" average blobs per frame {mean(2):.1f}  (more than 1 = it also catches other red things)",
        f"YOLO only   : frames with >=1 person {sum(r[3] > 0 for r in rows) / n:.0%},"
        f" average people per frame {mean(3):.1f}  (it cannot say which one is the user)",
        f"hybrid      : frames where a user was picked {mean(4):.0%}",
        f"speed       : colour {mean(6):.1f} ms/frame, YOLO {mean(7):.1f} ms/frame"
        f" (= about {1000 / max(mean(7), 1e-6):.0f} frames/s on this computer)",
        "",
        "These are COUNTS, not accuracy. For accuracy: open check/ and count, for each method,",
        "in how many frames it marked the right person (the actor). Write it in the table.",
    ]
    open(os.path.join(out_dir, "summary.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nSaved in: {out_dir}")


if __name__ == "__main__":
    main()
