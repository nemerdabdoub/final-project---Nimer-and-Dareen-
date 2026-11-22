# M05: why the numbers fall short, and how to fix it (Dareen, 22.11)

For Nimer's one-page summary and for the meeting. Measured on all 152 corrected labels with YOLO11n.
Reproduce: `python m05_diagnose.py` (in 1_CODE; prints only).

## Where M05 stands
| Step | Status |
|---|---|
| 152 frames, all labels corrected | done |
| Table A (C2-C4) + speed run | done (Nimer) |
| Table B (C1 + H1-H3), no-marker row, 2 screenshots | done (both laptops, identical numbers) |
| Winner | **to write down**: everything points to YOLO11n |
| Demo video | done (Dareen, YOLO11n, see "Demo video" below) |
| One-page summary, AI log lines | **open** (Nimer by Mon 12:00; both add an AI log line) |

**Winner sentence (proposal):** Winner = YOLO11n, because it is both the most accurate (85.4% detection, 94% precision)
and the fastest (21 FPS on a laptop CPU). The 90% target was not reached because of small and cut-off people;
for people at following distance it finds 96%.

## Problem 1: detection rate 82-85%, below the 90% target
All misses are small or cut-off people (YOLO11n, conf 0.25, 640 px):

| Person in the frame | People | Missed |
|---|---:|---:|
| large (> 50% of the frame height), fully visible | 124 | 0% |
| medium (25-50%), fully visible | 72 | 0% |
| large, cut by the frame edge | 18 | 11% |
| medium, cut by the edge | 25 | 28% |
| small (< 25% of the height) | 72 | **46%** |
| small and cut by the edge | 4 | 100% |

- Without the small people: 96% detected (230 of 239). Fully visible people taller than 1/4 of the frame: 100%.
- Tried: conf 0.15 → 86.3% but precision drops to 88.3%; 960 px input → 83.8% (no help).
- **Fixes:** a slightly bigger model (YOLO11s, test the speed); the M06 distance controller keeps the user large in the
  picture; define the target for people above a minimum size (the drone follows one nearby person, not the background).

## Problem 2: the hybrid finds the user in only 73-74%
Of its 28 misses on the 104 frames with the actor (YOLO11n hybrid):
- 23: YOLO boxed him, but too little turban colour on the head (9 of them 0%: turned away or hidden; the rest 0.1-3%,
  just under the 3% threshold).
- 4: colour there, but it failed the "2x the background beside the head" test.
- 1: YOLO did not box him at all.

Lowering the head-colour threshold is a trade-off (same 132 frames):

| Threshold | Found | Wrong person | False alarm |
|---|---:|---:|---:|
| 3% (now) | 73.1% | 0% | 7.1% |
| 2% | 77.9% | 0% | 10.7% |
| 1% | 81.7% | 1.0% | 14.3% |
| 0.5% | 84.6% | 1.0% | 28.6% |

- **Fix:** keep 3% (never the wrong person) and let **M06 tracking** keep the same person through the frames where the
  turban is not seen. Note: these thresholds were set on the same frames we test on; tuning them to these numbers
  would be fitting the test set, so we report the trade-off instead.

## Problem 3: without the turban the hybrid finds nobody
154124 (20 frames): 0% found, 0% wrong (it picks nobody, the safe failure). Colour only is wrong 100%.
- **Fix (M06):** tracking (ByteTrack / BoT-SORT + Kalman) + re-identification by appearance, or a printed ArUco marker
  (also gives the distance to the user).

## Problem 4: the hybrid's 2 false alarms = a hand in front of the lens
154848 frames 00114 and 00152: YOLO calls the hand a person and the pink skin passes as the turban colour.
- **Fix:** ignore "people" boxes that fill almost the whole frame (one line in `hybrid_user`).

