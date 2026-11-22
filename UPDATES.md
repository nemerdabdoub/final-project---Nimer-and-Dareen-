# Updates log (newest first)
**LATEST PUSHES (22.11, 07:30):** Nimer 07:27 – his half of the training labels DONE (173 frames, `M05_data/train/labels`) ·
Dareen 07:12 – classroom clip added to training (335 frames) · Dareen 07:07 – fine-tuning started (`m05_finetune.py`) ·
Nimer 06:47 – one-page summary PDF `4_DOCUMENTS/M05_summary_23.11.pdf` + `.gitattributes` · Dareen 06:28–06:44 – her
summary for Gabi (docx + pdf) and demo boxes tagged USER / person. **Next:** Dareen labels her half → `train` → test on the 152.
**Two summaries exist** (Dareen's 06:28 and Nimer's PDF): pick one together before Mon 12:00.

Shared between Nimer and Dareen and both Claude Code sessions. Every change pushed to GitHub gets one entry here.
Claude: read the newest entries at the start of each session and tell the user what the partner changed.

## 22.11.2026, Dareen: her 162 training labels done → all 335 training labels in
- Dareen's 162 (162603, 160733, 30 classroom): 217 people boxes, 35 empty frames, no bad lines; spot check of 6 frames
  OK (the portrait on the wall left unboxed, far and edge-cut people boxed). Nimer's 173 checked too: 149 boxes,
  74 empty, no bad lines.
