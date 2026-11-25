# M06 user tracking: plan done TOGETHER (Nimer + Dareen)

**25.11 night: the Wednesday day now covers M05 leftovers → controller; use `M06_field_day_manual.md`. Sticky ID, states and the controller are built (`1_CODE/m06_follow.py`); the paired test is done. Left after the day: labels + measuring + write-up.**

Due: **Mon 7.12.2026**. Written 25.11, revised the same day: **one long day together (Wednesday, 6–8 h), drone work FIRST**,
so everything after it can be done on the computer. Tick `- [ ]` → `- [x]` and push.

## 1. The aim (where we are heading)
**M06 question:** does the drone keep the SAME user through crossings and turned-away moments, and what does it do when unsure?
- M05 picks the user by the turban in **each frame alone** → identified 73% (lab), wrong person 8.2% on session 1 (red-shirt passer-by).
- M06 adds **memory**: a tracker (BoT-SORT) keeps the user's ID between turban sightings; a **sticky-ID rule** stops a
  passer-by from stealing it; **safety states** (FOLLOWING / UNSURE / LOST) tell the drone what to do.
- Then the first **closed loop**: box on screen → stick command → drone turns / keeps distance (M07 builds on it).

**Pass lines** (agree at the start of the day, then confirm with Gabi):
| What | Pass line | Source |
|---|---|---|
| User kept (correct ID) | >= 90% of frames she is in | work plan req. 1 |
| ID swaps on crossings | <= 1 in 10 crossings | mentor plan |
| Wrong-person follows | 0 | safety |
| Continuous tracking | 60 s, track losses counted | work plan req. 4 |
| Speed | >= 10 FPS for the whole pipeline, long run | work plan req. 3 |

## 2. Tools we need
**Hardware (bring to the field):** DJI Neo + **all batteries charged** (>= 3) · Samsung S10 with DJI Fly + USB cable · Dareen's
laptop (GPU) **fully charged** + charger · a second phone that films at 60 fps (for the command delay) · the purple-red turban ·
a **third person** as passer-by (ideally in a red shirt = the hard case) · cones / 2 marks on the ground (3 m and 6 m) · stopwatch app.
**Software (check at home):** scrcpy + ADB (lab repo) · `drone_interface.py` · `record_video.py` (laptop recording) ·
`m06_track.py` (YOLO11n + BoT-SORT + turban) · `latency_test.py` · GPU env `C:\Users\LOREN\venvs\gpu` ·
later: **CVAT** (labelling with IDs), **TrackEval** (IDF1 / HOTA), Ultralytics trackers (BoT-SORT, ByteTrack, OC-SORT).

---

## 3. THE DAY (tomorrow, Wednesday) — 6–8 h, drone first
**Detailed tick-box manual with commands and times: `M06_field_day_manual.md` (use that one on the day).**
### Block A — at the laptop, before leaving (≈ 1.5 h)
- [ ] A1 `git pull`, read this plan together; agree the pass lines above (15 min)
- [ ] A2 Charge check: all drone batteries, phone, laptop 100% (5 min)
- [ ] A3 **Fix the recording blocker:** `record_video.py` got no frames last time (DJI Fly must show the camera view; adb PATH
      first). Test it indoors, drone on the table, 30 s recording → a file with real frames (30 min)
- [ ] A4 Small command-delay script: on a key press, send ONE yaw command and print/log the exact time; also show the time
      big on the laptop screen (Claude writes it, we test it with the drone on the ground, props off) (30 min)
- [ ] A5 Test the new keys T = take off, L = land **on the ground first** (props off / motors only per checklist) (10 min)
**Backup if A3 fails:** the Neo also records video on the drone itself → download it later from DJI Fly. Film anyway.

### Block B — at the field (≈ 3.5–4.5 h incl. setup, ~6 batteries of flying)
Before every flight: phone in hand, DJI Fly in **Manual Control**, big open space, battery > 40%, Ctrl+C = stop, land by hand.
Fly at following height **1.5–2 m, 3–6 m from the user**. Each clip 60–90 s. Record on the laptop AND on the drone.

