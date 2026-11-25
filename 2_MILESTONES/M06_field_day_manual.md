# FIELD DAY MANUAL — from M05 leftovers to the CONTROLLER in one day (Wednesday, Nimer + Dareen, 7–8 h)

Tick each box as you go. Times are estimates. **Goal of the day: close M05, and fly the first closed loop (the drone turns
to keep the user in the picture), plus film the M06 test set.** Only labelling + measuring stays for the computer later.

## Why we are doing this (read together, 2 min)
- **Aim of M06:** the drone keeps the SAME user through crossings and turned-away moments, never follows the wrong person,
  and knows what to do when unsure: **FOLLOWING** (controller on) / **UNSURE** (hover) / **LOST** (hover, pilot lands).
- **Today:** (1) finish the M05 model choice with measurements, (2) test sticky ID + states + controller on the real drone,
  (3) film crossing scenes nobody has tuned on, (4) measure the command delay (the missing number in our delay budget:
  video 256 ms + detection ~34 ms + command ?).
- **Pass lines:** user kept >= 90% of frames · <= 1 ID swap in 10 crossings · 0 wrong-person follows · 60 s continuous ·
  >= 10 FPS long run (we aim for >= 15 for control).

## Ready before the day (done 25.11 night by Dareen + Claude)
- [x] **Paired test 11n vs 11m** (`m05_paired_test.py`, 403 frames): YOLO11m right where 11n is wrong in **7** frames,
      the opposite **0** → **p = 0.016, a real (small) gain of +1.7 pts**. YOLO26m vs 11n: 7 vs 2, p = 0.18 → could be luck.
      → **Rule for today: use YOLO11m if it keeps >= 15 FPS live on battery; otherwise YOLO11n.**
- [x] **`m06_follow.py`**: tracker (BoT-SORT) + **sticky ID** (switch only after 3 turban frames on the new person) +
      **3 safety states** + **controller** (yaw from box centre, forward from box height; dead band, max stick 0.25, rate limit).
      Offline test on 60 s of session 1: FOLLOWING 69%, UNSURE 10%, LOST 20% (not checked by eye yet).
