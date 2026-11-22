"""
m05.py - Project 3760, milestone 23.11 (M05): user detection.
Compares YOLO11n, YOLOv12n and YOLO26n, the colour marker (the purple-red turban) and the
hybrid (YOLO finds the people, the turban colour on the head picks the user), in normal light
and on darkened copies (x0.35 = the low-light check).

Run it from 1_CODE (OPEN_TERMINAL_HERE.bat). One-time install:  python -m pip install ultralytics
Everything is saved in  3_EVIDENCE/m05_user_detection/

 STEP 1  python m05.py extract VIDEO EVERY [VIDEO2 EVERY2 ...]
         takes every EVERY-th frame of each video into  frames/
         (use the clip WITH the actor, and one clip WITHOUT him for false-alarm tests)
 STEP 2  python m05.py prelabel
         draws SUGGESTED boxes with a big model (yolo11l) into  labels_suggested/  (YOLO format):
             class 0 = user (the actor in the turban)     class 1 = other person
         A PERSON MUST CORRECT THEM (Roboflow or makesense.ai): fix or add boxes, set the actor to
         class 0 and everyone else to class 1. Save the corrected files into  labels/  (same names).
 STEP 3  python m05.py run [colour | yolo11n | yolo12n | yolo26n | hybrid yolo11n | ...] [labels]
         the two results tables (person detection, and finding THE user), printed and saved as CSV.
         With no name: everything. With a name: only that check, saved as ..._<name>.csv
             colour          = colour only (the turban, no YOLO)          -> table B "colour only"
             yolo11n         = YOLO11n alone: finds people (table A); its guess for the user is the
                               biggest person box                         -> table B "yolo11n only"
             hybrid yolo11n  = YOLO11n + colour: the turban on a head picks the user
                                                                          -> table B "hybrid yolo11n"
         Optional, non-YOLO comparison (not part of "run" with no name):
             rtdetr-l        = RT-DETR alone (transformer detector)       -> table A + table B rows
             hybrid rtdetr-l = RT-DETR + colour                           -> table B "hybrid rtdetr-l"
 STEP 4  python m05.py video VIDEO [MODEL] [CONF]
         an annotated demo video: green = user (found by the turban colour), yellow = user kept by the
         fallback (colour lost, same person as the last frame), blue = other people.
         CONF (optional, default 0.25 like the tables): e.g. 0.4 hides most low-confidence wrong boxes (statues),
         but misses a few more people (on our frames: 17 -> 3 wrong boxes, 46 -> 55 missed people).
"""
import csv
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np

MODELS = ["yolo11n.pt", "yolo12n.pt", "yolo26n.pt"]
EXTRA_MODELS = ["rtdetr-l.pt"]       # optional non-YOLO comparison, only when named: run rtdetr-l


def load_model(name):
    """YOLO models and RT-DETR load with different classes in ultralytics."""
    from ultralytics import RTDETR, YOLO
    return RTDETR(name) if name.lower().startswith("rtdetr") else YOLO(name)
PRELABEL_MODEL = "yolo11l.pt"        # bigger than the tested ones, so the suggestions do not favour one of them
BRIGHTNESS = [1.0, 0.35]
CONF, IOU_MATCH = 0.25, 0.5

# turban colour: measured on the 20.11 footage. Turban = hue 170-179 (purple-red); the orange-red
# mural = hue 0-19 (only 1% of it reaches 170-179). OpenCV hue runs 0-179.
TURBAN_HSV = [((165, 110, 70), (179, 255, 255))]
MIN_BLOB_AREA = 60                    # colour only: ignore specks smaller than this (pixels)
HEAD_PART = 0.35                      # hybrid: look in the top 35% of each person box
MIN_HEAD_FRACTION = 0.03              # hybrid: at least 3% of the head area turban-coloured ...
CONTRAST = 2.0                        # ... and at least 2x more than the background just beside it
MAX_USER_W, MAX_USER_H = 0.6, 0.9     # hybrid: a "person" wider than 60% AND taller than 90% of the frame is a hand
                                      # in front of the lens, not the user (the actor is at most 22% wide in our labels)
