# Mid-semester presentation: running log

Everything we may want to show in the mid-semester presentation, collected as it happens.
**Rule (both of us and both Claudes):** every update that adds a result, a decision, a number, a video or a problem
gets one line in the right section below, with the date and where the proof is. Newest at the bottom of each section.
Presentation date: _to fill in_.

## 1. The project in one slide
- Goal: an autonomous drone that finds a user and guides them to a target (Project 3760, TAU, supervisor Dr. Gabi Davidov).
- Hardware: DJI Neo, controlled from a laptop by mirroring the DJI Fly app on an Android phone (Samsung S10, scrcpy + ADB,
  lab repo Penkov-D/DJI-Neo-to-PC). All control goes through one file, `1_CODE/drone_interface.py`.

## 2. Milestones and status
- M02 drone acquired, stable video for 10 min: done 19.10.
- M03 control from code: done. 7.11 take-off, hover and two-step landing from code; 12.11 six moves in flight
  (`flight_test.py moves 0.3 0.5`), landed from code about 7 s after the landing started, battery 69% → 66%.
  Proof: `3_EVIDENCE/2026-11-12/190414_flight_test_log.txt` + video.
- M04 work plan: submitted on Moodle 12.11.
- M05 user detection: in progress, due 23.11 (see section 4).
- M06 user tracking: due 7.12, not started.

## 3. Results and numbers
- 22.11 M05 test run on Nimer's laptop (CPU, stand-in labels, NOT final): speed YOLO11n 26 FPS (38 ms), YOLO26n 22 FPS
  (46 ms), YOLOv12n 16 FPS (62 ms). Proof: `3_EVIDENCE/m05_user_detection/m05_table_*_PRELIM_suggested_labels.csv`.
- 22.11 RT-DETR (non-YOLO) test on stand-in labels: about 0.9 FPS vs about 15 FPS for YOLO26n (15-20x slower). Source: Dareen.

## 4. Method and decisions (the "why")
- 22.11 M05 data: 4 clips from 20.11 (3 with the actor in a purple-red turban, 1 without, for false alarms), about
  1 frame/s, 152 frames, classes `user` and `person`, brightness 1.0 and 0.35 (low-light stand-in).
- 22.11 Compared: colour only, YOLO11n / YOLOv12n / YOLO26n alone, and hybrid (YOLO finds people, turban colour picks the user).
- 22.11 Winner rule: fastest model with detection rate ≥ 90% at brightness 1.0; a tie goes to the better result at 0.35.
- 22.11 Detector choice: YOLO over RT-DETR, MobileNet-SSD, MediaPipe, HOG, Faster R-CNN (best speed/accuracy on a laptop
  without a GPU). Source: `2_MILESTONES/M05_engineering_considerations.md`.
- 22.11 Platform: Crazyflie considered and not chosen (no camera without the AI-deck, 40 g payload, 320×320 greyscale).
- 22.11 Next ideas for M06: tracking (ByteTrack / BoT-SORT + Kalman), printed ArUco marker (also gives distance).

## 5. Demos and visuals we can show
- 12.11 flight video of the six moves (M03).
- 22.11 `3_EVIDENCE/m05_user_detection/M05_frames.mp4` and `M05_frames_suggested_boxes.mp4` (152 frames, 76 s, boxes drawn).

## 6. Problems we hit and how we solved them
- 7.11 Small stick pushes (0.1-0.2 for 0.4-0.5 s) moved the Neo only a few cm → raised to 0.3 for 0.5 s (cap 0.4).
- 22.11 Colour only gives many false alarms (a red mural in the scene) → hybrid: colour only counts on a person's head.

## 7. Teamwork and tools
- Shared GitHub repo; a GitHub action @mentions the partner on every push; `UPDATES.md` log; a live "Project updates"
  panel in VS Code (Claude Code plugin); M05 data shared in `M05_data/`; work split equally by method.

## 8. Next steps (to the end of the semester)
- M05: correct labels (both halves) → real tables A and B → winner → demo video → summary for Gabi.
- M06 user tracking by 7.12.
