# PROJECT NOTEBOOK — everything we said we would do, check or research (written 25.11.2026)

One place so nothing gets lost. Tick `[x]` when done and push. Newest decisions first in each section.
Tomorrow's step-by-step checklist: `M06_field_day_manual.md`. M06 plan after the day: `M06_plan_together_step_by_step.md`.

## A. Decisions already made (do not re-open without new data)
- **Method:** hybrid = YOLO finds people + turban colour on the head picks the user (colour alone / YOLO alone lose: 24–27% wrong person, 25–33% false alarms).
- **Detector:** YOLO11n = safe default; **YOLO11m is really better** (paired McNemar test, 403 frames: 7 vs 0 frames, p = 0.016, +1.7 pts).
  **Rule:** use 11m if it keeps >= 15 FPS live on battery (measured on the field day, B4), else 11n. YOLO26n dropped (no gain). YOLO26m = candidate for obstacles (finds more far people, 74% vs 68%).
- **Input size 640 px, confidence 0.25** (tweak sweep: lower cut-off adds wrong boxes; 800 px +2.5 pts at 23 FPS = re-test in M06).
- **Tracker lead: BoT-SORT** (best of 6 on the grid). **Sticky ID** (switch only after 3 turban frames on the new person) + **states FOLLOWING / UNSURE (<2 s) / LOST (>=2 s)** = in `1_CODE/m06_follow.py`.
- **User score per box** = identity score (Gabi), not YOLO confidence. Turban + clothes colour (`--colour`, E = "this is me").
- **No red shirt in the picture during closed-loop flights** (it can steal the lock). Red shirt = filming only.
- **Hold-out rule:** the 403 hand-labelled M05 frames are now a TEST set; the new crossing clips = M06 hold-out. Never tune thresholds on them.
- **Work-plan req. 1 honesty:** user DETECTED 99% (lab) but IDENTIFIED 73% → M06 must close the gap to >= 90%.

