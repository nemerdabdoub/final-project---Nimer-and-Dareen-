# Mid-project presentation: running log

Everything we may want to show in the mid-project presentation, collected as it happens.
**Rule (both of us and both Claudes):** every update that adds a result, a decision, a number, a video or a problem
gets one line in the right section below, with the date and where the proof is. Newest at the bottom of each section.
Presentation date: _to fill in_.
**Finished slides to reuse:** `presentation_material_end_of_semester_A/` (M05 full deck, 15 slides, with a list of which slides to reuse).

## 1. The project in one slide
- Goal: an autonomous drone that finds a user and guides them to a target (Project 3760, TAU, supervisor Dr. Gabi Davidov).
- Hardware: DJI Neo, controlled from a laptop by mirroring the DJI Fly app on an Android phone (Samsung S10, scrcpy + ADB,
  lab repo Penkov-D/DJI-Neo-to-PC). All control goes through one file, `1_CODE/drone_interface.py`.

## ★ MAIN FOCUS: detecting the SAME person, every frame, and what makes them that person
The key question of the project: finding *a* person is easy (YOLO finds people); the drone must find **the same person,
the user, in every frame**, even when other people are in view. The presentation leads with this.

**The user's characteristics we use (as in `1_CODE/m05.py`):**
- **Colour:** a purple-red turban, hue 170-179 in OpenCV (saturation ≥ 110, brightness ≥ 70), measured on the 20.11
  footage. The orange-red mural in the scene is hue 0-19, so only about 1% of it reaches the turban's range.
- **Where the colour is:** only on a **head**: the top 35% of a person box that YOLO found. Colour anywhere else is ignored.
- **How much:** at least 3% of that head area is turban-coloured, **and** at least 2× more than the background just beside
  the person (so a red wall behind someone does not make them the user).
- **Continuity (same person as a moment ago):** if the colour is lost (head turned, blur), the user is the person box that
  overlaps the last frame's user most (IoU ≥ 0.3), for at most about 1 second, then it gives up rather than guess.

**The metric that shows it:** Table B, "wrong person %" (the method chose someone who is not the user) and
"false alarm %" (it claimed a user in clips where he is not there).
- 22.11 test run, stand-in labels, NOT final: wrong person: YOLO alone (biggest person) about 42%, colour only about 31%,
  **hybrid 0%**; false alarms: colour only about 82%, **hybrid 0%**. Real numbers after the labels are corrected.

**Where it still fails (honest slide):** frames where the turban is hidden or very small (about 50 of the actor's frames
had no `user` box in the suggested labels); seen from behind or far away; another person wearing a similar colour.

**Next (M06), making "same person" stronger:** a tracker that gives each person a fixed ID across frames
(ByteTrack / BoT-SORT + Kalman filter), appearance re-identification (clothes colours, size), and a printed ArUco marker
as a second characteristic that also gives the distance to the user.

## 2. Milestones and status
- M02 drone acquired, stable video for 10 min: done 19.10.
- M03 control from code: done. 7.11 take-off, hover and two-step landing from code; 12.11 six moves in flight
  (`flight_test.py moves 0.3 0.5`), landed from code about 7 s after the landing started, battery 69% → 66%.
  Proof: `3_EVIDENCE/2026-11-12/190414_flight_test_log.txt` + video.
- M04 work plan: submitted on Moodle 12.11.
- M05 user detection: in progress, due 23.11 (see section 4). 22.11: Dareen's 81 labels corrected and shared
  (`M05_data/labels`); Nimer's 71 also in → all 152 labels done. Final Table B (Dareen's checks) done.
- M06 user tracking: due 7.12, not started.

## 3. Results and numbers
- 24.11 M06 first try, YOLO11n + BoT-SORT on the same 313 session-1 frames: in view 83.5% correct / 7.2% wrong / 0 false
  picks - no gain over M05 because the colour rule overrides the track ID (red-shirt passer-by). Diagnosis → "sticky ID"
  rule to test next (Nimer).
