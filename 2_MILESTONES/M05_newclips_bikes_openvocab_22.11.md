# M05 on NEW footage (22.11, Medical Faculty, bikes / cars / people) + YOLO-World / YOLOE (work-plan item)

Clips: `3_EVIDENCE/2026-11-22/143404_recording_session1.mp4` (ground level, the user in the turban, bike racks, passers-by)
and `144943_recording_session2.mp4` (first ~10 s on the ground WITH the user, then 7-8 m high over the car park without her; 42 s "signal lost").
Never used for tuning, so this is the first **honest** test of the M05 choice.
**No hand labels yet**, so detection is compared with a big model (YOLO11l at 1280 px) = **estimate**.
The hand-labelled score comes from Nimer's test set (`python m05_newclips.py label ...`, `M05_data/test_22.11/`).

Scripts: `1_CODE/m05_newclips_auto.py` (1 frame/s, 555 usable frames) and `1_CODE/m05_openvocab.py` (1 frame / 3 s, 186 frames).
Results: `M05_data/results/newclips_22.11/` and `M05_data/results/openvocab_22.11/`.

## 1. Finding the user (YOLO11n + turban colour, the M05 choice) - checked by eye, every pick
| | frames with a "user" | right | wrong |
|---|---|---|---|
| **Hybrid** (clip 1) | 88 | **83** | 5 = a passer-by in a **red shirt** (7-12 s): his box is small, so the "head" area (top 35%) reaches his red shoulders |
| **Hybrid** (clip 2: car park part, red cars + red dome) | 0 | - | **0 false alarms** (it also missed the user in the first 10 s: head cut off / back-lit) |
| Colour only (both clips) | 223 | ~90 | ~130 false: red dome, red fire boxes, red cars, a hand at the lens, the red "signal lost" icon |

- The hybrid did not see the user when she was **far away** (e.g. 187 s, 290-293 s): no person box around her (same as M05: small people).
- New problem found: **red clothes** on other people. Fixes (easy, test on the labelled set): head area 35% -> 20% for small boxes, or
  require the colour blob to sit *above* the widest part of the box (head, not shoulders); M06 tracking (ID kept from the right person)
  also stops a one-frame jump to the man in red.

## 2. People, riders and bikes (estimate vs YOLO11l @ 1280)
| model | all people | big people (> 1/4 height) | riders (11) | parked bikes found | extra boxes | ms/frame |
|---|---|---|---|---|---|---|
| **YOLO11n** | 66.5% | **100%** | 82% | 141 / 394 | 30 | **49** |
| YOLOv12n | 66.0% | 100% | 91% | **187 / 394** | 28 | 61 |
| YOLO26n | 66.0% | 99.2% | 82% | 159 / 394 | 33 | 47 |
| YOLO11n gentle fine-tune | 58.7% | 94.3% | 82% | **0** (forgot bikes) | 34 | 48 |

- Same picture as M05: **every big person is found** (following distance); the misses are small, far people (many from 7-8 m).
- Bikes: a **bike is almost never boxed as a person** (1 of 30 extra boxes) - good for the obstacle map.
  Parked bikes in a dense rack are hard for all nano models (overlapping); YOLOv12n is best there.
- The fine-tuned model was trained on person only and **lost the bike class** -> for next semester (obstacles) keep the original
  COCO model, or fine-tune with bikes/cars labelled too.

## 3. Open-vocabulary detectors (work plan: "check if YOLOE or YOLO-World detect strollers and scooters by 23.11")
Prompts: person, bicycle, car, motorcycle, electric scooter, baby stroller. Smallest available sizes (World v2 **s**, YOLOE-11 **s**).
| model | ms/frame | person | bicycle | car | motorcycle | scooter / stroller boxes |
|---|---|---|---|---|---|---|
| YOLO11n (COCO, 80 classes) | **49** | 67% | 31% | **52%** (many extra) | 12% | no such class |
| YOLO-World v2 s | 131 | **84%** | 36% | 20% | 4% | 0 / 0 |
| YOLOE-11s | 142 | 83% | 29% | 29% | 23% | 3 / 9 |

