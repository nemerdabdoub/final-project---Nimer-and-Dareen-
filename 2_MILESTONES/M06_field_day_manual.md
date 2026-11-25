# M06 FIELD DAY MANUAL (Wednesday, Nimer + Dareen together, 6–8 h)

Tick each box as you go. Times are estimates. **Rule of the day: everything that needs the drone gets done today;
everything else is computer work later** (see `M06_plan_together_step_by_step.md` §4).

## Why we are doing this (read together, 2 min)
- **Aim of M06:** the drone keeps the SAME user through crossings and moments when the turban is hidden, never follows
  the wrong person, and knows what to do when unsure (FOLLOWING / UNSURE / LOST).
- **Today's purpose:** collect the **test material** that proves it: crossing scenes nobody has tuned on, a 60 s clip
  (work-plan req. 4), and the **command delay** (the missing number in our delay budget: video 256 ms + detection ~34 ms + command ?).
- **Pass lines:** user kept >= 90% of frames · <= 1 ID swap in 10 crossings · 0 wrong-person follows · 60 s continuous ·
  >= 10 FPS long run.

## Tools checklist
**Hardware**
- [ ] DJI Neo + **3 or more batteries charged** (check the LEDs)
- [ ] Samsung S10 with DJI Fly, charged + USB cable (+ a spare cable)
- [ ] Dareen's laptop **100%** + charger
- [ ] Second phone that films **60 fps** (for the command delay) + a small stand or a person to hold it
- [ ] The purple-red turban (user)
- [ ] **A third person = passer-by**, ideally with a **red shirt** (the M05 failure case) + one other top (dark)
- [ ] 2 ground marks (cones / bags) at **3 m** and **6 m** from the drone
- [ ] Water, hat, power bank for the phones

