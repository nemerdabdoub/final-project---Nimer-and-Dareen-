# Project 3760 — Autonomous drone that guides a user to a target

Nimer Dabdoub & Dareen Jubran · Supervisor: Gabi · Drone: DJI Neo (controlled through the DJI Fly app on an Android phone)

## Status (22.11.2026)
| Milestone | Due | Status |
|---|---|---|
| M02 Drone acquired (stable video 10 min) | 19.10 | Done |
| M03 Control from code (take-off, 6 moves, landing) | 9.11 | Done in flight 12.11 (`flight_test.py moves 0.3 0.5`) |
| M04 Work plan on Moodle | 12.11 | Done (submitted) |
| M05 User detection: YOLO11 / YOLOv12 / YOLO26 vs colour marker vs YOLO + colour | 23.11 | In progress — `m05.py`, plan in `4_DOCUMENTS/M05_plan_final.pdf` |
| M06 User tracking | 7.12 | Not started |

## Folders
- `1_CODE/` — our code (see below)
- `2_MILESTONES/` — one how-to file per milestone
- `4_DOCUMENTS/` — plans and documents (current: `M05_plan_revised_22.11.pdf`; details: `M05_plan_final.pdf` / `.docx`; older: `Project_3493_Plan_until_Gabi_23.11.pdf`)
- `3_EVIDENCE/` (logs, videos, screenshots) stays on the laptop and is **not** in git (too big)

## Setup
1. Python 3 + `pip install opencv-python numpy ultralytics`
2. Copy the lab's files from [Penkov-D/DJI-Neo-to-PC](https://github.com/Penkov-D/DJI-Neo-to-PC) into `1_CODE/`:
   `DJIneo.py`, `scrcpy.py`, `scrcpy-server-v3.3.1.jar`, `adb.exe` and the `.dll` files (not committed: third-party code and binaries).
3. `settings.txt` is the screen map for our phone (Samsung S10, 1080×2280).

## Our files in `1_CODE/`
| File | What it does |
|---|---|
| `drone_interface.py` | One class `Drone`: takeoff, land (two-step, checks the screen), send_speeds, get_frame, battery from the app's ring. Changing the drone = changing this file only |
| `flight_test.py` | `dry` / `hover` / `cycle` / `moves` / `land` / `battery` — flight tests with logs |
| `connection_test.py` | Video link stability (FPS, worst gap, drops) |
| `latency_test.py` | Camera frame rate and end-to-end video delay (stopwatch method) |
| `m05.py` | **M05, used by the plan.** `extract` frames, `prelabel` (suggested labels), `run colour` / `run yolo11n` (YOLO alone) / `run hybrid yolo11n` (YOLO + turban colour), `video` demo. Results in `3_EVIDENCE/m05_user_detection/` |
| `record_video.py` | Records the drone camera to `3_EVIDENCE/<date>/<time>_recording_<label>.mp4` (`python record_video.py <minutes> <label>`, 0 = until Esc) |
| `m05_yolo_compare.py` | Earlier M05 version (orange/red marker). Kept for reference; the plan uses `m05.py` |
| `paths.py` | Saves results to `3_EVIDENCE/<date>/` |

## Notifications
On every push, the action `.github/workflows/notify-partner.yml` comments on the commit and @mentions the other partner, so GitHub notifies them (app + email). Install the GitHub app and turn on notifications for @mentions.

## Safety
Phone in hand, DJI Fly in Manual Control (never press START in Follow mode). Ctrl+C = sticks released, the drone hovers → land by hand. Big open space, battery above 40%.