BIG_PERSON = 0.25                     # table A extra column: people taller than 1/4 of the frame (following distance)

ROOT = Path(__file__).resolve().parent.parent / "3_EVIDENCE" / "m05_user_detection"
FRAMES, SUGGESTED, LABELS = ROOT / "frames", ROOT / "labels_suggested", ROOT / "labels"


# ---------------------------------------------------------------- helpers
def frames_in(folder):
    return sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))


def darken(img, k):
    return img if k == 1.0 else cv2.convertScaleAbs(img, alpha=k, beta=0)


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def match(pred, gt):
    """greedy IoU matching -> (TP, FP, FN)"""
    used, tp = set(), 0
    for p in pred:
        best, bi = 0.0, -1
        for i, g in enumerate(gt):
            if i not in used:
                v = iou(p, g)
                if v > best:
                    best, bi = v, i
        if best >= IOU_MATCH:
            used.add(bi)
            tp += 1
    return tp, len(pred) - tp, len(gt) - tp


def read_labels(folder, img_path, shape):
    """-> (user_boxes, person_boxes) in pixels, or None if the label file is missing"""
    f = Path(folder) / (img_path.stem + ".txt")
    if not f.exists():                                   # Roboflow renames files: name_jpg.rf.<code>.txt
        alt = sorted(Path(folder).glob(img_path.stem + "_jpg.rf.*.txt"))
        if not alt:
            return None
        f = alt[0]
    h, w = shape[:2]
    user, other = [], []
    for line in f.read_text().splitlines():
        v = line.split()
        if len(v) >= 5:
            c = int(float(v[0]))
            cx, cy, bw, bh = (float(x) for x in v[1:5])
            box = [(cx - bw / 2) * w, (cy - bh / 2) * h, (cx + bw / 2) * w, (cy + bh / 2) * h]
            (user if c == 0 else other).append(box)
    return user, other


def turban_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    # auto-gain: bring the average brightness up to about 110 first, so a dark picture still shows the colour
    v = hsv[:, :, 2].astype(np.float32)
    gain = min(4.0, 110.0 / max(1.0, float(v.mean())))
    hsv[:, :, 2] = np.clip(v * gain, 0, 255).astype(np.uint8)
    m = np.zeros(hsv.shape[:2], np.uint8)
    for lo, hi in TURBAN_HSV:
        m |= cv2.inRange(hsv, np.array(lo), np.array(hi))
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))


def colour_only_user(mask):
    """the biggest turban-coloured blob -> its centre (x, y), or None"""
    n, _, stats, cent = cv2.connectedComponentsWithStats(mask)
    best, area = None, MIN_BLOB_AREA - 1
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > area:
            best, area = tuple(cent[i]), stats[i, cv2.CC_STAT_AREA]
    return best