## Can we reach 90%? Tested on the same 152 frames (`python m05_improve.py`)
| Setting | Detection | Precision | Big people (> 1/4 height) | Speed (Dareen's laptop) |
|---|---:|---:|---:|---:|
| YOLO11n, 640 px (today) | 85.4% | 94.1% | 95.4% | 37 FPS |
| YOLO11n, 1280 px | 82.2% | 93.2% | 90.0% | 13 FPS |
| YOLO11n, 640 px + 2 tiles | 85.7% | 85.4% | 95.4% | 10 FPS |
| YOLO11s, 640 px | 84.8% | 93.0% | 93.3% | 18 FPS |
| **YOLO11s, 1280 px** | **91.7%** | 89.8% | 92.9% | 5 FPS |
| YOLO11s, 640 px + 2 tiles | 89.8% | 82.5% | 93.3% | 5 FPS |
| YOLO11m, 640 px | 87.9% | 94.2% | 96.2% | 7 FPS |
| YOLO11m, 1280 px | 88.6% | 90.0% | 93.3% | 2 FPS |
| YOLO11l, 640 px (biased: it made the suggested labels) | 88.3% | 97.5% | 95.4% | 5 FPS |

- **Only YOLO11s at 1280 px passes 90%** (91.7%), at the cost of precision (89.8%) and speed (about 5 FPS on a laptop
  CPU, too slow for live control). Bigger models alone (11m, 11l) reach about 88%.
- The gain is on the small, far people. For the people that matter for following (big in the picture), YOLO11n at 640 px
  is already about as good as anything here (95%).
- Caveats: picked after seeing these same frames, so it must be confirmed on new clips; speeds partly measured while the
  demo video was rendering (the ranking holds, exact FPS should be re-measured).
- **Practical option:** run YOLO11n live, and switch to YOLO11s at 1280 px only when the user is small or lost.

## What we would do differently, from easiest to hardest (what exactly to do)

### Very easy: code only, no new filming (about 30 min each)
**A. Ignore "people" that fill the whole frame** (the hand-in-front-of-the-lens false alarms)
- Do: in `m05.py`, `hybrid_user`, skip person boxes taller than ~90% and wider than ~60% of the frame (about 3 lines).
- Expect: the hybrid's 2 false alarms disappear (7.1% → about 0%). Then re-run H1-H3 (10 min).

**B. Count only people big enough to follow (extra Table A row)**
- Do: when scoring detection, add a second number for people taller than 1/4 of the frame. Show it NEXT TO the current
  number, not instead of it (so it is not "moving the goalposts").
- Expect: YOLO11n ~95% → the target is met for the people the drone follows; far background people stated as excluded.

### Easy: one short new filming session (1-2 h with the flight)
**C. Record on the drone, not the phone mirror**
- Do: in DJI Fly start recording on the drone (the Neo saves to its built-in storage, up to 4K; it has no SD card).
  After landing: DJI Fly → Album → download to the phone, or connect the Neo to the laptop with USB-C. Then `m05.py extract`.
- Expect: sharper frames, no DJI Fly buttons over the left/right edges → fewer "cut by the edge" misses.

**D. Film at following distance**
- Do: in the same flight keep the drone ~3-6 m from the actor so he is at least 1/4 of the frame height; a few other
  people walk by, closer and farther.
- Expect: a test set that matches the real task.

**E. More frames per second**
- Do: extract with a smaller step (e.g. 5 instead of 25 for a 25 fps clip = 5 frames/s). Use a short 20-30 s clip or
  `label_tool.py` (5x more frames = 5x more labelling).
- Expect: the 1-second fallback and the M06 tracking can actually be tested.

**F. Keep tuning and testing apart**
- Do: the 20.11 clips = tuning only; the new clips from C-E = testing only. No setting changed after seeing test results.
- Expect: numbers Gabi can trust; confirms (or not) the YOLO11s 1280 px 91.7%.

### Medium: needs a decision or something printed/bought (half a day)
**G. A marker colour found nowhere else**
- Do: a bright colour not in the lab (neon green / cyan cap or vest, visible from all sides); change `TURBAN_HSV` in `m05.py`.
- Expect: no confusion with skin, the red mural or the sofa.

**H. A printed ArUco marker**
- Do: print a large ArUco code (A4, ~20 cm); OpenCV has `cv2.aruco` built in.
- Expect: identifies the user AND gives distance + angle (useful for the M06 distance controller). Weak: must face the
  camera, motion blur. Ask Gabi first (question c).

**I. A real low-light flight**
- Do: the same flight as C-D in the evening or with the lab lights dimmed (keep the safety rules; the Neo struggles in
  very dark places).

### Hard: not before M06
**J. Fine-tune YOLO on drone-view frames** — a few hundred new labelled frames kept apart from the test set + training time.

**Proposal:** before the meeting only **A + B** (half an hour, no flying). Propose **C + D + E + F as one filming
session** next week, and ask Gabi about **G or H**.

## Demo video (C5) done
`3_EVIDENCE/m05_user_detection/demo_161951_recording_test60_yolo11n.mp4` (60 s, on Dareen's laptop; video not in git).
User picked by the turban colour in 70% of frames, kept by the 1-second fallback in 8%, no user in 22%.
Screenshots: `M05_data/results/demo_yolo11n_22.11/` (user in front of the red mural; user among other people).

## Problem 5: limits of the test
One place, one day, 152 frames; the dark test is darkened copies, not a real low-light flight; frames are 1 s apart,
so the 1-second fallback is barely tested. These match the 3 questions for Gabi (plan part 7).
