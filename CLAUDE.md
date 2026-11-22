# Project 3760 — autonomous DJI Neo drone that guides a user to a target

Team: Nimer Dabdoub and Dareen Jubran (TAU, B.Sc. final project 2026-27). Supervisor: Dr. Gabi Davidov.
Drone: DJI Neo, controlled from the PC by mirroring the DJI Fly app on an Android phone (Samsung S10) with scrcpy + ADB
(lab repo Penkov-D/DJI-Neo-to-PC). All drone control goes through `1_CODE/drone_interface.py`.

## Folder layout (one folder per laptop = this git repo)
- `1_CODE/` our scripts (run them from here; `OPEN_TERMINAL_HERE.bat` opens a terminal inside 1_CODE).
  Lab files (DJIneo.py, scrcpy.py, adb.exe, .dll, .jar) live here too but are NOT in git.
- `2_MILESTONES/` one how-to/status note per milestone.
- `3_EVIDENCE/<date>/` logs, videos, screenshots — on each laptop only, NOT in git (too big). Share via Drive.
- `4_DOCUMENTS/` plans. Current: `M05_plan_final.pdf` / `.docx`.
- `5_LOGS/` Project_logs.xlsx (includes the AI log) — laptop only.

## Status (22.11.2026)
- M02 drone acquired — done. M03 control from code — done (12.11 log `3_EVIDENCE/2026-11-12/190414_flight_test_log.txt`).
- M04 work plan — submitted on Moodle.
- **M05 user detection — due Monday 23.11 (meeting with Gabi).** Follow `4_DOCUMENTS/M05_plan_final.pdf` and
  `2_MILESTONES/M05_YOLO_comparison_23.11.md`. Script: `1_CODE/m05.py`.
- M06 user tracking — due 7.12, not started.

## M05 in short (details in the plan)
Data: four clips from `3_EVIDENCE/2026-11-20` (161951, 154848, 161825 with the actor in a purple-red turban; 154124 without him),
about 1 frame/s, 152 frames. Labels: Roboflow/makesense, classes `user` (0) and `person` (1).
Steps: `python m05.py extract ...` (command in the M05 note) → `python m05.py prelabel` → correct labels →
checks, first each method alone, then YOLO + colour:
- C1 `python m05.py run colour` · C2–C4 `run yolo11n` / `run yolo12n` / `run yolo26n` (YOLO alone)
- H1–H3 `run hybrid yolo11n` / `yolo12n` / `yolo26n` (YOLO finds people, turban colour on the head picks the user)
- speed for all on one computer: `python m05.py run` · demo: `python m05.py video <clip> <model>.pt`
Results go to `3_EVIDENCE/m05_user_detection/` (CSV tables A and B). Brightness 1.0 and 0.35 (low-light stand-in).

## Working rules for Claude in this repo
- Explain steps simply, one at a time; say what the user should see at the end of each step.
- Python 3.14 is installed with ultralytics; the first import of torch can take 20–40 s — don't treat it as a hang.
- **Commit and push automatically**: after each finished change to files in git (code, notes, CLAUDE.md), do
  `git pull`, then `git add` the changed files, `git commit` with a short clear message, and `git push` to `main`,
  without waiting to be asked. Tell the user in one line what was pushed. Never force-push. If the pull shows a
  conflict, stop and explain it simply instead of pushing.
- At the end of a work session, update the Status section of this file with what was done and push it.
- Don't edit the same file the partner is editing; a push triggers `.github/workflows/notify-partner.yml`, which
  @mentions the other partner on GitHub.
- Never commit 3_EVIDENCE, videos, model files (*.pt), lab binaries or 5_LOGS (see .gitignore).
- Safety for any flight: phone in hand, DJI Fly in Manual Control, big open space, battery > 40%, Ctrl+C = stop then land by hand.
