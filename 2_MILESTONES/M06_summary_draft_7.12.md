# Tracking milestone (due 7.12.26) — one-page summary, DRAFT (26.11)

**Question (approved work plan):** keep THE user identified and followed — user detection (colour marker vs YOLO), tracking
with a Kalman-based tracker, a distance controller, tracker comparison on labelled clips, YOLOE check for strollers/scooters.

## What works (measured)
| item | result | evidence |
|---|---|---|
| User detection (hybrid YOLO + turban) | 403 hand-labelled frames: 89.8 % frames correct (head area 20 %), 0 false alarms | `M05_data/results/head_area_25.11/` |
| Model choice | YOLO11m better than 11n (paired test p = 0.016); live on battery ~18–21 FPS | `paired_test_25.11/`, `speed_charger_vs_battery_25.11/` |
| User score per box (identity, not detection) | AUC 0.914 (turban), 0.978 (turban + clothes) | `user_score_25.11/`, `body_cues_25.11/` |
| Tracker | BoT-SORT (Kalman motion model) best of 6; guarded ID switch stops the red-shirt takeover (switches 10 → 3) | `M06_tracker_grid_23.11.md`, `head_area_25.11/summary.md` |
| Safety states | FOLLOWING / UNSURE (search turn) / LOST (hover); battery stop 30 %; people-close hold; FORCE LAND | `m06_follow.py`, `session.py` |
| **Closed loop in flight** | yaw: all turns in the right direction (282/282, 872/872); distance: stops at the target size; one fully automatic run (self take-off → turn/follow/side → self landing) | `M06_field_day_25.11.md` |
| Loop delay | ≈ 0.5 s total (command ≈ 256 ms) — 2 samples | field day note |
| Digital twin | model from field measurements; validated (50 vs 55 % followed); recognition is the bottleneck; clothes learning 50 → 82.6 % | `twin_25.11/twin_results.md` |
| Twin on the crossing clip (session 1, red shirt) | followed 62.7 % → 64.7 % with clothes learning (people in view only 68 %) — small gain; the twin cannot yet say WHO was followed (needs labels) | `twin_25.11/` |
| Twin vs hand labels (26.11) | right when in view: 11n 71 %, **11m 78 %**, 26m 80 %; hold-out 6/7 (11m); 0 false picks / 239; 6 trackers tied 73–78 %, BoT-SORT fewest wrong | `M06_twin_accuracy_and_trackers_26.11.md` |
| YOLOE / YOLO-World | not usable as is for strollers/scooters (boxed bikes as "stroller") → train later | `M05_newclips_bikes_openvocab_22.11.md` |

## Pass lines vs status
| pass line | status |
|---|---|
| user kept ≥ 90 % of frames | twin 82.6 % with clothes learning (flight: 33–55 % before the fix) → **not yet** |
| ≤ 1 ID swap in 10 crossings | needs labelled crossing clips → **open** |
| 0 wrong-person follows | session 1: red shirt never USER with the guarded switch → **so far yes** (1 clip) |
| 60 s continuous | `walk_60s` clip recorded; follow run 60 s flown → **partly** |
| ≥ 10 FPS long run | ~19 FPS live → **yes** |

## Still to do before 7.12 (Nimer abroad from 12.12)
1. Fly AUTO_TESTS with clothes learning → confirm the 82 % in flight.
2. Crossing clips (3 people) → label in CVAT → ID swaps, IDF1/HOTA (TrackEval), tracker comparison (work plan).
3. DELAY TEST ×10 + TURN SPEED TEST → calibrate the twin.
4. Final one-page version + demo video + questions for Gabi.