- [ ] B1 Setup, marks at 3 m / 6 m, first hover check (20 min)
- [ ] B2 **Crossing scenes** (the M06 hold-out test set — never tuned on) (≈ 75 min):
  - [ ] passer-by crosses **in front** of the user, left→right, then right→left
  - [ ] passer-by crosses **behind** the user, both directions
  - [ ] crossing **close** (1 m from the user) and **far** (5 m)
  - [ ] passer-by in a **red** shirt walks next to the user for 10 s (the M05 failure)
  - [ ] user **turns away** (turban hidden) for 3–5 s, then back
  - [ ] user walks **out of frame and back in**
  - [ ] **60 s continuous** clip, user walks normally (req. 4)
- [ ] B3 **Command delay** (≈ 40 min): drone hovering, the second phone films the laptop screen + the drone at 60 fps;
      press the key 10 times (yaw left/right) with pauses → later we count frames from "sent" to "drone moves"
- [ ] B4 Laptop battery % at start and end of the field time (the long speed test on battery is done at home, no drone needed)
- (moved to later: yaw-only follow test — needs the controller first)
- [ ] B6 Write the filming note on the phone right away: clip name, scene, time, light, who wore what (10 min)

### Block C — back at the laptop, same day (≈ 1–1.5 h)
- [ ] C1 Copy all videos to `3_EVIDENCE/<date>_M06_field/` (both laptops if needed; NOT git); upload to the shared Drive (30 min)
- [ ] C2 `2_MILESTONES/filming_M06_crossings.md`: list of clips + what each shows + safety notes (20 min)
- [ ] C3 First look: run `m06_track.py` on one crossing clip, watch it together → write 3 lines of what we saw (20 min)
- [ ] C4 Push note + UPDATES line + presentation-log line (10 min)
**End of the day you should have:** 8+ crossing clips, one 60 s clip, a command-delay video, a battery speed log —
everything that needs the drone. The rest is computer work.

---

## 4. After the day — computer only (each of us when free, or online together)
| # | Step | Time | Done |
|---|---|---|---|
| 1 | Requirement trace table (approved plan words → test → result) `M06_requirement_trace.md` | 30 min | [ ] |
| 2 | **Sticky-ID rule** in `m06_track.py` (switch ID only if the turban is on the new one for 3 frames in a row and not on the current one); re-test on session 1 vs M05 (85.6% / 8.2%) | 2 h | [ ] |
| 3 | **Safety states** FOLLOWING / UNSURE (< 2 s lost → hover) / LOST (> 2 s → hover, land by hand), shown on video | 2.5 h | [ ] |
| 4 | Label crossing clips with IDs in **CVAT** (~5 frames/s; user = ID 1), cross-check 20 frames each | 4 h | [ ] |
| 5 | **Measure** on the hold-out: M05 vs tracker + sticky ID, YOLO11n vs 11m — % user kept, wrong-person frames, ID swaps per crossing, recovery time, IDF1 / HOTA (**TrackEval**), 95% intervals, paired test 11n vs 11m | 3.5 h | [ ] |
| 6 | **Command delay**: count frames in the 60 fps video, 10 repeats → mean ± spread; delay budget = video 256 ms + detection ~34 ms + command ? | 1.5 h | [ ] |
| 7 | **Controller** offline: box centre → turn, box height → distance, dead band + rate limit; run on the recorded clips, plot the commands | 3 h | [ ] |
| 8 | One-page M06 summary + decision log + 1-min demo + questions for Gabi + CLAUDE.md status | 2.5 h | [ ] |
Total after the day ≈ 19 h. Target: done by **Sat 5.12**, Sun 6.12 buffer. A second short flight (controller hover test)
only if step 7 is ready before 6.12 and we both can.

## 5. Main risks
- `record_video.py` still gives no frames → film on the drone itself (backup in A3) so the day is not lost.
- Weather / wind → bring the plan to film the most important scenes first: crossings in front, red shirt, 60 s clip.
- No third person → the passer-by scenes are the core of M06; book someone tonight.
- Clips without real crossings → the tracker looks perfect and proves nothing.
