"""M05 - user detection: YOLO11 vs YOLOv12 vs YOLO26, plus the colour-marker idea.
Run from 1_CODE (OPEN_TERMINAL_HERE.bat). One-time install:  python -m pip install ultralytics

  python m05_yolo_compare.py extract <video.mp4> [every_n=10]   frames -> 3_EVIDENCE/<date>/m05_frames/
  python m05_yolo_compare.py run <frames_dir> [labels_dir]       results table (CSV + printout)
  python m05_yolo_compare.py marker <frames_dir> [labels_dir] [colour=orange]
  python m05_yolo_compare.py hybrid <frames_dir> <labels_dir> [model=yolo26n.pt] [colour=orange]
                                YOLO finds people, the marker picks WHICH one is the user
  python m05_yolo_compare.py video <video.mp4> [model=yolo26n.pt]  annotated demo video

labels_dir = YOLO-format .txt labels (Roboflow/CVAT export, same file names as the frames).
  Two classes: 0 = the user, 1 = any other person. run/marker count every box as "person";
  hybrid checks that the box it picked is the class-0 user.
Without labels the score is "frames with a person detected" (fine only if the user is in EVERY frame).
Every test also runs on a darkened copy of the frames (brightness x0.35) = the low-light check from the plan.
"""
import csv, sys, time
from datetime import date
from pathlib import Path
import cv2
import numpy as np

MODELS = ["yolo11n.pt", "yolo12n.pt", "yolo26n.pt"]   # add the "s" sizes if there is time
BRIGHTNESS = [1.0, 0.35]
CONF, IOU_MATCH = 0.25, 0.5
OUT = Path(__file__).resolve().parent.parent / "3_EVIDENCE" / date.today().isoformat()
COLOURS = {  # HSV ranges for a coloured vest / marker - check on 2-3 frames first
    "orange": [((5, 120, 120), (20, 255, 255))],
    "green":  [((40, 80, 80), (80, 255, 255))],
    "red":    [((0, 120, 100), (8, 255, 255)), ((170, 120, 100), (180, 255, 255))],
}


def frames_in(folder):
    return sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))


def gt_boxes(labels_dir, img_path, shape, only_cls=None):
    if labels_dir is None:
        return None
    f = Path(labels_dir) / (img_path.stem + ".txt")
    h, w = shape[:2]
    boxes = []
    if f.exists():
        for line in f.read_text().split("\n"):
            v = line.split()
            if len(v) >= 5 and (only_cls is None or int(float(v[0])) == only_cls):
                cx, cy, bw, bh = (float(x) for x in v[1:5])
                boxes.append([(cx - bw / 2) * w, (cy - bh / 2) * h, (cx + bw / 2) * w, (cy + bh / 2) * h])
    return boxes


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0


def match(pred, gt):
    """greedy IoU matching -> (TP, FP, FN)"""
    used, tp = set(), 0
    for p in pred:
        best, bi = 0, -1
        for i, g in enumerate(gt):
            if i not in used and iou(p, g) > best:
                best, bi = iou(p, g), i
        if best >= IOU_MATCH:
            used.add(bi)
            tp += 1
    return tp, len(pred) - tp, len(gt) - tp


def dark(img, k):
    return img if k == 1.0 else cv2.convertScaleAbs(img, alpha=k, beta=0)


def score(rows, name, k, tp, fp, fn, hit, n, t, has_gt):
    det = tp / (tp + fn) if has_gt and tp + fn else hit / n
    prec = tp / (tp + fp) if has_gt and tp + fp else float("nan")
    rows.append([name, k, n, f"{100 * det:.1f}", f"{100 * prec:.1f}", f"{n / t:.1f}", f"{1000 * t / n:.0f}"])


def write_table(rows, fname):
    OUT.mkdir(parents=True, exist_ok=True)
    head = ["method", "brightness", "frames", "detection rate %", "precision %", "FPS", "ms/frame"]
    with open(OUT / fname, "w", newline="") as f:
        csv.writer(f).writerows([head] + rows)
    print("\n" + " | ".join(head))
    for r in rows:
        print(" | ".join(str(x) for x in r))
    print(f"\nsaved: {OUT / fname}   (target in the plan: detection rate >= 90%)")


def cmd_extract(video, every=10):
    out = OUT / "m05_frames"
    out.mkdir(parents=True, exist_ok=True)
    cap, i, saved = cv2.VideoCapture(str(video)), 0, 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if i % every == 0:
            cv2.imwrite(str(out / f"{Path(video).stem}_{i:05d}.jpg"), fr)
            saved += 1
        i += 1
    print(f"{saved} frames -> {out}  (keep only frames you will label; aim for ~150)")


def cmd_run(folder, labels_dir=None):
    from ultralytics import YOLO
    imgs = frames_in(folder)
    rows = []
    for m in MODELS:
        model = YOLO(m)                       # downloads the weights the first time
        model(cv2.imread(str(imgs[0])), verbose=False)   # warm-up, not timed
        for k in BRIGHTNESS:
            tp = fp = fn = hit = 0
            t = 0.0
            for p in imgs:
                img = dark(cv2.imread(str(p)), k)
                t0 = time.perf_counter()
                r = model(img, classes=[0], conf=CONF, verbose=False)[0]
                t += time.perf_counter() - t0
                pred = r.boxes.xyxy.cpu().numpy().tolist()
                hit += bool(pred)
                g = gt_boxes(labels_dir, p, img.shape)
                if g is not None:
                    a, b, c = match(pred, g)
                    tp, fp, fn = tp + a, fp + b, fn + c
            score(rows, m.replace(".pt", ""), k, tp, fp, fn, hit, len(imgs), t, labels_dir is not None)
    write_table(rows, "m05_yolo_table.csv")


