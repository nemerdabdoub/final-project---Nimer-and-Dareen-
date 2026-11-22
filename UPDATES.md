# Updates log (newest first)

Shared between Nimer and Dareen and both Claude Code sessions. Every change pushed to GitHub gets one entry here.
Claude: read the newest entries at the start of each session and tell the user what the partner changed.

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
