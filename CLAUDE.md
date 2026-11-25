# Project 3760 — autonomous DJI Neo drone that guides a user to a target

Team: Nimer Dabdoub and Dareen Jubran (TAU, B.Sc. final project 2026-27). Supervisor: Dr. Gabi Davidov.
Drone: DJI Neo, controlled from the PC by mirroring the DJI Fly app on an Android phone (Samsung S10) with scrcpy + ADB
(lab repo Penkov-D/DJI-Neo-to-PC). All drone control goes through `1_CODE/drone_interface.py`.

## Folder layout (one folder per laptop = this git repo)
- `1_CODE/` our scripts (run them from here; `OPEN_TERMINAL_HERE.bat` opens a terminal inside 1_CODE).
  Lab files (DJIneo.py, scrcpy.py, adb.exe, .dll, .jar) live here too but are NOT in git.
- `2_MILESTONES/` one how-to/status note per milestone.
- `3_EVIDENCE/<date>/` logs, videos, screenshots — on each laptop only, NOT in git (too big). Share M05 data through `M05_data/`.
- `4_DOCUMENTS/` plans. Current: `M05_plan_revised_22.11.pdf`; details: `M05_plan_final.pdf`.
- `5_LOGS/` Project_logs.xlsx (includes the AI log) — laptop only.
- `M05_data/` M05 frames, labels and result CSVs shared through git (small files only; never videos or *.pt).