- 24.11 **Session 1 hold-out, labelled (313 frames ~1/s, never tuned on, different red marker):** user in view →
  correct 85.6% (95% CI 77-91), wrong person 8.2% (red-shirt passer-by + occlusion), missed 6.2%; user not in view →
  0 false picks / 189 (0-2.0%). The raw "70% no user" was mostly her being out of view.
  `2_MILESTONES/M05_session1_holdout_inview_24.11.md` (Nimer + Claude labels).
- 24.11 Session 1 (22.11 outdoor hold-out, never tuned on; user in a red head covering among other people): hybrid
  YOLO11n + turban picked the user by colour in 29% of 2,501 frames, fallback 1%, none 70% — raw share, not yet a
  miss rate (she is often out of view / only a sleeve in close-ups). Correct "USER 0.86" box when she is in view (Nimer).
- 24.11 Session 2 (22.11, DJI Fly screen recording from height, no people in view): hybrid YOLO11n + turban picked no user
  in 2,464 / 2,464 frames → 0 false user picks on a never-tuned no-user clip (Nimer). Note: screen recordings include app
  controls and a black gap; crop/skip before scoring.
- 22.11 M05 test run on Nimer's laptop (CPU, stand-in labels, NOT final): speed YOLO11n 26 FPS (38 ms), YOLO26n 22 FPS
  (46 ms), YOLOv12n 16 FPS (62 ms). Proof: `3_EVIDENCE/m05_user_detection/m05_table_*_PRELIM_suggested_labels.csv`.