## B. To-do — practical (owner)
- [ ] **Field day** (both) — `M06_field_day_manual.md`.
- [ ] Download the infographic deck as .pptx from claude.ai (signed in) and share it with Nimer (Dareen).
- [ ] Upload `3_EVIDENCE/2026-11-22/143404_recording_session1.mp4` + `3_EVIDENCE/2026-11-23_M05_final/demo_highlights_M05_1min.mp4` to the shared Drive (Dareen).
- [ ] Find the 12.11 "moves" flight video (only the log is on Dareen's laptop) — phone / Nimer.
- [ ] Nimer's AI-log line for M05 in `5_LOGS/Project_logs.xlsx`.
- [ ] Update the CLAUDE.md "switch to YOLO11m" line after B4 (11n or 11m, with the FPS on battery).
- [ ] Ask Gabi / the lab: portable power station for the laptop in the field (pure sine, >= 300 W, >= 500 Wh) or a budget.
- [ ] Crazyflie: reply to Israel with Nimer (advice: decline politely, keep as optional extension).
- [ ] Deck `4_DOCUMENTS/M05_for_Gabi_24.11_GPU_update.pptx`: final table in, speaker notes slides 13–15, keep/remove slide 15.
- [ ] `m05_final_table.py` — one final comparison table for the semester-A presentation (all methods, CI, speed CPU/GPU charger/battery).
- [ ] TensorRT FP16 for YOLO11m (faster on the GPU → maybe 11m without the speed worry); re-check accuracy on the 403 frames.
- [ ] Requirement trace table `2_MILESTONES/M06_requirement_trace.md`: exact words of the approved plan → test → result → status.
- [ ] Agree the M06 pass lines with Gabi (user kept >= 90%, <= 1 swap / 10 crossings, 0 wrong follows, 60 s, >= 10 FPS).

## C. To-do — M06 computer work after the field day (≈ 8 h)
- [ ] Label the crossing clips (+ the "above" clips) with track IDs in **CVAT** (~5 frames/s, user = ID 1). ~4 h.
- [ ] Measure M05 vs M06 on them: % user kept, wrong-person frames, ID swaps per crossing, recovery time, **IDF1 / HOTA (TrackEval)**, 95% intervals; turban-only vs `--colour`; 11n vs 11m (McNemar).
- [ ] Count the command delay in the 60 fps video (frames × 16.7 ms, 10 repeats) → delay budget: video 256 ms + detection ~34 ms + command ?
- [ ] Yaw-rate per stick from B3b → set K; add D term + prediction; step-test metrics (rise time, overshoot, settling, steady error) before/after.
- [ ] **Level vs above** (Gabi): turban seen %, user score, YOLO found % on the same scenes.
- [ ] One-page M06 summary + decision log + 1-min demo + questions for Gabi.

## D. Research / deep dives (ranked by how much they help the main risk = following the wrong person)
1. [ ] **Red-shirt fix at the source: YOLO pose (YOLO11n-pose)** → find the REAL head (nose/ears/shoulders) and look for the turban only there. Today the "head" = top 35% of the box, which holds a far person's shirt.
2. [ ] **Deep re-ID body score** (BoT-SORT `with_reid`, or OSNet via BoxMOT): appearance fingerprint learned at enrolment; compare with `--colour` (clothes histogram) on the crossing clips. Cost: GPU 2–4 ms/box.
3. [ ] **Combine the cues properly:** fit weights (logistic regression) for turban / colour / re-ID on TRAINING clips, test on hold-out → a calibrated "probability it's the user"; tune `COMBO_MIN` (now 0.55, first guess).
4. [ ] **Camera tilt automation** (gimbal, 1 axis): find the DJI Fly slider (field-day A3b) → `tilt_up / tilt_down / tilt_recentre` via ADB touches → controller "keep her head in the top third" (fixes the frames where her head is cut off = our lowest user scores).
5. [ ] **Yaw control done like control engineers:** model = yaw rate per stick + start/stop lag + 0.3 s video delay; PD + prediction (Smith-predictor idea); measured step response.
6. [ ] **Tracker comparison as in the work plan:** ByteTrack, BoT-SORT, OC-SORT, StrongSORT on the crossing hold-out (IDF1, HOTA, losses, recovery time).
7. [ ] **Laptop speed:** long-run FPS on charger vs battery (it throttles 4.6 → 2.6 GHz), TensorRT, power station; every number logged with conditions (the follow CSV now logs battery % / plugged).
8. [ ] **Optical flow** (not for identity): ego-motion check of how much the drone really turned; second check of the delay.
9. [ ] **Obstacles (next semester):** film strollers / e-scooters / bikes, label, train ONE YOLO11n with all classes together (fine-tuning on people only made it forget bikes); YOLOE / YOLO-World only as labelling helpers (they boxed bikes as "stroller"). Check YOLO26m for far people.
10. [ ] **Low light** (work plan, by 8.3.27): a real dusk flight instead of the ×0.35 brightness stand-in.
11. [ ] **End of project (work plan):** 20 runs → success rate, arrival time, minimum distance to an obstacle, track losses, latency.

12. [ ] **Nimer: synthesis / emulation / simulation (open-source)** — see Claude's view 25.11:
    - **DECIDED 25.11 (Dareen): build the emulator right after the field day** (needs the B3/B3b delay + yaw-rate numbers). Nimer's own meaning of the idea: still to write down here.
    - **Emulator first (cheap, ~1 day, high value):** replay our recorded clips as a fake live camera; the Neo sees ~118° wide →
      crop a narrower window and SHIFT it when the controller yaws (= virtual turning), with the measured command delay + yaw
      rate (field day B3/B3b). Tune K / D / prediction safely, repeat every crossing 100x, count wrong follows. No flying.
    - **3D simulator (open source: Gazebo + PX4 SITL, Webots; AirSim is archived):** a drone with a camera + a person model with
      a red turban; repeatable crossings and the 20-run end test. Days of setup; the Neo's real dynamics are unknown → only after the emulator.
    - **DJI Simulator in DJI Fly:** stick practice only — no real people in its camera view, so not for our vision tests.
    - **Synthesis (synthetic data):** pasted turbans / red shirts / strollers / scooters, or simulator images, to grow training
      data for next semester's obstacle classes; always test on REAL hold-out clips.

## E. Measured facts to quote (with source)
- Pipeline: video delay 256 ms (mirror hop 60 ms), detection 34 ms (11n CPU) → ~290 ms; command delay = field day.
- Final M05 table (403 frames, hand labels): hybrid 11n 87.8% frames correct, wrong person 1.8% (3/164), 0 false alarms, 96.2% people found at following distance; 11m 89.6%, 1/164, 0.
- User score: AUC 0.914 (turban), user median 0.85 vs others 0.000; turban + clothes colour 0.978; body edges 0.759 (no gain).
- Session 1 hold-out (Nimer): in view correct 85.6%, wrong person 8.2% (red shirt), 0 false picks in 189 empty frames.
- Laptop throttling under long load: all models ~8–10 FPS (24.11).

## F. Questions for Gabi (next meeting)
- [ ] Are our M06 pass lines OK (>= 90% kept, <= 1 swap / 10 crossings, 0 wrong follows)?
- [ ] Level vs above results — which camera angle for the final system?
- [ ] Req. 1 reached through tracking (identity kept between turban sightings) — acceptable as "identified"?
- [ ] Power station / budget for field runs?
- [ ] Is the turban marker acceptable for the final demo, or should identity rely on appearance (re-ID) too?
