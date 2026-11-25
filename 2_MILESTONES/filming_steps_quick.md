# Quick filming steps (one clip at a time) — keep every clip, decide later

**Every clip, same 4 steps:**
1. Nimer pastes the command (BEFORE take-off) in a PowerShell terminal.
2. "REC" window shows → take off by hand, hover 1.5 m facing Dareen 4 m away.
3. Do the scene.
4. Land by hand → click the REC window → **Esc** (saves to `3_EVIDENCE\<today>\..._recording_<name>.mp4`).

Command (change only the last word = clip name):
```powershell
cd "C:\Users\LOREN\Desktop\final-project---Nimer-and-Dareen-\1_CODE"; & 'C:\Users\LOREN\venvs\gpu\Scripts\python.exe' run_with_adb.py record_video.py 0 walk_60s
```

| # | name (last word) | scene |
|---|---|---|
| 1 | `walk_60s` | walk normally left / right for 60 s |
| 2 | `turn_away` | turn your back 3–5 s, 3 times |
| 3 | `out_and_back` | walk out of the picture and come back, 2 times |
| 4 | `cross_front` | Nimer (or anyone) crosses in front of Dareen, both ways — pilot stays at the base with the phone |
| 5 | `walk_close_far` | walk slowly toward the drone to 2 m, then back to 6 m |
| 6 | `from_above` | hover 3.5–4 m high; in a 2nd terminal: `& 'C:\Users\LOREN\venvs\gpu\Scripts\python.exe' gimbal.py to -30`; walk + turn away; after: `gimbal.py level` |
| 7 | `low_light` | any scene as it gets dark (low-light test data for the work plan) |

Rules: battery > 40% to start, land at 30%; sun behind the drone; "go" only when hovering; Esc after landing.
