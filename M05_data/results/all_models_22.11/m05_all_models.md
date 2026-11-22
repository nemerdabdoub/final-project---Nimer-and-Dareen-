# M05 — every detector, measured the same way (22.11, Dareen's laptop, i7-13650HX, CPU only)

Script: `1_CODE/m05_all_models.py` · CSV: `m05_all_models.csv`. Finding people on all 152 test frames; finding THE
user (hybrid = detector + turban colour) on the 132 turban frames; speed = the whole hybrid per frame, one run.
**Bold = best in that column.** ⭐ = recommended final choice.

| Model (+ turban colour) | Detection, all people | Detection, following distance (> ¼ height) | Detection, dark (×0.35) | Precision | User found | Wrong person | False alarm | Frames correct | FPS | Portrait seen as person |
|---|---|---|---|---|---|---|---|---|---|---|
| ⭐ **YOLO11n (original)** | 85.4% | 96.2% | 84.8% | 94.1% | 73.1% | **0%** | **0%** | 78.8% | 23.8 | 4/4 |
| YOLOv12n | 82.9% | 93.3% | 81.9% | 94.2% | 73.1% | **0%** | **0%** | 78.8% | 21.6 | 4/4 |
| YOLO26n | 82.5% | 92.5% | 82.9% | **95.2%** | 74.0% | **0%** | **0%** | 79.5% | 24.4 | 4/4 |
| YOLO11n fine-tuned (1st) | 77.1% | 85.4% | 69.5% | 92.4% | 66.3% | 1.9% | 10.7% | 71.2% | 26.7 | **0/4** |
| YOLO11n fine-tuned (gentle) | 84.4% | 95.0% | 83.5% | 93.7% | 70.2% | 1.9% | **0%** | 76.5% | **27.4** | **0/4** |
| YOLO11s | 84.8% | 94.6% | 84.1% | 93.0% | 75.0% | 1.0% | **0%** | 80.3% | 14.0 | 4/4 |
| YOLO11m | 88.3% | **97.1%** | 85.7% | 94.6% | **76.0%** | **0%** | **0%** | **81.1%** | 6.5 | 4/4 |
| YOLO11s at 1280 px | **91.7%** | 93.7% | **91.4%** | 89.8% | 75.0% | **0%** | 3.6% | 79.5% | 5.0 | 4/4 |

Speeds of the four nano models (21.6-27.4 FPS) are within normal run-to-run variation of each other; the real split is
nano ~22-27 FPS vs YOLO11s 14, YOLO11m 6.5, YOLO11s-1280 5.

## Requirements (work plan + what the drone needs)
1. Detection ≥ 90% (work plan). Met on **all people** only by YOLO11s at 1280 px; met at **following distance** by
   every model except the first fine-tune.
2. Fast enough for live control on the laptop (we use ≥ 15 FPS): only the four nano models.
3. Never follows the wrong person and no false alarms: YOLO11n, YOLOv12n, YOLO26n, YOLO11m.

**Meets all three: YOLO11n, YOLOv12n, YOLO26n. Best of those: YOLO11n** — highest detection (85.4% all, 96.2% at following
distance, 84.8% in the dark) at nano speed, 0% wrong person, 0% false alarms.

- YOLO11m is the best on quality (97.1% at following distance, 76% user found, 81.1% frames correct) but runs at 6.5 FPS.
- YOLO11s at 1280 px is the only one ≥ 90% on all people (also in the dark), but 5 FPS, lowest precision, 3.6% false alarms.
- The fine-tuned models are the only ones that do not see the portrait; the gentle one keeps nano speed and ~1 point less
  detection, but picks the wrong person in 2 of 104 frames. Promising with more training data.
