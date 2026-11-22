# Updates log (newest first)

Shared between Nimer and Dareen and both Claude Code sessions. Every change pushed to GitHub gets one entry here.
Claude: read the newest entries at the start of each session and tell the user what the partner changed.

## 22.11.2026 ~06:15, Nimer: THE COMPARISON (colour only vs YOLO only vs YOLO + colour), real labels
- Ran C1 + H1-H3 on the full `labels_marker` (132) and `labels_nomarker` (20) too, so **Dareen does not need to re-run
  them** (check the numbers if you like). CSVs + 2 screenshots in `M05_data/results/nimer_22.11/`.
- **Table B, turban frames (132; 104 with the user, 28 without), brightness 1.0 / 0.35:**

  | Method | User found % | Wrong person % | False alarm % | Frames correct % |
  |---|---|---|---|---|
  | colour only | 58.7 / 56.7 | 36.5 / 37.5 | 71.4 / 71.4 | 52.3 / 50.8 |
  | YOLO11n only (biggest person) | 62.5 / 62.5 | 36.5 / 36.5 | 67.9 / 64.3 | 56.1 / 56.8 |
  | YOLOv12n only | 62.5 / 61.5 | 35.6 / 36.5 | 71.4 / 64.3 | 55.3 / 56.1 |
  | YOLO26n only | 61.5 / 62.5 | 36.5 / 35.6 | 67.9 / 64.3 | 55.3 / 56.8 |
  | **hybrid YOLO11n + colour** | **73.1 / 74.0** | **0 / 0** | **7.1 / 7.1** | **77.3 / 78.0** |
  | hybrid YOLOv12n + colour | 73.1 / 73.1 | 0 / 0 | 7.1 / 7.1 | 77.3 / 77.3 |
  | hybrid YOLO26n + colour | 74.0 / 73.1 | 0 / 0 | 7.1 / 7.1 | 78.0 / 77.3 |

- **Extra row, actor WITHOUT the turban (154124, 20 frames):** colour only finds him 0% (wrong 100%); hybrid 0% found
  but 0% wrong (it picks nobody, as it should); YOLO only 90-95% (he is the biggest person there).
- **Read-out:** alone, each method is wrong about 1 in 3 times; combined, the hybrid **never picks the wrong person**
  and false alarms drop from ~70% to 7% (2 of 28 frames). Its misses are frames where it picks nobody (turban not seen).
- Screenshots: colour only picks a purple-red sofa, the hybrid picks the actor (frames 161951 _01000 and _01450).
- ms/frame in these runs is not the speed result (use the speed run).

## 22.11.2026 ~05:45, Nimer: 71 labels + C2-C4 + speed run (REAL labels, all 152)
- `M05_data/labels/`: Nimer's 71 corrected (154848 + 161825; 6 empty files = nobody in frame). Now 152/152.
- `M05_data/results/nimer_22.11/`: C2-C4 on all labels (Table A), on `labels_marker` (Table B "YOLO only"), speed run.
- **Table A, all 152 corrected frames:**

  | Model | Detection rate at 1.0 | Detection rate at 0.35 | Precision at 1.0 | Precision at 0.35 |
  |---|---:|---:|---:|---:|
  | YOLO11n | 85.4% | 84.8% | 94.1% | 95.4% |
  | YOLOv12n | 82.9% | 81.9% | 94.2% | 97.4% |
  | YOLO26n | 82.5% | 82.9% | 95.2% | 96.3% |

  **No model reaches the 90% detection-rate target.**
