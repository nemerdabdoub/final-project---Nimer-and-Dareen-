# Updates log (newest first)
**NEW (Nimer 23.11): panel section "מנחה · Mentor" (live)** - shows the current milestone (M06), days left, progress, the next
tasks, the pass line, what Gabi will ask, and one piece of advice that fits what is happening right now. It reads
`2_MILESTONES/mentor_plan.md`: **tick tasks there (`- [x]`) and push**; both panels update.

**NEW for both (Nimer 23.11): `4_DOCUMENTS/How_to_run_this_project_mentor_guide.pdf`** - 4 pages of supervisor-style advice:
see the whole loop and fix the weakest link (tracking, controller, command delay), the cycle for every experiment, a requirement
trace table, honest data rules (hold-out set), M06 states FOLLOWING/UNSURE/LOST, delay + simple controller, safety steps,
working with Gabi, and a day-by-day plan for M06 (due 7.12).

**>>> 30-MIN PREP BEFORE GABI (Nimer + Dareen) - tick as you go <<<**
- [ ] 0-5 min, both: read the meeting brief below; Nimer tells Dareen "YOLO11n + turban confirmed".
- [ ] 5-10 min, Dareen: send Nimer the 20-slide deck (link or .pptx); split it: Dareen = results slides, Nimer = work-plan check + M06 + questions.
- [ ] 10-15 min, demos open and paused: Dareen = `3_EVIDENCE/2026-11-23_M05_final/` demo video; Nimer = M06 tracker video
      `3_EVIDENCE/m06_tracking/161951_recording_test60_bytetrack.mp4` (user kept 76% -> 82%).
- [ ] 15-20 min, both: say the key numbers out loud once: detected 99%, identified 73% (never wrong), wrong person 1.8%,
      0 false alarms, 29.9 FPS, delay ~290 ms, M06 76% -> 82%.
- [ ] 20-25 min, both: agree the 4 questions for Gabi (slide 20): req. 1 via tracking OK? enough labelled frames? real low-light
      flight? turban marker OK? + say the next step: M06 tracking, due 7.12.
- [ ] **Add to what we say (Dareen: one line on the "where it fails" / questions slide):** when someone passes by the
      user, the person boxes OVERLAP. Today: strict turban-on-head rule → wrong person only 1.8%, and when unsure we give no
      user instead of a wrong one. M06: tracker keeps IDs through the crossing, turban re-confirms the user, drone holds
      position while boxes overlap; we will count ID swaps (not measured yet). Ask Gabi: is "hold while overlapping" OK?
- [ ] **Talking points PDF (2 pages, what to say, numbers, questions): `4_DOCUMENTS/Talking_points_Gabi_23.11.pdf`** - both read it.
- [ ] 25-30 min: laptops charged + chargers, deck open on one laptop, HDMI/adapter; Nimer: AI-log line done? 12.11 moves video
      found (phone)? If not, say "will send after the meeting".

**>>> NIMER + NIMER'S CLAUDE: READ FIRST - MEETING BRIEF (23.11, 1 hour before Gabi) <<<**
- **Decision: YOLO11n + turban colour (hybrid).** Final test on ALL our videos, hand-labelled by Dareen (403 frames: 20.11 lab + both
  22.11 campus clips): user found 70.1% of her frames, **wrong person 1.8% (3/164), false alarms 0/239**, frames correct 87.8%,
  29.9 FPS. Colour only / YOLO alone pick the wrong person ~25% of frames. Bigger models (11s/11m) +2-4 points but 16 / 6 FPS.
- **Work plan check (approved plan):** req. 1 = user in >= 90% of frames in lab → user **detected 99%** (103/104), **identified 73%**
  (76/104, never wrong) = half met, **M06 tracking closes the gap** (your first run 76% → 82%). Req. 3 >= 10 FPS ✓ (29.9).
  YOLO comparison table ✓, demo video ✓, YOLOE/YOLO-World on strollers/scooters ✓ (checked: not reliable, ~7 FPS → plan for semester B).
- People detection (all videos): 96.2% at following distance, 59.4% all people (tiny far people from 7-8 m). Precision 94.7%.
- Tried and rejected with numbers: lower confidence (adds golf carts), 800/960 px input (+1-2 points, slower; re-test in M06),
  fine-tune (removes the portrait but forgot bikes).
- **Deck (20 slides, infographics):** claude.ai artifact, private to Dareen - she shares it / downloads the .pptx. Slides 13-14 = work-plan
  check + final choice; slide 20 = questions for Gabi (req. 1 via tracking OK? labelled frames enough? real low-light flight? marker OK?).
