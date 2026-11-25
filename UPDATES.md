# Updates log (newest first)
**>>> DAREEN'S OPEN TASKS - ONE LIST (updated 24.11, 02:30). Tick [x] when done. <<<**
Model decision now: **M05 delivered 23.11 = hybrid YOLO11n + turban. Proposal 24.11 = hybrid YOLO11m** (final only if Nimer agrees AND field speed holds).

A. Wed 25.11 night - finish the model choice (in this order, with Claude)
- [ ] 1. Speed check ON CHARGER: Fn+Q performance mode -> say "speed check".
- [ ] 2. Speed check ON BATTERY (the field case) -> say "speed check on battery". Also note how long the laptop battery lasts.
- [ ] 3. "TensorRT FP16": convert YOLO11m, re-check accuracy (403 frames) + speed.
- [ ] 4. FINAL COMPARISON TABLE for the semester-A final presentation: `1_CODE/m05_final_table.py` builds it from saved results
      (markdown + Excel + slide). Rows: colour only, YOLO alone, hybrids YOLO11n/s/m, 12n, 26n/s/m, RT-DETR-L, RF-DETR N/S/M,
      fine-tuned, + YOLO11m TensorRT. Columns: family/year, size, licence | frames correct, user found /164, wrong person /164 + 95% CI,
      false alarms /239 | frames correct on never-tuned 22.11 clips | people: all, following distance, precision | speed: CPU, GPU
      charger, GPU battery | verdict. Footnote with the rules. Slide = compact 6 columns.
- [ ] 5. Deck `4_DOCUMENTS/M05_for_Gabi_24.11_GPU_update.pptx`: put the final table in; speaker notes for slides 13-15;
      decide: keep or remove slide 15 (trackers).

B. Ask other people
- [ ] 6. Nimer: confirm YOLO11m (or keep YOLO11n).
- [ ] 7. Gabi / lab: is there a portable power station (AC socket, pure sine, >= 300 W, >= 500 Wh)? Otherwise budget?
- [ ] 8. Crazyflie: reply to Israel with Nimer (advice: decline politely, keep as optional extension).
- [ ] 9. Upload `3_EVIDENCE/2026-11-22/143404_recording_session1.mp4` to the shared Drive for Nimer (if not done yet).

C. Drone (next time at the field / with the drone)
- [ ] 10. `record_video.py`: last try got no camera frames (DJI Fly must show the camera view; adb PATH line first).
- [ ] 11. Test the new keys T = take off, L = land - on the ground first, with the flight checklist.

D. M06 tracking (due 7.12) - task list in `2_MILESTONES/mentor_plan.md`; first step: YOLO11(m) + BoT-SORT on the 22.11 clips, crossing scenes.

FYI: Windows power mode on charger was set to "Best performance" (24.11). Mentor coach panel hidden this session (files kept; "open the mentor panel").


**NEW for both (Nimer 24.11): message box in the Project updates panel.** At the top: "💬 Message Dareen" (on Dareen's
laptop "💬 Message Nimer"). Type, press Enter → the message is saved as one small file in `messages/`, committed alone
and pushed at once; the other laptop shows a Windows pop-up **"💬 Message from …"** within 2 min, and both panels list
the last 6 messages. Nothing else is committed with it.

**Nimer 24.11 (M06 BoT-SORT on session 1):** `m06_track.py --tracker botsort --step 3` scored on the same 313 labelled
frames: in view **81/97 correct (83.5%), 7 wrong person, 9 none**; 0 false picks in 189 empty frames - about the same as
M05 (83 / 8 / 6). BoT-SORT keeps her ID (frame 7 is now right), but **the colour rule overrides the ID**: the red-shirt
passer-by passes the colour test and the user ID switches to him (frames 8-12; 25 such switches in the clip).
**Proposal (not coded yet - Dareen, tell me if you are editing `m06_track.py`):** "sticky ID" - a colour hit on a
different ID only takes over after ~1 s or if her ID is gone. Details: `2_MILESTONES/M05_session1_holdout_inview_24.11.md`.

**Nimer 24.11 (session 1 in-view labels):** Claude labelled 313 frames (~1/s) of session 1 by eye from the original video:
97 user in view, 27 partly, 189 not in view; then checked every detector pick. **When she is in view: correct 83/97 = 85.6%
(95% CI 77-91), wrong person 8/97 = 8.2%, no pick 6.** Not in view: **0 false picks / 189.** All 8 wrong-person frames are
in the first 13 s: occlusion by a man in front (2) and a **passer-by in a red shirt** (6) - the same failure as the 22.11
clips. → M06 tracker should hold her ID through it. Note + numbers: `2_MILESTONES/M05_session1_holdout_inview_24.11.md`;
CSV + scripts: `M05_data/results/session1_inview_24.11/`. **Dareen or Nimer: spot-check ~30 of Claude's labels.**