## Status (22.11.2026)
- M02 drone acquired — done. M03 control from code — done (12.11 log `3_EVIDENCE/2026-11-12/190414_flight_test_log.txt`).
- M04 work plan — submitted on Moodle.
- **M05 user detection — due Monday 23.11 (meeting with Gabi).** Current plan: `4_DOCUMENTS/M05_plan_revised_22.11.pdf`
  (one plan, Python works on both laptops). Check details, tables and formulas: `4_DOCUMENTS/M05_plan_final.pdf`.
  Script: `1_CODE/m05.py`. Session notes: `2_MILESTONES/M05_session_notes_22.11_Dareen.md`.
  - **Done (22.11):** 152 frames, all labels corrected (`M05_data/labels`), Table A (C2-C4 + speed, Nimer), Table B
    (C1 + H1-H3, both laptops identical), no-marker row, fixes A (hand filter) + B (people > 1/4 height column) in `m05.py`,
    full comparison table (`M05_data/results/full_comparison_22.11/`), diagnosis + improvements
    (`2_MILESTONES/M05_diagnosis_and_improvements_22.11.md`), demo videos (YOLO11n, on Dareen's laptop), AI log lines (Dareen).
  - **Summary for Gabi:** `4_DOCUMENTS/M05_summary_for_Gabi_23.11.pdf` / `.docx` (5 pages).
  - **24.11 GPU re-selection (Nimer to confirm): switch to hybrid YOLO11m** — Dareen's (drone) laptop has an RTX 5050 that
    PyTorch was not using; GPU env `C:\Users\LOREN\venvs\gpu`. 12 detectors (YOLO, RT-DETR, RF-DETR) on 403 frames: YOLO11m
    89.6% frames correct, 1 wrong / 164, 0 false alarms; ~45 FPS on GPU. YOLO11n stays the CPU-only fallback.
    `2_MILESTONES/M05_reselection_GPU_12_detectors_24.11.md`. Trackers: BoT-SORT leads of 6 (`M06_tracker_grid_23.11.md`).
  - **Winner until 23.11:** YOLO11n + turban colour — most accurate (85.4% all, 96.2% people > 1/4 height)
    and fastest. Work-plan req. 1 (user in >= 90% of frames, lab): user detected 99%, identified by the turban 73% → M06 tracking closes the gap.
  - Open before the meeting: Nimer confirms the winner + reads the summary; Nimer's AI log line; the 12.11 moves
    video is not on Dareen's laptop (only the log) — find it (phone / Nimer).
- **New clips 22.11 (bikes, Med Faculty) tested:** hybrid 83/88 right (5 wrong = man in red shirt), 0 false alarms; YOLO-World/YOLOE
  checked for scooters/strollers = not usable as is. `2_MILESTONES/M05_newclips_bikes_openvocab_22.11.md`. Test set hand-labelled (Dareen, 23.11). **Final all-videos table (403 frames, hand labels): hybrid YOLO11n 1.8% wrong, 0 false alarms,
  87.8% correct, 96.2% detection at following distance → YOLO11n confirmed** (note §7).
- **25.11 (night):** paired test 11m vs 11n p = 0.016 (11m really better, +1.7 pts) → rule: 11m if >= 15 FPS live on battery,
  else 11n (decided on the field day). User score per box (identity, Gabi): AUC 0.914, turban + clothes colour 0.978 (Nimer's idea).
  `1_CODE/m06_follow.py` = BoT-SORT + sticky ID + FOLLOWING/UNSURE/LOST + yaw/forward controller, `--colour` (E = "this is me");
  red shirt can steal the lock with turban only. Field-day checklist `2_MILESTONES/M06_field_day_manual.md`; all to-dos,
  research and deep dives: `2_MILESTONES/PROJECT_NOTEBOOK_todo_research_25.11.md`.
- **25.11 field day:** first closed loop flown (yaw FOLLOWING 77-95%, all turns right way; distance stops at target), loop
  delay ≈ 0.5 s, camera tilt coded (`gimbal.py`), adb fix `run_with_adb.py`. Results `2_MILESTONES/M06_field_day_25.11.md`.
  Open: crossings / 60 s / from above clips, delay with 10 presses, live 11m check, prediction for the delay.
- **25.11 evening:** `AUTO_TESTS.bat` = self take-off → TURN/FOLLOW/SIDE/ORBIT → self landing (laptop speaks user commands,
  people-close safety, battery stop 30 %); full auto run flown (all turns right way, user followed 33–55 %). DIGITAL TWIN
  `1_CODE/twin.py` (validated 50 vs 55 %): recognition, not turning, is the bottleneck; clothes learning → 82.6 % (twin, to confirm
  in flight). No DJI battery-protection bypass (decided). Simple test names + protocol: `2_MILESTONES/M06_flight_test_protocol.md`.
  Next: charge, fly AUTO_TESTS with clothes learning; crossings / 60 s / from above clips; delay test ×10.
- M06 user tracking — due 7.12. Started 22.11: `1_CODE/m06_track.py` (YOLO11n + ByteTrack/BoT-SORT + turban, old-vs-new
  comparison, dry-run distance controller). New footage 22.11 (Med Faculty, bikes): `2_MILESTONES/filming_22.11_bikes_med_faculty.md`.

## M05 in short (details in the plan)
Data: four clips from `3_EVIDENCE/2026-11-20` (161951, 154848, 161825 with the actor in a purple-red turban; 154124 without him),
about 1 frame/s, 152 frames. Labels: Roboflow/makesense, classes `user` (0) and `person` (1).
Steps: `python m05.py extract ...` (command in the M05 note) → `python m05.py prelabel` → correct labels →
checks, first each method alone, then YOLO + colour:
- C1 `python m05.py run colour` · C2–C4 `run yolo11n` / `run yolo12n` / `run yolo26n` (YOLO alone)
- H1–H3 `run hybrid yolo11n` / `yolo12n` / `yolo26n` (YOLO finds people, turban colour on the head picks the user)
- speed for all on one computer: `python m05.py run` · demo: `python m05.py video <clip> <model>.pt`
- optional non-YOLO comparison: `run rtdetr-l` / `run hybrid rtdetr-l` (slow on CPU; see `2_MILESTONES/M05_engineering_considerations.md`)
Results go to `3_EVIDENCE/m05_user_detection/` (CSV tables A and B). Brightness 1.0 and 0.35 (low-light stand-in).
Frame sets (decided 22.11): user = the actor always; Table B on `labels_marker` (all except 154124, where he has no turban),
extra row on `labels_nomarker` (154124 only), Table A on all `labels`. Details at the end of the M05 note.

## Working rules for Claude in this repo
- **Act as a senior project advisor** (both partners asked for it): with every step add a short **"Advisor's view"**:
  why it matters, what comes next, the main risk, and what an examiner would ask. Follow `4_DOCUMENTS/ADVISOR_GUIDE.md`
  (map, 7-step method per milestone, engineering principles, M06 definition of done). Be honest when something is weak.
- **Stand out (both partners' goal until the final exam):** we are the third team on this topic with Gabi, so every
  step must show engineering the earlier teams did not: measured (not observed) results with baseline, data size and
  uncertainty; hold-out data; delay budget; safety states; requirement trace; decisions with trade-offs; AI use per
  block that both of us can explain. Follow `4_DOCUMENTS/STAND_OUT_STRATEGY.md` and name the stand-out angle in the Advisor's view.
- Explain steps simply, one at a time; say what the user should see at the end of each step.
- Python 3.14 is installed with ultralytics; the first import of torch can take 20–40 s — don't treat it as a hang.
- **Commit and push automatically**: after each finished change to files in git (code, notes, CLAUDE.md), do
  `git pull`, then `git add` the changed files, `git commit` with a short clear message, and `git push` to `main`,
  without waiting to be asked. Tell the user in one line what was pushed. Never force-push. If the pull shows a
  conflict, stop and explain it simply instead of pushing. **Never use `git stash`** (Nimer's rule): pull without
  stashing; if git refuses because a local change would be overwritten, commit that change first or tell the user.
  The Project updates panel (`tools/project-updates`) also auto-pulls and auto-pushes every 2 min, with the same rules.
- At the end of a work session, update the Status section of this file with what was done and push it.
- **Keep the partner and their Claude in sync** through `UPDATES.md` (in git, newest first):
  at the start of every session, `git pull`, read the newest entries in `UPDATES.md` and tell the user in a few lines
  what the partner changed; after every finished change, add a short dated entry there (who, what, results, what is
  open) in the same commit, then push. The push @mentions the partner on GitHub.
  Also keep the **"LATEST PUSHES" line at the very top of `UPDATES.md`** current (Nimer's rule): newest push first,
  "who time – what" for the last few pushes of both, then **Next:**; update it in every commit that adds an entry.
- **Mid-project presentation log**: every update that adds a result, number, decision, video/demo or problem solved
  also gets one dated line in the right section of `4_DOCUMENTS/mid_project_presentation_log.md` (same commit).
- Don't edit the same file the partner is editing; a push triggers `.github/workflows/notify-partner.yml`, which
  @mentions the other partner on GitHub.
- Never commit 3_EVIDENCE, videos, model files (*.pt), lab binaries or 5_LOGS (see .gitignore).
- Safety for any flight: phone in hand, DJI Fly in Manual Control, big open space, battery > 40%, Ctrl+C = stop then land by hand.