**Software (on Dareen's laptop, in `1_CODE`)**
- [ ] scrcpy + ADB working (lab files in 1_CODE) · `drone_interface.py`
- [ ] `record_video.py` (records the mirror; keys T = take off, L = land, Esc = stop + save)
- [ ] `command_delay_test.py` (NEW: red flash + stopwatch on every command; Y = yaw right, U = yaw left)
- [ ] `m06_track.py` (YOLO11n + BoT-SORT + turban) for the first look in the evening

---

## TONIGHT (before the day) — 20 min
- [ ] 0.1 Charge everything: drone batteries, S10, laptop, second phone (5 min to plug in)
- [ ] 0.2 Book the passer-by (red shirt) and agree the time and place (big open space, little wind) (10 min)
- [ ] 0.3 Check the weather forecast (wind < 20 km/h) (5 min)

## BLOCK A — at the laptop, before leaving · ≈ 1 h 30 min
- [ ] **A1 Pull and agree (15 min)** — open a terminal in `1_CODE` (`OPEN_TERMINAL_HERE.bat`):
      `git pull` · read "Why we are doing this" above together · agree the pass lines.
      *You should see:* both of you can say the aim in one sentence.
- [ ] **A2 Connect the drone indoors (15 min)** — drone on the table, props OFF or drone not armed, S10 by USB, DJI Fly open
      **on the camera view**, Manual Control. Run `python connection_test.py`.
      *You should see:* the drone picture on the laptop.
- [ ] **A3 Fix the recording (30 min)** — `python record_video.py 0.5 indoor_test` (30 s).
      *You should see:* "Recording to: …" and at the end "Saved: … N frames". Open the .mp4 and check it plays.
      If it says "No frames were received": DJI Fly is not on the camera view, or adb is not on PATH → fix, try again.
      **If it still fails after 30 min → backup:** record on the drone itself (record button in DJI Fly) and download later.
- [ ] **A4 Command-delay script, dry run (15 min)** — `python command_delay_test.py --dry`. Press Y and U a few times.
      *You should see:* the screen flashes RED with a big stopwatch and "press #n"; nothing is sent to the drone;
      Esc → "Saved: …_command_delay_dry.csv".
- [ ] **A5 Take-off / land keys on the ground (10 min)** — only with the flight checklist and props on, in a safe spot:
      in `record_video.py`, T must show the take-off status, L the landing. If unsure, skip and take off by hand today.
- [ ] **A6 Pack (5 min)** — everything from the tools checklist.

## BLOCK B — at the field · ≈ 4 h (about 6 batteries)
**Before EVERY flight:** phone in hand · DJI Fly in **Manual Control** · big open space, nobody under the drone ·
battery > 40% · Ctrl+C / Esc ready · if anything looks wrong: **take over with the phone and land by hand**.
Fly at **following height 1.5–2 m**, user **3–6 m** away. Each clip **60–90 s**.
To record a clip: `python record_video.py 0 <name>` → T (or take off by hand) → film → land → Esc (saves).

- [ ] **B1 Set up (20 min)** — marks at 3 m and 6 m; laptop in the shade, on battery (note the battery %: ____ %);
      a 30 s test hover + short recording; check the file is saved.
- [ ] **B2 Crossing scenes = the M06 test set (≈ 90 min, ~3 batteries)** — film in this order (most important first):
  - [ ] `cross_front_LR` — passer-by walks **in front** of the user, left → right (do 3 crossings in one clip)
  - [ ] `cross_front_RL` — in front, right → left (3 crossings)
  - [ ] `redshirt_side` — passer-by in **red shirt** walks next to the user for 10 s, then away (the M05 failure)
  - [ ] `turn_away` — user turns her back (turban hidden) 3–5 s, 3 times
  - [ ] `continuous_60s` — **60 s+** of the user walking normally, the drone keeps her in view (req. 4)
  - [ ] `cross_behind` — passer-by walks **behind** the user, both directions
  - [ ] `cross_close` — crossing **1 m** from the user · `cross_far` — crossing **5 m** behind
  - [ ] `out_and_back` — user walks out of the picture and back in
  *You should see:* 8+ files in `3_EVIDENCE/<today>/`, each 60–90 s, the user mostly in the picture.
- [ ] **B3 Command delay (≈ 40 min, 1 battery)** — drone hovering at 1.5 m, nobody near. The second phone films the
      **laptop screen and the drone together** at **60 fps** (start filming first). Run `python command_delay_test.py`.
      Press **Y** (yaw right), wait 3 s, **U** (yaw left), wait 3 s … **10 presses** in total. Esc → hover → land by hand.
      *You should see:* the red flash on the screen, the drone turning a bit after it, "picture moved after … ms"
      in the terminal and "Saved: …_command_delay.csv". Repeat once if the phone video missed the screen.
- [ ] **B4 Laptop battery note (2 min)** — battery % at the end: ____ % after ____ h on battery.
- [ ] **B5 Filming note on the phone right away (10 min)** — for every clip: name, what happened (e.g. "2nd crossing too
      far"), time, light/sun, who wore what.
- [ ] **B6 Pack up, count batteries and props (10 min)**

*Not today:* the yaw-only "follow" test needs the controller (computer work after today). Do not improvise it in the field.

## BLOCK C — back at the laptop · ≈ 1 h 15 min
- [ ] **C1 Back up the videos (20 min)** — copy `3_EVIDENCE/<today>/` + the 60 fps phone video into
      `3_EVIDENCE/<today>_M06_field/` (NOT git); upload to the shared Drive for Nimer.
- [ ] **C2 Filming note (20 min)** — `2_MILESTONES/filming_M06_crossings.md`: table clip → scene → length → notes;
      plus the automatic loop-delay numbers from B3.
- [ ] **C3 First look (25 min)** — `python m06_track.py ..\3_EVIDENCE\<today>_M06_field\<cross_front_LR clip>.mp4 --tracker botsort`
      Watch the output video together. Write 3 lines: when was the user kept, when did the passer-by steal the ID.
      (First torch import can take 20–40 s.)
- [ ] **C4 Push (10 min)** — note + UPDATES line + presentation-log line ("field day: N crossing clips, loop delay X ms").

## End of the day — you should have
- [ ] 8+ crossing clips + one 60 s clip (the M06 hold-out test, never tuned on)
- [ ] Command-delay CSV + 60 fps phone video (counted later: frames from red flash to drone turn × 16.7 ms)
- [ ] Laptop battery use on a field day
- [ ] Filming note pushed; first impression of BoT-SORT on a crossing

**Total:** A 1 h 30 + travel + B 4 h + C 1 h 15 ≈ **7 h** (+ travel).
**Next (computer, later):** sticky-ID rule → safety states → CVAT labels → measure vs M05 → delay from the video →
controller offline → write-up (`M06_plan_together_step_by_step.md` §4). Long speed test on battery = at home, no drone needed.