- **Speed run (Nimer's laptop, CPU, one computer):** YOLO11n 21.0 FPS (48 ms), YOLO26n 19.2 FPS (52 ms),
  YOLOv12n 16.3 FPS (61 ms). Colour only 13 ms/frame.
- **Table B "YOLO only" on `labels_marker` (132 frames, 104 with the user), 1.0:** user found 61.5-62.5%,
  wrong person 35.6-36.5% for all three.
- **For the 17:30 call:** the winner rule (fastest with ≥ 90%) picks nobody. YOLO11n is both the most accurate and
  the fastest, so it wins on both counts; we report that the 90% target was not met in the lab, and why.
- **Dareen:** re-run C1 + H1-H3 on the full `labels_marker` (132) and `labels_nomarker` (20) now that all labels are in.

## 22.11.2026, Nimer: label_tool.py, faster than makesense.ai
- New `1_CODE/label_tool.py`: `python label_tool.py nimer` / `python label_tool.py dareen` opens each frame with the
  suggested boxes and saves corrected YOLO labels straight into `M05_data/labels/` (no upload/export). Click = select,
  drag = new box, right-click = delete, u = user, p = person, n/b = next/back. Continues where you stopped.
- **Dareen:** optional, makesense.ai still works the same; both write the same files.

## 22.11.2026, Nimer: it is the MID-PROJECT presentation (not mid-semester)
- Renamed to `4_DOCUMENTS/mid_project_presentation_log.md`; wording fixed in CLAUDE.md and here.

## 22.11.2026, Dareen: C1 + H1-H3 on her half (PRELIMINARY, 61 marker frames of 161951)
- Folders on her laptop: `labels_marker` (61, all except 154124) and `labels_nomarker` (20, 154124 only).
- Table B on `labels_marker`, brightness 1.0 / 0.35 (56 frames with the actor):
  colour only: user found 41.1 / 39.3%, **wrong person 55.4%** (the red mural), frames correct 45.9 / 44.3%.
  hybrid yolo11n: 78.6 / 80.4%, wrong 0%, correct 80.3 / 82.0%. hybrid yolo12n and yolo26n: 78.6%, wrong 0%, correct 80.3%.
  The hybrid never picks the wrong person; its misses are frames where it picks nobody (turban not seen on a head).
- ms/frame here is not the speed result (Nimer's speed run on one computer is).
- Open: re-run the same commands on the full `labels_marker` when Nimer's 71 labels arrive; extra row on `labels_nomarker`.

## 22.11.2026, Dareen: her 81 corrected labels shared
- `M05_data/labels/`: 81 corrected files (161951: 61, actor = user in 56, 2 empty frames; 154124: 20, actor = user
  without the turban in all 20). Checked: only classes 0/1, values 0-1, at most one user per frame.
- **Nimer:** add your 71 corrected files to the same folder and push. Then both copy `M05_data/labels` into
  `3_EVIDENCE/m05_user_detection/labels` before running checks.

## 22.11.2026 04:55, Dareen (with Claude in the Claude app)
- Dareen's 81 labels corrected (makesense.ai): `3_EVIDENCE/m05_user_detection/labels` on her laptop (2 empty files added
  for frames with nobody). In clip 154124 the actor is there **without the turban**, labelled as user.
- Decision on frame sets: Table B on `labels_marker` (all except 154124), extra row "without marker" on `labels_nomarker`,
  Table A on all labels. Written in the M05 note and CLAUDE.md.

## 22.11.2026, Nimer: presentation focus = detecting the SAME person
- `4_DOCUMENTS/mid_project_presentation_log.md`: new ★ main-focus section on finding the same person every frame and
  the characteristics used (turban hue 170-179 on the head only, ≥3% and 2× the background, 1 s IoU fallback),
  the "wrong person %" metric, where it fails, and M06 ideas (tracking IDs, re-ID, ArUco). Please keep it the lead topic.

## 22.11.2026, Nimer: mid-project presentation log
- New `4_DOCUMENTS/mid_project_presentation_log.md`, seeded with M02-M05 status, numbers, decisions, demos, problems.
- New rule in CLAUDE.md: every result, number, decision, demo or problem solved also gets a line there.
- M05 frame videos made (on Nimer's laptop, not in git): `3_EVIDENCE/m05_user_detection/M05_frames.mp4` and
  `M05_frames_suggested_boxes.mp4`.

## 22.11.2026, Dareen: M05_data shared in git
- New `M05_data/`: `frames/` (152), `to_label_Dareen/` (81 frames + suggested labels + `labels.txt`),
  `to_label_Nimer/` (71 frames + suggested labels + `labels.txt`), empty `labels/` and `results/`, and a README
  with the makesense.ai steps. About 44 MB (the to_label folders repeat the frames so each half uploads on its own).
- Also on Dareen's laptop: yolo11n / yolo12n / yolo26n downloaded and tested (not in git).
- **Nimer:** `git pull`, then label `M05_data/to_label_Nimer` and put your corrected `.txt` files in `M05_data/labels/`.
- Open: both halves of the labels by Sun 14:00.

## 22.11.2026 03:40, Dareen (with Claude in the Claude app)
- `4_DOCUMENTS/M05_plan_revised_22.11.pdf/.docx`: the plan from now to Monday. One plan (Python on both laptops),
  data shared in `M05_data/`, model checks split equally by method: Dareen C1 colour + H1, H2, H3 (YOLO + colour);
  Nimer C2, C3, C4 (YOLO alone) + speed run. Labels by Sun 14:00, winner together Sun 17:30. Aims-coverage table added.
- `2_MILESTONES/M05_engineering_considerations.md`: alternatives to YOLO (RT-DETR, MobileNet-SSD, MediaPipe, HOG,
  Faster R-CNN), to the colour marker (ArUco, tracking, re-ID), and Crazyflie vs DJI Neo. In the Monday order as item 5.
- `1_CODE/m05.py`: optional non-YOLO check `python m05.py run rtdetr-l` / `run hybrid rtdetr-l` (not part of the speed
  run). Test on stand-in labels: about 0.9 FPS vs about 15 FPS for YOLO26n, so roughly 15-20x slower.
- Open: label correction (both halves) is the next step for both of us.

## 22.11.2026 03:35, Nimer: live "Project updates" panel for Claude Code
- New `tools/project-updates/` + `.claude-plugin/marketplace.json`: a panel beside the Claude chat in VS Code showing
  sync with GitHub, uncommitted files, and the last 20 pushes by both of us (click a file to open it).
- **Dareen, to install:** in the Claude chat type
  `/plugin install project-updates --marketplace nemerdabdoub/final-project---Nimer-and-Dareen-`, then `/updates`.

## 22.11.2026, Nimer's laptop (with Claude Code)
- Nimer's laptop set up: Python 3.14.10, ultralytics 8.4.216, torch 2.15.0 (CPU), OpenCV 5.1.0, av, keyboard.
  Lab files copied into `1_CODE`. Dareen's zip copied in: `3_EVIDENCE`, `5_LOGS`, the four `.pt` models (not in git).
- Test run of all M05 checks (`python m05.py run ..\3_EVIDENCE\m05_user_detection\labels_suggested`): all 7 checks run
  without errors. **Not the real results**: scored against the uncorrected suggested labels, which yolo11l made, so the
  accuracy is too high. Files: `3_EVIDENCE/m05_user_detection/m05_table_*_PRELIM_suggested_labels.csv`.
  - Speed (real, Nimer's laptop, CPU): YOLO11n 26 FPS (38 ms), YOLO26n 22 FPS (46 ms), YOLOv12n 16 FPS (62 ms).
  - Test accuracy at brightness 1.0: person detection 92.6-95.4% for all three; finding the user: colour only 69%
    (82% false alarms), YOLO alone 58%, hybrid 96-97% with 0 false alarms.
- Still open for M05: Nimer corrects 71 frames (`to_label_Nimer`), Dareen corrects 81. All 152 corrected `.txt`
  files go into `3_EVIDENCE/m05_user_detection/labels/`, then `python m05.py run` gives the real tables.