def hybrid_user(mask, people):
    """the person box whose head is most turban-coloured (and clearly more than the background beside it)"""
    best, best_frac = None, 0.0
    H, W = mask.shape[:2]
    for (x1, y1, x2, y2) in people:
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        if x2 - x1 > MAX_USER_W * W and y2 - y1 > MAX_USER_H * H:
            continue                                     # fills the frame: a hand at the lens, not the user
        hy2 = y1 + max(1, int((y2 - y1) * HEAD_PART))
        head = mask[max(0, y1):hy2, max(0, x1):x2]
        if not head.size:
            continue
        frac = float((head > 0).mean())
        sw = max(4, (x2 - x1) // 2)
        side = np.concatenate([mask[max(0, y1):hy2, max(0, x1 - sw):max(0, x1)].ravel(),
                               mask[max(0, y1):hy2, min(W, x2):min(W, x2 + sw)].ravel()])
        side_frac = float((side > 0).mean()) if side.size else 0.0
        if frac >= CONTRAST * side_frac and frac > best_frac:
            best, best_frac = [x1, y1, x2, y2], frac
    return best if best_frac >= MIN_HEAD_FRACTION else None


def people_of(model, img):
    r = model(img, classes=[0], conf=CONF, verbose=False)[0]
    return r.boxes.xyxy.cpu().numpy().tolist()


# ---------------------------------------------------------------- step 1
def cmd_extract(args):
    if len(args) < 2 or len(args) % 2:
        sys.exit("Use: python m05.py extract VIDEO EVERY [VIDEO2 EVERY2 ...]")
    FRAMES.mkdir(parents=True, exist_ok=True)
    total = 0
    for video, every in zip(args[0::2], args[1::2]):
        every = int(every)
        cap, i, saved = cv2.VideoCapture(video), 0, 0
        if not cap.isOpened():
            sys.exit(f"Cannot open {video}")
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            if i % every == 0:
                cv2.imwrite(str(FRAMES / f"{Path(video).stem}_{i:05d}.jpg"), fr)
                saved += 1
            i += 1
        print(f"{video}: {saved} frames")
        total += saved
    print(f"\n{total} frames in {FRAMES}   (aim for about 150 in total)")


# ---------------------------------------------------------------- step 2
def cmd_prelabel(args):
    from ultralytics import YOLO
    model = YOLO(PRELABEL_MODEL)
    SUGGESTED.mkdir(parents=True, exist_ok=True)
    imgs = frames_in(FRAMES)
    n_user = 0
    for k, p in enumerate(imgs, 1):
        img = cv2.imread(str(p))
        h, w = img.shape[:2]
        people = people_of(model, img)
        user = hybrid_user(turban_mask(img), people)
        lines = []
        for b in people:
            c = 0 if user is not None and iou(b, user) > 0.9 else 1
            n_user += c == 0
            cx, cy = (b[0] + b[2]) / 2 / w, (b[1] + b[3]) / 2 / h
            lines.append(f"{c} {cx:.6f} {cy:.6f} {(b[2] - b[0]) / w:.6f} {(b[3] - b[1]) / h:.6f}")
        (SUGGESTED / (p.stem + ".txt")).write_text("\n".join(lines) + ("\n" if lines else ""))
        if k % 25 == 0:
            print(f"  {k}/{len(imgs)} ...")
    (SUGGESTED / "classes.txt").write_text("user\nperson\n")
    print(f"\nSuggested labels for {len(imgs)} frames in {SUGGESTED}")
    print(f"({n_user} boxes suggested as 'user'). NOW A PERSON CORRECTS THEM, and saves them into {LABELS}")


# ---------------------------------------------------------------- step 3
def cmd_run(args):
    from ultralytics import YOLO
    names = ["colour", "hybrid"] + [m.replace(".pt", "") for m in MODELS + EXTRA_MODELS]
    chosen = [a.lower() for a in args if a.lower() in names]
    rest = [a for a in args if a.lower() not in names]
    labels = Path(rest[0]) if rest else LABELS
    want_hybrid = "hybrid" in chosen
    picked = [c for c in chosen if c not in ("colour", "hybrid")]
    do_colour = not chosen or "colour" in chosen
    models = [m for m in MODELS + EXTRA_MODELS
              if (m in MODELS and not picked and (not chosen or want_hybrid)) or m.replace(".pt", "") in picked]
    do_alone = not chosen or (bool(picked) and not want_hybrid)     # "run yolo11n"
    do_hybrid = not chosen or want_hybrid                            # "run hybrid yolo11n"
    suffix = ("_" + "_".join(chosen)) if chosen else ""
    what = (["colour only"] if do_colour else []) + \
           [m.replace(".pt", "") + " alone" for m in models if do_alone] + \
           ["hybrid " + m.replace(".pt", "") for m in models if do_hybrid]
    print("Checking: " + ", ".join(what))
    has_gt = labels.exists() and any(labels.glob("*.txt"))
    imgs = frames_in(FRAMES)
    if not imgs:
        sys.exit(f"No frames in {FRAMES}: run STEP 1 first")
    if not has_gt:
        print(f"No labels in {labels}: printing COUNTS only (no accuracy). Correct the labels first (STEP 2).\n")
    gts = {}
    for p in imgs:
        img = cv2.imread(str(p))
        gts[p] = read_labels(labels, p, img.shape) if has_gt else None
    missing = sum(g is None for g in gts.values()) if has_gt else 0
    if has_gt and missing:
        print(f"Note: {missing} frames have no label file and are skipped in the scores.")

    det_rows, user_rows = [], []

    def user_score(name, k, outcomes, t_ms):
        n = len(outcomes)
        with_user = [o for o in outcomes if o[0]]
        without = [o for o in outcomes if not o[0]]
        found = sum(o[1] == "right" for o in with_user)
        wrong = sum(o[1] == "wrong" for o in with_user)
        false_alarm = sum(o[1] == "alarm" for o in without)
        correct = found + sum(o[1] == "none" for o in without)
        user_rows.append([name, k, n, len(with_user),
                          f"{100 * found / max(1, len(with_user)):.1f}",
                          f"{100 * wrong / max(1, len(with_user)):.1f}",
                          f"{100 * false_alarm / max(1, len(without)):.1f}" if without else "-",
                          f"{100 * correct / max(1, n):.1f}", f"{t_ms:.0f}"])

    def judge(gt, pred_box=None, pred_point=None):
        """one frame -> (user_in_frame, 'right' | 'wrong' | 'missed' | 'alarm' | 'none')"""
        users = gt[0]
        if users:
            u = users[0]
            if pred_box is not None:
                return True, "right" if iou(pred_box, u) >= IOU_MATCH else "wrong"
            if pred_point is not None:
                x, y = pred_point
                return True, "right" if u[0] <= x <= u[2] and u[1] <= y <= u[3] else "wrong"
            return True, "missed"
        return False, "alarm" if (pred_box is not None or pred_point is not None) else "none"

    # colour only
    for k in (BRIGHTNESS if do_colour else []):
        outcomes, t, hits = [], 0.0, 0
        for p in imgs:
            img = darken(cv2.imread(str(p)), k)
            t0 = time.perf_counter()
            pt = colour_only_user(turban_mask(img))
            t += time.perf_counter() - t0
            hits += pt is not None
            if gts[p] is not None:
                outcomes.append(judge(gts[p], pred_point=pt))
        if has_gt:
            user_score("colour only", k, outcomes, 1000 * t / len(imgs))
        else:
            print(f"colour only  k={k}: a 'user' blob in {100 * hits / len(imgs):.0f}% of frames")

    # the YOLO models: person detection, and the hybrid with each of them
    for m in models:
        model = load_model(m)
        model(cv2.imread(str(imgs[0])), verbose=False)          # warm-up, not timed
        name = m.replace(".pt", "")
        for k in BRIGHTNESS:
            tp = fp = fn = 0
            big_tp = big_n = 0                                  # people taller than BIG_PERSON of the frame
            outcomes, alone, t, hits, picks = [], [], 0.0, 0, 0
            for p in imgs:
                img = darken(cv2.imread(str(p)), k)
                t0 = time.perf_counter()
                people = people_of(model, img)
                t += time.perf_counter() - t0
                user = hybrid_user(turban_mask(img), people)
                hits += bool(people)
                picks += user is not None
                g = gts[p]
                if g is not None:
                    a, b, c = match(people, g[0] + g[1])
                    tp, fp, fn = tp + a, fp + b, fn + c
                    big_gt = [q for q in g[0] + g[1] if (q[3] - q[1]) >= BIG_PERSON * img.shape[0]]
                    big_tp += match(people, big_gt)[0]
                    big_n += len(big_gt)
                    outcomes.append(judge(g, pred_box=user))
                    big = max(people, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])) if people else None
                    alone.append(judge(g, pred_box=big))
            fps = len(imgs) / t
            if has_gt:
                if do_alone:
                    det_rows.append([name, k, len(outcomes), f"{100 * tp / max(1, tp + fn):.1f}",
                                     f"{100 * tp / max(1, tp + fp):.1f}", f"{fps:.1f}", f"{1000 / fps:.0f}",
                                     f"{100 * big_tp / max(1, big_n):.1f}"])
                    user_score(f"{name} only (biggest person)", k, alone, 1000 / fps)
                if do_hybrid:
                    user_score(f"hybrid {name}", k, outcomes, 1000 / fps)
            else:
                print(f"{name:9s} k={k}: people in {100 * hits / len(imgs):.0f}% of frames, user picked in "
                      f"{100 * picks / len(imgs):.0f}%, {fps:.1f} FPS")
    if not has_gt:
        return

    ROOT.mkdir(parents=True, exist_ok=True)
    head_a = ["model", "brightness", "frames", "person detection rate %", "precision %", "FPS", "ms/frame",
              "detection rate % (people > 1/4 of the frame height)"]
    head_b = ["method", "brightness", "frames", "frames with the user", "user found %", "wrong person %",
              "false alarm % (frames without the user)", "frames correct %", "ms/frame"]
    for fname, head, rows in ((f"m05_table_A_person_detection{suffix}.csv", head_a, det_rows),
                              (f"m05_table_B_finding_the_user{suffix}.csv", head_b, user_rows)):
        if not rows:
            continue
        with open(ROOT / fname, "w", newline="") as f:
            csv.writer(f).writerows([head] + rows)
        print("\n" + fname)
        print(" | ".join(head))
        for r in rows:
            print(" | ".join(str(x) for x in r))
    print(f"\nSaved in {ROOT}.  Target in the plan: detection rate >= 90%.")
    print("Brightness 0.35 = darkened copies (a stand-in for low light, not a real dark flight).")


