# M06 user tracking: step-by-step plan, done TOGETHER (Nimer + Dareen)

Due: **Mon 7.12.2026**. Written 25.11. Tick `- [ ]` → `- [x]` and push after each session.
Times are estimates for the two of us working together, with Claude. Total ≈ **27 h over 8 sessions** + 1 day buffer.

**The aim in one line:** keep the SAME user's identity in >= 90% of frames, even when the turban is hidden or someone
walks past; never follow the wrong person; and the drone knows what to do when it is unsure.
Why: M05 picks the user by the turban in each frame alone (identified 73%). A tracker remembers her between sightings.

**Where we start:** `1_CODE/m06_track.py` (YOLO + tracker + turban). BoT-SORT best of 6 trackers. Nimer's session-1 run:
no gain yet (83.5% vs 85.6%) because the colour always overrides the track ID → a red-shirt passer-by takes over.

---

## Session 1 (Thu 26.11) — goals + the sticky-ID rule · ≈ 3.5 h
- [ ] 1.1 `git pull`, read this plan and the newest `UPDATES.md` entries together (10 min)
- [ ] 1.2 Write the M06 pass lines in this file (section "Pass lines" below) — agree on each number (20 min)
- [ ] 1.3 Requirement trace table: exact words of the approved work plan → our test → result → status
      (`2_MILESTONES/M06_requirement_trace.md`) (30 min)
- [ ] 1.4 Watch Nimer's session-1 failure (red-shirt frames) together; write in 3 lines WHY it fails (20 min)
- [ ] 1.5 Code the **sticky-ID rule** in `m06_track.py`: keep following the tracked ID; switch to another ID only if
      the turban is seen on it in N frames in a row AND not on the current one (N = 3 to start) (90 min)
- [ ] 1.6 Re-run on session 1 (same 313 frames) → compare with M05 baseline: correct 85.6%, wrong person 8.2%, 0 false picks (20 min)
- [ ] 1.7 Push code + result + one UPDATES line (10 min)
**You should see:** wrong-person frames drop clearly below 8.2% on session 1.

## Session 2 (Fri 27.11) — safety states · ≈ 2.5 h
- [ ] 2.1 Define the 3 states and their exact rules (30 min):
      FOLLOWING (user track seen) → move · UNSURE (user track lost < 2 s, or two candidates) → hover, wait ·
      LOST (> 2 s, no turban) → hover, then pilot lands by hand
- [ ] 2.2 Code the states in `m06_track.py`, show the state on the demo video (60 min)
- [ ] 2.3 Run on all clips we have; count frames in each state; check by eye that UNSURE/LOST appear when they should (45 min)
- [ ] 2.4 Push + UPDATES line (15 min)
**You should see:** a video with FOLLOWING / UNSURE / LOST written on it, matching what happens on screen.

## Session 3 (Sat 28.11 or Sun 29.11) — film crossing scenes (field) · ≈ 3 h incl. travel
- [ ] 3.1 Before: flight checklist (phone in hand, Manual Control, open space, battery > 40%), 2 batteries charged, a third
      person in a different red/dark shirt as the "passer-by" (15 min)
- [ ] 3.2 Film at following height (1.5–2 m, 3–6 m away), 60–90 s each (≈ 90 min on site):
      - [ ] passer-by crosses IN FRONT of the user, left→right and right→left
      - [ ] passer-by crosses BEHIND the user
      - [ ] passer-by close (1 m) and far (5 m)
      - [ ] user turns away (turban hidden) for 3–5 s
      - [ ] user walks out of frame and back in
      - [ ] one clip of 60 s continuous following with no tricks (work-plan req. 4)
- [ ] 3.3 Write a short filming note (what each clip shows, time, light) `2_MILESTONES/filming_M06_crossings.md` (20 min)
**These clips are the M06 hold-out test: we never tune on them.**

## Session 4 (Mon 30.11) — label the crossing clips · ≈ 4 h
- [ ] 4.1 Extract ~5 frames/s from the crossing clips (enough to see each crossing) (15 min)
- [ ] 4.2 Label with track IDs in CVAT (work-plan tool; it fills boxes between key frames): user = ID 1, others = 2, 3… (3 h)
- [ ] 4.3 Check 20 random frames each (swap laptops), fix mistakes (30 min)
- [ ] 4.4 Push labels to `M05_data/` style folder `M06_data/` (small files only) (15 min)

## Session 5 (Tue 1.12) — measure: does tracking beat M05? · ≈ 3.5 h
- [ ] 5.1 Run on the hold-out clips: M05 baseline (no tracker) vs tracker + sticky ID, with YOLO11n and YOLO11m (60 min)
- [ ] 5.2 Count per method: % user kept, wrong-person frames, ID swaps per crossing, recovery time after the turban
      comes back, IDF1 and HOTA (TrackEval) (90 min)
- [ ] 5.3 One table + 95% intervals; paired test 11n vs 11m on the same frames (McNemar) (40 min)
- [ ] 5.4 Push results + UPDATES + presentation-log line (20 min)
**You should see:** one table that says if we pass "user kept >= 90%" and "<= 1 swap in 10 crossings".

## Session 6 (Wed 2.12) — command delay (drone) · ≈ 2 h
- [ ] 6.1 Script sends one stick command and logs the exact time; film the drone + the laptop screen with the phone at 60 fps (45 min)
- [ ] 6.2 Count frames from "command sent" to "drone starts moving"; 10 repeats → mean and spread (60 min)
- [ ] 6.3 Write the delay budget: video 256 ms + detection ~34 ms + command ? ms = total (15 min)

## Session 7 (Thu 3.12 + Fri 4.12) — controller · ≈ 6 h
- [ ] 7.1 Proportional controller: box centre → turn, box height → forward/back; dead band (no tiny moves) and rate limit (90 min)
- [ ] 7.2 Run it OFFLINE on the recorded clips; plot the commands over time; check they make sense (90 min)
- [ ] 7.3 Ground test: drone NOT flying, commands only printed, user walks in front of the camera (45 min)
- [ ] 7.4 Hover-only test with the flight checklist: only turn (yaw) on, Ctrl+C = stop (90 min incl. setup)
- [ ] 7.5 Push + UPDATES (15 min)

## Session 8 (Sat 5.12) — write-up · ≈ 2.5 h
- [ ] 8.1 One-page M06 summary: question → method → table → decision → limits (60 min)
- [ ] 8.2 Decision log (why BoT-SORT, why sticky ID, why 11n/11m, thresholds) (30 min)
- [ ] 8.3 Demo video 1 min of the best crossing (30 min)
- [ ] 8.4 Questions for Gabi + update CLAUDE.md status + presentation log (30 min)

**Sun 6.12 = buffer** (things always slip, especially filming and flights).

---

## Pass lines (agree in step 1.2, then confirm with Gabi)
| What | Pass line | Source |
|---|---|---|
| User kept (correct ID) | >= 90% of frames she is in | work plan req. 1 |
| ID swaps on crossings | <= 1 in 10 crossings | mentor plan |
| Wrong-person follows | 0 (drone never moves toward the wrong person) | safety |
| Continuous tracking | 60 s, track losses counted | work plan req. 4 |
| Speed | >= 10 FPS for the whole pipeline, long run | work plan req. 3 |

## Main risks
- Test clips without real crossings → the tracker looks perfect and proves nothing. Film crossings FIRST.
- Weather / field access for sessions 3, 6, 7 → swap the order with sessions 4–5 if needed.
- Laptop slows itself under long load (~8–10 FPS) → check speed in step 5.1 on a long run.
