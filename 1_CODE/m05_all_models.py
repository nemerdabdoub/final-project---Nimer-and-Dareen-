"""m05_all_models.py - every detector we tried, measured the SAME way on ONE laptop, YOLO + turban colour (hybrid).
Run from 1_CODE (nothing else running, charger in):  python m05_all_models.py
Needs the 152 corrected test frames/labels in 3_EVIDENCE/m05_user_detection. Saves m05_all_models.csv there.
Finding people: all 152 frames. Finding THE user: the 132 turban frames. Speed = the whole hybrid per frame.
Portrait = the framed painting at the end of clip 154848 (56.5 / 57.5 / 58.5 / 59.5 s): boxed as a person or not."""
import csv, os, sys, time
sys.argv = ["m05"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import m05
from ultralytics import YOLO

E = m05.ROOT
frames = [p for p in m05.frames_in(E / "frames")]
imgs = {p: cv2.imread(str(p)) for p in frames}
gts = {p: m05.read_labels(E / "labels", p, imgs[p].shape) for p in frames}
frames = [p for p in frames if gts[p] is not None]
marker = [p for p in frames if not p.name.startswith("154124")]
H = imgs[frames[0]].shape[0]
cap = cv2.VideoCapture(str(m05.ROOT.parent / "2026-11-20" / "154848_connection_test_video.mp4"))
fps_v = cap.get(cv2.CAP_PROP_FPS)
portrait = []
for t in (56.5, 57.5, 58.5, 59.5):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps_v)); portrait.append(cap.read()[1])

TESTS = [("YOLO11n (original)", "yolo11n.pt", 640), ("YOLOv12n", "yolo12n.pt", 640), ("YOLO26n", "yolo26n.pt", 640),
         ("YOLO11n fine-tuned (1st)", "yolo11n_drone.pt", 640), ("YOLO11n fine-tuned (gentle)", "yolo11n_drone_gentle.pt", 640),
         ("YOLO11s", "yolo11s.pt", 640), ("YOLO11m", "yolo11m.pt", 640), ("YOLO11s at 1280 px", "yolo11s.pt", 1280),
         ("YOLO26s", "yolo26s.pt", 640), ("YOLO26m", "yolo26m.pt", 640)]   # 26s/26m added 24.11 (downloaded on first use)

# Which hardware runs the model: Ultralytics uses the NVIDIA GPU automatically when PyTorch has CUDA
# (Dareen's GPU environment C:\Users\LOREN\venvs\gpu, RTX 5050); the normal Python is CPU-only.
# The hardware is written in every row and in the file name, so CPU and GPU numbers are never mixed.
import torch
DEVICE = f"GPU {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU only"
OUT_NAME = "m05_all_models_gpu.csv" if torch.cuda.is_available() else "m05_all_models.csv"
print("running on:", DEVICE)
rows = []
for label, w, sz in TESTS:
    model = YOLO(w)
    det = lambda im, k=1.0: model(m05.darken(im, k) if k != 1.0 else im, classes=[0], conf=m05.CONF, imgsz=sz,
                                  verbose=False)[0].boxes.xyxy.cpu().numpy().tolist()
    det(imgs[frames[0]])                                                     # warm-up
    r = {"method": label, "hardware": DEVICE}
    for k in (1.0, 0.35):
        tp = fp = fn = btp = bn = 0
        found = wrong = alarm = nonepick = nu = nw = 0
        t = 0.0
        for p in frames:
            im = imgs[p] if k == 1.0 else m05.darken(imgs[p], k)
            t0 = time.perf_counter()
            people = det(im)
            user = m05.hybrid_user(m05.turban_mask(im), people)
            t += time.perf_counter() - t0
            g = gts[p][0] + gts[p][1]
            a, b, c = m05.match(people, g); tp, fp, fn = tp + a, fp + b, fn + c
            big = [q for q in g if q[3] - q[1] >= m05.BIG_PERSON * H]
            btp += m05.match(people, big)[0]; bn += len(big)
            if p in marker:
                u = gts[p][0]
                if u:
                    nu += 1
                    if user is not None:
                        found += m05.iou(user, u[0]) >= m05.IOU_MATCH; wrong += m05.iou(user, u[0]) < m05.IOU_MATCH
                else:
                    nw += 1; alarm += user is not None
        if k == 1.0:
            r.update({"detection all %": 100 * tp / (tp + fn), "detection following distance %": 100 * btp / bn,
                      "precision %": 100 * tp / (tp + fp), "user found %": 100 * found / nu,
                      "wrong person %": 100 * wrong / nu, "false alarm %": 100 * alarm / nw,
                      "frames correct %": 100 * (found + nw - alarm) / (nu + nw), "FPS (hybrid)": len(frames) / t})
        else:
            r["detection all % (dark 0.35)"] = 100 * tp / (tp + fn)
    hits = sum(any(b[0] < 330 and b[1] < 260 and b[3] < 380 for b in det(f)) for f in portrait)
    r["portrait seen as person"] = f"{hits}/4"
    rows.append(r); print(label, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items() if k != "method"})

cols = list(rows[0].keys())
with open(E / OUT_NAME, "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in rows:
        w.writerow([f"{r[c]:.1f}" if isinstance(r[c], float) else r[c] for c in cols])
print("saved", E / OUT_NAME)