- Next: `python m05_finetune.py train` (Dareen's laptop), then the full table + the 154848 demo with the new model.

## 22.11.2026, Dareen: classroom drone clip added to the training frames (both halves)
- Added `2026-10-20/1621_drone_view_classroom_flight_REALTIME.mp4` (drone camera, another room, people in ~1/3):
  60 frames, every other second to each of us → **Nimer now 173 frames (30 classroom), Dareen 162 (30 classroom)**,
  335 in total. Same command: `python m05_finetune.py label nimer` after `git pull`.
- Older 7.11 phone videos NOT used (phone camera in portrait, not the drone's view); 20.10 flight 3 has nobody.

## 22.11.2026, Nimer: my half of the TRAINING labels is done
- `M05_data/train/labels/`: all 173 frames of `to_label_Nimer` (152950, 153832, 161703, 161723); checked: classes 0/1 only,
  values 0-1. 149 boxes (52 user, 97 person) vs 161 suggested; 74 empty frames; 53 frames changed, ~15 wrong boxes
  removed (portrait / statues), ~3 people added.
- **Dareen:** when your half is in, `python m05_finetune.py train`, then test `yolo11n_drone.pt` on the 152 test frames.

## 22.11.2026, Dareen: FINE-TUNING YOLO11n started — training frames ready to label (your half: 143 frames)
- Why: at the end of the 154848 demo YOLO boxes the framed portrait on the wall as "person" at confidence 0.50-0.69, so a
  higher confidence cannot remove it without losing real people (0.4 → detection 82.5%). Only teaching the model fixes
  it, and the same YOLO11n keeps the same FPS while (hopefully) also finding more small people → aim: 90%+ at full speed.
- Training data ONLY from the 6 unused 20.11 clips (152950, 153832, 160733, 161703, 161723, 162603): 275 frames,
  1 per second. The 152 test frames stay test-only, so the comparison stays fair.
- New `1_CODE/m05_finetune.py`: `extract` / `prelabel` (done) / `label dareen|nimer` (your label_tool, pointed at
  `M05_data/train/`, file not changed) / `train` (→ `1_CODE/yolo11n_drone.pt`, not in git).
- **Nimer: `git pull`, then `python m05_finetune.py label nimer`** (143 frames: 152950, 153832, 161703, 161723).
  Dareen: `label dareen` (132 frames: 162603, 160733). Saved to `M05_data/train/labels/` → push.
- **Rule for training:** box EVERY real person (user/person both fine); NO box on the portrait, statues, mural, hands,
  app buttons — empty is what teaches "not a person". Many frames have nobody: just press n.
- Only 140 suggested people boxes in 275 frames → few people to learn from; older videos mostly do not help (see below).
  The real fix for more data is the new filming session (many people, following distance).

## 22.11.2026, Dareen: demo videos now label every box (USER / person + confidence)
- `m05.py video`: every box gets a tag — green "USER 0.94" (yellow "USER (kept)" for the fallback), blue "person 0.81"
  = YOLO's class + confidence. Detection and user choice unchanged (same percentages as before).
- All 4 demo videos re-made on Dareen's laptop (161951 + 154848, at 0.25 and 0.4). Still with labels:
  `M05_data/results/demo_yolo11n_22.11/demo_with_labels_user_and_person.jpg`. Pull before you make a video.

## 22.11.2026, Dareen: cleaner demo at confidence 0.4 (statue boxes) + why the demo has mistakes
- The demo is YOLO11n's raw output; our corrected labels only score it, they do not train it → statues / missed far
  people in the video are the Table A mistakes (17 wrong boxes, 46 missed).
- `m05.py video VIDEO MODEL [CONF]`: new optional confidence (tables stay at 0.25). At 0.4: 17 → 3 wrong boxes, 46 → 55
  missed (detection 82.5%, precision 98.9%). Videos `demo_*_yolo11n_conf0.4.mp4` on Dareen's laptop (161951: colour 69%,
  fallback 7%, none 24%; 154848: 45 / 6 / 49%). Example of what 0.4 removes (a duplicate box, but also a real seated man):
  `M05_data/results/demo_yolo11n_22.11/conf_0.25_vs_0.4_what_is_removed.jpg`.
- Proposal for Monday: show the 0.25 demo (same setting as the tables) and say the blue mistakes are counted in Table A;
  keep the 0.4 version as a backup if Gabi asks about the statue boxes.

## 22.11.2026, Dareen: SUMMARY FOR GABI + demo re-made + loose ends
- **Nimer: please read `4_DOCUMENTS/M05_summary_for_Gabi_23.11.pdf`** (5 pages; `.docx` to edit). It covers: result in
  one paragraph, M03 closed, data + method + hybrid design, Table A + Table B (one laptop), one line per check (C1-C5),
  winner, 2 pictures, where it fails + fixes, tried toward 90%, alternatives, lessons, M06, 4 questions for Gabi.
  It took over the one-page summary from your list — change anything you want.
- **Winner (proposed): YOLO11n + turban colour.** Please confirm, or reply with your choice.
- Demo videos re-made with the hand filter (on Dareen's laptop, not in git): 161951 (colour 70%, fallback 8%,
  none 22%) and 154848 (46% / 9% / 45%; the actor is out of the picture in much of it). Dareen will send you the video.
- AI log: Dareen's 4 lines added in `5_LOGS/Project_logs.xlsx` (laptop only). **Add yours too.**
- Open: the 12.11 moves video is not on Dareen's laptop (only the log) — do you have it? CLAUDE.md status updated.

## 22.11.2026, Nimer: ONE-PAGE M05 SUMMARY (PDF) for Gabi
- **Dareen: please read `4_DOCUMENTS/M05_summary_23.11.pdf`** (one A4 page, plan part 7): goal + M03 closed, Table A
  (your one-laptop full table), Table B with the hand filter, winner sentence (YOLO11n inside the hybrid), the 2
  screenshots, design, M06, limits, the 3 questions. Tell me (or your Claude) anything to change before Mon 12:00.

## 22.11.2026 ~06:40, Nimer: hand filter (Dareen's fix A) tested on Nimer's laptop + 2% threshold
- Same result as Dareen with the filter at the 3% threshold: false alarm **7.1% → 0%**, found 73-74%, wrong 0%,
  frames correct 78.8-79.5%.
- **Filter + head threshold 2%** (turban frames, 132): found **76-78%** (was 73-74%), wrong **0%**, false alarm **0%**
  (without the filter, 2% gave 10.7% false alarms), frames correct 81-83%. No turban (20): finds him in 1 frame (5%), 0% wrong.
- So the filter makes the 2% threshold safe on our frames. **Not changed in m05.py** (still 3%): the threshold was
  picked on the same frames we test on, so 2% = "promising, confirm on new clips". CSVs: `M05_data/results/nimer_22.11/*HANDFILTER*`.

## 22.11.2026, Dareen: ONE full comparison table (all methods, accuracy + speed + CPU, one laptop)
- New `1_CODE/m05_full_table.py` → `M05_data/results/full_comparison_22.11/m05_full_comparison.md/.csv`: colour only,
  YOLO11n / v12n / 26n alone, and hybrid with each, at 1.0 and 0.35, with detection (all / people > 1/4 height),
  precision, user found, wrong person, false alarm, frames correct, FPS, ms/frame, CPU % and cores used.
- Dareen's laptop (i7-13650HX, 20 logical cores, CPU only), brightness 1.0:
  colour only 130 FPS, 4% CPU (1 core) but 37% wrong person; YOLO alone 29-36 FPS, ~40% CPU (8 cores), 36% wrong person;
  **hybrid YOLO11n 31 FPS, ~40% CPU, 96% detection of big people, 0% wrong person, 0% false alarm, 79% frames correct.**
  Hybrid costs ~5 ms/frame more than YOLO alone. YOLOv12n is the slowest (24 FPS hybrid).
- Speeds differ from Nimer's laptop (his YOLO11n 21 FPS); compare models within one laptop only.

## 22.11.2026, Dareen: fixes A + B done in m05.py (re-run, pushed)
- **A (hybrid ignores "people" that fill the frame = a hand at the lens):** false alarm 7.1% → **0%**; found unchanged
  73-74%, wrong 0%, frames correct → 79-80%. Safe: the actor is at most 22% wide in our labels, the hand boxes 75-84%.
- **B (Table A: new last column, people taller than 1/4 of the frame):** YOLO11n **96.2%**, YOLOv12n 93.3%, YOLO26n 92.5%
  at 1.0 → all pass 90% for following distance. Old column unchanged (85.4 / 82.9 / 82.5%), matches your run.
- CSVs: `M05_data/results/fixes_A_B_22.11/`. `m05.py` changed (new constants `MAX_USER_W/H`, `BIG_PERSON`): **pull before
  you run it.** The demo video was made before fix A (only hand frames would differ).
- Winner proposal stays YOLO11n (best on all columns and fastest).

## 22.11.2026, Dareen: what to change, ranked from easiest to hardest
- **Nimer: read the new section "What we would do differently, from easiest to hardest" in
  `2_MILESTONES/M05_diagnosis_and_improvements_22.11.md`** — each item says what exactly to do and what to expect.
- Very easy (code, ~30 min): A ignore boxes that fill the frame (removes the 2 hand false alarms); B extra Table A row
  for people > 1/4 of the frame (~95%). Easy (one filming session): C record on the drone (built-in storage, no SD card),
  D film at 3-6 m, E 5 frames/s, F tune on old clips / test on new. Medium: G unique marker colour, H ArUco, I real low light.
  Hard: J fine-tune YOLO.
- Proposal: A + B before the meeting; C-F as one session next week; ask Gabi about G or H. Your opinion?

## 22.11.2026, Dareen: demo video done + tests toward 90%
- **Demo (C5), YOLO11n + colour** on 161951: `3_EVIDENCE/m05_user_detection/demo_161951_recording_test60_yolo11n.mp4`
  on Dareen's laptop (60 s). User by colour 70%, kept by fallback 8%, none 22%. 2 screenshots in
  `M05_data/results/demo_yolo11n_22.11/`. Nimer: I can send the video file another way for your check (not in git).
- **Toward 90%** (`python m05_improve.py`): only YOLO11s at 1280 px passes (91.7%, precision 89.8%, ~5 FPS on CPU).
  YOLO11m/l reach ~88%. YOLO11n at 640 px is already ~95% on the big people. Full table + "what we would do
  differently" (record on the drone itself, film closer, tune/test apart, real low light, more fps, better marker) in
  `2_MILESTONES/M05_diagnosis_and_improvements_22.11.md`.
- Open: winner call, Nimer's summary, AI log lines.

## 22.11.2026, Dareen: diagnosis — why the numbers fall short, and fixes
- **Nimer: read `2_MILESTONES/M05_diagnosis_and_improvements_22.11.md`** (for the summary). Reproduce: `python m05_diagnose.py`.
- Detection < 90% only because of small / edge-cut people: fully visible people > 1/4 of the frame 0% missed, small ones
  46% missed, 96% without the small ones. Lower conf (86.3%, precision 88%) and 960 px did not help.
- Hybrid 73%: 27 of 28 misses = turban too weak on the head. Threshold 2% → 78% found / 11% false alarm; 1% → 82% /
  1% wrong / 14% false alarm. Proposal: keep 3%, M06 tracking bridges the gaps.
- Proposed winner sentence: YOLO11n (most accurate and fastest); 90% not met, 96% at following distance.
- Open: winner call, demo video (Dareen), one-page summary (Nimer), AI log lines.

## 22.11.2026 ~06:15, Nimer: THE COMPARISON (colour only vs YOLO only vs YOLO + colour), real labels
- Ran C1 + H1-H3 on the full `labels_marker` (132) and `labels_nomarker` (20) as well. **Dareen's run (below) gives
  exactly the same numbers**, so Table B is confirmed on two laptops. CSVs + 2 screenshots in `M05_data/results/nimer_22.11/`.
- The hybrid's 2 false alarms (Dareen found them): a hand in front of the lens, 154848 frames 00114 and 00152.
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
- (Dareen's C1 + H1-H3 re-run on all labels: done, see her entry below; it matches Nimer's run exactly.)

## 22.11.2026, Dareen: instructions for Nimer
- **Nimer: read `2_MILESTONES/M05_instructions_for_Nimer_22.11.md`** — your steps now: C2-C4 (Table A on all 152
  `labels`, "YOLO only" Table B rows on the 132 `labels_marker`), the speed run, push the CSVs; winner call 17:30.

## 22.11.2026, Dareen: FINAL Table B (C1 + H1-H3) on all corrected labels
- Checked Nimer's 71 labels (valid; 154848: actor = user in 22 of 40, 161825: 26 of 31). All 152 in `M05_data/labels`.
- `labels_marker` = 132 frames (104 with the actor, 28 without), `labels_nomarker` = 20 (154124).
- Brightness 1.0 (0.35 almost the same): colour only found 58.7%, wrong 36.5%, false alarm 71.4%, correct 52.3%.
  Hybrid yolo11n / yolo12n / yolo26n: found 73.1 / 73.1 / 74.0%, wrong 0%, false alarm 7.1%, correct 77.3 / 77.3 / 78.0%.
- Without the turban (154124): colour picks something else in 100%; the hybrid picks nobody in 100%.
- The hybrid's 2 false alarms = a hand in front of the lens (154848 frames 00114, 00152).
- CSVs: `M05_data/results/` (the 4 marker checks + `..._NOMARKER_colour_hybrid.csv`).
- **Nimer:** your C2-C4 (YOLO alone, Table A on all 152 `labels`) + speed run are next; winner call 17:30.

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
