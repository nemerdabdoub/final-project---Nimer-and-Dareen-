"""m05_diagnose.py - why do the M05 numbers fall short? (run from 1_CODE: python m05_diagnose.py)
Needs 3_EVIDENCE/m05_user_detection/frames and labels (all 152). Prints only, saves nothing."""
import sys, collections
sys.argv = ["m05"]
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import cv2, numpy as np
import m05
from ultralytics import YOLO

E = m05.ROOT
imgs = m05.frames_in(E / "frames")
data = []
for p in imgs:
    img = cv2.imread(str(p))
    gt = m05.read_labels(E / "labels", p, img.shape)
    if gt is not None:
        data.append((p, img, gt))
H, W = data[0][1].shape[:2]
print(f"{len(data)} labelled frames, {W}x{H}")

def best_iou(box, preds):
    return max((m05.iou(box, q) for q in preds), default=0.0)

# ---- A: detection rate, misses by size, and two settings to try
model = YOLO("yolo11n.pt")
for conf, sz in [(0.25, 640), (0.15, 640), (0.25, 960), (0.15, 960)]:
    tp = fn = fp = 0
    miss = collections.Counter(); tot = collections.Counter()
    for p, img, (u, o) in data:
        r = model(img, classes=[0], conf=conf, imgsz=sz, verbose=False)[0]
        preds = r.boxes.xyxy.cpu().numpy().tolist()
        gts = u + o
        used = set()
        for g in gts:
            h = (g[3] - g[1]) / H
            size = "small (<25% of height)" if h < 0.25 else "medium (25-50%)" if h < 0.5 else "large (>50%)"
            edge = g[0] < 3 or g[2] > W - 3
            key = size + (" cut by edge" if edge else "")
            tot[key] += 1
            j = max(range(len(preds)), key=lambda k: m05.iou(g, preds[k]), default=None)
            if j is not None and j not in used and m05.iou(g, preds[j]) >= 0.5:
                tp += 1; used.add(j)
            else:
                fn += 1; miss[key] += 1
        fp += len(preds) - len(used)
    print(f"\nyolo11n conf={conf} imgsz={sz}: detection {100*tp/(tp+fn):.1f}%  precision {100*tp/max(1,tp+fp):.1f}%")
    if (conf, sz) == (0.25, 640):
        for k in sorted(tot):
            print(f"   {k:32s} {tot[k]:3d} people, missed {miss[k]:3d} ({100*miss[k]/tot[k]:.0f}%)")

# ---- B: why the hybrid misses the actor (turban frames only)
reasons = collections.Counter(); fracs = []
for p, img, (u, o) in data:
    if p.name.startswith("154124") or not u:
        continue
    preds = m05.people_of(model, img)
    mask = m05.turban_mask(img)
    pick = m05.hybrid_user(mask, preds)
    if pick is not None and m05.iou(pick, u[0]) >= 0.5:
        reasons["found"] += 1; continue
    if best_iou(u[0], preds) < 0.5:
        reasons["YOLO did not box the actor"] += 1; continue
    x1, y1, x2, y2 = map(int, u[0])
    head = mask[max(0, y1):y1 + max(1, int((y2 - y1) * m05.HEAD_PART)), max(0, x1):x2]
    f = float((head > 0).mean()) if head.size else 0
    fracs.append(f)
    reasons["boxed, but turban colour too weak on the head" if f < m05.MIN_HEAD_FRACTION
            else "boxed, colour there but failed the background-contrast test"] += 1
print("\nHybrid (yolo11n) on the 104 frames with the actor wearing the turban:")
for k, v in reasons.most_common():
    print(f"   {k:55s} {v}")
if fracs:
    print("   turban share on the head in the colour misses:", " ".join(f"{100*f:.1f}%" for f in sorted(fracs)))
