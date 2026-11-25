"""
m05_body_cues.py - Project 3760: Nimer's idea - do classic body cues (colour shades, body shape/edges) separate the user
from other people, alone and together with the turban? CPU-cheap, no neural network.

Same 403 hand-labelled frames as the final M05 table; YOLO11n gives the person boxes.
Per clip, a live-style ENROLMENT: the first 5 frames where one box has turban score >= 0.8 -> that box's body is the
user's template (like the drone would do at take-off: "this is me"). Then every box in the clip gets:
  turban   user_score.py (turban on the head)
  colour   body colour shades: HSV histogram (hue x saturation) of the body (below the head), similarity to the template
  shape    body edges/outline: HOG descriptor of the body resized to 64x128, cosine similarity to the template
  turban+colour, turban+colour+shape   simple averages
For each: ROC AUC (user vs other people), median user / other, and CPU time per box.
Writes M05_data/results/body_cues_25.11/summary.md
"""
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

import m05
from m05 import turban_mask, iou
from m05_userpick_allvideos import framesets, user_box, load_detector
from m05_user_score_hist import auc
from user_score import user_score

OUT = Path(__file__).resolve().parent.parent / "M05_data" / "results" / "body_cues_25.11"
ENROL_N, ENROL_MIN = 5, 0.8


def body(img, b):
    x1, y1, x2, y2 = [int(v) for v in b]
    yb = y1 + int((y2 - y1) * m05.HEAD_PART)
    c = img[max(0, yb):max(yb + 1, y2), max(0, x1):max(x1 + 1, x2)]
    return c if c.size else None


def colour_feat(c):
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv], [0, 1], None, [18, 8], [0, 180, 0, 256])
    return cv2.normalize(h, h).flatten()


def shape_feat(c):
    """HOG-style edge descriptor: body resized to 64x128, gradient directions in 8x8 cells, 9 bins each (512 cells... 1152 numbers)"""
    g = cv2.cvtColor(cv2.resize(c, (64, 128)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag, ang = np.hypot(gx, gy), (np.degrees(np.arctan2(gy, gx)) % 180)
    b = np.minimum((ang / 20).astype(int), 8)
    f = np.zeros((16, 8, 9), np.float32)
    for i in range(16):
        for j in range(8):
            f[i, j] = np.bincount(b[8 * i:8 * i + 8, 8 * j:8 * j + 8].ravel(),
                                  weights=mag[8 * i:8 * i + 8, 8 * j:8 * j + 8].ravel(), minlength=9)
    f = f.flatten()
    return f / (np.linalg.norm(f) + 1e-6)


def main():
    model = load_detector("yolo11n.pt")
    clips = defaultdict(list)                     # clip -> [(img, user box)] in time order
    for s, items in framesets().items():
        for it in items:
            clips[Path(it[0]).name.split("_")[0]].append(it)
    rows = []                                     # (is_user, turban, colour, shape, clip, frame)
    t_col = t_shape = n_box = 0
    for clip, items in clips.items():
        items = sorted(items, key=lambda it: Path(it[0]).name)
        data = []
        for it in items:
            img = cv2.imread(str(it[0]))
            people = m05.people_of(model, img)
            mask = turban_mask(img)
            data.append((it, img, user_box(it, img), people, [user_score(mask, b) for b in people]))
        enrol_c, enrol_s = [], []
        for it, img, u, people, ts in data:       # enrolment from the first confident turban frames
            if ts and max(ts) >= ENROL_MIN and len(enrol_c) < ENROL_N:
                c = body(img, people[int(np.argmax(ts))])
                if c is not None:
                    enrol_c.append(colour_feat(c))
                    enrol_s.append(shape_feat(c))
        if not enrol_c:
            print(f"clip {clip}: no confident turban frame -> skipped ({len(items)} frames)")
            continue
        tc, tsh = np.mean(enrol_c, 0).astype(np.float32), np.mean(enrol_s, 0)
        tsh /= np.linalg.norm(tsh) + 1e-6
        for it, img, u, people, ts in data:
            for b, t in zip(people, ts):
                c = body(img, b)
                if c is None:
                    continue
                t0 = time.perf_counter()
                col = 1.0 - cv2.compareHist(tc, colour_feat(c), cv2.HISTCMP_BHATTACHARYYA)
                t1 = time.perf_counter()
                shp = float(np.dot(tsh, shape_feat(c)))
                t2 = time.perf_counter()
                t_col += t1 - t0
                t_shape += t2 - t1
                n_box += 1
                is_user = u is not None and iou(b, u) >= m05.IOU_MATCH
                rows.append((is_user, t, col, shp, clip, Path(it[0]).name))
    R = np.array([[r[0], r[1], r[2], r[3]] for r in rows], dtype=float)
    U, O = R[R[:, 0] == 1], R[R[:, 0] == 0]
    cues = {"turban (today)": 1, "body colour shades": 2, "body shape / edges (HOG)": 3}
    comb = {"turban + colour": lambda A: (A[:, 1] + A[:, 2]) / 2,
            "turban + colour + shape": lambda A: (A[:, 1] + A[:, 2] + A[:, 3]) / 3}
    lines = [f"# Classic body cues vs the turban (YOLO11n boxes, {len(R)} boxes: {len(U)} user / {len(O)} other, "
             f"clips with an enrolment: {len(set(r[4] for r in rows))})", "",
             "| cue | ROC AUC | median user | median other | CPU ms / box |", "|---|---|---|---|---|"]
    ms = {"turban (today)": "<1", "body colour shades": f"{1000 * t_col / n_box:.2f}",
          "body shape / edges (HOG)": f"{1000 * t_shape / n_box:.2f}"}
    for name, k in cues.items():
        lines.append(f"| {name} | {auc(U[:, k], O[:, k]):.3f} | {np.median(U[:, k]):.2f} | {np.median(O[:, k]):.2f} | {ms[name]} |")
    for name, f in comb.items():
        fu, fo = f(U), f(O)
        lines.append(f"| {name} | {auc(fu, fo):.3f} | {np.median(fu):.2f} | {np.median(fo):.2f} | sum |")
    red = [r for r in rows if not r[0] and r[1] >= 0.9]
    lines += ["", "Other people with turban score >= 0.9 (the red-shirt problem) - what the body cues say:",
              "| frame | turban | colour | shape | turban+colour |", "|---|---|---|---|---|"]
    lines += [f"| {r[5]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f} | {(r[1] + r[2]) / 2:.2f} |" for r in red]
    um = np.median(U[:, 2])
    lines += ["", f"For comparison, the user's median colour similarity = {um:.2f}.",
              "Enrolment = first 5 frames per clip with a turban score >= 0.8 (live-style). Not tuned on these frames."]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
