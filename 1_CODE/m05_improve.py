"""m05_improve.py - can we reach the 90% detection target? Tries bigger models, bigger input and tiling
on the same 152 corrected frames (Table A rules: a box is correct if IoU >= 0.5).
Run from 1_CODE:  python m05_improve.py      (downloads yolo11s.pt ~19 MB and yolo11m.pt ~39 MB once)
Prints only, saves nothing.  Note: yolo11l made the SUGGESTED labels, so its score is biased upwards."""
import sys, time
sys.argv = ["m05"]
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import cv2, numpy as np
import m05
from ultralytics import YOLO

E = m05.ROOT
data = []
for p in m05.frames_in(E / "frames"):
    img = cv2.imread(str(p))
    gt = m05.read_labels(E / "labels", p, img.shape)
    if gt is not None:
        data.append((img, gt[0] + gt[1]))
H = data[0][0].shape[0]


def detect(model, img, sz, conf, tiles):
    boxes, scores = [], []
    views = [(0, img)]
    if tiles:                                   # two overlapping halves, each enlarged by YOLO -> small people get bigger
        w = img.shape[1]
        views += [(0, img[:, : int(0.6 * w)]), (int(0.4 * w), img[:, int(0.4 * w):])]
    for dx, v in views:
        r = model(v, classes=[0], conf=conf, imgsz=sz, verbose=False)[0]
        for b, s in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy()):
            boxes.append([b[0] + dx, b[1], b[2] + dx, b[3]]); scores.append(float(s))
    if not boxes:
        return []
    keep = cv2.dnn.NMSBoxes([[b[0], b[1], b[2] - b[0], b[3] - b[1]] for b in boxes], scores, conf, 0.5)
    return [boxes[i] for i in np.array(keep).flatten()]


def score(preds_per_frame, min_h=0.0):
    tp = fn = fp = 0
    for (img, gts), preds in zip(data, preds_per_frame):
        gts = [g for g in gts if (g[3] - g[1]) / H >= min_h]
        if min_h:   # only judge boxes of the same size class
            preds = [q for q in preds if (q[3] - q[1]) / H >= min_h * 0.8]
        used = set()
        for g in gts:
            j = max(range(len(preds)), key=lambda k: m05.iou(g, preds[k]), default=None)
            if j is not None and j not in used and m05.iou(g, preds[j]) >= 0.5:
                tp += 1; used.add(j)
            else:
                fn += 1
        fp += len(preds) - len(used)
    return 100 * tp / max(1, tp + fn), 100 * tp / max(1, tp + fp)


tests = [("yolo11n.pt", 640, 0.25, False), ("yolo11n.pt", 1280, 0.25, False), ("yolo11n.pt", 640, 0.25, True),
         ("yolo11s.pt", 640, 0.25, False), ("yolo11s.pt", 1280, 0.25, False), ("yolo11s.pt", 640, 0.25, True),
         ("yolo11m.pt", 640, 0.25, False), ("yolo11m.pt", 1280, 0.25, False), ("yolo11l.pt", 640, 0.25, False)]
print(f"{len(data)} frames.  detection / precision on all people | detection on people > 1/4 of the height | speed")
for name, sz, conf, tiles in tests:
    model = YOLO(name)
    model(data[0][0], verbose=False)                      # warm-up
    t = time.time()
    preds = [detect(model, img, sz, conf, tiles) for img, _ in data]
    ms = 1000 * (time.time() - t) / len(data)
    d, pr = score(preds)
    d4, _ = score(preds, 0.25)
    label = f"{name[:-3]} {sz}px{' + tiles' if tiles else ''}"
    print(f"{label:24s} detection {d:5.1f}%  precision {pr:5.1f}%  | big people {d4:5.1f}%  | {ms:5.0f} ms = {1000/ms:4.1f} FPS")
