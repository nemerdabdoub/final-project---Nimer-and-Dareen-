# M06 - User tracking (due 7.12.2026)

**Goal:** from "find the user in a frame" (M05) to "follow the same user over time": keep the user's identity when the
turban is hidden, and turn the user's box into drone commands (distance controller, dry run first).

## Method (tool: `1_CODE/m06_track.py`)
- YOLO11n (the M05 choice) + a tracker: **ByteTrack** (fast, motion only) or **BoT-SORT** (adds appearance re-ID).
- The turban colour (M05 hybrid) **identifies** the user and gives his track ID; the tracker **keeps** that ID while the
  turban is not visible (max 10 s); the colour corrects the tracker whenever the turban is seen again.
- Dry-run controller: user box height vs a target (45% of the frame) → forward / back; horizontal offset → turn left/right.

## What we measure (on the 22.11 clips, never used for tuning)
| Metric | Meaning |
|---|---|
| user known % | frames where the system has a user (colour or track) - compared with the M05 1-second fallback |
| wrong person (by eye) | yellow "USER (track)" boxes on someone else = tracker swaps; count them in the video |
| re-identifications | colour picked a different ID than the tracker kept = the tracker had lost/swapped him |
| longest gap | longest time without a user (the drone would hover) |
| FPS | must stay real-time on the laptop |
Compare: ByteTrack vs BoT-SORT; old (M05) vs new (M06).

## Steps
1. Once on each laptop: `python -m pip install lap`.
2. Run on both 22.11 clips: `python m06_track.py ..\3_EVIDENCE\2026-11-22\<clip>.mp4` and again with `--tracker botsort`.
3. Watch each output video; write down the times of wrong yellow boxes. Fill the table above.
4. Choose the tracker; tune MAX_HOLD and the controller thresholds.
5. First live test (later, safe setup): controller commands shown on screen only, drone hovering, user walking slowly.
6. Then real following at walking speed, open space, spotter, land at 30%.

## Test 22.11 (code check only)
On a video built from the M05 test frames (1 picture per second, so IDs reset between jumps): runs end to end,
user known 74% (new) vs 72% (old). Real numbers come from the continuous 22.11 clips.
