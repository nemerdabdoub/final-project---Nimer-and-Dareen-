# M05 user detection: what we did, what we chose and why (20.11 - 23.11.2026)

One page for the meeting and the report. Each step: **the problem → what we did → the evidence → the choice**.
Alternatives we considered but did not build (RT-DETR, ArUco, face recognition, Crazyflie): `M05_engineering_considerations.md`.

## 1. The question
The drone must find **every person** (they are obstacles) and know **which one is the user** in every frame, fast enough to
steer live on a laptop without a GPU. Work-plan targets: detection >= 90%; we added >= 15 FPS (live control), never the
wrong person, no false alarms.

## 2. Data: honest, hand-labelled, and tested on new footage
| Action | Why |
|---|---|
| 4 drone clips (20.11), 1 frame/s → 152 frames; one clip without the turban | enough frames for a fair comparison; the no-turban clip tests what happens without the marker |
| Draft boxes by a **bigger** model (YOLO11l), then **corrected by hand** (makesense) | a person decides the truth; the big model does not favour any of the small ones we test |
| Two classes: `user` (always the actor) and `person` | one label set scores both questions: find people / find the user |
| Brightness x0.35 copies | a low-light stand-in (no night flight yet) |
| **New footage 22.11** (bikes, car park, passers-by), 299 frames, hand-labelled by Dareen, **never tuned on** | the 20.11 thresholds were set on the 20.11 frames; a fresh test shows if they hold |

## 3. Methods compared (same frames, same rules)
- **Colour only**: biggest turban-coloured blob = the user.
- **YOLO alone** (YOLO11n, YOLOv12n, YOLO26n, YOLO11s, YOLO11m): finds people; its guess for the user = the biggest person.
- **Hybrid** (our design): YOLO finds the people; the turban colour **on the head** (top 35% of the box, >= 3% of the head,
  2x more than beside it) picks the user.

## 4. Problems we found and how we solved them
| Problem (seen in the results) | Action | Result |
|---|---|---|
| Colour alone fires on red objects (mural, sofa, red cars, dome) | colour only counts **on a person's head** (hybrid) | false alarms 71% → **0%** |
| YOLO alone cannot tell people apart | the turban picks the person | wrong person ~36% → **0%** (20.11) |
| A hand at the lens became the "user" | **hand filter**: skip boxes wider than 60% AND taller than 90% of the frame | the hand false alarm gone |
| Overall detection 85%, target 90% | measured **why**: every miss is a small, far or edge-cut person; 0% misses for big, fully visible people | new column "following distance (> 1/4 height)": **96-98%** → target met where the drone works |
| Tried to reach 90% on all people | lower confidence, bigger models, 1280 px input, tiles | only YOLO11s at 1280 px passes (91.7%) but runs at 5 FPS → rejected |
| A framed portrait detected as a person | **fine-tuned** YOLO11n on 335 of our own frames (gentle: frozen backbone, 80 classes kept) | portrait gone, detection 85.4 → 84.4%, but it **forgot bikes** → not adopted; lesson for next semester |
| New footage: a passer-by in a **red shirt** | found on the new clips; 3 wrong frames of 164 | next fix: M06 tracking keeps the ID; smaller head area for small boxes |
| Low-quality frames ("signal lost", user's head cut off, sun behind her) | skip black frames; label rule "the actor is ALWAYS user" | honest misses counted (hybrid 0 of 7 in clip 2's first seconds) |

## 5. The final comparison (all our videos, hand labels, 403 frames, re-run on the charger)
| method | user found | wrong person | false alarm | frames correct | people found at following distance | FPS |
|---|---|---|---|---|---|---|
| colour only | 64.0% | 24.4% | 33.1% | 65.8% | - | 145 |
| YOLO11n alone | 66.5% | 27.4% | 24.7% | 71.7% | 96.2% | 29.9 |
| **hybrid YOLO11n** ⭐ | 70.1% | 1.8% | **0%** | 87.8% | 96.2% | **29.9** |
| hybrid YOLOv12n | 70.1% | 1.8% | 0% | 87.8% | 95.0% | 25.0 |
| hybrid YOLO26n | 70.7% | 2.4% | 0.8% | 87.6% | 94.3% | 30.1 |
| hybrid YOLO11s | 73.8% | 1.8% | 0.8% | 88.8% | 95.8% | 15.8 |
| hybrid YOLO11m | 74.4% | 0.6% | 0% | 89.6% | 97.3% | 6.2 |
Full tables: `M05_data/results/userpick_allvideos_22.11/table.md`. All 8 detectors on the 20.11 set (incl. dark, 1280 px):
`M05_data/results/all_models_22.11/m05_all_models.md`.

## 6. The choice: YOLO11n + turban colour (hybrid)
1. **Hybrid, not colour or YOLO alone**: 15x fewer wrong-person frames (3 vs ~45), no false alarms (0 vs 59-79).
2. **YOLO11n, not a bigger YOLO**: the bigger ones gain 2-4 points but drop to 16 or 6 FPS; 11n keeps ~30 FPS, which leaves CPU
   time for M06 (tracker + controller). Among the fast models 11n has the best following-distance detection and no false alarms.
3. **90% target**: met at following distance (96.2%); not for small far people (59.4% with the 7-8 m footage) - the drone will follow at 3-6 m.

## 7. Extra work-plan item: strollers and e-scooters (obstacles, next semester)
COCO (80 classes) and Open Images (601) have bikes but no scooter/stroller. YOLO-World / YOLOE can be asked for them by text,
but on our clips they boxed bikes as "stroller/scooter" and run at ~7 FPS. Plan: film strollers/scooters, label them, train ONE YOLO11n
with person/bike/car + scooter + stroller (all classes together - the fine-tune taught us that), YOLOE only as a labelling helper.
Details: `M05_newclips_bikes_openvocab_22.11.md`.

## 8. Evidence (on Dareen's laptop, not in git)
`3_EVIDENCE/2026-11-23_M05_final/`: demo videos of both new clips (YOLO11n + turban, every box tagged USER / person + confidence),
result pictures (hybrid picks, colour false alarms, YOLO-World/YOLOE side by side, portrait before/after) and the final table.
Earlier demos: `3_EVIDENCE/m05_user_detection/demo_*.mp4`.

## 9. Next (M06, due 7.12)
Tracker (ByteTrack / BoT-SORT) keeps the user's ID when the turban is hidden or someone in red passes; distance controller
(dry run first); a filming session at following height (1.5-2 m, 3-6 m away).
