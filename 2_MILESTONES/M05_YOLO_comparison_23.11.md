# M05 - User detection (due Monday 23.11)

**Status 22.11: done.** Final results and the summary for Gabi: `4_DOCUMENTS/M05_summary_for_Gabi_23.11.pdf`.
Full table: `M05_data/results/full_comparison_22.11/`. Why / fixes: `M05_diagnosis_and_improvements_22.11.md`.

Full plan, who does what and when: `4_DOCUMENTS/M05_plan_final.pdf` (Word version to fill in: `.docx`).
Script: `1_CODE/m05.py` (run from 1_CODE, window from OPEN_TERMINAL_HERE.bat). Install once: `python -m pip install ultralytics` (Python 3.10-3.14).

## Data (no new filming)
Four clips from `3_EVIDENCE/2026-11-20`, about 1 frame per second, 152 frames:

| Clip | Who is in it | Frames |
|---|---|---|
| 161951_recording_test60.mp4 | the actor in the purple-red turban + others | 61 |
| 154848_connection_test_video.mp4 | the actor + others | 40 |
| 161825_recording_test30.mp4 | the actor + others | 31 |
| 154124_connection_test_video.mp4 | others only, no actor (false-alarm test) | 20 |

```
python m05.py extract "..\3_EVIDENCE\2026-11-20\161951_recording_test60.mp4" 25 "..\3_EVIDENCE\2026-11-20\154848_connection_test_video.mp4" 38 "..\3_EVIDENCE\2026-11-20\161825_recording_test30.mp4" 25 "..\3_EVIDENCE\2026-11-20\154124_connection_test_video.mp4" 75
python m05.py prelabel
```
Correct the suggested labels in Roboflow or makesense.ai, two classes: `user` (0, only the man in the turban) and `person` (1, everyone else). Export in YOLO format into `3_EVIDENCE/m05_user_detection/labels/`.

## The checks (normal light 1.0 and darkened copies 0.35)
**First each method alone:**

| Check | Command | Fills |
|---|---|---|
| C1 colour only | `python m05.py run colour` | Table B: colour only |
| C2 YOLO11n alone | `python m05.py run yolo11n` | Table A + Table B "YOLO11n only" (biggest person = guess) |
| C3 YOLOv12n alone | `python m05.py run yolo12n` | the same |
| C4 YOLO26n alone | `python m05.py run yolo26n` | the same |

**Then YOLO + colour (hybrid):** YOLO finds the people, the turban colour on the head picks the user, the same person is kept for up to 1 s if the colour is lost.

| Check | Command |
|---|---|
| H1 | `python m05.py run hybrid yolo11n` |
| H2 | `python m05.py run hybrid yolo12n` |
| H3 | `python m05.py run hybrid yolo26n` |

Speed (FPS) on one computer only: `python m05.py run` (everything). Demo: `python m05.py video "..\3_EVIDENCE\2026-11-20\161951_recording_test60.mp4" yolo26n.pt`.

## Tables
- **Table A (finding people):** detection rate = TP / (TP + FN), precision = TP / (TP + FP), a box is correct if IoU >= 0.5; FPS, ms/frame.
- **Table B (finding THE user):** user found %, wrong person %, false alarm % (frames without the actor), frames correct %.
- **Winner:** the fastest model with detection rate >= 90% at brightness 1.0; a tie goes to the better result at 0.35.

Formulas with worked examples: part 4 of the plan. Keep the AI log up to date.

Alternatives considered (to YOLO, to the colour marker, Crazyflie): `M05_engineering_considerations.md`.

## Which frames go into which table (decided 22.11)
- **user = the actor, always** (with or without the turban). In clip **154124 he is there without the turban**.
- **Table B (finding THE user: colour vs YOLO vs hybrid)** uses only frames where he wears the marker:
  folder `3_EVIDENCE/m05_user_detection/labels_marker` = all corrected labels **except** the 154124 files.
  Example: `python m05.py run colour ..\3_EVIDENCE\m05_user_detection\labels_marker`
  (the script skips frames that have no label file).
- **Extra row "user without marker"**: the same checks on `labels_nomarker` (only the 20 files from 154124).
- **Table A (finding people)** uses **all** corrected labels: folder `labels` (every person counts, turban or not).
- False alarms: frames with no actor at all (if Nimer's clips have some). If there are none, say so and drop that column.