- [x] **User score per box** (`user_score.py`, Gabi's request: identity score, not YOLO confidence): on 403 frames the user's
      median 0.85 vs others 0.000, **ROC AUC 0.914**; BUT a far red shirt scores 0.97-0.99 (red shirt in the "head" area).
      The demo boxes in `m06_follow.py` now show this score.
- [x] **`--colour` option in `m06_follow.py`** (Nimer's idea): user score = (turban + clothes colour) / 2 after a
      "this is me" **enrolment** (live: user alone, close, facing the drone → press **E** 3 times; offline: automatic on the
      first clear turban frames with one person). Offline, 60 s of session 1: the red shirt **no longer steals the lock**
      (user 0.71, red shirt 0.64 - before: red shirt "USER 0.99"); ID switches 10 → 5. Margin still small → test tomorrow.
- [x] **`command_delay_test.py`**: red flash + stopwatch on every command; also measures the loop delay by itself.
- [ ] Nothing of the above has touched the real drone yet → that is today.

## Tools checklist
**Hardware**
- [ ] DJI Neo + **4 batteries charged** (today has more flying)
- [ ] Samsung S10 with DJI Fly, charged + USB cable (+ spare cable)
- [ ] Dareen's laptop **100%** + charger
- [ ] Second phone that films **60 fps** + someone to hold it or a stand
- [ ] Purple-red turban · **a third person = passer-by in a RED shirt** (+ one dark top)
- [ ] 2 ground marks at **3 m** and **6 m** · water, hat, power bank

**Software (Dareen's laptop, terminal in `1_CODE`; use the GPU python:** `C:\Users\LOREN\venvs\gpu\Scripts\python.exe`, written `GPU` below)
- [ ] scrcpy + ADB · `record_video.py` · `command_delay_test.py` · `m06_follow.py` · `m06_track.py` · `python -m pip install lap` done

## Power rules (drone + laptop) — longer flights, clean numbers
**Drone battery (Neo ≈ 18 min per battery in calm air; idle-on also drains it)**
- [ ] Charge **the evening before / that morning**: DJI batteries can slowly discharge themselves to a storage level when
      left for days, and the Neo drains while switched on even on the table (camera, video link, Wi-Fi to the phone, fan).
- [ ] Do ALL laptop setup and script tests with the **drone OFF**; switch it on only when the script is ready.
- [ ] Use **one battery for all table tests** (A3–A6b); keep the full ones for flying.
- [ ] **Land between clips** instead of hovering while you talk; start the recording BEFORE take-off (`record_video.py` → T).
- [ ] Plan each flight: 2–3 clips per battery, written in order (see B2). Hover/turning costs less than flying forward fast.
- [ ] Keep batteries out of the sun and not cold (a bag in the shade); wind = shorter flights → film the important scenes first.
- [ ] Land at **30%** (not later); recharge used batteries on the spot if a power point/power bank is there.

**Laptop (clean, comparable speed results)**
- [ ] Before measuring: close the browser, Teams, OneDrive/Google Drive sync, Windows Update (pause 1 day), the Project
      updates panel (it git-pulls every 2 min).
- [ ] Windows power mode **Best performance** also on battery; Lenovo **Fn+Q** = performance mode; screen brightness ~60%.
- [ ] Laptop on a **hard surface in the shade**, lid open, vents free (it slows itself when hot: 4.6 → 2.6 GHz measured 24.11).
- [ ] Python on the **NVIDIA GPU** (GPU env); give it 20 s warm-up before reading FPS.
- [ ] Every speed number = **with its conditions**: plugged / battery %, model, GPU/CPU. `m06_follow.py` now logs the laptop
      battery % and plugged-in state in every CSV row, so results stay comparable.

---

## TONIGHT — 20 min
- [ ] 0.1 Charge: 4 drone batteries, S10, laptop, second phone
- [ ] 0.2 Book the passer-by (red shirt): time + place (big open space, little wind)
- [ ] 0.3 Weather: wind < 20 km/h

## BLOCK A — at the laptop, before leaving · ≈ 1 h 45 min
- [ ] **A1 Pull + aim (10 min)** — `git pull`; read "Why" and "Ready before the day" together; agree the pass lines.
- [ ] **A2 Look at the follow script offline (20 min)** — open `3_EVIDENCE/m06_tracking/143404_recording_session1_follow.mp4`.
      Check by eye: green box = always the user? Does the red-shirt man ever get the USER box? Do UNSURE/LOST appear when
      she is really hidden? Write 3 lines.
      Then open `143404_recording_session1_colour_follow.mp4` (same clip, **--colour**) and compare at ~10 s:
      without colour the red shirt is "USER 0.99"; with colour the user keeps the USER box. *You should see:* that difference.
- [ ] **A3 Connect the drone indoors (15 min)** — drone on the table (not flying), S10 by USB, DJI Fly on the **camera view**,
      Manual Control. `python connection_test.py` → *you should see* the drone picture on the laptop.
- [ ] **A3b Camera tilt (gimbal) discovery (10 min)** — drone on the table, DJI Fly on the camera view. On the phone:
      press and hold on the live picture ~1 s → does a gimbal slider/arc appear? Drag it up/down → does the picture tilt?
      If not: Settings (⋯) → Control → Gimbal. Tell Claude "ready" with the slider visible → Claude takes ADB screenshots
      for the exact positions and writes `tilt_up / tilt_down / tilt_recentre` (why: our lowest user scores = her head cut
      off at the top; tilting keeps the turban in view). Write the angle range the app shows: ____ .
- [ ] **A4 Recording (20 min)** — `python record_video.py 0.5 indoor_test` → "Saved: … N frames", the .mp4 plays.
      If "No frames were received": DJI Fly not on camera view / adb PATH → fix. **Backup:** record on the drone (DJI Fly button).
- [ ] **A5 Delay script dry (10 min)** — `python command_delay_test.py --dry`, press Y / U → red flash, "Saved …_dry.csv".
- [ ] **A6 Follow script live DRY on the table (20 min)** — drone on the table, camera pointed at one of you wearing the
      turban: `GPU m06_follow.py --live --dry`. Walk left / right / turn away / leave the picture.
      *You should see:* FOLLOWING + yaw sign follows you (you go right → yaw +), UNSURE then LOST when you leave,
      yaw back to 0 at once. Note the FPS for 11n: ____ ; then `--model yolo11m.pt`: FPS ____ (on charger).
- [ ] **A6b Colour enrolment, live DRY (15 min)** — `GPU m06_follow.py --live --dry --colour`. Top line says "NOT enrolled".
      The user stands **alone, 2–3 m, facing the camera** → press **E** 3 times → top line "enrolled", terminal "enrolled view 3".
      Then the second person walks in front (non-red top): *you should see* the user's tag stay clearly higher (e.g. 0.8 vs 0.3)
      and the USER box stay on her. FPS with colour: ____ (should be ~same as without).
- [ ] **A7 Speed on charger, long run (runs while you pack, 10 min)** — `GPU m06_follow.py --video ..\3_EVIDENCE\2026-11-22\143404_recording_session1.mp4 --model yolo11m.pt --seconds 600`
      → FPS at the end of the run in the CSV (last rows): ____ .
- [ ] **A8 T / L keys (5 min)** — only with the flight checklist; if unsure, take off and land by hand today.
- [ ] **A9 Pack (5 min).**

## BLOCK B — at the field · ≈ 4 h 30 min (about 7 batteries of flying, with charging breaks)
**Before EVERY flight:** phone in hand · DJI Fly in **Manual Control** · open space, nobody under the drone · battery > 40% ·
Esc / Ctrl+C ready · if anything looks wrong: **take over with the phone and land by hand**.
Fly at **1.5–2 m height**, user **3–6 m** away. Laptop **on battery** (field case). Battery at start: ____ %.

- [ ] **B1 Setup (15 min)** — marks at 3 m / 6 m; 30 s hover test with `python record_video.py 0.5 field_test`.
- [ ] **B2 Film the crossing scenes = the M06 test set, never tuned on (≈ 90 min, ~3 batteries)**
      For each: `python record_video.py 0 <name>` → take off → film 60–90 s → land → Esc.
      **Start EVERY clip with 3 s of the user ALONE, close, facing the drone** (= the enrolment view for `--colour` later).
      Most important first:
  - [ ] `cross_front_LR` — passer-by walks **in front** of the user left → right (3 times)
  - [ ] `cross_front_RL` — in front, right → left (3 times)
  - [ ] `redshirt_side` — red shirt walks **next to** the user 10 s, then away (the M05 failure)
  - [ ] `turn_away` — user turns her back 3–5 s, 3 times
  - [ ] `continuous_60s` — 60 s+ walking normally (work-plan req. 4)
  - [ ] `cross_behind` — behind the user, both directions
  - [ ] `cross_close` (1 m) and `cross_far` (5 m)
  - [ ] `out_and_back` — user leaves the picture and comes back
- [ ] **B2b FROM ABOVE — Gabi's request (≈ 40 min, ~1.5 batteries)** — same scenes, drone **higher (3.5–4 m)**, about
      **4 m away**, camera **tilted down ~30–40°** (pilot drags the gimbal slider on the phone by hand; geometry:
      tilt ≈ atan((height − 1.7 m) / distance) = atan(2.3 / 4) ≈ 30°). Name the clips with `_above`:
  - [ ] `cross_front_LR_above` (3 crossings) · [ ] `turn_away_above` (turban seen from above even with her back turned?)
  - [ ] `redshirt_side_above` · [ ] `continuous_60s_above`
      Write the height + tilt you used: ____ m, ____ °.
      **Why:** from above, the turban is the TOP of the head → visible from every side (turned away too) and people overlap
      less in crossings. **Price:** she is smaller in the picture (our misses were small, far people) and YOLO learned people
      mostly from the side. → Later we compare level vs above on the same scenes: turban seen %, user score, YOLO found %.
- [ ] **B3 Command delay (30 min, 1 battery)** — drone hovering, second phone films **screen + drone** at **60 fps**.
      `python command_delay_test.py` → Y, wait 3 s, U, wait 3 s … **10 presses** → Esc → land.
      *You should see:* red flash → drone turns; terminal "picture moved after … ms"; "Saved …_command_delay.csv".
- [ ] **B3b Yaw rate per stick (the drone's turning "torque" response) (15 min, same battery)** — still hovering, phone still
      filming at 60 fps from the side. Long pulses, 5 s between them:
      `python command_delay_test.py --pulse 2 --deflect 0.2` → Y 2 times · then `--deflect 0.3` → Y 2 times · `--deflect 0.4` → Y 2 times.
      Write how far it turned each time (a landmark in the DJI Fly view, or the compass/heading if DJI Fly shows it):
      0.2: ____ ° · 0.3: ____ ° · 0.4: ____ ° (in 2 s).
      **Why:** a quadcopter turns (yaw) only by the small torque difference between its motors → yaw is its slowest axis:
      it needs time to speed up and to stop. Together with the ~0.3 s video delay this is what makes a turning loop wobble.
      These numbers give: degrees per second per stick value + how long it takes to start/stop → we set K (and the D term /
      prediction) from measurements, not by guessing. From the videos we also read: rise time, overshoot, settling time.
- [ ] **B4 Live DRY on battery = the speed test on battery (20 min, 1 battery)** — drone hovering, user in front:
      `GPU m06_follow.py --live --dry --seconds 300` (11n), then `--model yolo11m.pt --seconds 300`.
      FPS 11n ____ , 11m ____ ; laptop battery ____ % → **decide the model: 11m if >= 15 FPS, else 11n** → chosen: ____
      Then 2 min with `--colour` (press E with the user alone first): FPS ____ .
- [ ] **B5 FIRST CLOSED LOOP: yaw only (30 min, 1 battery)** — drone hovering 1.5 m, user 4 m in front, nobody else near.
      `GPU m06_follow.py --live --model <chosen> --max-yaw 0.2 --seconds 60`. User walks slowly in an arc left and right.
      *You should see:* the drone **turns** to keep her centred, stops turning in the middle (dead band), hovers when she
      hides (UNSURE / LOST). Esc at once if it turns the wrong way or keeps spinning. Repeat with a passer-by crossing
      in a **NON-red** top first. **No red shirt in the picture during closed-loop tests**: the 25.11 user-score check showed a
      far red shirt can score 0.99 and steal the lock (`M05_data/results/user_score_25.11/`). Red shirt = filming only (B2).
- [ ] **B5b Yaw only WITH colour (20 min) — only if B5 was calm and correct** — user alone in view, press **E** 3 times, then
      `GPU m06_follow.py --live --colour --model <chosen> --max-yaw 0.2 --seconds 60`; the passer-by (non-red) crosses
      in front twice. *You should see:* the drone keeps turning to the USER, not to the passer-by. Write: kept / lost / swapped.
- [ ] **B6 Yaw + distance (30 min, 1 battery) — ONLY if B5 was calm and correct** —
      `GPU m06_follow.py --live --forward --model <chosen> --max-yaw 0.2 --seconds 60`. User walks slowly away / closer,
      2–3 m of space all around. *You should see:* the drone follows slowly (max stick 0.15), stops at ~3–4 m.
- [ ] **B7 Filming note on the phone now (10 min)** — per clip / test: name, what happened, time, light, who wore what,
      anything unsafe.
- [ ] **B8 Pack up, count batteries and props (10 min).** Battery at end: ____ %.

## BLOCK C — back at the laptop · ≈ 1 h 15 min
- [ ] **C1 Back up (20 min)** — `3_EVIDENCE/<today>/` + `3_EVIDENCE/m06_tracking/live_*` + the 60 fps phone video →
      `3_EVIDENCE/<today>_M06_field/` (NOT git) + shared Drive.
- [ ] **C2 Note (20 min)** — `2_MILESTONES/M06_field_day_<date>.md`: clips, delay numbers, FPS on charger vs battery,
      model chosen + why, what the closed loop did (worked / problems), safety events.
- [ ] **C3 First look at a crossing (25 min)** — `GPU m06_follow.py --video ..\3_EVIDENCE\<today>\<…cross_front_LR>.mp4`
      and again with `--colour` → compare the two videos: did the passer-by ever get the USER box? ID switches (printed at
      the end): turban only ____ vs with colour ____ . Do the same on `redshirt_side`.
- [ ] **C4 Push (10 min)** — note + UPDATES + presentation-log lines (model decision, delay, first closed loop).

## End of the day — you should have
- [ ] M05 closed: model chosen with a paired test + live FPS on battery
- [ ] Sticky ID + states + controller tested live: dry → yaw only → yaw with colour → (yaw + distance)
- [ ] Turban only vs turban + colour compared on the new crossing clips (first look)
- [ ] 8+ crossing clips + 60 s clip (M06 hold-out) + 4 clips FROM ABOVE (Gabi)
- [ ] Yaw rate per stick (0.2 / 0.3 / 0.4) + command delay · command-delay CSV + 60 fps video
**Total:** A 1 h 45 + travel + B ~5 h 15 (with B2b from above + B3b yaw rate) + C 1 h 15 ≈ **8 h** (+ travel).
**If short on time / batteries, drop in this order:** B6 (distance) → B5b → `cross_far` / `out_and_back` → B2b red shirt above.

**Left for the computer (≈ 8 h, any time before 7.12):** label the crossing clips with IDs in CVAT (4 h) → measure M05 vs
M06 on them: % user kept, ID swaps, recovery, IDF1/HOTA with TrackEval (2.5 h) → count the delay in the 60 fps video (1 h) →
one-page summary + decision log + demo (1.5 h). Tuning K_YAW / dead band from today's CSV if the loop was slow or jerky.

## Main risks
- The loop turns the wrong way or oscillates → Esc, check the yaw sign / lower `--max-yaw` / bigger dead band; don't push it.
- Recording gives no frames → record on the drone itself, film anyway.
- No passer-by → crossings are the core of M06; book someone tonight.
- Laptop slows down on battery → B4 measures exactly that; fall back to 11n.