- 22.11 Table B, PRELIMINARY (Dareen's corrected half, 61 frames with the turban, brightness 1.0): colour only finds the
  user in 41% and picks the WRONG person in 55% (red mural); hybrid (any of the 3 YOLO) finds him in 79% and never picks
  the wrong person (misses = picks nobody). Same at 0.35. Source: Dareen, `m05_table_B_finding_the_user_*.csv`.
- 22.11 **Table B FINAL (all corrected labels, 132 frames with the turban marker: 104 with the actor, 28 without him),
  brightness 1.0:** colour only: user found 58.7%, WRONG person 36.5%, false alarm 71.4%, frames correct 52.3%.
  Hybrid YOLO11n / v12n / 26n: user found 73.1 / 73.1 / 74.0%, wrong person **0%**, false alarm 7.1% (2 of 28 frames),
  frames correct 77.3 / 77.3 / 78.0%. At 0.35 almost the same (colour 56.7%, hybrids 73-74%).
  The hybrid never follows the wrong person; when it misses it picks nobody. Source: `M05_data/results/`.
- 22.11 **Extra row, actor WITHOUT the turban (154124, 20 frames):** colour only picks something else in 100% of frames;
  hybrid picks nobody in 100% (0% found, 0% wrong). Shows the identity depends on the marker → M06 tracking / re-ID.
- 22.11 RT-DETR (non-YOLO) test on stand-in labels: about 0.9 FPS vs about 15 FPS for YOLO26n (15-20x slower). Source: Dareen.

- 22.11 **REAL M05 Table A** (152 hand-corrected frames, Nimer's laptop CPU): detection rate at 1.0 / 0.35 —
  YOLO11n 85.4 / 84.8%, YOLOv12n 82.9 / 81.9%, YOLO26n 82.5 / 82.9%; precision 94-97%. 90% target not met by any model.
  Proof: `M05_data/results/nimer_22.11/`.
- 22.11 **REAL speed run** (one computer): YOLO11n 21.0 FPS (48 ms), YOLO26n 19.2 FPS (52 ms), YOLOv12n 16.3 FPS
  (61 ms); colour only 13 ms/frame. Darkened copies (0.35) change detection by about 1 point at most.
- 22.11 **Same-person evidence, YOLO alone** (turban frames, 104 with the user): picks the wrong person 35.6-36.5% of
  the time; finding *a* person is not finding *the* user. Hybrid numbers on the same frames: Dareen's re-run.

- 22.11 **REAL comparison, Table B** (turban frames: 104 with the user, 28 without, brightness 1.0): wrong person —
  colour only 36.5%, YOLO only 35.6-36.5%, **hybrid 0% (all three models)**; false alarms — colour 71.4%, YOLO only
  67.9-71.4%, **hybrid 7.1% (2 of 28)**; frames correct — colour 52.3%, YOLO only 55-56%, **hybrid 77-78%**.
  Darkened copies: within about 1 point. **This is the headline slide for "the SAME person".**
- 22.11 Without the turban (20 frames): hybrid picks nobody (0% wrong) instead of guessing; colour only is 100% wrong.
- 22.11 **Hand filter** (ignore "people" wider than 60% and taller than 90% of the frame): hybrid false alarms
  **7.1% → 0%**, nothing else lost (tested on both laptops). With the filter, a 2% head threshold finds the user in
  76-78% (was 73-74%) still with 0% wrong / 0% false alarms: promising, to confirm on new clips (picked on the test frames).
- 22.11 **Why detection is below 90% (YOLO11n):** every miss is a small or cut-off person. Fully visible people taller
  than 1/4 of the frame: 0% missed (196 people); small people (< 1/4 height): 46% missed; without the small ones: 96%.
  Source: Dareen, `1_CODE/m05_diagnose.py`, `2_MILESTONES/M05_diagnosis_and_improvements_22.11.md`.
- 22.11 **Why the hybrid finds the user in 73%:** 27 of its 28 misses = YOLO boxed him but too little turban on the head.
  Lower head-colour threshold: 2% → 78% found / 11% false alarm; 1% → 82% / 1% wrong / 14% false alarm. Kept 3%.
- 22.11 **Toward 90% detection:** only YOLO11s at 1280 px passes (91.7%, precision 89.8%, ~5 FPS on a laptop CPU);
  YOLO11m / 11l ~88%; YOLO11n 640 px 85.4% but ~95% on big people. Source: Dareen, `1_CODE/m05_improve.py`.
- 22.11 **Fine-tuning YOLO11n on 335 own drone frames** (6 unused 20.11 clips + 20.10 classroom; tested on the same 152):
  the framed portrait is no longer detected (was "person 0.64"), same speed — but detection fell 85.4% → 77.1%
  (people > 1/4 height 96.2% → 85.4%) and the hybrid got 1.9% wrong / 10.7% false alarms. Too few people in the
  training data (~366). Kept the original YOLO11n. `M05_data/results/finetune_22.11/`, `1_CODE/m05_finetune.py`.
- 22.11 **Gentle fine-tuning** (keep the 80-class head, freeze the backbone, small learning rate, 15 epochs): portrait
  still gone, detection 84.4% (original 85.4%), people > 1/4 height 95.0%, same speed; hybrid 70.2% found, 1.9% wrong,
  0% false alarm. Lesson: the first run's drop came from rebuilding the class layer (1-class training). Original
  YOLO11n stays the winner; the gentle model is the promising direction with more training data.
- 22.11 **All 8 detectors in one table, measured the same way** (`M05_data/results/all_models_22.11/m05_all_models.md`,
  script `1_CODE/m05_all_models.py`): best per column — all people YOLO11s-1280 91.7%, following distance YOLO11m 97.1%,
  precision YOLO26n 95.2%, user found / frames correct YOLO11m 76.0% / 81.1%, no portrait = the fine-tuned models.
  Requirements (≥90%, ≥15 FPS, 0% wrong person, 0% false alarm) met by YOLO11n, YOLOv12n, YOLO26n → **YOLO11n best
  trade-off** (85.4% all, 96.2% following distance, nano speed). YOLO11m = best quality at 6.5 FPS; YOLO11s-1280 = only
  ≥90% on all people at 5 FPS. **Candidate final slide.**
- 22.11 **Fix B, Table A extra column — people taller than 1/4 of the frame (following distance):** YOLO11n 96.2% /
  95.4% (1.0 / 0.35), YOLOv12n 93.3 / 91.6%, YOLO26n 92.5 / 92.9% → **all three pass 90%** for the people the drone
  follows; the original column (all people incl. far background) stays 82-85%. `M05_data/results/fixes_A_B_22.11/`.
- 22.11 **Fix A, hybrid ignores "people" that fill the frame (a hand at the lens):** false alarm 7.1% → **0%**, user found
  unchanged (73-74%), wrong person 0%, frames correct 77-78% → 79-80%. Same file.
- 22.11 **Full comparison table, one laptop (i7-13650HX, CPU only)**, brightness 1.0: colour only 130 FPS / 4% CPU but
  37% wrong person; YOLO alone 29-36 FPS / ~40% CPU (8 of 20 cores), 36% wrong person; **hybrid YOLO11n 31 FPS / ~40% CPU,
  96% big-people detection, 0% wrong, 0% false alarm, 79% frames correct** (≈ +5 ms/frame over YOLO alone).
  `M05_data/results/full_comparison_22.11/` (script `1_CODE/m05_full_table.py`). **Candidate main results slide.**

## 4. Method and decisions (the "why")
- 22.11 M05 data: 4 clips from 20.11 (3 with the actor in a purple-red turban, 1 without, for false alarms), about
  1 frame/s, 152 frames, classes `user` and `person`, brightness 1.0 and 0.35 (low-light stand-in).
- 22.11 Compared: colour only, YOLO11n / YOLOv12n / YOLO26n alone, and hybrid (YOLO finds people, turban colour picks the user).
- 22.11 **Experiment settings were chosen based on colour, height, and wind:** the actor's purple-red turban colour was
  used to identify the user, person height in the frame to assess detection at the intended following distance, and
  wind conditions were also considered when setting up the experiment. Results were reported separately for people
  taller than 1/4 of the frame. Source: `1_CODE/m05.py`, `2_MILESTONES/M05_diagnosis_and_improvements_22.11.md`.
- 22.11 Winner rule: fastest model with detection rate ≥ 90% at brightness 1.0; a tie goes to the better result at 0.35.
- 22.11 **Winner (proposed by Dareen, Nimer to confirm): YOLO11n + turban colour** — most accurate (85.4% all people,
  96.2% at following distance) and fastest; the literal rule picks no model, the 90% is met for following distance only.
- 22.11 **Summary for Gabi:** `4_DOCUMENTS/M05_summary_for_Gabi_23.11.pdf` (5 pages: result, M03, method, tables A + B,
  winner, pictures, failures + fixes, alternatives, lessons, M06, questions).
- 22.11 Detector choice: YOLO over RT-DETR, MobileNet-SSD, MediaPipe, HOG, Faster R-CNN (best speed/accuracy on a laptop
  without a GPU). Source: `2_MILESTONES/M05_engineering_considerations.md`.
- 22.11 Platform: Crazyflie considered and not chosen (no camera without the AI-deck, 40 g payload, 320×320 greyscale).
- 22.11 Next ideas for M06: tracking (ByteTrack / BoT-SORT + Kalman), printed ArUco marker (also gives distance).

## 5. Demos and visuals we can show
- 12.11 flight video of the six moves (M03).
- 22.11 `3_EVIDENCE/m05_user_detection/M05_frames.mp4` and `M05_frames_suggested_boxes.mp4` (152 frames, 76 s, boxes drawn).
- 22.11 Two comparison screenshots: colour only picks a purple-red sofa, YOLO + colour picks the actor.
  `M05_data/results/nimer_22.11/screenshots/`.
- 22.11 **Demo video (C5), YOLO11n + turban colour**, clip 161951, 60 s: user by colour 70%, kept by the 1-s fallback 8%,
  none 22%. Green = user, blue = others; picks the actor in front of the red mural. Video on Dareen's laptop
  (`3_EVIDENCE/m05_user_detection/demo_161951_recording_test60_yolo11n.mp4`); stills in `M05_data/results/demo_yolo11n_22.11/`.
- 22.11 **Why the demo shows wrong blue boxes (statues) and misses (far woman):** the video is YOLO11n's raw output on the
  original clip; our corrected labels are only the answer key for scoring, they do not train the model. These mistakes
  are the ones counted in Table A (17 wrong boxes, 46 missed people in 152 frames). Cleaner demo at confidence 0.4
  (`python m05.py video <clip> yolo11n.pt 0.4`): 17 → 3 wrong boxes but 46 → 55 missed people (detection 85.4 → 82.5%,
  precision 94.1 → 98.9%); removes ~3.5-6% of the boxes in the clips, including some real, partly hidden people
  (`conf_0.25_vs_0.4_what_is_removed.jpg`). Only fine-tuning on our drone frames would teach "statue ≠ person".

## 6. Problems we hit and how we solved them
- 7.11 Small stick pushes (0.1-0.2 for 0.4-0.5 s) moved the Neo only a few cm → raised to 0.3 for 0.5 s (cap 0.4).
- 22.11 Colour only gives many false alarms (a red mural in the scene) → hybrid: colour only counts on a person's head.
- 22.11 The hybrid's only 2 false alarms (154848 frames 00114, 00152): a hand right in front of the lens; YOLO calls it a
  person and the pink-red skin passes as the turban colour. **Solved 22.11:** the hybrid skips boxes wider than 60% and
  taller than 90% of the frame (the actor is at most 22% wide) → 0 false alarms.
- 22.11 90% detection target not met (82-85%) → cause: small / far and edge-cut people. Fixes: YOLO11s, keep the user
  large with the M06 distance controller, or a minimum-size target. Lower confidence (86%) and 960 px input did not help.
- 22.11 Hybrid misses when the turban is not visible → keep the strict 3% rule (never the wrong person) and bridge the
  gaps with M06 tracking instead of loosening the colour rule (thresholds were set on the test frames themselves).

- 23.11 **Someone passes by the user → the two person boxes overlap** (seen in our videos). Risks: YOLO merges them or
  shifts a box, the turban can fall inside the passer-by's head area, and the 1 s IoU fallback can jump to the wrong box.
  **What to say to Gabi:** today the strict rules keep it safe (turban only on a head, 2× background, wide/close boxes
  skipped) → wrong person 1.8% on all videos, and when unsure the method gives *no* user rather than a wrong one.
  **Fix in M06:** the tracker keeps each person's ID through the crossing (Kalman motion + IoU), the turban re-confirms the
  user after it, an ID switch is allowed only with the turban seen, and while boxes overlap (IoU > ~0.3) the drone holds
  its position instead of following. We will count ID swaps on the crossing scenes as the M06 metric (not measured yet).

## 7. Teamwork and tools
- Shared GitHub repo; a GitHub action @mentions the partner on every push; `UPDATES.md` log; a live "Project updates"
  panel in VS Code (Claude Code plugin); M05 data shared in `M05_data/`; work split equally by method.
- 22.11 Own labelling tool `1_CODE/label_tool.py`: loads the suggested boxes, saves YOLO labels directly into the repo.

## 8. Next steps (to the end of the semester)
- M05: correct labels (both halves) → real tables A and B → winner → demo video → summary for Gabi.
  22.11: labels, tables A and B, demo video done; open: winner sentence (proposal YOLO11n), summary.
- Lessons for the next data: record on the drone's built-in storage (not the 1080x608 mirror with app buttons), film at
  following distance, tune and test on different clips, real low-light flight, 5 frames/s, a colour found nowhere else.
- M06 user tracking by 7.12.

## New filming and M06
- 22.11: second filming session outside the Medical Faculty (bike racks): 2 drone clips of ~5 min each; battery 59% → 14% in ~5 min at 7-8 m (~11 min per battery, land at 30%). `2_MILESTONES/filming_22.11_bikes_med_faculty.md`.
- 22.11: M06 tracking tool started (`1_CODE/m06_track.py`): YOLO11n + ByteTrack keeps the user's ID between turban sightings; compared with the M05 1-second fallback on the same frames.
- 22.11: first HONEST test of the M05 choice on the new clips (never tuned on): hybrid user picks 83/88 right by eye; the 5 wrong = a passer-by in a red shirt (new problem: red clothes); 0 false alarms over a car park with red cars and a red dome (colour only: ~130 false). Every big person found (100% vs YOLO11l reference); a bike is almost never boxed as a person. `2_MILESTONES/M05_newclips_bikes_openvocab_22.11.md`.
- 22.11: work-plan item done - YOLO-World v2 s and YOLOE-11s asked for e-scooters and strollers: 1 real scooter (mislabelled), 11 wrong (bikes, backpack), no strollers in the clips; ~3x slower than YOLO11n (7 FPS). Not usable as is -> next semester: film scooters/strollers, then tuned prompts or fine-tune YOLO11n with extra classes. The fine-tuned person-only model lost the bike class.
- 23.11: VERIFIED on ALL videos (392 frames: 20.11 + both 22.11 clips, same Table-B rules; the code reproduces Table B exactly): hybrid YOLO11n wrong person 1.3% (2/153) vs 26-29% for colour or YOLO alone, false alarms 0/239 vs 23-31%, frames correct 90.3% vs 67-74%. Nano hybrids tie (75.2% found); 11s/11m +3% at 2-6x slower → keep YOLO11n. New clip 1: user found 88.6%, frames correct 96.5%. Plan: 11n + tracker for M06; next semester ONE fine-tuned 11n with person/bike/car + scooter + stroller (COCO and Open Images have no scooter/stroller; YOLOE only as labelling helper). `2_MILESTONES/M05_newclips_bikes_openvocab_22.11.md` §5-6.
- 23.11: FINAL on hand labels (Dareen labelled all 299 new frames): 403 frames, 13 methods. Hybrid YOLO11n wrong person 1.8% vs 24-27% (colour / YOLO alone), false alarms 0/239 vs 59-79, frames correct 87.8% vs 66-72%. Detection at following distance 96.2% (meets 90%), all people 59.4% (far people from 7-8 m). YOLO11m slightly better but 6.5 FPS → keep YOLO11n. Note §7.
- 23.11: one-page M05 story for the report (problem → action → evidence → choice): `2_MILESTONES/M05_engineering_journey_23.11.md`. Demo videos of both 22.11 clips (YOLO11n + turban, tagged boxes) in `3_EVIDENCE/2026-11-23_M05_final/`.
- 23.11: simple YOLO11n tweaks (cut-off 0.25/0.20/0.15 × input 640/800/960, 403 hand-labelled frames): lower cut-off adds golf carts and wrong-person frames → no; 800 px +2.5 points at 23 FPS → small gain, re-test in M06; M05 stays 640/0.25. Gabi deck updated (18 slides): all-13-methods chart, new-footage slide, strollers/scooters slide. Note §8.
- 24.11: **Re-selection on the drone laptop's GPU (RTX 5050; PyTorch had been CPU-only)**: accuracy identical on GPU and CPU; 12 detectors from 3 families (YOLO11n/s/m, 12n, 26n/s/m, RT-DETR-L, RF-DETR Nano/Small/Medium) on all 403 hand-labelled frames. **Hybrid YOLO11m best: user found 74.4%, wrong person 0.6% (1/164), 0 false alarms, frames correct 89.6%** (YOLO11n 70.1 / 1.8% / 0 / 87.8%). Transformers find more far people (up to 80% vs 68%) but precision 62-66% at the same cut-off and 1.5-2× slower → rejected for now. Proposal: switch to YOLO11m (Nimer to confirm). `2_MILESTONES/M05_reselection_GPU_12_detectors_24.11.md`.
- 24.11: **All 6 Ultralytics trackers compared** (ByteTrack, BoT-SORT, OC-SORT, Deep OC-SORT, FastTrack, TrackTrack CVPR 2025) on 161951: BoT-SORT best (84% user kept, 8 corrections), TrackTrack 83% / 10, ByteTrack 82% / 15; clip 161825 cannot separate them (all 61%).
- 23.11: **Gabi's YOLO26n idea checked (M06 first look, clip 161951, 751 frames):** the adaptive (NSA) Kalman is in the Ultralytics tracker and works with any detector, not built into YOLO26n. User kept: YOLO11n + ByteTrack 82% (reproduces Nimer), **YOLO11n + BoT-SORT 84%**, YOLO26n 81% with both. BoT-SORT needs half the turban corrections (8 vs 12-15) → lead candidate YOLO11n + BoT-SORT; one clip only, differences in % within noise. `2_MILESTONES/M06_tracker_grid_23.11.md`.
- 23.11: **correction against the approved work plan**: requirement 1 = identify the USER in >= 90% of frames in lab conditions (earlier notes wrongly read it as person detection). Lab: user detected by YOLO11n in 99.0% (103/104), identified by the turban in 73.1% (76/104, never wrong); all videos 92.7% / 70.1%. Req. 3 = >= 10 FPS (29.9 ✓). Identification above 90% = M06 tracking. Gabi deck updated (work-plan check slide).
