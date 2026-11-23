# M05 re-selection on the drone laptop's GPU: 12 detectors, 3 families (24.11, Dareen)

**Why:** until 23.11 every speed was measured on the CPU (PyTorch was the CPU-only build). The drone runs from Dareen's
laptop, which has an **NVIDIA RTX 5050 Laptop GPU (8 GB)**. Bigger models had been rejected only for CPU speed
(YOLO11m 6.2 FPS). Gabi also asked us to check newer models. So we re-ran the choice on the GPU and added non-YOLO detectors.

Setup: separate GPU environment `C:\Users\LOREN\venvs\gpu` (torch 2.14.1+cu130, ultralytics 8.4.218, rfdetr), so the
working CPU setup is untouched. Scripts: `1_CODE/m05_userpick_allvideos.py` (accuracy, adapter for RT-DETR / RF-DETR),
`1_CODE/m05_all_models.py` (152 M05 frames), `1_CODE/m05_speed_gpu.py` (speed, repeated, median).

## 1. Accuracy does not depend on CPU vs GPU
Same model + same frames gave **identical** accuracy numbers on GPU and CPU (152-frame table, every column). Only speed changes.

## 2. Picking THE user: 12 detectors in the hybrid, all 403 hand-labelled frames (164 with the user, 239 without)
`M05_data/results/userpick_allvideos_gpu_24.11/table.md`

| Hybrid with | Family | User found | Wrong person | False alarms | Frames correct |
|---|---|---|---|---|---|
| YOLO11n (choice until 23.11) | YOLO | 70.1% (115) | 1.8% (3) | 0/239 | 87.8% |
| YOLOv12n | YOLO | 70.1% | 1.8% (3) | 0 | 87.8% |
| YOLO26n | YOLO | 70.7% | 2.4% (4) | 2 | 87.6% |
| YOLO11s | YOLO | 73.8% | 1.8% (3) | 2 | 88.8% |
| **YOLO11m** | YOLO | **74.4% (122)** | **0.6% (1)** | **0** | **89.6%** |
| YOLO26s | YOLO | 73.8% | 0.6% (1) | 1 | 89.1% |
| YOLO26m | YOLO | **74.4%** | 1.2% (2) | 2 | 89.1% |
| RT-DETR-L | transformer (Baidu) | 73.2% | 1.8% (3) | 1 | 88.8% |
| RF-DETR-Nano | transformer (Roboflow) | 67.1% | 7.3% (12) | 1 | 86.4% |
| RF-DETR-Small | transformer | 73.8% | 1.2% (2) | 4 | 88.3% |
| RF-DETR-Medium | transformer | 72.6% | 1.8% (3) | 1 | 88.6% |
| (fine-tuned YOLO11n, gentle) | YOLO | 65.9% | 3.7% (6) | 1 | 85.9% |

Colour only / any detector alone: wrong person 24-28%, false alarms 25-37% → the **hybrid** stays (unchanged conclusion).

## 3. Finding all people (604 labelled people, Table A rules)

| Detector | All people | Following distance (> 1/4 height) | Precision |
|---|---|---|---|
| YOLO11n | 59.4% | 96.2% | 94.7% |
| YOLO11m | 68.2% | 97.3% | **96.9%** |
| YOLO26s | 68.2% | 96.9% | 94.5% |
| YOLO26m | 74.2% | 97.3% | 94.3% |
| RT-DETR-L | 79.0% | 96.6% | 62.2% |
| RF-DETR-Small | 77.8% | **98.9%** | 66.4% |
| RF-DETR-Medium | **80.3%** | 98.5% | 63.8% |

The transformers find more people (small, far) but at the same confidence cut-off (0.25) about a third of their boxes are
not people (precision 62-66%), which is why they do not pick the user better. A fair DETR test needs its own cut-off,
chosen on the M05 frames and tested on the new clips (never tuned on) → follow-up, relevant for obstacles/crowds later.

## 4. Speed on the RTX 5050

- First GPU run (laptop in use, 152 frames, one pass): hybrid YOLO11n 54 FPS, YOLO11s 53, YOLO26n 53, YOLO26s 52,
  YOLO11m 45, YOLO26m 44 FPS (`3_EVIDENCE/m05_user_detection/m05_all_models_gpu.csv`, laptop only).
- Repeated test (`M05_data/results/speed_gpu_24.11.csv`, 100 frames × 3, median): run at ~00:30 with the laptop idle;
  **Windows had throttled it** (the CPU-only colour step took 22 ms instead of 7), so the absolute numbers are too slow.
  Same conditions for all, so the **relative** cost holds: YOLO11m +18 ms vs YOLO11n; RF-DETR +44-65 ms; RT-DETR-L +79 ms.
- On the GPU the model size costs little: most of the time is CPU work around the model (resize, colour mask).
- **To do:** one confirmation run with Dareen at the laptop ("Best performance" power mode), and the end-to-end loop
  with the tracker: `m06_track.py --model yolo11m.pt --tracker botsort`.

## 5. Decision (proposal by Dareen, Nimer to confirm)

**Switch the hybrid from YOLO11n to YOLO11m** (same turban rule, same thresholds).
- Most accurate at picking the user on all videos: 89.6% frames correct, 1 wrong-person frame of 164, 0 false alarms.
- Fast enough on the drone laptop's GPU (~45 FPS hybrid in normal conditions; target ≥ 10 FPS for the whole loop).
- Backup: YOLO26m (same user found, finds more far people, 2 wrong / 2 false alarms).
- Price: needs the GPU. On CPU only YOLO11n stays the fallback (29.9 FPS).
- Honest limit: YOLO11m vs YOLO26m vs YOLO26s differ by 1-2 frames of 164 → within noise; YOLO11m wins on cleanliness
  (fewest wrong person, 0 false alarms, highest precision), not by a big margin.
- What we tried and rejected, with numbers: RT-DETR-L and RF-DETR (no better at picking the user, 1.5-2× slower);
  YOLO26n (Gabi's suggestion: no gain over YOLO11n); fine-tuning (forgets classes); lower cut-offs (golf carts).

**What to tell Gabi:** "We found our laptop has a GPU that our software was not using. On it we re-tested 12 detectors
from 3 families, including the newest (YOLO26, RF-DETR, RT-DETR), on our 403 hand-labelled frames. The best for picking
our user is YOLO11m in the hybrid: 89.6% of frames correct, 1 wrong frame, no false alarms, fast enough on the GPU."
