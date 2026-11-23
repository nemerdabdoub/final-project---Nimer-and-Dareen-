# Newer models and algorithms: what exists (Nov 2026) and how we choose (24.11, Dareen)

Gabi (23.11): "check for newer algorithms and models and choose the best for our project". We do not choose from
papers or blogs: their numbers come from GPUs and other datasets. **We shortlist from the literature, then measure on
our own hand-labelled clips with the same scripts** (M05: `m05_all_models.py`; M06: `m06_track.py`).

## 1. What "best for our project" means (criteria, from the approved work plan and our system)

| Criterion | Why | Pass line |
|---|---|---|
| Keeps THE user (not just "a person") | req. 1: identify the user in ≥ 90% of frames | user kept ≥ 90%, wrong person ≈ 0 |
| Survives crossings and occlusion | the earlier team's main failure (new ID after occlusion) | ID swaps ≤ 1 in 10 crossings |
| Real time on our laptop, CPU only | i7-13650HX, no GPU; req. 3 ≥ 10 FPS for the whole loop | ≥ 10 FPS detector + tracker |
| Moving camera, small/far people | drone at 5-8 m, moving | detection at following distance ≥ 90% |
| Low added delay | video already ~290 ms | ≤ ~50 ms per frame for detection + tracking |
| Can install and explain it | course rule: explain AI-made and borrowed parts | pip-installable, licence OK, we understand it |

## 2. The system in layers, and the newest candidates per layer

| Layer | Now | Newer candidates (literature, 2025-26) | Cost to test | Verdict |
|---|---|---|---|---|
| **Detector** | YOLO11n | **YOLO26n** (Jan 2026, NMS-free; ~39 ms CPU ONNX reported) | done (M05 + M06 grid) | no gain on our data (82.5% vs 85.4%; 81% vs 82-84% kept) |
| | | **RF-DETR-Nano** (Roboflow, Apache-2.0; leads on GPU; no official CPU numbers, DINOv2 backbone is heavy on CPU) | `pip install rfdetr` + small adapter in the M05 harness | **test next** (accuracy on our labels + CPU FPS) |
| | | D-FINE, DEIM (DETR family, GPU numbers only) | separate repos | only if RF-DETR shows DETRs win on our data |
| **Multi-object tracker** | ByteTrack (BoT-SORT leads, 23.11) | **TrackTrack** (CVPR 2025, top HOTA on MOT17), **OC-SORT**, **Deep OC-SORT**, **FastTrack**: all already inside Ultralytics 8.4.216 | zero install, one flag | **running now** on 2 clips |
| **Identity / re-ID** | turban colour on the head | BoT-SORT / Deep OC-SORT with **YOLO26 ReID** models (appearance features); NSA-Kalman (confidence-adaptive) is already in the trackers | config flag | test after the tracker grid |
| **Lock onto one person** (single-object tracking) | none | SGLATrack (2025, ~75 FPS CPU reported), SSTrack (IJCAI 2025, CPU real time), CFTrack | research code, integration days | semester B, only if multi-object tracking cannot reach 90% |
| **Moving-camera motion** | BoT-SORT camera-motion compensation | EMTS-Det (2026, ego-motion-normalised "follow-me" on a Raspberry Pi) | research | idea for the controller/report, not a swap |

Not chosen and why: SAM-2/SAMURAI-style trackers (too slow on CPU), big DETRs and YOLO s/m/l (M05: +2-4 points at 2-6× slower).

## 3. Plan (each step one command, results in `M05_data/results/`)

1. **All 6 Ultralytics trackers × YOLO11n on 161951 + 161825** (running 24.11) → keep the best 2.
2. Best 2 trackers on both 22.11 Med-Faculty clips (never tuned on) + count tracker swaps by eye.
3. RF-DETR-Nano vs YOLO11n on the 403 hand-labelled frames: detection, wrong person, FPS (install in a separate
   virtual environment so the working setup is not touched).
4. Best tracker + ReID on/off.
5. Crossing scenes (film + label) → ID swaps per 10 crossings = the deciding M06 test.

**Stand-out angle:** neither earlier team compared trackers; we compare 6 (incl. a CVPR 2025 tracker) and a 2026
detector on our own labelled drone footage, and report what was rejected and why.

## Sources (literature shortlist)
- YOLO26 analysis: https://arxiv.org/pdf/2601.12882 · YOLO26 vs YOLOv8 benchmark: https://arxiv.org/pdf/2605.24831
- RF-DETR vs alternatives (Roboflow): https://roboflow.com/blog/rf-detr-vs-alternatives · JetBrains overview 2026: https://blog.jetbrains.com/pycharm/2026/07/best-object-detection-models-for-machine-learning-in-2026/
- D-FINE: https://arxiv.org/pdf/2410.13842
- TrackTrack (CVPR 2025): https://openaccess.thecvf.com/content/CVPR2025/papers/Shim_Focusing_on_Tracks_for_Online_Multi-Object_Tracking_CVPR_2025_paper.pdf
- Tracker guide 2026 (secondary, numbers inconsistent): https://www.forasoft.com/learn/ai-for-video-engineering/articles-ai/multi-object-tracking-deepsort-bytetrack-ocsort
- EMTS-Det (follow-me on milliwatt hardware): https://arxiv.org/pdf/2607.16282
- SGLATrack: https://arxiv.org/html/2503.06625v1 · SSTrack: https://www.ijcai.org/proceedings/2025/147 · CFTrack: https://arxiv.org/html/2502.19705v1
- Drone follow-me code with occlusion re-ID: https://github.com/1destroyer100yt/drone-tracker
