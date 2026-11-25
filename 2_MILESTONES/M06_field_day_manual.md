# FIELD DAY CHECKLIST — Wednesday, Nimer + Dareen (~8 h + travel)
**From M05 leftovers to the first closed loop (the drone turns by itself to keep the user in view) + the M06 test footage.**
Tick `- [ ]` → `- [x]` as you go (edit this file and push, or tick on paper and copy in the evening).
Times: slot length + suggested clock if you start at **10:00**. Everything to research later: `PROJECT_NOTEBOOK_todo_research_25.11.md`.

---

## 0. Why we do this today (read together, 2 min)
- **M06 aim:** keep the SAME user through crossings and turned-away moments, **never follow the wrong person**, and know
  what to do when unsure: **FOLLOWING** (controller on) / **UNSURE** (hover) / **LOST** (hover, pilot lands).
- **Today:** (1) close the M05 model choice with live speed on battery, (2) test sticky ID + states + controller on the real
  drone, (3) film crossing scenes at normal height AND from above (Gabi) — never tuned on, (4) measure the command delay and
  the yaw rate (the numbers the controller needs).
- **Pass lines:** user kept >= 90% · <= 1 ID swap in 10 crossings · 0 wrong-person follows · 60 s continuous · >= 10 FPS long run (aim 15).
- **Rehearsed on the computer first (Nimer's "simulate like Vivado" idea, 25.11 night):** `1_CODE/sim_drone.py` = a simulated
  drone (plays a recorded clip as the camera; yaw slides the view, with delay 0.25 s and 90°/s at full stick). Every script runs
  unchanged with `set DRONE_SIM=<video>`. Results: `m06_follow.py --live --dry` and `--live` (yaw) run without errors;
  **yaw sign = error sign in 111/111 frames, and each turn moved the user back toward the centre** (right turn → error −0.02,
  left turn → +0.10 in 0.6 s); `record_video.py` records (226 frames / 9 s); ~15 FPS in the sim. Not tested in the sim:
  key presses (E, Y/U) — do those in A5/A6b.
- **Ready from last night:** paired test (11m really better than 11n, p = 0.016) · `m06_follow.py` (BoT-SORT + sticky ID +
  states + controller + `--colour`) · `command_delay_test.py` · user score per box. **None of it has touched the real drone yet.**

## 1. Roles (decide now — people swap between blocks)
| role | does | who |
|---|---|---|
| **Pilot** | phone in hand all flight, DJI Fly in Manual Control, takes over / lands by hand | ____ |
| **Laptop operator** | runs the commands, watches FPS / state, finger on Esc | ____ |
| **User** | wears the turban, walks the scenes | ____ |
| **Passer-by** (3rd person) | crosses, walks next to the user; red top for filming, dark/other top for closed loop | ____ |
| **60 fps filmer** | films screen + drone in B3/B3b (passer-by or user; else phone on a tripod) | ____ |

## 2. Equipment and tools — pack list (check tonight)
**Drone and flight**
- [ ] DJI Neo + **4 batteries charged** (charge tonight; DJI batteries can drain themselves over days) + charger / hub
- [ ] Spare propellers (if you have them) + small screwdriver
- [ ] Site: open space, nobody under the flight path, wind < 20 km/h (forecast app)

**Phones, cables, apps**
- [ ] Samsung S10 (control phone) charged, **DJI Fly** updated · USB cable S10 ↔ laptop **+ a spare cable**
- [ ] Second phone that films **60 fps** (camera → video → 60 fps) + **small tripod / phone stand** (or a person)
- [ ] Power bank for the phones
- [ ] Phone apps: Notes (field notes), Stopwatch, Weather/wind, a **level / angle app** (camera tilt, if DJI Fly doesn't show it)

**Laptop and software (Dareen's laptop = GPU)**
- [ ] Laptop **100%** + charger (+ extension cord if there is a power point)
- [ ] Terminal: `OPEN_TERMINAL_HERE.bat` (opens inside `1_CODE`)
- [ ] GPU Python, once per terminal window: `set GPU=C:\Users\LOREN\venvs\gpu\Scripts\python.exe`
      (checked 25.11: drone scripts + YOLO + lap + CUDA all import fine in it)
- [ ] Models in `1_CODE`: `yolo11n.pt`, `yolo11m.pt` (present 25.11)
- [ ] Scripts: `connection_test.py`, `record_video.py`, `command_delay_test.py`, `m06_follow.py` (+ `user_score.py`, `m05.py`)
- [ ] ADB sees the phone (checked 25.11: device `RF8MB2CG6SE`)
- [ ] **Free disk space >= 20 GB** (File Explorer → This PC)

**Measuring tools**
- [ ] **Tape measure** (10 m+; or steps ≈ 0.75 m) · **4 ground marks** (cones / bottles / bags) for 3 m, 4 m, 6 m
- [ ] Phone stopwatch · DJI Fly shows height **H** and distance **D** (use them for "3.5–4 m high")
- [ ] Notebook + pen or phone notes (fill the ____ blanks)

**User and passer-by**
- [ ] The **purple-red turban** · user in her usual clothes
- [ ] Passer-by: **one red top** (filming only) + **one dark / non-red top** (closed-loop tests)

## 3. Power rules (longer flights, clean numbers)
- [ ] Drone **OFF** during all laptop setup; switch on only when a script is ready (it drains on the table: camera, link, fan).
- [ ] **One battery for all table tests** (A3–A6b); full ones for flying. Land at **30%**; land between clips; record BEFORE take-off.
- [ ] Batteries in the shade, not cold; wind = shorter flights → most important scenes first.
- [ ] Laptop before measuring: close browser, Teams, OneDrive/Google Drive sync, pause Windows Update, close the Project updates
      panel (git-pulls every 2 min). Power mode **Best performance** also on battery, Lenovo **Fn+Q**, brightness ~60%.
- [ ] Laptop on a **hard surface in the shade**, vents free (it slows itself when hot: 4.6 → 2.6 GHz, 24.11). 20 s GPU warm-up before reading FPS.
- [ ] Every FPS number goes with its conditions; `m06_follow.py` logs laptop battery % + plugged-in in every CSV row.

---

## TONIGHT (≈ 25 min)
- [ ] **T1 Charge (5 min):** 4 drone batteries, S10, second phone, laptop, power bank.
- [ ] **T2 Passer-by (10 min):** book the third person; tell them: red top + another top, time and place.
- [ ] **T3 Weather (5 min):** wind < 20 km/h; pick a backup time.
- [ ] **T4 Pack (5 min):** everything from §2 in one bag.
**Tip:** don't leave the drone switched on tonight.

---

## BLOCK A — at the laptop before leaving · 1 h 50 min · 10:00–11:50

- [ ] **A1 Pull + agree (10 min) · 10:00**
      `OPEN_TERMINAL_HERE.bat` → `git pull` → `set GPU=C:\Users\LOREN\venvs\gpu\Scripts\python.exe`
      Read §0, fill §1 roles, agree the pass lines.
      **CRITICAL:** make sure the simulator is OFF: type `set DRONE_SIM=` (empty). If a script prints `[SIM]`, it is NOT the real drone.
      Optional 10-min rehearsal before the drone is on: `set DRONE_SIM=.._EVIDENCE6-11-22c404_recording_session1.mp4` →
      try `%GPU% command_delay_test.py --dry` and `%GPU% m06_follow.py --live --dry --colour` (press E) → then `set DRONE_SIM=` again.
      *You should see:* "Already up to date" (or new files); both can say the aim in one sentence.

- [ ] **A2 Watch last night's offline results (15 min) · 10:10** (drone OFF)
      Open `3_EVIDENCE\m06_tracking\143404_recording_session1_follow.mp4` (turban only) and
      `143404_recording_session1_colour_follow.mp4` (with `--colour`); jump to ~10 s.
      *You should see:* turban only → the red-shirt man is "USER 0.99"; with colour → the user keeps "USER 0.71", red shirt "person 0.64".
      Write 2 lines: where does it still go wrong? **Note:** the tag = **user score** (is it OUR user, 0–1), not YOLO confidence.

- [ ] **A3 Connect the drone on the table (15 min) · 10:25**
      Drone on the table, **not flying**. S10 by USB. DJI Fly → "Connected" → **GO FLY / camera view** → Manual Control.
      `%GPU% connection_test.py 1` (1 minute)
      *You should see:* the drone picture in a window, FPS lines, "Saved …" at the end.
      **If "Connection failed":** battery empty / drone off → swap battery. **If no picture:** DJI Fly must show the camera view.

- [ ] **A3b Camera tilt (gimbal) discovery (10 min) · 10:40**
      On the phone: press and hold on the live picture ~1 s → **gimbal slider / arc**? Drag slowly up/down → does the picture
      tilt? If not: DJI Fly settings (⋯) → Control → Gimbal. **Tell Claude "ready"** with the slider visible → Claude takes ADB
      screenshots and writes `tilt_up / tilt_down / tilt_recentre`.
      How to tilt ____ · angle range shown ____ · "recenter" exists? ____
      **Why:** her head cut off at the top = our lowest user scores; tilting keeps the turban in view; needed for B2b.

- [ ] **A4 Recording works (15 min) · 10:50**
      `%GPU% record_video.py 0.5 indoor_test` (30 s)
      *You should see:* "Recording to: …", a window with "REC", then "Saved: … N frames"; the .mp4 plays.
      **If "No frames were received":** DJI Fly not on the camera view / adb not found → fix, repeat.
      **Backup:** press record in DJI Fly (records on the drone), download later — film anyway.
      **Tip:** only ONE drone program at a time (they all use the mirror) — close one before starting the next.

- [ ] **A5 Delay script, dry (10 min) · 11:05**
      `%GPU% command_delay_test.py --dry` → click the window → **Y** / **U** a few times → Esc
      *You should see:* RED flash + big stopwatch + "press #n"; nothing sent; "Saved …_command_delay_dry.csv".

- [ ] **A6 Follow script live DRY on the table (15 min) · 11:15**
      Camera at the user (turban on), 2–3 m away: `%GPU% m06_follow.py --live --dry`
      User walks left / right / turns away / leaves the picture.
      *You should see:* FOLLOWING, **yaw sign follows her** (she moves to the right of the picture → yaw **+**), UNSURE then LOST
      when she leaves, yaw back to 0 at once. FPS 11n ____ → Esc → `%GPU% m06_follow.py --live --dry --model yolo11m.pt` → FPS 11m ____ .
      **CRITICAL:** if the yaw sign is the wrong way round, STOP — tell Claude before any flight (one sign in the code).

- [ ] **A6b Colour enrolment, live DRY (10 min) · 11:30**
      `%GPU% m06_follow.py --live --dry --colour` → top line "NOT enrolled". User **alone, 2–3 m, facing the camera** → press
      **E** 3 times → "enrolled view 3". Passer-by (non-red top) walks in front.
      *You should see:* user's tag clearly higher (e.g. 0.8 vs 0.3), USER box stays on her. FPS with colour ____ .
      **Tip:** enrol only when she is ALONE — a wrong enrolment teaches it the wrong clothes.

- [ ] **A7 Speed on charger, long run (runs while you pack) · 11:40** (drone OFF)
      `%GPU% m06_follow.py --video ..\3_EVIDENCE\2026-11-22\143404_recording_session1.mp4 --model yolo11m.pt` (runs to the end)
      FPS in the last rows of `3_EVIDENCE\m06_tracking\143404_recording_session1_follow.csv`: ____ .

- [ ] **A8 Take-off / land keys (5 min) · 11:45** — flight checklist, safe spot. In `record_video.py`: **T** take off, **L** land.
      If unsure → by hand today.
- [ ] **A9 Pack + travel · 11:50** — full batteries in, laptop charging until you leave.

---

## BLOCK B — at the field · ≈ 5 h 15 min incl. breaks · ~12:30–17:45
**Before EVERY flight (30 s):** pilot has the phone · DJI Fly **Manual Control** · nobody under the drone · battery **> 40%** ·
laptop operator's finger on **Esc** · anything wrong → **pilot takes over and lands by hand**.
Laptop on battery (field case), shade. Battery at start: ____ %.

- [ ] **B1 Set up (15 min) · 12:30**
      Marks at 3 m, 4 m, 6 m (tape measure). `%GPU% record_video.py 0.5 field_test` → take off → hover 1.5 m → land → Esc → saved.

- [ ] **B2 Crossing scenes at following height = M06 test set (≈ 90 min, ~3 batteries) · 12:45**
      Drone **1.5–2 m high**, user **3–6 m** away, camera level, clips **60–90 s**:
      `%GPU% record_video.py 0 <name>` → take off → **3 s of the user ALONE, close, facing the drone** (enrolment view for
      `--colour`) → scene → land → Esc. Most important first:
  - [ ] `cross_front_LR` — passer-by **in front** of the user, left → right, 3 times
  - [ ] `cross_front_RL` — in front, right → left, 3 times
  - [ ] `redshirt_side` — **red top** walks next to the user 10 s, then away (the M05 failure)
  - [ ] `turn_away` — user turns her back 3–5 s, 3 times
  - [ ] `continuous_60s` — 60 s+ normal walking (work-plan req. 4)
  - [ ] `cross_behind` — behind the user, both directions
  - [ ] `cross_close` (1 m from her) · [ ] `cross_far` (5 m behind her)
  - [ ] `out_and_back` — user leaves the picture and comes back
      **Tips:** say the clip name out loud at the start; ~3 clips per battery; redo a failed crossing at once.

- [ ] **B2b FROM ABOVE — Gabi (≈ 40 min, ~1.5 batteries) · 14:15**
      Drone **3.5–4 m high** (DJI Fly "H"), ~**4 m away**, camera **tilted down ~30–40°** (pilot drags the gimbal slider;
      tilt ≈ atan((height − 1.7) / distance) = atan(2.3 / 4) ≈ 30°). Same start: 3 s alone facing the drone.
  - [ ] `cross_front_LR_above` · [ ] `turn_away_above` · [ ] `redshirt_side_above` · [ ] `continuous_60s_above`
      Height ____ m · tilt ____ ° · distance ____ m.
      **Why:** turban = top of the head → seen from every side, less overlap. **Price:** smaller in the picture; YOLO learned side views.

- [ ] **Break + charge (15 min) · 14:55** — water, shade, swap batteries. Laptop battery ____ %.

- [ ] **B3 Command delay (25 min, 1 battery) · 15:10**
      Drone hovering 1.5 m, nobody near. Filmer films **laptop screen AND drone in one picture at 60 fps**.
      `%GPU% command_delay_test.py` → **Y**, wait 3 s, **U**, wait 3 s … **10 presses** → Esc → land.
      *You should see:* red flash → drone turns a bit later; "picture moved after … ms"; "Saved …_command_delay.csv".
      **Tip:** the phone must see the flash and the drone sharply; repeat once if not.

- [ ] **B3b Yaw rate per stick — turning response (15 min, same battery) · 15:35**
      Hovering, still filming. 5 s between pulses:
      `%GPU% command_delay_test.py --pulse 2 --deflect 0.2` → Y twice → Esc
      `%GPU% command_delay_test.py --pulse 2 --deflect 0.3` → Y twice → Esc
      `%GPU% command_delay_test.py --pulse 2 --deflect 0.4` → Y twice → Esc
      Degrees in 2 s (landmark / DJI Fly heading): 0.2 ____ ° · 0.3 ____ ° · 0.4 ____ °
      **Why:** a quadcopter turns only through the motors' small torque difference → yaw is its slowest axis; with our ~0.3 s
      delay this is what makes a turning loop wobble → these numbers set the controller gain.

- [ ] **B4 Live DRY on battery = the model choice (20 min, 1 battery) · 15:50**
      Hovering, user 4 m in front: `%GPU% m06_follow.py --live --dry --seconds 300` →
      `%GPU% m06_follow.py --live --dry --model yolo11m.pt --seconds 300` → 2 min with `--colour` (E with her alone first).
      FPS 11n ____ · 11m ____ · colour ____ · laptop battery ____ %.
      **Decide: YOLO11m if >= 15 FPS, else YOLO11n → chosen ____** (closes the M05 model question).

- [ ] **B5 FIRST CLOSED LOOP: yaw only (30 min, 1 battery) · 16:10**
      Hovering 1.5 m, user 4 m in front, **nobody else in view, no red tops**.
      `%GPU% m06_follow.py --live --model <chosen>.pt --max-yaw 0.2 --seconds 60`
      User walks slowly in an arc left and right, then hides 3 s; then once more with the passer-by (non-red) crossing.
      *You should see:* the drone turns to keep her centred, stops in the middle (dead band), hovers when she hides.
      **CRITICAL: Esc at once** if it turns the wrong way, keeps spinning, or wobbles more and more → land → note it.

- [ ] **B5b Yaw only WITH colour (20 min) — only if B5 was calm · 16:40**
      User alone → **E** 3 times → `%GPU% m06_follow.py --live --colour --model <chosen>.pt --max-yaw 0.2 --seconds 60`
      Passer-by (non-red) crosses twice. Result: kept / lost / swapped ____ .

- [ ] **B6 Yaw + distance (30 min) — ONLY if B5 was calm and correct · 17:00**
      2–3 m free all around. `%GPU% m06_follow.py --live --forward --model <chosen>.pt --max-yaw 0.2 --seconds 60`
      User walks slowly away / closer. *You should see:* slow following (max 0.15), stops at ~3–4 m.
      **Tip:** pilot's thumbs on the sticks; first try only 20 s (`--seconds 20`).

- [ ] **B7 Field note on the phone (10 min) · 17:30** — every clip / test: name, what happened, time, light, who wore what,
      anything unsafe, all ____ numbers.
- [ ] **B8 Pack (10 min) · 17:40** — count batteries and props. Laptop battery ____ %.

**Short on time / batteries → drop in this order:** B6 → B5b → `cross_far` / `out_and_back` → `redshirt_side_above`.
**Never drop:** first 5 clips of B2, B3, B4, B5.

---

## BLOCK C — back at the laptop · 1 h 15 min · ~18:30–19:45
- [ ] **C1 Back up (20 min)** — `3_EVIDENCE\<today>\` + `3_EVIDENCE\m06_tracking\live_*` + the 60 fps phone video →
      `3_EVIDENCE\<today>_M06_field\` (NOT git) → shared Drive.
- [ ] **C2 Field note in git (20 min)** — `2_MILESTONES\M06_field_day_<date>.md`: clips, delay, yaw rates, FPS charger vs battery,
      model chosen + why, closed-loop result, safety events.
- [ ] **C3 First look at a crossing (25 min)** — `%GPU% m06_follow.py --video ..\3_EVIDENCE\<today>\<…cross_front_LR>.mp4`, then
      the same + `--colour`. Passer-by ever "USER"? ID switches: turban ____ · colour ____ . Same on `redshirt_side`.
- [ ] **C4 Push (10 min)** — note + UPDATES + presentation-log lines (model, delay, yaw rate, first closed loop, level vs above).

---

## End of the day — you should have
- [ ] M05 closed: model chosen (paired test + live FPS on battery)
- [ ] Sticky ID + states + controller tested live: dry → yaw only → yaw with colour → (yaw + distance)
- [ ] 8+ crossing clips + 60 s clip at following height + 4 clips from above (M06 hold-out, never tuned on)
- [ ] Command delay (CSV + 60 fps video) + yaw rate per stick
- [ ] Camera-tilt method found (A3b) → tilt code next
**Total:** A 1 h 50 + travel + B ~5 h 15 + C 1 h 15 ≈ **8 h 20** (+ travel).

## Critical safety notes (read before the first flight)
- The pilot can ALWAYS take over on the phone; Esc / Ctrl+C on the laptop = sticks released = hover.
- Closed loop: max yaw 0.2, nobody within 3 m of the drone except the user at 4 m, **no red tops in view**.
- One drone program at a time. Mirror freezes → pilot lands by hand, then restart the program.
- Battery > 40% to start, land at 30%. Gusts → land and wait.