**Nimer 24.11 (session 1 result):** G:sync copied `143404_recording_session1.mp4` (+5 missing demo videos → `3_EVIDENCE/from_drive/`).
YOLO11n + turban demo on session 1 (2,501 frames at 8.3 fps, DJI Fly screen recording walking around Med Faculty):
**user picked by the turban colour 29%, fallback 1%, no user 70%.** Checked by eye: when she is in view at a few metres
she gets a correct green "USER 0.86" box; misses include frames where she is out of view and close-ups where only her
sleeve/hand fills the frame (YOLO says "person", no head → no turban). The 70% is NOT a miss rate yet: we need labels
(user in view yes/no) to split it. Open: hand-label ~1 frame/s of session 1 → real "user found / in view" number; her
head covering is a brighter red than the purple-red turban → check the colour range. Demo:
`3_EVIDENCE/m05_user_detection/demo_143404_recording_session1_yolo11n.mp4` (Nimer's laptop).

**NEW for both (Nimer 24.11): push pop-ups.** The Project updates panel (`tools/project-updates`) now shows a Windows
notification for every new commit on GitHub: **Dareen's push → pop-up on Nimer's laptop "New from Dareen" + the commit
titles** (within 2 min), and the pusher gets **"Sent to Nimer ✓"** right away. Pushes made while a laptop was off pop up
once at the next start. **Dareen: nothing to do** if the panel is installed from the repo (it reloads by itself; else
`/plugin install project-updates --marketplace nemerdabdoub/final-project---Nimer-and-Dareen-`). Turn Windows "Do not disturb"
off to see them.

**Nimer 24.11 (session 2 result):** YOLO11n + turban demo on `144943_recording_session2.mp4` finished
(2,464 frames, 8.3 fps): user by turban 0%, fallback 0%, no user 100%. **This is correct:** the clip is a DJI Fly screen
recording from height over the car park/trees with no people near the camera (plus a black gap mid-clip and the app's
on-screen controls). So it counts as a no-user hold-out clip: 0 false user picks in 2,464 frames. Demo:
`3_EVIDENCE/m05_user_detection/demo_144943_recording_session2_yolo11n.mp4` (Nimer's laptop). Open: session 1 (143404) is on
the Drive now → G:sync and test it for the actor; crop app controls / skip black frames before scoring screen recordings.

**Nimer 24.11:** panel got an optional personal "Moodle – upcoming" section (reads a private calendar link kept outside the
repo; it does not show on Dareen's laptop). G:sync: `144943_recording_session2.mp4` copied from the Drive into
`3_EVIDENCE/2026-11-22/` (thanks Dareen!) and YOLO11n + turban detection demo running on it.

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
**LATEST PUSHES (25.11):** Dareen 18:50 – **FULL AUTOMATIC run ✓ (AUTO_TESTS.bat): took off, TURN/FOLLOW/SIDE, landed by itself; all turns right way; user in view 33–55% → drone too slow at max yaw 0.2 → next: 0.3 + predictor** · Dareen 18:00 – `m06_follow.py --side` = SIDE mode (slides sideways with the user, max 0.15; sim runs, sliding not simulated → SIDE TEST in flight after FOLLOW TEST) + video keeps saving when the picture size changes (_part1.mp4) · Dareen 17:05 – `m06_follow.py --predict` (Smith predictor for the 0.5 s loop delay, OFF by default); first sim check inconclusive (real-time sim → runs saw different frames: 0.36 vs 0.30 error) → needs the frame-stepped emulator before any flight; also new `record_loop.py`, field clips walk_60s (143 s) + turn_away (14 s), battery saver fired at 27% ✓ · Dareen 16:45 – **FIELD DAY: first closed loop flown ✓ (yaw FOLLOWING 77-95%, turns 282/282 right way; distance stops at target; loop delay ≈ 0.5 s)** → `2_MILESTONES/M06_field_day_25.11.md`. **Next:** crossings + 60 s + from above (light, passer-by), prediction for the delay · Nimer 16:25 – **`/start_ready` = read-only pre-flight check (`1_CODE/preflight.py`)**: phone by ADB, DRONE_SIM empty, no FORCE_LAND flag, DJI Fly Take Off screen, drone battery > 40%, laptop power, disk → READY / NOT READY; never presses anything (take-off stays by hand, T) · Nimer 16:15 – **FORCE LAND: `/force_land`, `FORCE_LAND.bat` or `python force_land.py` → any running drone script stops the sticks and lands** (check inside `drone_interface.py` + `sim_drone.py`; sim test passed, 0 stick commands after the land order; **NOT table-tested on the real drone yet**) + **`m07_orbit_sim.py`: top-down orbit / sun-fix simulator** (orbit radius error 0.05 m, user centred ±1°, in view 100%; sun-fix from backlit 15 s) · **Next: Block B at the field (B1 → B2 crossing scenes → B4 live speed on battery decides 11m/11n); before the first flight: table-test force land (A6 dry + `FORCE_LAND.bat`)** · Dareen 15:10 – speed/battery corrected for the field: live ~12% slower than offline (27.8 vs 31.7 FPS) → on battery 11m ~18 FPS (B4 decides); laptop also charges the S10 → ~50–55 min heavy work · Dareen 15:05 – checklist §2c **field layout: S10 cabled to the laptop = one BASE** (pilot + laptop at the base, sun behind base and drone, drone 2–4 m in front facing the user, passer-by never between base and drone, 60 fps phone to the side) · Dareen 15:00 – notebook item 13: **sun/backlight self-correction** (detect backlight → orbit so the sun is behind the drone / tilt down / raise EV), planned for when sideways moves exist (M07) · Dareen 14:55 – **A6b colour enrolment live ✓ (FOLLOWING 100%, USER ~0.9, 27 FPS) after fixing the setup; try 1 failed with a window BEHIND her (turban black) → field rule: sun behind the drone**; E key now 1 view/s · Dareen 14:45 – **speed charger vs battery (whole pipeline, GPU): 11n 31.7 / 23.1 FPS, 11m 28.8 / 20.7 FPS → 11m passes ">= 15 FPS on battery" → YOLO11m unless live B4 < 15** (`M05_data/results/speed_charger_vs_battery_25.11/`) · Dareen 14:35 – **table tests passed: recording 751 frames/30 s, live follow dry yaw sign right 269/269, ~28 FPS; adb fix = start drone scripts via `run_with_adb.py`** (+ `countdown.py` for testing alone) · Dareen 14:15 – **camera tilt coded: `gimbal.py to -30` / `level` (range -90..+50 deg, tested on the table)** · Nimer 25.11 – panel cleanup: the shared Project updates panel is now project-only (two personal, laptop-only sections moved out); nothing changes on Dareen's side · Nimer 25.11 – **`1_CODE/make_video_gallery.py`: all project videos on one visual page** (`3_EVIDENCE/ALL_VIDEOS.html`, not in git) → Dareen: run it for your videos · Dareen 25.11 morning – **RED-SHIRT FIX: guarded switch (Nimer's rule) + head area 20% → red shirt never USER on session 1 (was 3 s), switches 10→3; 403 frames: 89.8% correct (was 87.8)** · Nimer 25.11 – **panel for BOTH: messages every 15 s (read from GitHub even if a pull is stuck), live ✅ Checklist of the field-day manual, `/updfd` Dareen log, `/send` box** + `m06_follow.py` reproduced on Nimer's laptop (69/10/20 %, 11.7 FPS CPU) + **BoT-SORT ReID = no gain (5/1500 frames): tracker IDs are right, the selection rule is the weak point** · Dareen 25.11 – **`command_delay_test.py` fixed after the simulator rehearsal**: turn = whole-picture shift (phase correlation, people walking no longer fool it), taps < 2.5 s apart ignored, new `--auto 10` (presses by itself, 3 s apart); sim check 294 ms for a set 250 ms, direction 10/10; checklist B3/B3b use --auto · Dareen 25.11 night – **Nimer's "simulate first": `sim_drone.py` (DRONE_SIM=<video>) - tomorrow rehearsed on the computer, yaw loop sign correct 111/111** · Dareen 25.11 – **easy Word checklist with click-to-tick boxes: `4_DOCUMENTS/M06_field_day_checklist.docx`** (same content as the .md, 74 boxes, 6 pages) · Dareen 25.11 night – **FULL field-day checklist (commands, tools, times, tips) + PROJECT NOTEBOOK of all to-dos / research → Nimer: open `2_MILESTONES/M06_field_day_manual.md`** · Dareen 25.11 night – **checklist: B2b film FROM ABOVE (Gabi; 3.5-4 m, tilt ~30-40 deg) + B3b yaw rate per stick (torque response)**; day ~8 h · Dareen 25.11 night – **power rules in the checklist** (drone: charge the night before, drone OFF during setup, one battery for table tests, land between clips, land at 30%; laptop: close sync/updates/panel, best-performance mode, shade, GPU warm-up) + `m06_follow.py` logs laptop battery % / plugged in each CSV row · Dareen 25.11 night – checklist A3b: camera tilt (gimbal) discovery tomorrow (Neo tilts up/down only; keeps her head in view; tonight the drone battery was empty) · Dareen 25.11 night – **`m06_follow.py --colour` (turban + clothes colour, E = "this is me"): red shirt no longer steals the lock offline; tests added to tomorrow's checklist** · Dareen 25.11 night – **Nimer's cues tested: turban + body colour AUC 0.978 (vs 0.928), edges no gain, flow = ego-motion only; yaw-loop note** · Dareen 25.11 night – **user score per box (Gabi): AUC 0.914, user 0.85 vs others 0.000; red shirt scores 0.99 = main M06 risk** (`M05_data/results/user_score_25.11/`) · Dareen 25.11 night – **tomorrow = M05 leftovers → controller; open `2_MILESTONES/M06_field_day_manual.md`** · paired test 11m vs 11n p = 0.016 (real, +1.7 pts) · new `m06_follow.py` (sticky ID + states + controller, not flown yet) · Dareen 25.11 – **field-day manual** (`2_MILESTONES/M06_field_day_manual.md`, tick boxes + commands + times, ~7 h) + new `command_delay_test.py` (red flash + auto loop delay; dry-run first) · Dareen 25.11 – **M06 plan revised: one 6-8 h day together on Wednesday, drone work first** (crossing scenes, command delay, battery speed), rest on the computer → **Nimer: book a passer-by (red shirt), charge all batteries** · Dareen 25.11 – **M06 plan together, step by step with tick boxes + times** (`2_MILESTONES/M06_plan_together_step_by_step.md`, 8 sessions, ~27 h) → **Nimer: Session 1 tomorrow together** · Dareen 25.11 – **11n vs 11m considerations (not decided):** gap small (+1.8 pts), needs paired test; 11n on GPU not yet measured; neither meets req. 1 → decide in M06 by user identified after tracking; long-run speed (throttling) still open → **Nimer: agree "11n default, 11m candidate"?** · Nimer 24.11 – **panel: "💬 Message Dareen/Nimer" box** (type + Enter → pops up on the other laptop) · Nimer 24.11 – M06 BoT-SORT on session 1, same 313 frames: in view correct 83.5% / wrong 7.2% / 0 false picks ≈ M05 (85.6 / 8.2 / 0) → no gain because the colour always overrides the track ID (red-shirt passer-by takes over); next: "sticky ID" rule · Nimer 24.11 – **session 1 hold-out labelled (313 frames): user in view → correct 85.6% [77–91], wrong person 8.2% (red-shirt passer-by + occlusion, first 13 s), 0 false picks in 189 empty frames** (`2_MILESTONES/M05_session1_holdout_inview_24.11.md`) · Nimer 24.11 – session 1 raw demo run: turban 29%, fallback 1%, none 70% · Nimer 24.11 – **panel now pops up a Windows notification for every push** (yours: "Sent to …", partner's: "New from …") · Nimer 24.11 – session 2 detection result: no people in the clip → 0 users picked in 2,464 frames (correct; 0 false picks) · Nimer 24.11 – panel Moodle section · Dareen 02:00 – laptop speed finding: the Lenovo slows itself under long load (CPU 4.6 → 2.6 GHz) → all models ~8-10 FPS; on battery in the field the same → plan: power station + TensorRT; `m05_speed_gpu.py` now warms the GPU up 20 s · Dareen 01:20 – deck updated: `4_DOCUMENTS/M05_for_Gabi_24.11_GPU_update.pptx` (20 slides: old 17 + new 13 = 12 detectors on GPU, 14 = new choice YOLO11m, 15 = 6 trackers; slide 12 marked "choice on 23.11, CPU only") · Dareen 00:45 – **GPU found on Dareen's (drone) laptop → 12 detectors re-tested (YOLO, RT-DETR, RF-DETR) on 403 frames: proposal = switch to hybrid YOLO11m** (89.6% correct, 1 wrong, 0 false alarms) + all 6 trackers: BoT-SORT best → **Nimer: please confirm YOLO11m** · Dareen 24.11 – Gabi's "check newer models": shortlist + criteria + plan (`2_MILESTONES/M06_newest_models_shortlist_24.11.md`); `m06_track.py --tracker` now also ocsort / deepocsort / fasttrack / tracktrack (all inside Ultralytics 8.4); grid of all 6 running · Dareen 23:58 – **M06 first look at Gabi's YOLO26n idea:** Kalman is in the tracker (any detector); YOLO11n + BoT-SORT 84% user kept, YOLO26n 81%; BoT-SORT half the corrections → lead candidate YOLO11n + BoT-SORT (`2_MILESTONES/M06_tracker_grid_23.11.md`) · Dareen 21:20 – **`4_DOCUMENTS/STAND_OUT_STRATEGY.md`: how we beat the two earlier teams on this topic** (grade weights, what they did and how they measured, our 8 edges, moves per milestone, checklist) + CLAUDE.md rule → **Nimer: please read it** · Dareen 20:55 – new **Mentor coach** panel `tools/mentor-coach` (shows the playbook of the process we are in + "Ask the mentor" buttons; `/mentor`); added to the marketplace → **Nimer: `/plugin install mentor-coach --marketplace nemerdabdoub/final-project---Nimer-and-Dareen-`** · Dareen 20:39 – mentor playbooks `2_MILESTONES/mentor_playbooks.md` (what Gabi would say for each process: flight, experiment, data, controller, decision, meeting, writing, code, debug, pair, new milestone, feeling lost) · Dareen 23.11 – CORRECTION vs approved work plan: req. 1 = user in ≥90% of frames (lab) → detected 99%, identified 73% (M06 tracking closes it); notes, CLAUDE.md and deck fixed · Dareen 23.11 – simple YOLO11n tweaks tested (lower cut-off no; 800 px +2.5 points at 23 FPS → keep 640 for M05, re-test in M06, note §8); Gabi deck updated to 18 slides (all methods, new footage, strollers/scooters) · Nimer 23.11 – panel: new "Claude right now" section (live: what Claude is doing, last 8 actions with times; works for Dareen's Claude too) · Dareen 23.11 – one-page M05 story: problems → actions → evidence → choice (`2_MILESTONES/M05_engineering_journey_23.11.md`); demos of the new clips in `3_EVIDENCE/2026-11-23_M05_final/` (laptop) · Nimer 23.11 – panel: optional "Lab reports" section (Nimer's personal course labs; reads a file outside the repo, so it never shows on Dareen's laptop — no change for her) · Dareen 23.11 – FINAL table on hand labels (all 299 new frames labelled by Dareen): hybrid YOLO11n 1.8% wrong, 0 false alarms, 87.8% correct; 96.2% detection at following distance → YOLO11n confirmed (note §7) · Dareen 23.11 – her 149 test labels done (user agrees with Claude's by-eye marks in 126/129) and **she is labelling Nimer's half too → Nimer: do NOT run `label nimer`** · Dareen 23.11 – hybrid VERIFIED on all videos (392 frames: wrong person 1.3% vs 26-29%, 0 false alarms, 90.3% correct; nano hybrids tie → keep YOLO11n) + which YOLO for M06 / obstacles (note §5-6) · Nimer 17:50 – `4_DOCUMENTS/Next_three_steps_22.11.pdf` + first M06 run on 161951 (tracker keeps the user in 82% of frames vs 76% old way) ·
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

## 25.11.2026, Nimer: video gallery script (all project videos on one page)
`1_CODE/make_video_gallery.py` → `3_EVIDENCE/ALL_VIDEOS.html` + `3_EVIDENCE/_thumbs/` (both not in git): every .mp4 under
3_EVIDENCE as a card (thumbnail at 30 %, date, length, MB, codec, folder), grouped by category with tabs, dark mode; click the
picture = play. On Nimer's laptop: 32 videos (first flights 8, lab 20.11 10, field 22.11 2, M05 demos 10, M06 tracking 2).
Dareen: `python make_video_gallery.py` on your laptop (you have more clips) - re-run after each G:sync / field day.
G:sync 25.11: nothing new on the Drive (the 403 labelled frames for the ML test are not there yet).

## 25.11.2026, Nimer: follow script reproduced + ReID test + panel upgrades for both
- **`m06_follow.py` (Dareen's, default = no `--colour`) on 60 s of session 1, Nimer's laptop, YOLO11n + BoT-SORT, CPU:** exactly
  Dareen's numbers - FOLLOWING 69 % / UNSURE 10 % / LOST 20 %, 10 turban switches, median 11.7 FPS. Checked by eye: t=1 s USER on
  the man in front (occlusion, no history); t=4 s on her (ID 2) ✓; **t=7-11 s on the red-shirt passer-by (ID 4, score 0.97-1.00)
  while she is visible (0.85-0.98)** ✗; t=14 s back on her ✓ → without `--colour` the sticky ID holds the mistake 4-7 s.
  (Dareen's `--colour` run reports the red shirt no longer steals the lock - next: run the same frames with `--colour` and compare.)
- **Deep-learning test: BoT-SORT with ReID** (`with_reid: True`, `model: auto` = YOLO features), same 60 s: **no gain** - same
  69/10/20 %, 10 switches, only 5/1500 frames differ, 11.0 FPS. Why: **the tracker's IDs were already right** (she = 2, he = 4
  all the time); the error is the **identity-selection rule**, not association. → next fix to test on the new crossing clips only:
  enrol her appearance once on a clear view (embedding) + appearance similarity + turban + body colour → learned score
  (logistic / small MLP, leave-one-clip-out); switch only if clearly better for ~1 s and never while her track is visible.
  Needs the 403 frames (`newclips_22.11_frames`, only on Dareen's laptop) → Drive or run there.
- **Panel (`tools/project-updates`, both laptops):** 💬 messages now fetched every 15 s and read straight from GitHub (they show even
  when a local pull is blocked); **live ✅ Checklist** of `M06_field_day_manual.md` (progress bar, per block, next 5 - tick + save);
  `/updfd` = live chronological Markdown log of Dareen's pushes (outside the repo); Moodle date fix. (Nimer's local pull was blocked
  tonight by a stray "A" typed on line 1 of the manual - removed.)

## 25.11.2026 16:15, Nimer: FORCE LAND + M07 orbit simulator
- **Force land (safety back-up, not the first choice - the thumb on the phone stays first):** `/force_land` in Claude Code,
  double-click `FORCE_LAND.bat` (repo root, fastest), or `python 1_CODE/force_land.py`. It creates `1_CODE/FORCE_LAND`;
  `Drone.get_frame()` / `send_speeds()` (and `SimDrone`) check it on every loop → sticks released, `land()` (the 2-step DJI Fly
  landing with screen checks), every later stick command ignored; result in `1_CODE/FORCE_LAND_RESULT.txt`. If no script picks it
  up in 3 s it prints "LAND BY HAND NOW" and removes the flag (so it can never land the NEXT script by surprise).
  Sim test: script landed, **0 stick commands after the order**, no flag left. **Open: table test with the real drone** (A6 dry run →
  `FORCE_LAND.bat` → STOP screen must appear), then once in the air at 1 m. Dareen: I touched `drone_interface.py` and
  `sim_drone.py` only in these two places - tell me if you have local edits there.
- **`1_CODE/m07_orbit_sim.py`** (notebook item 13, curved orbit track): sim_drone can't show sideways moves, so this is a
  top-down sim with the same sticks, delay (SIM_DELAY) and yaw rate (SIM_YAW_RATE). Controller uses only camera-measurable
  inputs (bearing → yaw + feed-forward, box-height distance → forward, constant sideways = orbit). Modes follow / orbit / sun-fix.
  Results (headless): orbit, user still: in view 100%, radius error RMS 0.05 m, centring 1.0°; user walking: 0.49 m / 4.0°;
  sun-fix from fully backlit: sun behind the drone after 15.3 s (random walk 16.9 s). Assumes V_MAX 2 m/s at full stick → replace
  by the B3b field numbers. Run: `python m07_orbit_sim.py` (O orbit, S sun, D direction, W walk).

## 25.11.2026 16:45, Dareen + Nimer: FIELD DAY results - first closed loop flown ✓
`2_MILESTONES/M06_field_day_25.11.md`. Highlights: **B5 yaw-only closed loop: FOLLOWING 77% / 95%, all 282 turns in the right
direction, ~20 FPS live**; **B6 distance + yaw: moved toward the user and stopped at the target size (0.47 vs 0.45) by itself**;
**loop delay ≈ 0.5 s (command ≈ 256 ms, 2 samples)**; table tests: tilt coded, recording, dry follow (yaw sign 269/269), colour
enrolment (USER ~0.9 after fixing backlight). Not done: crossings, 60 s clip, from above (no light). Lessons: "go" only when
hovering; keep DJI Fly on the camera view; sun behind the drone; delay → prediction next.

## 25.11.2026 14:15, Dareen: camera tilt (gimbal) found and coded - `1_CODE/gimbal.py`
- In DJI Fly's camera view the handle ( ^ = v ) LEFT of the picture tilts the camera: drag up = up, down = down, angle shown on a scale.
- Range **-90 deg (straight down) ... ~+50 deg**, **11.4 px per degree** (portrait screen). Tested from the laptop by ADB:
  `python gimbal.py to -30` -> exactly -30 deg; `python gimbal.py level` -> 0-1 deg. tilt_to() goes to the -90 stop first (known start).
- Remove the gimbal guard before tilting. Measured in PORTRAIT layout; if flights run in landscape, re-measure.
- Next: "keep her head in the top third" tilt controller; B2b "from above" can use `gimbal.py to -30`.

## 25.11.2026 morning, Dareen: RED-SHIRT FIX = guarded switch + head area 20% (thanks Nimer for the eye check + ReID test)
- Nimer's finding: the tracker IDs are right (her 2, red shirt 4; ReID changed only 5/1500 frames) -> the problem is the CHOICE rule.
- **Head area 20% instead of 35%** (anatomy: head ~1/8 of the body + turban, chosen before the run): `1_CODE/m05_head_area_test.py`
  on 403 frames: user found 70.1 -> **75.0%**, frames correct 87.8 -> **89.8%**, wrong 3 -> 2, false alarms 0 -> 0, AUC 0.914 -> 0.919.
  Alone it does NOT stop the red shirt (still 0.98).
- **Guarded switch** (Nimer's rule 3, now the default in `m06_follow.py`): USER moves to another person only if that person looks
  like the user for **1 s** AND her track is **out of view** or her smoothed score is **< 0.30** (and the other is 0.30 higher).
  Session 1, 60 s: **red-shirt man never gets USER** (old: 3 s, at 0.97-1.00), switches 10 -> 3. Cost: 1 s longer on the man in
  front at the very start. With `--colour` + automatic enrolment it stuck 9 s on that man (enrolment learned a merged box) ->
  enrol with E only when she is alone. Old rule: `--old-switch --head 0.35`. Table: `M05_data/results/head_area_25.11/summary.md`.
- One clip seen before -> confirm on the new crossing clips. Checklist A2 updated (old vs new video).
- Nimer's re-ID + fitted-score plan (enrol embedding, logistic/MLP, leave-one-clip-out): agreed as the next step on the crossing clips.

## 25.11.2026 night, Dareen: Nimer's "simulate first, like Vivado" - done: simulated drone + rehearsal of tomorrow
- `1_CODE/sim_drone.py`: a simulated drone with the same methods as `Drone` (camera = recorded clip shown through a 60% window;
  yaw slides the window = virtual turning, delay 0.25 s, 90 deg/s at full stick - replace with the field-day numbers).
  Switch: `set DRONE_SIM=<video>` (cmd) -> every script uses it unchanged; `set DRONE_SIM=` = real drone. 3 lines added at the end
  of `drone_interface.py` (nothing changes when DRONE_SIM is empty).
- Rehearsal on session 1: `m06_follow.py --live --dry` and `--live` run; **yaw sign = error sign 111/111, turns re-centre the user**
  (right turn -> error -0.02, left -> +0.10 in 0.6 s); `record_video.py` records. Key presses not tested (A5/A6b tomorrow).
- Checklist (md + Word) updated: A1 **"set DRONE_SIM=" before the real drone** + optional 10-min rehearsal.

## 25.11.2026 night, Dareen: full field-day CHECKLIST (exact steps, commands, tools, times, tips) + PROJECT NOTEBOOK
**Nimer: open `2_MILESTONES/M06_field_day_manual.md` - tick each box as we go.** New in it: roles table, pack list
(drone, phones, cables, apps, laptop, measuring tools: tape measure, ground marks, 60 fps phone + tripod, angle app),
tonight T1-T4, every step with the exact command (`set GPU=...` then `%GPU% ...`), what you should see, tips, clock slots
(start 10:00: A 10:00-11:50, field ~12:30-17:45, C ~18:30-19:45), drop order, critical safety notes.
**`2_MILESTONES/PROJECT_NOTEBOOK_todo_research_25.11.md`:** decisions made, practical to-dos with owners, M06 computer work,
11 research / deep-dive points ranked (pose head, re-ID, fitted weights, gimbal, yaw control, trackers, laptop speed,
optical flow, obstacles, low light, 20 end runs), facts to quote, questions for Gabi. CLAUDE.md status updated.

## 25.11.2026 night, Dareen: Gabi's "film from above" + yaw rate (torque) added to tomorrow's checklist
- **B2b from above:** same scenes at 3.5-4 m height, ~4 m away, camera tilted down ~30-40 deg (pilot moves the gimbal on the
  phone by hand): cross_front_LR_above, turn_away_above, redshirt_side_above, continuous_60s_above. Why: the turban is the top
  of the head -> seen from every side and less overlap in crossings; price: smaller in the picture, YOLO learned side views.
  Later: level vs above compared (turban seen %, user score, YOLO found %).
- **B3b yaw rate per stick:** 2 s pulses at stick 0.2 / 0.3 / 0.4, filmed at 60 fps -> degrees per second per stick, start/stop
  time. Yaw is a quadcopter's slowest axis (motor torque difference); with the ~0.3 s delay it sets K / D / prediction.
- Day is now ~8 h + travel; drop order if short: B6 -> B5b -> cross_far/out_and_back -> redshirt above. Camera tilt automation
  after A3b discovery.

## 25.11.2026 night, Dareen: `--colour` in m06_follow.py (turban + clothes colour) + added to tomorrow's checklist
- `1_CODE/user_score.py`: body colour functions; `1_CODE/m06_follow.py --colour`: user score = (turban + clothes colour) / 2,
  decides the user after a **"this is me" enrolment** (LIVE: user alone, close, facing the drone -> press **E** 3x; OFFLINE:
  automatic on the first 5 frames with a clear turban and one person). Without --colour nothing changes.
- Offline, 60 s of session 1: **red shirt no longer steals the lock** (user 0.71 vs red shirt 0.64; turban only: red shirt
  "USER 0.99"); ID switches 10 -> 5. Margin small (0.64 vs threshold 0.55) -> test on the new crossing clips.
- Manual updated: A2 compare both videos, **A6b live dry enrolment**, B2 **every clip starts with 3 s of the user alone**
  (enrolment view), B4 FPS with colour, **B5b yaw with colour** (only after B5 is calm), C3 compare both on the crossings.

## 25.11.2026 night, Dareen: Nimer's ideas tested - colour shades, body edges, pixel motion, CPU vs GPU, yaw loop
Note: `2_MILESTONES/M06_nimer_ideas_body_cues_motion_yaw_25.11.md` · script `1_CODE/m05_body_cues.py` · `M05_data/results/body_cues_25.11/`.
- Live-style enrolment (first 5 confident-turban frames per clip = user template), 350 boxes: **turban 0.928, body colour
  0.846, body edges 0.759, turban + colour 0.978 (AUC)**, colour costs 0.13 ms/box on CPU -> **Nimer was right: colour shades
  help and are CPU-cheap**; body outline adds nothing. Red shirt 0.93-0.99 -> 0.62-0.79 (better, not solved; enrol on a clear view).
- Optical flow: not an identity cue; useful for ego-motion (how much the drone really turned) and the delay check.
- CPU vs GPU: YOLO needs the GPU; cues + controller on CPU.
- Yaw loop explained (error -> angle -> stick, dead band, max, rate limit; delay causes wobble -> small K, then D term + predict
  ahead) + how to measure it (rise time, overshoot, settling, steady error) from tomorrow's B5 CSV.

## 25.11.2026 night, Dareen: USER SCORE per box (Gabi's "0.0x for person, high for user") + histogram
Gabi read the box numbers as "is this the user"; they were YOLO detection confidence (is it a person). New **user score 0..1**
(`1_CODE/user_score.py`, built from the hybrid's own turban measurements) = identity score, like a re-ID match score.
`1_CODE/m05_user_score_hist.py` on the 403 hand-labelled frames (YOLO11n): **user median 0.85 vs other people 0.000,
>= 0.5: user 76% / others 2.2%, ROC AUC 0.914**, user top-scored in 147/152 frames. Histogram + hard cases + summary:
`M05_data/results/user_score_25.11/`. Demo boxes in `m06_follow.py` now show the user score.
**Honest weak spot:** the red-shirt passer-by (session 1) scores 0.97-0.99 (far = small box, the "head" area holds his shirt) and
the follow demo LOCKED on him at the start -> live, the drone would turn to the wrong person. Manual updated: no red shirt
during closed-loop tests tomorrow; fix ideas to test on the new crossing clips (not on these test frames).

## 25.11.2026 night, Dareen: tomorrow = M05 leftovers -> CONTROLLER in one day; paired test done; `m06_follow.py` built
**Nimer: open `2_MILESTONES/M06_field_day_manual.md` - the tick-box checklist for tomorrow (7.5 h + travel).**
- **Paired test 11n vs 11m** (`1_CODE/m05_paired_test.py`, 403 frames, `M05_data/results/paired_test_25.11/paired.md`):
  11m right / 11n wrong in 7 frames, the opposite in 0 -> **p = 0.016: a real but small gain (+1.7 pts)**. 26m vs 11n: 7 vs 2, p = 0.18.
  Rule for tomorrow: **YOLO11m if it keeps >= 15 FPS live on battery, else YOLO11n** (measured in the field, step B4).
- **`1_CODE/m06_follow.py`** (new file; m06_track.py untouched): BoT-SORT + **sticky ID** (switch only after 3 turban frames
  on the new person, not on ours) + **FOLLOWING / UNSURE (<2 s) / LOST (>=2 s)** + **P-controller** (yaw from box centre,
  forward from box height only with --forward; dead band, max yaw 0.25, rate limit; non-FOLLOWING = hover at once).
  Modes: `--video` offline, `--live --dry`, `--live` (yaw only), `--live --forward`. Offline 60 s of session 1: FOLLOWING 69%,
  UNSURE 10%, LOST 20%, 10 turban switches (NOT checked by eye). Never run on the real drone yet.
- Day plan: A) laptop 1h45 (check follow video by eye, connect, recording, dry runs, FPS) -> B) field 4h30 (crossings,
  command delay, live dry on battery = model choice, **first closed loop yaw only**, then yaw + distance if calm) -> C) 1h15.
- Left for later: CVAT labels of the crossings + measuring (IDF1/HOTA) + delay from the 60 fps video + write-up (~8 h).

## 25.11.2026, Dareen: field-day MANUAL (tick boxes, commands, times) + new `command_delay_test.py`
`2_MILESTONES/M06_field_day_manual.md`: aim, tools checklist, tonight prep, Block A laptop 1.5 h (connect, fix recording,
dry-run delay script, T/L keys), Block B field ~4 h (8 crossing clips in priority order + 60 s clip, command delay 10 presses
filmed at 60 fps), Block C 1.25 h (backup, filming note, first BoT-SORT look). ~7 h + travel.
`1_CODE/command_delay_test.py` (not flight-tested yet; `--dry` sends nothing): Y/U = short yaw, screen flashes RED with a
stopwatch for the 60 fps video, and it auto-measures the loop delay from the drone picture (command delay ~ loop - 256 ms).
Field yaw-follow test moved to later (needs the controller); long battery speed test = at home.

## 25.11.2026, Dareen: M06 plan REVISED - one long day together (Wednesday, 6-8 h), drone first
`2_MILESTONES/M06_plan_together_step_by_step.md` now: aim + pass lines + tools list; THE DAY = A) laptop prep 1.5 h (fix
record_video.py, command-delay script, test T/L keys) -> B) field 3.5-4.5 h (8+ crossing scenes incl. red shirt, 60 s clip,
command delay filmed at 60 fps, speed on battery live, optional yaw-only test) -> C) copy + first look 1-1.5 h.
After the day: computer only (~19 h: sticky ID, states, CVAT labels, measure, delay, controller offline, write-up) by 5.12.
**Nimer: we need a third person as passer-by (red shirt) and all batteries charged.**