By eye, the 12 YOLOE scooter/stroller boxes: **1 real e-scooter** (90 s, but called "stroller"), the other 11 are bikes, a motorcycle,
a backpack, a planter. There were **no strollers** in the clips, so recall cannot be measured yet.
- **Answer for the work plan:** open-vocabulary detectors *can* be asked for scooters/strollers, but here they confuse them with bikes,
  and they are ~3x slower (7 FPS) than YOLO11n. Not ready to use as is.
- **Next semester (obstacles):** film real strollers and e-scooters (campus has many scooters), then either use YOLOE with tuned
  prompts / visual prompts, or fine-tune YOLO11n on a small labelled set with the extra classes (work-plan fallback). Person / bike / car
  stay with standard YOLO.

## 4. Other lessons from this filming
- 7-8 m height = people too small for following; the following view is 1.5-2 m high, 3-6 m away.
- 42 s of "signal lost": the app banner and red icon remain - skip such frames (and the colour must ignore the app's red icons).
- Battery ~9%/min; land at 30%.

## 5. (Preliminary, by-eye user boxes) finding THE user on ALL our videos - replaced by section 7 (hand labels)
Script `1_CODE/m05_userpick_allvideos.py`, results `M05_data/results/userpick_allvideos_22.11/` (`table.md`, `counts.csv`).
- Same rules as Table B in `m05.py` (each frame judged alone: right = IoU >= 0.5 with the user box; colour = point inside it).
  **Check that the code is the same:** on the M05 frames it reproduces Table B exactly (hybrid YOLO11n 73.1% / 0% / 0% / 78.8%).
- New clips: user box marked **by eye** (Claude, 23.11) on all 299 frames, from YOLO11l boxes: `user_gt_22.11.json`.
  39 frames left out (black "signal lost", or the user only half in view with no box). To be replaced by the hand labels.
- Sets: M05 132 frames (104 with user) · NEW1 142 (44) · NEW2 118 (5) → **392 frames, 153 with the user, 239 without**.

| method (ALL videos, 392 frames) | user found | wrong person | false alarm | frames correct | ms/frame |
|---|---|---|---|---|---|
| colour only | 65.4% (100/153) | 26.1% (40) | 31.0% (74/239) | 67.6% | 15 |
| YOLO11n alone (biggest person) | 69.9% (107) | 28.8% (44) | 23.0% (55) | 74.2% | 35 |
| YOLO11m alone | 72.5% (111) | 26.8% (41) | 31.4% (75) | 70.2% | 213 |
| **hybrid YOLO11n (our choice)** | **75.2% (115)** | **1.3% (2)** | **0% (0)** | **90.3%** | **35** |
| hybrid YOLOv12n | 75.2% (115) | 1.3% (2) | 0% | 90.3% | 42 |
| hybrid YOLO26n | 75.2% (115) | 2.0% (3) | 0% | 90.3% | 34 |
| hybrid YOLO11s | 77.8% (119) | 2.0% (3) | 0% | 91.3% | 65 |
| hybrid YOLO11m | 78.4% (120) | 0.7% (1) | 0% | 91.6% | 213 |
| hybrid gentle fine-tune | 70.6% (108) | 3.9% (6) | 0% | 88.5% | (timing noisy) |

**Answers**
1. **Hybrid vs the others, on all videos: yes, clearly better.** Wrong person 2 of 153 vs 40-45 for colour or YOLO alone (20x fewer),
   false alarms 0 of 239 vs 55-75. Frames correct 90.3% vs 67-74%.
2. **Hybrid YOLO11n vs other hybrids: a tie.** The three nano hybrids find the same 115 frames; 11s / 11m find 4-5 frames more
   (3%) but are 2x / 6x slower. 4-5 frames out of 153 is too small a difference to call one better. → keep YOLO11n.
3. **Better than before?** On the new clip 1 (user closer, good light): user found **88.6%**, frames correct **96.5%** vs 73.1% / 78.8%
   on the 20.11 frames; still 0 false alarms. Weak spots that remain: user far away, head out of frame or back-lit (clip 2 start: 0 of 5),
   and other people in red (2 wrong frames here, 5 at 1 frame/s).

## 6. Which YOLO for our aims (recommendation, 23.11)
- **Now (M06, following the user): YOLO11n + turban colour + a tracker (ByteTrack/BoT-SORT, `m06_track.py`).**
  Not a bigger model: the remaining misses (head cut off, back-lit, far, red clothes) are fixed by *keeping the ID over time*,
  not by a few % more detection. 11n leaves CPU time for the tracker and the controller.
- **Do not run two YOLOs on every frame** on the laptop CPU (11n 35 ms + 11s 65 ms ~ 10 FPS): too slow for control.
- **Next semester (obstacles: people, bikes, cars, e-scooters, strollers with kids): ONE enhanced YOLO11n** (or 11s if it stays >= 15 FPS),
  fine-tuned with **all needed classes together**: keep person/bicycle/car/motorcycle (COCO) and add `scooter` and `stroller`.
  Lesson from our gentle fine-tune: training on person only made the model forget bikes, so the training set must contain every class.
  Data: our own clips (campus has many e-scooters; film strollers) + public labelled sets; draft boxes by YOLOE / YOLO-World, corrected by hand.
- **Ready-made models checked:** COCO (80 classes) and Open Images V7 (601 classes) have bikes but **no scooter and no stroller**.
  YOLOE prompt-free (4585 classes) has `scooter` and `baby carriage`, and YOLOE / YOLO-World take text prompts, but on our clips
  they called bikes "stroller/scooter" and run at ~7 FPS → use them as the **labelling helper**, not as the flying detector.
  Fallback if fine-tuning is not ready: 11n every frame + YOLOE on every 5th frame only for scooters/strollers.
- **Stroller with a kid** = stroller box (new class) + a person box inside it; either way it goes into the obstacle map.

## 7. FINAL (hand labels, 23.11): all 13 methods on all our videos
Dareen hand-labelled all 299 new frames (`M05_data/test_22.11/labels`, both halves). Same script, now on hand labels:
`M05_data/results/userpick_allvideos_22.11/table.md` (by-eye version kept as `table_byeye.md`).
Frames: M05 132 + NEW1 151 + NEW2 120 = **403 frames, 164 with the user, 239 without**; 604 labelled people.

**Finding THE user (ALL videos)** - bold = best in the column

| method | user found | wrong person | false alarm | frames correct |
|---|---|---|---|---|
| colour only | 64.0% (105/164) | 24.4% (40) | 33.1% (79/239) | 65.8% |
| YOLO11n alone (biggest person) | 66.5% | 27.4% (45) | 24.7% (59) | 71.7% |
| YOLO11m alone | 68.9% | 25.6% (42) | 32.6% (78) | 68.0% |
| **hybrid YOLO11n (our choice)** | 70.1% (115) | 1.8% (3) | **0% (0)** | 87.8% |
| hybrid YOLOv12n | 70.1% (115) | 1.8% (3) | **0%** | 87.8% |
| hybrid YOLO26n | 70.7% (116) | 2.4% (4) | 0.8% (2) | 87.6% |
| hybrid YOLO11s | 73.8% (121) | 1.8% (3) | 0.8% (2) | 88.8% |
| hybrid YOLO11m | **74.4% (122)** | **0.6% (1)** | **0%** | **89.6%** |
| hybrid gentle fine-tune | 65.9% (108) | 3.7% (6) | 0.4% (1) | 85.9% |

**Finding people (ALL videos, Table A rules)**

| detector | all people | following distance (> 1/4 height) | precision | speed, whole hybrid (clean re-run 23.11, on charger) |
|---|---|---|---|---|
| **YOLO11n** | 59.4% (359/604) | 96.2% (251/261) | 94.7% | 33.5 ms = **29.9 FPS** |
| YOLOv12n | 59.3% | 95.0% | 93.2% | 40.0 ms = 25.0 FPS |
| YOLO26n | 58.8% | 94.3% | 93.4% | 33.2 ms = **30.1 FPS** |
| YOLO11s | 64.9% | 95.8% | 93.6% | 63.3 ms = 15.8 FPS |
| YOLO11m | **68.2%** | **97.3%** | **96.9%** | 161.4 ms = 6.2 FPS |
| gentle fine-tune | 56.5% | 95.4% | 91.2% | 33.4 ms = 29.9 FPS |

(Re-run 23.11 with nothing else running, on the charger: every accuracy count identical to the first run; speeds above from this clean run.
 Colour only alone: 6.9 ms. YOLO11s at 15.8 FPS is just at our 15 FPS limit, with no time left for the tracker and controller.)

**What it means**
- **The hybrid beats colour-only and YOLO-alone on every video**: wrong person 1.8% vs 24-27%, false alarms 0 vs 59-79 frames,
  frames correct 87.8% vs 66-72%. This is the main M05 result and it holds on footage we never tuned on.
- **YOLO11n stays the choice.** YOLO11m is a little better everywhere (+7 user frames of 164, +9% people) but runs at 6.2 FPS, below the
  15 FPS we need. Among the fast (nano) models 11n is tied best on the user, has the best following-distance detection (96.2%) and no false alarms.
- **Correction 23.11 - work-plan requirement 1 is "identify the user in >= 90% of frames in lab conditions"** (not person detection):
  the user is **detected** (YOLO11n box on her) in 99.0% of lab frames (92.7% all videos) but **identified** by the turban in 73.1%
  (70.1% all videos) → identification above 90% comes from M06 tracking. Person detection for reference: following distance 96.2%, all people 59.4%:
  the new clips have many small far people (7-8 m height). The drone will follow at 3-6 m, where the target is met.
- Hand labels vs Claude's by-eye boxes: same user in 126 of 129 checked frames; the hand labels also count 11 half-visible user frames,
  which is why "user found" is a bit lower here (70.1% vs 75.2%) - the conclusions do not change.

## 8. Simple tweaks of YOLO11n (23.11): confidence cut-off x input size
Script `1_CODE/m05_tweak_sweep.py`, same 403 hand-labelled frames, results `M05_data/results/tweak_sweep_23.11/sweep.md`.
Triggered by a frame at 1:59 of clip 1: a far woman got person 0.23 (just under the 0.25 cut-off); YOLO11n also gave 0.23 to a golf cart.

| setting | people (all) | following distance | precision | user found | wrong person | false alarm | frames correct | FPS |
|---|---|---|---|---|---|---|---|---|
| 640 px, 0.25 (current) | 59.4% | **96.2%** | **94.7%** | 70.1% | 3 | 0 | 87.8% | **29.2** |
| 640 px, 0.15 | 61.9% | 96.6% | 87.2% | 68.9% | 5 | 0 | 87.3% | 29.0 |
| **800 px, 0.25** | 61.9% | 95.0% | 92.6% | **72.6%** | 3 | 0 | **88.8%** | 23.0 |
| 960 px, 0.25 | 64.2% | 95.0% | 91.3% | 72.6% | 3 | 1 | 88.6% | 18.3 |
| 960 px, 0.15 | **66.9%** | 95.4% | 83.6% | 70.7% | 7 | 2 | 87.6% | 18.3 |

- **Lowering the cut-off does not pay:** +1-2.5 points of people, but up to 2.7x more wrong boxes (golf carts) and more wrong-person frames.
- **Input 800 px is the one simple tweak that helps a little:** +2.5 points people and user found, same 3 wrong / 0 false alarms, 23 FPS
  (+10 ms). Cost: 3 fewer near people (96.2 → 95.0%), 10 more wrong boxes.
- **Decision: keep 640 px / 0.25 for M05**; re-test 800 px in M06 once the tracker's CPU cost is known (candidate for the obstacle model).
