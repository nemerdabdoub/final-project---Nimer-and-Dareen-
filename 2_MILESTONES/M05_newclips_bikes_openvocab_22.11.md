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

## 5. VERIFIED: finding THE user on ALL our videos, same rules (added 23.11)
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
