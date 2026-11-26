# Tracking (7.12): accuracy sweep, 6 trackers, YOLO26 — all scored against hand labels in the digital twin (26.11, Dareen)

**Why:** the 24.11 tracker grid had no ground truth (every tracker ≈ "user known 61 % / 82–84 %"), so it could not say
which tracker follows the WRONG person. Now every setting runs in the digital twin (`1_CODE/twin.py`) over a whole clip
and the locked box is compared with the hand labels (IoU ≥ 0.3 = right).
**Data:** tuning clip = session 1 (22.11, red-shirt passer-by): 151 labelled frames, **41 with the user in view**, 98 empty.
Hold-out = session 2 (never tuned on): 148 labelled frames, **only 7 with the user in view**, 141 empty.
Raw CSVs: `M05_data/results/twin_accuracy_26.11/`. GPU env, BoT-SORT, 640 px, clothes learning on unless said.
"right %" = right / (right + wrong + missed) over frames where the user is inside the twin's view.

## 1. Accuracy sweep (one change at a time from the flight setting) — session 1
| setting | right % | right / wrong / missed | false picks /98 |
|---|---|---|---|
| YOLO11n, no clothes | 68 % | 28 / 1 / 12 | 0 |
| YOLO11n + clothes (= flight setting today) | 71 % | 29 / 1 / 11 | 0 |
| clothes threshold 0.40 or 0.50 (instead of 0.45) | 71 % | same | 0 |
| wide turban range (+ hue 0–7, measured on session 1: her head covering = hue 168–187) | 71 % | same | 0 |
| 800 px picture | 73 % | 32 / 1 / 11 | 0 |
| **YOLO11m + clothes** | **78 %** | 32 / 1 / 8 | 0 |
| YOLO11m, no clothes | 80 % | 33 / 0 / 8 | 0 |
| YOLO26n + clothes | 73 % | 30 / 1 / 10 | 0 |
| **YOLO26m + clothes** | **80 %** | 35 / 1 / 8 | 0 |

**Hold-out (session 2):** YOLO11n 5/7 right, YOLO11m **6/7**; both 0 wrong, **0 false picks / 141**.

**Findings.** Only the detector size moves the result (small 71–73 % → medium 78–80 %). Threshold and colour range:
no effect → dropped (a "no effect" result is still reported). Clothes learning: no gain outdoors where the turban is seen
(its gain was indoors: 50 → 83 %). YOLO11m vs YOLO26m: 1–3 frames apart = noise, as on 24.11.
**Three checks now agree that 11m > 11n:** paired test on 403 frames (p = 0.016, 25.11), this sweep, the hold-out.
→ By our rule (11m if ≥ 15 FPS live on battery; measured 18–21 FPS) **the flights should use YOLO11m**.
Weakness (say it): 41 + 7 user frames is small; a 4-frame gain alone would be noise — it counts because it agrees with the paired test.

## 2. Six trackers, same detector (YOLO11m + clothes) — session 1
| tracker | idea in one line | right % | wrong | ID changes of the lock |
|---|---|---|---|---|
| **BoT-SORT** (2022) | ByteTrack + **camera-motion compensation** + optional ReID | **78 %** | **1** | 10 |
| OC-SORT (2023) | re-fixes the Kalman track from real detections after an occlusion | 78 % | 2 | 9 |
| Deep OC-SORT (2023) | OC-SORT + appearance | 78 % | 2 | 9 |
| ByteTrack (2022) | also matches low-confidence boxes | 76 % | 2 | 11 |
| FastTrack (in Ultralytics 8.4) | lightweight motion tracker | 76 % | 2 | 11 |
| TrackTrack (CVPR 2025) | track-focused matching, top HOTA on MOT17 | 73 % | 1 | 10 |
SORT (2016, Kalman + IoU) and DeepSORT (2017, + ReID CNN) are the ancestors: OC-SORT and BoT-SORT-with-ReID replace them,
so they are not run separately. StrongSORT is not in Ultralytics (its NSA-Kalman idea is).

**Findings.** On this clip the trackers are **nearly tied** (73–78 %, 1–2 wrong frames). The tracker is not the weak
spot — recognising the user is. **Keep BoT-SORT:** fewest wrong-person frames here, fewest corrections on 23.11, and the
only one that compensates the drone's own turning. The test that can really separate trackers = **crossing clips**
(3 people, ID swaps per 10 crossings) + BoT-SORT with ReID on/off.

## 3. Clothes change (other day / other person)
- The clothes are **learned again at every take-off** (6 s, user alone, facing the drone) → other clothes on another day,
  or another user, are no problem. The **turban is the fixed marker**; clothes only help.
- Risks: (a) clothes change **during** a flight (jacket off) → the clothes score drops, the turban carries the lock;
  (b) a passer-by in similar clothes → the guarded switch (1 s + margin 0.30) stops a takeover; (c) **no turban** →
  clothes only: not measured yet. Idea (not coded): update the clothes template slowly only while the turban confirms her.

## 4. Will the drone find the user and follow her now?
Chain: take-off → learn clothes 6 s → lock by turban + clothes → turn (yaw) + keep distance; UNSURE = slow search turn,
LOST = hover. **Measured in flight (25.11):** every turn in the right direction, distance stops at target, full automatic
run, but the user was FOLLOWED only **33–55 %** of the time (recognition). The twin predicts a clear gain with clothes
learning indoors and with YOLO11m outdoors — **not flown yet**. Honest answer: it will find and turn to her; whether it
keeps her ≥ 80 % of the time is the next flight's question (pass line below).

## 5. What must be done until 7.12 (Nimer abroad from 12.12)
| # | task | pass line / output | who, when |
|---|---|---|---|
| 1 | Flights on YOLO11m (`--model yolo11m.pt` in AUTO_TESTS) | FOLLOW test ≥ 80 % FOLLOWING, 0 wrong-person | both, next field day |
| 2 | Film crossing clips: 3 people, ≥ 10 crossings, from hover | videos in 3_EVIDENCE | both, same field day |
| 3 | Label crossings (CVAT) → ID swaps, IDF1/HOTA (TrackEval); BoT-SORT vs OC-SORT vs TrackTrack, ReID on/off | ≤ 1 swap / 10 crossings | by 3.12 |
| 4 | DELAY TEST ×10 + TURN SPEED → calibrate the twin | delay mean ± sd | field day |
| 5 | One no-turban run (clothes only) | right % without the marker | field day |
| 6 | Final one-page summary + demo video + requirement trace + questions for Gabi | `M06_summary_draft_7.12.md` | by 6.12 |