- One-page story: `2_MILESTONES/M05_engineering_journey_23.11.md` · all numbers: `2_MILESTONES/M05_newclips_bikes_openvocab_22.11.md` §7-8.
- Pipeline facts to quote: video delay 256 ms (mirror 60 ms of it) + detection 34 ms ≈ 290 ms; command delay not measured yet (M06).

**DAREEN, PLEASE:** upload `3_EVIDENCE/2026-11-22/143404_recording_session1.mp4` (450 MB) to our shared Google Drive folder
"Final Project Dareen and Nimer" — Nimer needs the video (videos are not in git). Tell him when it is there.
**LATEST PUSHES (24.11):** Dareen 01:20 – deck updated: `4_DOCUMENTS/M05_for_Gabi_24.11_GPU_update.pptx` (20 slides: old 17 + new 13 = 12 detectors on GPU, 14 = new choice YOLO11m, 15 = 6 trackers; slide 12 marked "choice on 23.11, CPU only") · Dareen 00:45 – **GPU found on Dareen's (drone) laptop → 12 detectors re-tested (YOLO, RT-DETR, RF-DETR) on 403 frames: proposal = switch to hybrid YOLO11m** (89.6% correct, 1 wrong, 0 false alarms) + all 6 trackers: BoT-SORT best → **Nimer: please confirm YOLO11m** · Dareen 24.11 – Gabi's "check newer models": shortlist + criteria + plan (`2_MILESTONES/M06_newest_models_shortlist_24.11.md`); `m06_track.py --tracker` now also ocsort / deepocsort / fasttrack / tracktrack (all inside Ultralytics 8.4); grid of all 6 running · Dareen 23:58 – **M06 first look at Gabi's YOLO26n idea:** Kalman is in the tracker (any detector); YOLO11n + BoT-SORT 84% user kept, YOLO26n 81%; BoT-SORT half the corrections → lead candidate YOLO11n + BoT-SORT (`2_MILESTONES/M06_tracker_grid_23.11.md`) · Dareen 21:20 – **`4_DOCUMENTS/STAND_OUT_STRATEGY.md`: how we beat the two earlier teams on this topic** (grade weights, what they did and how they measured, our 8 edges, moves per milestone, checklist) + CLAUDE.md rule → **Nimer: please read it** · Dareen 20:55 – new **Mentor coach** panel `tools/mentor-coach` (shows the playbook of the process we are in + "Ask the mentor" buttons; `/mentor`); added to the marketplace → **Nimer: `/plugin install mentor-coach --marketplace nemerdabdoub/final-project---Nimer-and-Dareen-`** · Dareen 20:39 – mentor playbooks `2_MILESTONES/mentor_playbooks.md` (what Gabi would say for each process: flight, experiment, data, controller, decision, meeting, writing, code, debug, pair, new milestone, feeling lost) · Dareen 23.11 – CORRECTION vs approved work plan: req. 1 = user in ≥90% of frames (lab) → detected 99%, identified 73% (M06 tracking closes it); notes, CLAUDE.md and deck fixed · Dareen 23.11 – simple YOLO11n tweaks tested (lower cut-off no; 800 px +2.5 points at 23 FPS → keep 640 for M05, re-test in M06, note §8); Gabi deck updated to 18 slides (all methods, new footage, strollers/scooters) · Nimer 23.11 – panel: new "Claude right now" section (live: what Claude is doing, last 8 actions with times; works for Dareen's Claude too) · Dareen 23.11 – one-page M05 story: problems → actions → evidence → choice (`2_MILESTONES/M05_engineering_journey_23.11.md`); demos of the new clips in `3_EVIDENCE/2026-11-23_M05_final/` (laptop) · Nimer 23.11 – panel: optional "Lab reports" section (Nimer's personal course labs; reads a file outside the repo, so it never shows on Dareen's laptop — no change for her) · Dareen 23.11 – FINAL table on hand labels (all 299 new frames labelled by Dareen): hybrid YOLO11n 1.8% wrong, 0 false alarms, 87.8% correct; 96.2% detection at following distance → YOLO11n confirmed (note §7) · Dareen 23.11 – her 149 test labels done (user agrees with Claude's by-eye marks in 126/129) and **she is labelling Nimer's half too → Nimer: do NOT run `label nimer`** · Dareen 23.11 – hybrid VERIFIED on all videos (392 frames: wrong person 1.3% vs 26-29%, 0 false alarms, 90.3% correct; nano hybrids tie → keep YOLO11n) + which YOLO for M06 / obstacles (note §5-6) · Nimer 17:50 – `4_DOCUMENTS/Next_three_steps_22.11.pdf` + first M06 run on 161951 (tracker keeps the user in 82% of frames vs 76% old way) ·
Dareen 17:36 – `record_video.py`: keys T = take off, L = land in the recording window (not flight-tested yet) · Dareen 17:40 – new clips tested (hybrid 83/88 right, 5 wrong = man in red shirt; 0 false alarms over the car park) + YOLO-World / YOLOE work-plan check (not usable as is) + `prepare` done → **Nimer: `python m05_newclips.py label nimer`** · Nimer 15:45 – labelling set-up for the new 22.11 clips (`1_CODE/m05_newclips.py`, test-only) — **Dareen: run `python m05_newclips.py prepare` and push** ·
Nimer 15:30 – short plain project summary `4_DOCUMENTS/Project_summary_22.11.pdf` (1 page, everything so far) ·
Dareen 15:15 – new filming at the Med Faculty (2 clips, `2_MILESTONES/filming_22.11_bikes_med_faculty.md`) + M06 tracking tool `1_CODE/m06_track.py` ·
Dareen 10:05 – Gabi deck shortened to 11 slides (`4_DOCUMENTS/M05_for_Gabi_23.11_short.pptx`: comparisons + decision, new all-results table slide); full 16-slide deck saved in `4_DOCUMENTS/presentation_material_end_of_semester_A/` ·
Dareen 09:05 – ONE table of all 8 detectors (`M05_data/results/all_models_22.11/`), final choice YOLO11n ·
Dareen 08:50 – GENTLE fine-tuning: portrait gone, detection 84.4% (orig. 85.4%), 1.9% wrong person → keep YOLO11n, gentle = next step ·
Nimer 08:40 – panel: new "Files Dareen changed" section ·
Dareen 08:30 – fine-tuning tested: portrait gone but detection 85.4% → 77.1%, keep original YOLO11n ·
Dareen 07:34 – her 162 training labels DONE → **all 335 training labels in** ·
Nimer 07:27 – his half of the training labels DONE (173 frames, `M05_data/train/labels`) · Dareen 07:12 – classroom clip added to training (335 frames) · Dareen 07:07 – fine-tuning started (`m05_finetune.py`) ·
Nimer 06:47 – one-page summary PDF `4_DOCUMENTS/M05_summary_23.11.pdf` + `.gitattributes` · Dareen 06:28–06:44 – her
summary for Gabi (docx + pdf) and demo boxes tagged USER / person. **Next:** agree the winner = original YOLO11n (fine-tuning reported as tried) and pick ONE summary before Mon 12:00.
**Two summaries exist** (Dareen's 06:28 and Nimer's PDF): pick one together before Mon 12:00.

Shared between Nimer and Dareen and both Claude Code sessions. Every change pushed to GitHub gets one entry here.
Claude: read the newest entries at the start of each session and tell the user what the partner changed.

## 24.11.2026 00:45, Dareen: GPU re-selection, 12 detectors, 6 trackers → proposal: hybrid YOLO11m
- **Found:** Dareen's laptop (= the drone laptop) has an NVIDIA RTX 5050 (8 GB); our PyTorch was the CPU-only build, so
  every speed until now was CPU. New separate GPU env `C:\Users\LOREN\venvs\gpu` (torch 2.14.1+cu130, ultralytics, rfdetr).
- **Accuracy is identical on GPU and CPU** (152-frame table, every column) → no milestone needs redoing; only speed changes.
- **12 detectors on all 403 hand-labelled frames** (YOLO11n/s/m, 12n, 26n/s/m, gentle fine-tune, RT-DETR-L, RF-DETR Nano/Small/Medium):
  hybrid **YOLO11m best**: user found 74.4%, wrong 0.6% (1/164), 0 false alarms, 89.6% correct (YOLO11n: 70.1 / 1.8% / 0 / 87.8%).
  YOLO26m ties on user found (2 wrong, 2 false alarms) and finds most far people of the YOLOs. Transformers: up to 80% of
  people found but precision 62-66% at our cut-off, no better at the user, 1.5-2× slower → rejected for now.
- **Speed:** first GPU run (laptop in use) YOLO11m hybrid ~45 FPS, YOLO11n ~54. The repeated test ran with the laptop idle
  and throttled by Windows (colour step 22 ms instead of 7) → only relative numbers valid (YOLO11m +18 ms vs 11n). Confirmation
  run with Dareen at the laptop still to do, incl. the tracker (`m06_track.py --model yolo11m.pt --tracker botsort`).
- **All 6 trackers** on 161951: BoT-SORT 84% / 8 corrections, OC-SORT and Deep OC-SORT (ReID off) 83% / 9, TrackTrack 83% / 10,
  ByteTrack and FastTrack 82% / 14-15; 161825 cannot separate them (61% all).
- Files: `2_MILESTONES/M05_reselection_GPU_12_detectors_24.11.md`, `M05_data/results/userpick_allvideos_gpu_24.11/`,
  `speed_gpu_24.11.csv`, `all_models_22.11/m05_all_models_gpu_24.11.csv`, `m06_all_trackers_24.11/`. Scripts:
  `m05_userpick_allvideos.py` (+26s/26m, RT-DETR/RF-DETR adapter, GPU output folder), `m05_all_models.py` (+26s/26m,
  GPU file), new `m05_speed_gpu.py`.
- **Open:** Nimer confirms YOLO11m; clean speed + loop run; DETR with its own cut-off (tune on M05, test on new clips); PowerPoint update (next).

## 24.11.2026, Dareen: newer models and algorithms (Gabi's request) — shortlist and plan
- Web search (Nov 2026) → `2_MILESTONES/M06_newest_models_shortlist_24.11.md`: criteria from the work plan (user kept ≥ 90%,
  ID swaps on crossings, ≥ 10 FPS on our CPU laptop, small/far people, low delay, explainable), candidates per layer
  (detector: YOLO26n done, **RF-DETR-Nano** next; trackers: **TrackTrack (CVPR 2025)**, OC-SORT, Deep OC-SORT, FastTrack,
  BoT-SORT, ByteTrack; ReID: YOLO26 ReID; single-object trackers SGLATrack/SSTrack = semester B), sources listed.
- `1_CODE/m06_track.py`: `--tracker` accepts all 6 Ultralytics trackers (one-line change, defaults unchanged).
- Running: all 6 trackers × YOLO11n on 161951 + 161825. Results + table follow in the next push.
- Open: RF-DETR-Nano test (separate virtual environment), best 2 trackers on the 22.11 clips, crossings.

## 23.11.2026 23:58, Dareen: M06 tracker grid (answer to Gabi's YOLO26n suggestion) + Crazyflie
- Fact check: in Ultralytics 8.4.216 the Kalman filter (incl. the adaptive NSA-Kalman) is in the **tracker** code and works
  with any detector; YOLO26 only adds ReID models for BoT-SORT. Not "built into" YOLO26n.
- 2×2 on clip 161951 (751 frames, `m06_track.py` defaults): user kept YOLO11n + ByteTrack 82% (= Nimer's run), **YOLO11n +
  BoT-SORT 84%**, YOLO26n + ByteTrack 81%, YOLO26n + BoT-SORT 81%; turban corrections 15 / **8** / 12 / **8**.
  → YOLO26n no gain; BoT-SORT loses the user half as often → lead candidate **YOLO11n + BoT-SORT**. One clip, % within noise.
- Files: `2_MILESTONES/M06_tracker_grid_23.11.md`, `M05_data/results/m06_tracker_grid_23.11/` (summaries + per-frame CSV).
  Installed `lap` on Dareen's laptop (trackers need it).
- Crazyflie (Israel's emails): kit to assemble, no camera (AI deck discontinued; Wi-Fi/ESP32 camera needs its own battery),
  40 g payload, 8-10 min flights → Dareen's view: stay with the Neo, decline politely, keep it as an optional extension.
- Open: same grid on 161825 + both 22.11 clips; count tracker swaps by eye; BoT-SORT + ReID; crossing scenes.
  **Nimer:** agree on Crazyflie reply to Israel (you have the thread).

## 23.11.2026 21:20, Dareen: stand-out strategy (we are the third team on this topic)
- Read the course Moodle files (syllabus, opening meeting, mid-presentation guidelines, timetable, faculty project site)
  and the two earlier project books with Gabi: Fridman & Adda (Tello, YOLO11 + ByteTrack + template matching,
  hysteresis, RRT*, user typed by ID, results "from empirical observations") and Qasem Ali & Atallah (Tello, red-shirt
  HSV user, PD, RRT; 30 runs by eye, "not formal dataset-based accuracy metrics").
- New `4_DOCUMENTS/STAND_OUT_STRATEGY.md`: grade weights (final examiner 25% + Gabi 30%; mid presentation 20%),
  comparison table vs both teams, our 8 edges (measured + CIs, hold-out data, baselines/ablations, delay budget,
  ID swaps on crossings + states, safety/FMEA, requirement trace, decision log + AI use per block), moves per milestone, checklist.
- Key number: their 93.3% user detection = 28/30 runs → 95% CI 79-98%; ours is per frame on hand labels
  (wrong person 3/164 = 1.8%, CI 0.6-5.2%; false alarms 0/239, CI 0-1.6%).
- CLAUDE.md: new "Stand out" rule; two new principles in the mentor playbooks. The earlier books stay off git (other students' work).
- Open: both read it; next M06 step = count ID swaps on crossing scenes vs the M05 baseline.

## 23.11.2026 20:55, Dareen: Mentor coach panel (a stand-in supervisor beside the chat)
- New plugin `tools/mentor-coach` (own folder; Nimer's `tools/project-updates` untouched), listed in `.claude-plugin/marketplace.json`.
- It guesses the process we are in from our messages and Claude's commands/edited files (git and notes are ignored;
  our own messages count more than Claude's commands for 10 min) and shows that playbook from
  `2_MILESTONES/mentor_playbooks.md`: why, steps, what Gabi will ask, traps, done-when, plus M06 days left + next task
  from `mentor_plan.md` and one principle per hour. It also tells Claude the process, so the Advisor's view matches.
- Buttons send a question to Claude: where are we / ONE next step · review like Gabi · practice Gabi's hardest
  questions · plan the next 2 hours · explain the idea simply. `/mentor`, `/mentor flight` (pin), `/mentor auto`.
- It never runs git or changes files. First version: the guessing rules were tested in Python on 14 sample commands/messages;
  the panel itself loads on Dareen's laptop now. Tell Dareen if something looks wrong on yours.
- Open: Nimer installs it (command above) and says whether the advice fits; both: edit the playbooks when Gabi says something new.

## 23.11.2026 20:39, Dareen: mentor playbooks for every process
- New `2_MILESTONES/mentor_playbooks.md`: for each kind of work (feeling lost, flight test, experiment, data/labelling,
  controller, decision, meeting with Gabi, writing, code, debugging, working as a pair, new milestone): why it matters,
  steps, what Gabi will ask, traps, done-when; plus 10 engineering principles. Plain Markdown: both of us can edit it.
- Coming next (Dareen): a separate **Mentor coach** panel (`tools/mentor-coach`, its own folder — Nimer's
  `tools/project-updates` is not touched) that guesses which process we are in and shows that playbook, with buttons
  that ask Claude for a supervisor-style review / plan / practice questions.
- Not pushed on purpose: `tools/project-updates/tsconfig.json` (generated by Claude Code on Dareen's laptop, editor-only).

## 23.11.2026 20:20, Dareen: Advisor's guide for the whole project
- `4_DOCUMENTS/ADVISOR_GUIDE.md`: the project map (M06 → first closed loop in Dec-Jan → mid-project presentation → semester B),
  the 7-step method for every milestone, engineering principles (whole-loop delay ~290 ms, hover when unsure, dry run before live),
  working with the supervisor, what examiners ask, and the **M06 definition of done**. Open design question flagged:
  **how the system knows where the target is** (decide early).
- CLAUDE.md rule: both Claudes add an "Advisor's view" to every step.

## 23.11.2026, Dareen: correction against the approved work plan (requirement 1)
- The approved plan says **requirement 1 = identify the user in at least 90% of frames in lab conditions**; req. 3 = at least 10 FPS.
  Our notes had read the 90% as person detection. Measured on the hand labels: user **detected** by YOLO11n in 99.0% of lab frames
  (103/104; all videos 92.7%), **identified** by the turban in 73.1% (76/104, never wrong; all videos 70.1%).
- So for Gabi: req. 1 half met; identification above 90% = M06 tracking (Nimer's first run 76% → 82%). Fixed in the journey note,
  the new-clips note, CLAUDE.md, the presentation log and the Gabi deck (new work-plan check slide).

## 23.11.2026, Dareen: simple YOLO11n tweaks + deck updated
- `1_CODE/m05_tweak_sweep.py`: cut-off 0.25/0.20/0.15 × input 640/800/960 on the 403 hand-labelled frames → `M05_data/results/tweak_sweep_23.11/`.
  Lower cut-off: more golf carts and wrong-person frames → no. 800 px: +2.5 points, same 0 false alarms, 23 FPS → re-test in M06. M05 stays 640/0.25.
- Gabi deck (claude.ai) updated to 18 slides: all 13 methods on all videos, redrawn speed-vs-accuracy chart with the tweaks, new-footage slide, strollers/scooters slide.

## 23.11.2026, Nimer: panel – live "Claude right now" section
- `tools/project-updates`: the Project updates panel now shows, at the top, what Claude is doing at this moment
  (running a command, reading/editing a file, thinking, waiting for you) and its last 8 actions with times and durations.
  It reads only the Claude session on the same laptop; nothing is sent anywhere. No project results changed. Open: nothing.

## 23.11.2026, Dareen: M05 engineering journey (for the meeting / report)
- New `2_MILESTONES/M05_engineering_journey_23.11.md`: data, methods, every problem we hit and how we fixed it, the final table
  (re-run on the charger: same accuracy, YOLO11n hybrid 29.9 FPS), the choice and why, strollers/scooters, M06.
- Evidence (Dareen's laptop): `3_EVIDENCE/2026-11-23_M05_final/` = demo videos of both 22.11 clips + result pictures + final table.

## 23.11.2026, Nimer: panel – optional "Lab reports" section
- `tools/project-updates`: the Project updates panel can show a "Lab reports" list (status + open-PDF button) read from
  a local status file outside the repo. It is not project work and appears only on a laptop that has that file, so
  Dareen's panel looks the same as before. No project results changed. Open: nothing.

## 23.11.2026, Dareen: FINAL all-videos table on hand labels
- Dareen labelled BOTH halves of `M05_data/test_22.11` (299 frames) → pushed. `m05_userpick_allvideos.py` now uses hand labels and also
  scores person detection. 403 frames, 164 with the user, 604 people, 13 methods.
- Hybrid YOLO11n: user found 70.1%, wrong 1.8% (3), false alarms 0/239, frames correct 87.8% (colour 64/24/33/66, YOLO11n alone 67/27/25/72).
  Detection: following distance 96.2%, all people 59.4% (small far people at 7-8 m). YOLO11m best on quality but 6.5 FPS.
- **Decision stands: YOLO11n + turban.** Details `2_MILESTONES/M05_newclips_bikes_openvocab_22.11.md` §7.

## 23.11.2026, Dareen: test-set labels (22.11 clips)
- Dareen's half: 149 frames hand-labelled and pushed (`M05_data/test_22.11/labels`); one corrupted file (143404 f00050) redone.
  User boxes agree with Claude's by-eye marks in 126 of 129 frames (98%).
- **Dareen is labelling Nimer's half now (he is busy) → Nimer: don't run `label nimer`.** Then the all-videos table is re-run on hand labels.

## 23.11.2026, Dareen: hybrid verified on ALL videos + which YOLO to use
- `1_CODE/m05_userpick_allvideos.py`: Table-B rules on the 20.11 frames + both 22.11 clips (392 frames, 153 with the user).
  Reproduces the old Table B exactly. User box on the new clips marked by eye (Claude) → `M05_data/results/userpick_allvideos_22.11/`.
- **Hybrid YOLO11n: found 75.2%, wrong person 1.3% (2), false alarms 0/239, frames correct 90.3%** vs colour 65/26/31/68 and YOLO alone 70/29/23/74.
  Nano hybrids tie; 11s/11m +4-5 frames at 2-6x slower. New clip 1 alone: 88.6% found, 96.5% correct.
- Correction: clip 2 (144943) has the user in its first ~10 s (hybrid missed those 5 frames: head cut off / back-lit).
- **Recommendation:** M06 = YOLO11n + turban + tracker (not a bigger model, not two YOLOs per frame). Next semester obstacles =
  ONE fine-tuned YOLO11n with person/bike/car/motorcycle + scooter + stroller (COCO and Open Images V7 have no scooter/stroller;
  YOLOE prompt-free has them but is slow and confuses bikes → use it to draft labels). Note §5-6.
- Open: hand labels of `M05_data/test_22.11` (both) replace Claude's by-eye user boxes.

## 22.11.2026 17:50, Nimer: next-steps PDF + first M06 tracking run on Nimer's laptop
- `4_DOCUMENTS/Next_three_steps_22.11.pdf` (one calm page): Monday prep, label the new footage, start following the user.
- `python m06_track.py ..\3_EVIDENCE\2026-11-20\161951_recording_test60.mp4 --seconds 60` (YOLO11n + ByteTrack, every 2nd
  frame): user known in **82%** of frames with the tracker (colour 70% + tracker 13%) vs **76%** the old M05 way
  (colour + 1 s fallback); 15 re-identifications by colour; 13 gaps, longest 5.4 s. Still to check by eye: no yellow
  "USER (track)" box on someone else. Video + CSV in `3_EVIDENCE/m06_tracking/` (Nimer's laptop).

## 22.11.2026 17:36, Dareen: take-off / land keys in record_video.py
- `1_CODE/record_video.py`: in the recording window **T = take off, L = land** (uses `drone_interface.takeoff()` / `land()`
  in a background thread, so the video keeps recording; result shown on the image and in the terminal). Esc still only
  stops the recording — it does NOT land.
- **Not flight-tested yet** (syntax check only). Note: run `$env:PATH = "$PWD;$env:PATH"` in 1_CODE first, otherwise
  the lab's scrcpy.py cannot find `adb` ("WinError 2"). A first try today connected to the phone but got no camera frames.
- Open: test T/L on the drone; Dareen labels her half of `M05_data/test_22.11` (started now).

## 22.11.2026 17:40, Dareen: new 22.11 clips analysed + YOLO-World / YOLOE (work-plan item) + test set prepared
- `python m05_newclips.py prepare` done (Nimer's script) → `M05_data/test_22.11/` pushed. **Both: label your half** (`label nimer` / `label dareen`).
- Quick test without labels (`1_CODE/m05_newclips_auto.py`, renamed so it doesn't clash with Nimer's `m05_newclips.py`):
  hybrid user picks **83 of 88 right** by eye; **5 wrong = a passer-by in a red shirt** (small box, "head" area reaches his shoulders)
  → new problem to fix; **0 false alarms** in the car-park clip (red cars, red dome) vs ~130 for colour only.
  People vs YOLO11l reference: big people 100% for YOLO11n/12n, all people ~66% (small, far, 7-8 m). Bikes almost never boxed as people.
  The gentle fine-tuned model finds **0 bikes** (lost the class) → for obstacles keep the COCO model.
- **YOLO-World v2 s / YOLOE-11s** (`1_CODE/m05_openvocab.py`), as promised in the work plan for 23.11: asked for e-scooters and strollers →
  1 real scooter (called "stroller"), 11 wrong (bikes, backpack, planter); no strollers in the clips; ~140 ms/frame (3x YOLO11n).
  Not usable as is; next semester: film scooters/strollers, tune prompts or fine-tune with extra classes.
- Note: `2_MILESTONES/M05_newclips_bikes_openvocab_22.11.md`. YOLOE downloads a 600 MB text encoder (`mobileclip_blt.ts`, ignored in git).
- Open: label the test set (both); fix for red clothes (smaller head area for small boxes) tested on those labels.

## 22.11.2026 15:45, Nimer: labelling set-up for the new clips (Med Faculty, bikes) — TEST-ONLY
- New `1_CODE/m05_newclips.py`, same pattern as `m05_finetune.py`. The frames become a **new test set** (never train on
  them): an honest check of the hand filter, the head-colour threshold and later M06 tracking on unseen footage.
- **Dareen (you have the clips): `python m05_newclips.py prepare`** → 1 frame every 2 s from both clips (~300 frames),
  draft labels (YOLO11l + turban colour), every other frame to each half → `M05_data/test_22.11/` → push.
  Tested end to end on a 20.11 clip on Nimer's laptop.
- Then both: `python m05_newclips.py label nimer` / `label dareen` (label_tool, same keys) → `M05_data/test_22.11/labels`;
  `python m05_newclips.py check` shows both halves' progress. **Rules = M05 test labels:** user = the turban man always,
  person = every other real person (small and far ones too), no box on bikes / posters / hands / app buttons.
- Please also fill the shot log (who wore the turban, when he is hidden) in `2_MILESTONES/filming_22.11_bikes_med_faculty.md`.

## 22.11.2026 15:15, Dareen: NEW FILMING outside the Medical Faculty (bikes) + M06 tracking tool started
- Two new drone clips on Dareen's laptop, `3_EVIDENCE/2026-11-22/`: `143404_recording_session1.mp4` (~5 min, 450 MB),
  `144943_recording_session2.mp4` (~5 min, 7-8 m high next to trees). Battery 59% → 14% in ~5 min (~9%/min, ~11 min per
  battery). Lesson: land at 30%. Details + shot log to fill in: `2_MILESTONES/filming_22.11_bikes_med_faculty.md`.
- New `1_CODE/m06_track.py` (M06): YOLO11n + ByteTrack/BoT-SORT keeps the user's ID once the turban identified him;
  compares with the old M05 method (colour + 1 s fallback) on the same frames, and prints a dry-run distance-controller
  command (turn / forward / back / hold) on the video. `python m06_track.py <clip> [--tracker botsort]`.

## 22.11.2026, Dareen: deck for Monday shortened; full deck kept for the semester presentation
- **For Gabi on 23.11: `4_DOCUMENTS/M05_for_Gabi_23.11_short.pptx` / `.pdf` (11 slides):** title, M03 closed, the M05 question,
  three ways compared, key result (wrong person 36.5% → 0%), picture, the three YOLO models vs 90%, **all 8 detectors
  (accuracy vs speed chart)**, **all results in one table** (new slide, from full_comparison_22.11), final choice, M06 +
  questions. 11 slides. Focus: comparing and deciding.
- **Full 15-slide deck saved as material** in `4_DOCUMENTS/presentation_material_end_of_semester_A/` with a README of which
  slides to reuse (design, all 8 detectors, failures, fine-tuning, earlier projects). Linked from the presentation log.

## 22.11.2026 ~09:05, Dareen: ONE TABLE OF ALL 8 DETECTORS (same laptop, same run) + final choice
- `M05_data/results/all_models_22.11/m05_all_models.md` (best per column in bold; script `1_CODE/m05_all_models.py`):
  YOLO11n, YOLOv12n, YOLO26n, both fine-tunes, YOLO11s, YOLO11m, YOLO11s at 1280 px — detection (all / following
  distance / dark), precision, hybrid found / wrong / false alarm / frames correct, FPS, portrait yes/no.
- New numbers: YOLO11s hybrid 75.0% found, 1.0% wrong, 14 FPS; YOLO11m hybrid 76.0% found, 0% wrong, 97.1% at following
  distance but 6.5 FPS; YOLO11s-1280 hybrid 0% wrong but 3.6% false alarms, 5 FPS.
- Requirements ≥90% (following distance) + ≥15 FPS + 0% wrong + 0% false alarm → met by the three nano models;
  **final choice YOLO11n + turban colour** (best of the three on detection). Nimer: agree?

## 22.11.2026 ~08:50, Dareen: GENTLE fine-tuning — portrait still gone, detection almost back (84.4%)
- Found the main cause of the first run's drop: it trained a 1-class model, so YOLO's class layer was rebuilt from
  scratch. Gentle run (`python m05_finetune.py train 15 gentle`): keeps the 80-class head (person = 0), freezes the first
  10 layers, AdamW lr 0.0005, 15 epochs (~13 min) → `1_CODE/yolo11n_drone_gentle.pt` (not in git).
- Same 152 test frames, brightness 1.0 (0.35 in brackets) — `M05_data/results/finetune_22.11/m05_full_comparison_3models.md`:

  | Model | Detection all | People > 1/4 | Precision | Hybrid found / wrong / false alarm | Portrait |
  |---|---|---|---|---|---|
  | YOLO11n original | **85.4 (84.8)** | **96.2** | **94.1** | **73.1 / 0 / 0** | person 0.55-0.62 |
  | fine-tuned (1st) | 77.1 (69.5) | 85.4 | 92.4 | 66.3 / 1.9 / 10.7 | gone |
  | **fine-tuned gentle** | 84.4 (83.5) | 95.0 | 93.7 | 70.2 / **1.9** / 0 | **gone** |

- Gentle = the portrait false positive removed for only −1 point detection, same speed — but 2 of 104 frames now pick
  the wrong person (the original had 0), and still below 90% on all people.
- **Proposal:** Monday winner stays the original YOLO11n (best on every test number); show the gentle model as the
  promising next step ("removes painting false positives at the same speed; needs more people in the training data").

## 22.11.2026 ~08:40, Nimer: panel shows the files Dareen changed
- `tools/project-updates`: new section "Files Dareen changed" = every file in Dareen's pushed commits of the last 2 days,
  newest first, click to open; frame/label folders under `M05_data/` (and folders with >10 files) are one row each.
  Only pushed work is visible. (Dareen: the same panel can show Nimer's files; ask your Claude if you want it.)
- Nimer agrees with keeping the original YOLO11n (his own re-training was stopped at round 6: your result settles it).

## 22.11.2026 ~08:30, Dareen: FINE-TUNING RESULT — portrait gone, but fewer people found → keep YOLO11n
- Trained `yolo11n_drone.pt` (30 epochs, 288 train / 47 val frames from the 335, ~40 min on CPU; not in git).
  Tested on the SAME 152 test frames (`M05_data/results/finetune_22.11/`):

  | Model | Detection all (1.0 / 0.35) | Detection people > 1/4 | Precision | Hybrid: found / wrong / false alarm | FPS |
  |---|---|---|---|---|---|
  | YOLO11n (original) | **85.4 / 84.8%** | **96.2%** | 94.1% | **73.1 / 0 / 0%** | 28 |
  | YOLO11n_drone (fine-tuned) | 77.1 / 69.5% | 85.4% | 92.4% | 66.3 / 1.9 / 10.7% | 32 |

- **Good:** the framed portrait in 154848 is no longer detected at all (was "person 0.63-0.64"); same speed.
  Picture: `portrait_before_after_yolo11n_vs_drone.jpg`.
- **Bad:** it finds 8 points fewer people (worse in the dark) at every confidence (0.1: 79.0% vs 86.7%). Likely reason:
  335 frames with only ~366 people (109 empty) is too little — the model "forgets" part of what it knew about people.
- **Decision proposal: keep the original YOLO11n** as the winner; report fine-tuning as tried. Next try needs more
  people (new filming) and gentler training (freeze the backbone, lower learning rate, mix in general person images).

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
