# M05 on NEW footage (22.11, Medical Faculty, bikes / cars / people) + YOLO-World / YOLOE (work-plan item)

Clips: `3_EVIDENCE/2026-11-22/143404_recording_session1.mp4` (ground level, the user in the turban, bike racks, passers-by)
and `144943_recording_session2.mp4` (7-8 m high over the car park, no user; 42 s "signal lost").
Never used for tuning, so this is the first **honest** test of the M05 choice.
**No hand labels yet**, so detection is compared with a big model (YOLO11l at 1280 px) = **estimate**.
The hand-labelled score comes from Nimer's test set (`python m05_newclips.py label ...`, `M05_data/test_22.11/`).

Scripts: `1_CODE/m05_newclips_auto.py` (1 frame/s, 555 usable frames) and `1_CODE/m05_openvocab.py` (1 frame / 3 s, 186 frames).
Results: `M05_data/results/newclips_22.11/` and `M05_data/results/openvocab_22.11/`.

## 1. Finding the user (YOLO11n + turban colour, the M05 choice) - checked by eye, every pick
| | frames with a "user" | right | wrong |
|---|---|---|---|
| **Hybrid** (clip 1) | 88 | **83** | 5 = a passer-by in a **red shirt** (7-12 s): his box is small, so the "head" area (top 35%) reaches his red shoulders |
| **Hybrid** (clip 2, no user, red cars + red dome) | 0 | - | **0 false alarms** |
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
