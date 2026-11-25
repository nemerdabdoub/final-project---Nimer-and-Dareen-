# Session handoff (Dareen's long session 24–26.11) — read this first in a new session

## Where things are
- **Tracking milestone (due 7.12.26)** — draft summary: `2_MILESTONES/M06_summary_draft_7.12.md`.
- Field day results: `2_MILESTONES/M06_field_day_25.11.md`. Test protocol + simple names: `2_MILESTONES/M06_flight_test_protocol.md`.
- To-dos / research / deep dives: `2_MILESTONES/PROJECT_NOTEBOOK_todo_research_25.11.md` (items 1–13).
- Milestone dates (approved plan): 7.12 tracking · 11.1.27 RRT* (sim by 21.12) · 15.2 mid presentation · 5.4 static obstacles ·
  17.5 dynamic obstacles · 7.6 moving target · 21.6 20 field runs · 19.7 book. **Nimer abroad 12.12.26–3.1.27.**

## Code that matters (1_CODE)
- `AUTO_TESTS.bat` (repo root) → `session.py --auto`: self take-off → learn user's clothes 6 s → TURN 40 / FOLLOW 60 / SIDE 40 /
  ORBIT 30 s → self landing; speaks commands to the user; people-close hold; battery stop 30 %. Short low-battery version:
  `AUTO_TESTS_SHORT_LOWBATT.bat`. `FORCE_LAND.bat` = emergency (works through any running script).
- `m06_follow.py` (follow logic, guarded ID switch, head area 20 %, search turn, side, `--predict` off, `--colour`),
  `twin.py` (digital twin + `--labels` right/wrong-person check), `sim_drone.py` (`set DRONE_SIM=<video>`), `gimbal.py`
  (camera tilt −90…+50°), `command_delay_test.py --auto 10`, `record_video.py`, `record_loop.py`, `run_with_adb.py`
  (ALWAYS start drone scripts through it: adb not on PATH), `countdown.py`.
- Run with the GPU python: `C:\Users\LOREN\venvs\gpu\Scripts\python.exe`.

## Key results (with sources)
- Paired test 11m vs 11n p = 0.016 (11m better); live on battery ~18–21 FPS. Head area 20 %: 89.8 % frames correct (403 frames).
- User score AUC 0.914 (turban), 0.978 (+clothes). Guarded switch: red shirt never USER on session 1.
- Flights: all turns in the right direction; distance stops at target; full automatic run flown; loop delay ≈ 0.5 s (2 samples).
- Twin validated (50 vs 55 % followed). **Bottleneck = recognising the user, not turning.** Clothes learning 50 → 82.6 % (twin,
  walk clip); crossing clip 62.7 → 64.7 %. Right/wrong-person check vs session-1 labels: was running at handoff (see `twin_25.11/`).

## Decisions
- Keep turn 0.3 + search turn; predictor OFF (no gain); 640 px; YOLO11n default in flights (11m candidate).
- **Never bypass DJI battery protection / never open the firmware** (safety + lab property). Land at 30 %.
- Every step that moves the drone: ask the user first (SPACE in session.py = permission).
- Milestones are named by DATE, not M-numbers. Short answers (~5–10 lines).

## Open / next
1. Accuracy sweep on the twin with labels: YOLO11m, turban colour range for indoor lamps, clothes threshold 0.40/0.50, 800 px.
2. Next flight: AUTO_TESTS with clothes learning → confirm ≥ 80 % followed. Then DELAY TEST ×10 + TURN SPEED → calibrate twin.
3. Crossing clips with 3 people → CVAT labels → ID swaps, IDF1/HOTA, tracker comparison (work plan).
4. Final 7.12 summary + demo video + questions for Gabi. Requirement trace table.
5. Later: backlight self-correction (notebook 13), from-above comparison (Gabi), obstacles training, RRT* sim (11.1).
Side notes: video size change → new file part (fixed); session.py ignores SPACE in auto; FORCE LAND table test passed (real test
needs a hover); Google Drive for Desktop not installed (no auto cloud copy); battery saver + stop-on-landing in follow script.
