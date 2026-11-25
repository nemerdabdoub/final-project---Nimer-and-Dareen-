# M06 field day 25.11.2026 (Dareen + Nimer) — results

Late start (13:30) → about 2.5 h of light; table tests alone indoors, flights with Nimer 16:05–16:37 (sunset ~16:40).
Files (laptop only, not git): `3_EVIDENCE/2026-11-25/`, `3_EVIDENCE/m06_tracking/live_20261125_*`.

## Table tests (drone not flying)
| test | result |
|---|---|
| Camera tilt (gimbal) | handle left of the picture; −90° … ~+50°; 11.4 px/°; `gimbal.py to -30` → −30° exactly, `level` → 0–1° |
| A4 recording | 751 frames / 30 s ✓ (needed `run_with_adb.py`: adb not on PATH in a fresh terminal) |
| A6 live follow, dry | FOLLOWING while in view, **yaw sign right 269/269**, ~28 FPS (GPU, plugged) |
| Speed (offline, whole pipeline) | charger 11n 31.7 / 11m 28.8 FPS; battery 11n 23.1 / 11m 20.7 FPS; live ≈ −12% |
| A6b colour enrolment | try 1 FAILED: window behind her → turban black, score 0.30–0.48, never USER (no false pick). Try 2 (light on her face, camera higher): **FOLLOWING 100%, USER ~0.9**, ~27 FPS |

## Flights
| step | result |
|---|---|
| B1 hover + recording | take-off from code (attempt 1), 751 frames ✓ |
| **B5 first closed loop, yaw only** (max yaw 0.2, YOLO11n) | run 1: **FOLLOWING 77%**, ~20 FPS live, turn commands 74% of the time, **all 282 in the right direction**; mean off-centre 0.27; slow to catch up at the edge (0.81) · run 2: drone was still on the ground → LOST 100%, nothing sent (safe) · run 3: **FOLLOWING 95%** (stopped after ~8 s) |
| **B3b yaw response** (stick 0.3, 2 s, `--auto 2`) | picture shifted the right way after **483 and 540 ms** → total loop ≈ **0.5 s**, command part ≈ **256 ms** (2 samples only) |
| **B6 distance + yaw** (`--forward`, max fwd 0.15) | her height in the picture grew 0.31 → **0.47 (target 0.45)**, then forward = 0 → **stopped at the target distance by itself**; off-centre 0.45 → 0.04 while turning toward her |
| Crossings, 60 s clip, from above | **not done** (light / time) |

## Lessons
1. **Say "go" only when the drone is hovering at 1.5 m facing the user** — the follow script never takes off (run 2).
2. **Keep DJI Fly on the camera view** — a tap opened the "Smart Snaps" menu and the script saw no people (first B5 try).
3. **Sun / window behind the drone, never behind the user** (A6b try 1).
4. **The ~0.5 s loop delay makes the turn lag** (looks "late / opposite" to the eye) → next: prediction / D term, tuned in the simulator with SIM_DELAY=0.5.
5. Start drone scripts through `run_with_adb.py`.

## Open (next session)
- Crossing clips (top 5) + 60 s continuous + 2 "from above" clips (Gabi) — need light and a passer-by.
- Command delay with 10 presses (`--auto 10`) + 60 fps phone video; yaw rate at 0.2 / 0.4.
- Live 11m check on battery (B4) → final model.
- Dev: follow script records until landing (not fixed seconds); auto-copy videos to a Drive folder (needs Google Drive for Desktop); prediction for the delay.

## Evening: FULL AUTOMATIC run (AUTO_TESTS.bat, 18:42, indoor hall, Dareen pilot, Nimer user)
One double-click: countdown → **take-off by itself** → TURN 40 s → FOLLOW 60 s → SIDE 40 s → **landed by itself**. One video
(`session_20261125_184201.mp4`, 105 MB) + CSV. Drone battery 50 → 34%. ~19 FPS live.
| test | FOLLOWING | mean off-centre | turn direction right | forward / side used |
|---|---|---|---|---|
| TURN | 34% | 0.44 | 235/235 | – |
| FOLLOW | 55% | 0.26 | 423/423 | forward in 442 frames |
| SIDE | 33% | 0.42 | 214/214 | side in 217, forward in 116 frames |
- Every turn in the right direction; forward and sideways commands were used. **Weak point: the user was in view only 33–55%**
  and far off-centre (0.42–0.44) → the drone turns too slowly to keep up (max yaw 0.2, ~0.5 s delay). Next: max yaw 0.3,
  predictor test, slower walking; check the video for when he left the picture.