## 25.11.2026, Dareen: M06 plan to do TOGETHER, step by step with tick boxes and times
`2_MILESTONES/M06_plan_together_step_by_step.md`: 8 sessions 26.11-5.12 (~27 h) + buffer 6.12. Order: pass lines + requirement
trace + sticky-ID rule (26.11) -> safety states -> film crossing scenes (hold-out) -> label in CVAT -> measure vs M05 baseline
(% kept, ID swaps, recovery, IDF1/HOTA, 11n vs 11m paired) -> command delay -> controller offline/ground/hover -> write-up.
**Nimer: we start with Session 1 tomorrow (26.11) together.**

## 25.11.2026, Dareen: YOLO11n vs YOLO11m - considerations before we decide (no new runs; NOT decided)
Discussion only, to settle together. Numbers are the existing ones (403 hand-labelled frames, hybrid = + turban).

| | YOLO11n CPU | YOLO11m CPU | YOLO11m GPU |
|---|---|---|---|
| frames correct | 87.8% | same as GPU | 89.6% |
| wrong person | 3 / 164 | | 1 / 164 |
| false alarms | 0 | | 0 |
| speed (short benchmark) | ~30 FPS | ~6 FPS (fails >= 10) | ~45 FPS |

Considerations:
1. **The accuracy gap is small** (+1.8 points, 2 fewer wrong frames). ~+-3 points is the range of ONE method alone; the right
   check for two models on the SAME frames is a **paired test (McNemar: only frames where one is right and the other wrong)**. Not run yet.
2. **Missing option: YOLO11n on the GPU** (probably > 100 FPS, not measured). Fair GPU comparison = 11n vs 11m, both on GPU.
3. **Neither meets req. 1** (identify the user in >= 90%): 11n 70.1%, 11m 74.4% of her frames. Tracking (M06) must close the gap,
   not the detector. Nimer's session-1 hold-out (8.2% wrong person, red shirt) says the same: the fix is the sticky-ID rule.
4. **Caution on "11n on CPU meets everything":** the ~30 FPS is a short benchmark; Dareen's 02:00 finding = under long load the
   laptop slows itself (CPU 4.6 -> 2.6 GHz) and all models drop to ~8-10 FPS. So the long-run speed tests (charger + battery) still decide.
5. **Battery:** laptop stays on the ground, Neo flights < 20 min -> one 10-min test of 11m on GPU on battery answers it.

**Suggested wording (Nimer, agree?):** "YOLO11n = default (safe fallback); YOLO11m = candidate. Detector is one setting in the M06 code;
we run the tracker comparison with BOTH on the GPU and choose by *user identified after tracking* + ID switches (the req. 1 number)."
Open: paired test, long-run speed on charger + battery (tasks A1-A2 above), Nimer's answer to task B6.

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
