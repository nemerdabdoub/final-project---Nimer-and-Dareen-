# M06: which detector + tracker keeps the user? First look (23.11, Dareen's laptop)

**Why:** in the meeting on 23.11 Gabi suggested YOLO26n "because it has an adaptive / advanced Kalman built in".
We said we would check it in tracking. This is the first check.

## 1. Fact check: where the Kalman filter is

In the installed Ultralytics (8.4.216) the Kalman filter is **in the tracker, not in the detector**
(`ultralytics/trackers/utils/kalman_filter.py`). It is used by every tracker (ByteTrack, BoT-SORT, OC-SORT,
Deep OC-SORT, FastTrack, TrackTrack) with **any** detector. The "adaptive" part exists: **NSA-Kalman** (from StrongSORT)
scales the measurement noise by the detection confidence, so a weak detection moves the track less.
What is tied to YOLO26: ReID models `yolo26{n,s,m,l,x}-reid.onnx` for BoT-SORT's appearance matching. With YOLO26 as the
detector, BoT-SORT cannot reuse the detector's own features for ReID (end-to-end head) and falls back to a separate
classifier on each crop (extra time). Detection alone was already measured in M05: YOLO26n 82.5% / 92.5% at
following distance vs YOLO11n 85.4% / 96.2%, same speed, both 0% wrong person.

## 2. The test

`python m06_track.py ../3_EVIDENCE/2026-11-20/161951_recording_test60.mp4 --model <m>.pt --tracker <t>`,
default settings (every 2nd frame, 751 frames, 60 s, turban rule and thresholds from M05, MAX_HOLD 10 s).
Raw files: `M05_data/results/m06_tracker_grid_23.11/` (summary + per-frame CSV per run). Videos on Dareen's laptop
(`3_EVIDENCE/m06_tracking/grid_<model>/`).

| Clip 161951 | User kept (M06 tracker) | Old M05 way, same run | Turban corrected the tracker | Gaps / longest |
|---|---|---|---|---|
| YOLO11n + ByteTrack | 82% (colour 70 + track 13) | 76% | 15 | 13 / 5.4 s |
| **YOLO11n + BoT-SORT** | **84%** (70 + 14) | 78% | **8** | 10 / 5.0 s |
| YOLO26n + ByteTrack | 81% (69 + 12) | 78% | 12 | 12 / 5.1 s |
| YOLO26n + BoT-SORT | 81% (70 + 11) | 76% | **8** | 11 / 5.0 s |

YOLO11n + ByteTrack reproduces Nimer's first run exactly (82% vs 76%) on another laptop.

## 3. What it means (and what it does not)

- **YOLO26n brings no gain here:** 81% with both trackers vs 82-84% for YOLO11n. Consistent with M05 (it finds fewer people).
- **BoT-SORT needs about half the turban corrections** (8 vs 12-15) with both detectors: it loses or swaps the user's
  track less often. Likely reason: BoT-SORT's camera-motion compensation (`gmc_method: sparseOptFlow`), which matters on a
  moving drone camera. **Lead candidate: YOLO11n + BoT-SORT.**
- **Limits (say them out loud):**
  - One clip. 751 consecutive frames are strongly correlated, so 81% vs 84% is **within noise** (±3 points even if the
    frames were independent). The corrections count is the clearer signal, but it is also from one clip.
  - "Corrections" = the turban picked a different ID than the remembered one. It is a **proxy** for lost/swapped tracks,
    not a ground-truth ID-swap count. Real wrong-person-by-tracker = yellow "USER (track)" boxes on someone else,
    to be counted by eye in the videos.
  - The "old M05 way" column moves 76-78% between runs because `model.track()` returns only tracked boxes, so the
    detections it gets differ per tracker. Compare old vs new **within a row only**.
  - The run times printed (137 / 66 / 34 / 37 s) are **not** a speed comparison: the first run includes loading and warm-up.

## 4. Next (to settle it properly)

1. Same grid on the other clips: 161825 (20.11) and both 22.11 Med-Faculty clips (never tuned on).
2. Count tracker swaps by eye in the 4 videos (yellow box on someone else).
3. Add BoT-SORT **with ReID** (`with_reid: True`, YOLO26 ReID model) as a 5th option; measure FPS on one fixed run.
4. Film and label crossing scenes (someone walks past the user) → ID swaps per 10 crossings = the M06 metric.

**What to tell Gabi:** "We checked: the adaptive Kalman (NSA) is part of the tracker in Ultralytics and works with any
detector. On our clip YOLO26n did not keep the user better than YOLO11n (81% vs 82-84%), but the tracker choice
mattered: BoT-SORT needed half the corrections of ByteTrack. We are testing it on more clips and on crossing scenes."
