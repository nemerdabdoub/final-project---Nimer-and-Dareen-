# M05: Nimer's next steps (from Dareen, 22.11)

Labels: all 152 are in `M05_data/labels` and checked. Dareen's final Table B (C1 colour + H1-H3 hybrid) is done:
`M05_data/results/`. Now your part: **C2, C3, C4 (each YOLO alone) + the speed run**, then the winner call at 17:30.
You can paste each step to your Claude Code as written. Run everything from `1_CODE`.

## Step 1: get the latest (1 min)
```
git pull
```
You should see: `M05_data/labels` has 152 files and `M05_data/results` has Dareen's 5 CSVs.

## Step 2: copy the labels into place and make the folders (1 min)
Copy `M05_data/labels/*.txt` into `3_EVIDENCE/m05_user_detection/` as:
- `labels` = all 152 files (Table A: every person counts)
- `labels_marker` = all except the `154124_*` files = 132 files (Table B, same frames as Dareen's rows)

Also check that `3_EVIDENCE/m05_user_detection/frames` has the same 152 frames as `M05_data/frames`.
You should see: labels 152, labels_marker 132.

## Step 3: Table A, each YOLO alone on ALL labels (C2, C3, C4)
```
python m05.py run yolo11n ..\3_EVIDENCE\m05_user_detection\labels
python m05.py run yolo12n ..\3_EVIDENCE\m05_user_detection\labels
python m05.py run yolo26n ..\3_EVIDENCE\m05_user_detection\labels
```
After each run, copy its `m05_table_A_person_detection_<model>.csv` into `M05_data/results/`.
You should see per model, at 1.0 and 0.35: detection rate %, precision %. Target: detection rate >= 90% at 1.0.

## Step 4: Table B "YOLO only" rows on the SAME 132 frames as Dareen's rows
```
python m05.py run yolo11n ..\3_EVIDENCE\m05_user_detection\labels_marker
python m05.py run yolo12n ..\3_EVIDENCE\m05_user_detection\labels_marker
python m05.py run yolo26n ..\3_EVIDENCE\m05_user_detection\labels_marker
```
These overwrite the files of Step 3, so do Step 3's copying first. After each run, copy
`m05_table_B_finding_the_user_<model>.csv` into `M05_data/results/` (rename it to
`m05_table_B_finding_the_user_<model>_only.csv` so it is not confused with Dareen's hybrid files).
Expect: "wrong person" above 0 (the biggest person is not always the actor). That is the point: YOLO alone cannot
tell who the user is; Dareen's hybrid rows have 0% wrong person.

## Step 5: speed run, all models on your laptop (20-25 min, charger in, close other programs)
```
python m05.py run ..\3_EVIDENCE\m05_user_detection\labels
```
Copy only FPS and ms/frame into Table A (Dareen's ms/frame values are NOT the speed result; yours are).

## Step 6: save and push
Push `M05_data/results/` + a short entry in `UPDATES.md` + one line in `4_DOCUMENTS/mid_project_presentation_log.md`
(section 3) with the Table A numbers and FPS.

## Then (from the revised plan)
- **17:30 winner call together.** Rule: the fastest model with detection rate >= 90% at brightness 1.0; if close, the
  one that holds up better at 0.35. Dareen's hybrids are equal (73-74% found, 0% wrong), so Table A + speed decide.
- **18:00** Dareen makes the demo video with the winner. **18:30** you check it (3 lines: right / fails / why).
- **Mon 12:00** your one-page summary.

## Dareen's final Table B, for your summary (132 marker frames, brightness 1.0)
| Method | User found % | Wrong person % | False alarm % | Frames correct % |
|---|---|---|---|---|
| Colour only | 58.7 | 36.5 | 71.4 | 52.3 |
| Hybrid YOLO11n | 73.1 | 0 | 7.1 | 77.3 |
| Hybrid YOLOv12n | 73.1 | 0 | 7.1 | 77.3 |
| Hybrid YOLO26n | 74.0 | 0 | 7.1 | 78.0 |

Without the turban (154124): colour picks something else 100%, the hybrid picks nobody 100%.
The hybrid's 2 false alarms = a hand in front of the lens (154848 frames 00114, 00152).