# ---------------------------------------------------------------- step 4
def cmd_video(args):
    from ultralytics import YOLO
    if not args:
        sys.exit("Use: python m05.py video VIDEO [MODEL] [CONF]")
    global CONF
    video = args[0]
    model_name = args[1] if len(args) > 1 else "yolo26n.pt"
    if len(args) > 2:
        CONF = float(args[2])                       # people_of() reads CONF; only this demo run changes
    model = load_model(model_name)
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        sys.exit(f"Cannot open {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    ROOT.mkdir(parents=True, exist_ok=True)
    tag = f"_conf{CONF:g}" if len(args) > 2 else ""
    out = ROOT / f"demo_{Path(video).stem}_{model_name.replace('.pt', '')}{tag}.mp4"
    writer, step, i = None, 3, 0
    last, by_colour, by_fallback, none, run = None, 0, 0, 0, 0
    max_run = max(1, round(fps / step))          # the fallback bridges at most about 1 second
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if i % step == 0:
            people = people_of(model, fr)
            user = hybrid_user(turban_mask(fr), people)
            kept = False
            if user is None and last is not None and people and run < max_run:
                # fallback: the colour was lost, so keep the person who overlaps most with last frame's user.
                # Safety: if two people overlap that position (people crossing), do NOT guess; bridge at most 1 second.
                near = [b for b in people if iou(b, last) >= 0.3]
                if len(near) == 1:
                    user, kept = [int(v) for v in near[0]], True
            run = run + 1 if kept else 0
            if user is None:
                none += 1
            elif kept:
                by_fallback += 1
            else:
                by_colour += 1
            last = user if user is not None else None
            for b in people:
                b = [int(v) for v in b]
                if user is None or iou(b, user) < 0.9:
                    cv2.rectangle(fr, b[:2], b[2:], (255, 120, 0), 2)
            if user is not None:
                col = (0, 200, 255) if kept else (0, 220, 0)
                cv2.rectangle(fr, tuple(user[:2]), tuple(user[2:]), col, 3)
                cv2.putText(fr, "USER (kept)" if kept else "USER", (user[0], max(20, user[1] - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, col, 2)
            cv2.putText(fr, f"{model_name.replace('.pt', '')} + turban colour (conf {CONF:g})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            if writer is None:
                h, w = fr.shape[:2]
                writer = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), fps / step, (w, h))
            writer.write(fr)
        i += 1
    cap.release()
    if writer:
        writer.release()
    tot = max(1, by_colour + by_fallback + none)
    print(f"Saved: {out}")
    print(f"user picked by the turban colour in {100 * by_colour / tot:.0f}% of frames, kept by the fallback in "
          f"{100 * by_fallback / tot:.0f}%, no user in {100 * none / tot:.0f}%")


if __name__ == "__main__":
    cmds = {"extract": cmd_extract, "prelabel": cmd_prelabel, "run": cmd_run, "video": cmd_video}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