def marker_box(img, colour, min_area=150):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = sum(cv2.inRange(hsv, np.array(lo), np.array(hi)) for lo, hi in COLOURS[colour])
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cs = [c for c in cs if cv2.contourArea(c) >= min_area]
    if not cs:
        return None
    x, y, w, h = cv2.boundingRect(max(cs, key=cv2.contourArea))
    return [x, y, x + w, y + h]


def cmd_marker(folder, labels_dir=None, colour="orange"):
    imgs, rows = frames_in(folder), []
    for k in BRIGHTNESS:
        tp = fp = fn = hit = 0
        t = 0.0
        for p in imgs:
            img = dark(cv2.imread(str(p)), k)
            t0 = time.perf_counter()
            b = marker_box(img, colour)
            t += time.perf_counter() - t0
            hit += b is not None
            g = gt_boxes(labels_dir, p, img.shape)
            if g is not None:   # marker counts as correct if its centre is inside a labelled person box
                inside = b is not None and any(
                    q[0] <= (b[0] + b[2]) / 2 <= q[2] and q[1] <= (b[1] + b[3]) / 2 <= q[3] for q in g)
                tp += inside
                fp += (b is not None) and not inside
                fn += len(g) - inside
        score(rows, f"colour marker ({colour})", k, tp, fp, fn, hit, len(imgs), t, labels_dir is not None)
    write_table(rows, "m05_marker_table.csv")


def cmd_hybrid(folder, labels_dir, model_name="yolo26n.pt", colour="orange"):
    """User identification: among the YOLO person boxes, take the one that contains the marker.
    No marker seen -> fall back to the box closest to where the user was last frame (a 1-line tracker)."""
    from ultralytics import YOLO
    model = YOLO(model_name)
    imgs, rows = frames_in(folder), []
    model(cv2.imread(str(imgs[0])), verbose=False)
    for k in BRIGHTNESS:
        ok_id = n_user = by_marker = by_fallback = 0
        last, t = None, 0.0
        for p in imgs:
            img = dark(cv2.imread(str(p)), k)
            t0 = time.perf_counter()
            people = model(img, classes=[0], conf=CONF, verbose=False)[0].boxes.xyxy.cpu().numpy().tolist()
            m = marker_box(img, colour)
            pick = None
            if m is not None:
                cx, cy = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2
                inside = [b for b in people if b[0] <= cx <= b[2] and b[1] <= cy <= b[3]]
                if inside:
                    pick = min(inside, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
                    by_marker += 1
            if pick is None and people and last is not None:
                pick = max(people, key=lambda b: iou(b, last))
                by_fallback += 1
            t += time.perf_counter() - t0
            if pick is not None:
                last = pick
            user = gt_boxes(labels_dir, p, img.shape, only_cls=0)
            if user:
                n_user += 1
                ok_id += pick is not None and iou(pick, user[0]) >= IOU_MATCH
        n = len(imgs)
        rows.append([f"{model_name.replace('.pt', '')} + marker", k, n, f"{100 * ok_id / max(n_user, 1):.1f}",
                     f"marker {100 * by_marker / n:.0f}% / fallback {100 * by_fallback / n:.0f}%",
                     f"{n / t:.1f}", f"{1000 * t / n:.0f}"])
    OUT.mkdir(parents=True, exist_ok=True)
    head = ["method", "brightness", "frames", "user identified %", "picked by", "FPS", "ms/frame"]
    with open(OUT / "m05_hybrid_table.csv", "w", newline="") as f:
        csv.writer(f).writerows([head] + rows)
    print("\n" + " | ".join(head))
    for r in rows:
        print(" | ".join(str(x) for x in r))
    print(f"\nsaved: {OUT / 'm05_hybrid_table.csv'}")


def cmd_video(video, model_name="yolo26n.pt"):
    from ultralytics import YOLO
    model = YOLO(model_name)
    cap = cv2.VideoCapture(str(video))
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 30
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / f"m05_demo_{model_name.replace('.pt', '')}_{Path(video).stem}.mp4"
    writer = None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        t0 = time.perf_counter()
        r = model(fr, classes=[0], conf=CONF, verbose=False)[0]
        ms = 1000 * (time.perf_counter() - t0)
        img = r.plot()
        cv2.putText(img, f"{model_name}  {ms:.0f} ms/frame", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        if writer is None:
            writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps_in, img.shape[1::-1])
        writer.write(img)
    if writer:
        writer.release()
    print(f"saved: {out_path}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd, rest = a[0], a[1:]
    labels = rest[1] if len(rest) > 1 and cmd in ("run", "marker") else None
    if cmd == "extract":
        cmd_extract(rest[0], int(rest[1]) if len(rest) > 1 else 10)
    elif cmd == "run":
        cmd_run(rest[0], labels)
    elif cmd == "marker":
        cmd_marker(rest[0], labels, rest[2] if len(rest) > 2 else "orange")
    elif cmd == "hybrid":
        cmd_hybrid(rest[0], rest[1], rest[2] if len(rest) > 2 else "yolo26n.pt", rest[3] if len(rest) > 3 else "orange")
    elif cmd == "video":
        cmd_video(rest[0], rest[1] if len(rest) > 1 else "yolo26n.pt")
    else:
        sys.exit(__doc__)
