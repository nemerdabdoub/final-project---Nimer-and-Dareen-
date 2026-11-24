"""m05_speed_gpu.py - Project 3760: clean SPEED test of every detector inside the hybrid, on THIS laptop.

Why a separate test: the accuracy tables time one pass over 403 frames; if the laptop is busy (browser, Windows) for a
moment, those ms/frame are wrong (24.11: colour-only went 6.9 -> 33 ms in one run). Here every detector is timed
REPEATEDLY on the same 100 frames and the MEDIAN is reported, plus colour-only as a check that the CPU was not busy.

Run (from 1_CODE, charger in, nothing else running):
  C:\\Users\\LOREN\\venvs\\gpu\\Scripts\\python.exe m05_speed_gpu.py        GPU (the drone laptop's RTX 5050)
  python m05_speed_gpu.py                                                  CPU only (normal Python), for comparison
Output: M05_data/results/speed_<gpu|cpu>_24.11.csv  (median and 90th-percentile ms per frame, detector alone and hybrid)
"""
import csv
import statistics
import sys
import time
from pathlib import Path

import cv2
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m05
from m05_userpick_allvideos import load_detector

HERE = Path(__file__).resolve().parent
FRAMES = sorted((HERE.parent / "3_EVIDENCE" / "m05_user_detection" / "frames").glob("*.jpg"))[:100]
DETS = ["yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo26n.pt", "yolo26s.pt", "yolo26m.pt"]
GPU = torch.cuda.is_available()
if GPU:
    DETS += ["rtdetr-l.pt", "rfdetr-nano", "rfdetr-small", "rfdetr-medium"]   # transformers: GPU only
REPEATS = 3
HW = f"GPU {torch.cuda.get_device_name(0)}" if GPU else "CPU only"


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def main():
    imgs = [cv2.imread(str(p)) for p in FRAMES]
    print("hardware:", HW, "| frames:", len(imgs), "| repeats:", REPEATS)
    if GPU:
        # 24.11: the laptop GPU starts in a power-saving state and needs ~10-20 s of load to reach full clocks;
        # without this the first models in the list were timed "cold" (YOLO11n ~100 ms instead of ~15 ms).
        warm = load_detector("yolo11n.pt")
        t_end = time.time() + 20
        while time.time() < t_end:
            for im in imgs:
                m05.people_of(warm, im)
        del warm
        print("GPU warmed up for 20 s")
    rows = []
    t_col = []
    for _ in range(REPEATS):
        for im in imgs:
            t0 = time.perf_counter(); m05.colour_only_user(m05.turban_mask(im)); t_col.append(1000 * (time.perf_counter() - t0))
    rows.append({"method": "colour only (CPU check)", "hardware": "CPU", "detector median ms": "", "hybrid median ms": round(statistics.median(t_col), 1),
                 "hybrid p90 ms": round(pct(t_col, 0.9), 1), "hybrid FPS": round(1000 / statistics.median(t_col), 1)})
    print(rows[-1])
    for det in DETS:
        model = load_detector(det)
        for im in imgs[:10]:
            m05.people_of(model, im)                                  # warm-up
        t_det, t_hyb = [], []
        for _ in range(REPEATS):
            for im in imgs:
                if GPU:
                    torch.cuda.synchronize()
                t0 = time.perf_counter()
                people = m05.people_of(model, im)
                t1 = time.perf_counter()
                m05.hybrid_user(m05.turban_mask(im), people)
                t2 = time.perf_counter()
                t_det.append(1000 * (t1 - t0)); t_hyb.append(1000 * (t2 - t0))
        med = statistics.median(t_hyb)
        rows.append({"method": det.replace(".pt", ""), "hardware": HW, "detector median ms": round(statistics.median(t_det), 1),
                     "hybrid median ms": round(med, 1), "hybrid p90 ms": round(pct(t_hyb, 0.9), 1), "hybrid FPS": round(1000 / med, 1)})
        print(rows[-1], flush=True)
        del model
        if GPU:
            torch.cuda.empty_cache()
    out = HERE.parent / "M05_data" / "results" / f"speed_{'gpu' if GPU else 'cpu'}_24.11.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("saved", out)


if __name__ == "__main__":
    main()
