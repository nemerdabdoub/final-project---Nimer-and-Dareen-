# M05: why the numbers fall short, and how to fix it (Dareen, 22.11)

For Nimer's one-page summary and for the meeting. Measured on all 152 corrected labels with YOLO11n.
Reproduce: `python m05_diagnose.py` (in 1_CODE; prints only).

## Where M05 stands
| Step | Status |
|---|---|
| 152 frames, all labels corrected | done |
| Table A (C2-C4) + speed run | done (Nimer) |
| Table B (C1 + H1-H3), no-marker row, 2 screenshots | done (both laptops, identical numbers) |
| Winner | **to write down**: everything points to YOLO11n |
| Demo video | **not made** (Dareen): `python m05.py video "..\3_EVIDENCE\2026-11-20\161951_recording_test60.mp4" yolo11n.pt` |
| One-page summary, AI log lines | **open** (Nimer by Mon 12:00; both add an AI log line) |

**Winner sentence (proposal):** Winner = YOLO11n, because it is both the most accurate (85.4% detection, 94% precision)
and the fastest (21 FPS on a laptop CPU). The 90% target was not reached because of small and cut-off people;
for people at following distance it finds 96%.

## Problem 1: detection rate 82-85%, below the 90% target
All misses are small or cut-off people (YOLO11n, conf 0.25, 640 px):

| Person in the frame | People | Missed |
|---|---:|---:|
| large (> 50% of the frame height), fully visible | 124 | 0% |
| medium (25-50%), fully visible | 72 | 0% |
| large, cut by the frame edge | 18 | 11% |
| medium, cut by the edge | 25 | 28% |
| small (< 25% of the height) | 72 | **46%** |
| small and cut by the edge | 4 | 100% |

- Without the small people: 96% detected (230 of 239). Fully visible people taller than 1/4 of the frame: 100%.
- Tried: conf 0.15 → 86.3% but precision drops to 88.3%; 960 px input → 83.8% (no help).
- **Fixes:** a slightly bigger model (YOLO11s, test the speed); the M06 distance controller keeps the user large in the
  picture; define the target for people above a minimum size (the drone follows one nearby person, not the background).

## Problem 2: the hybrid finds the user in only 73-74%
Of its 28 misses on the 104 frames with the actor (YOLO11n hybrid):
- 23: YOLO boxed him, but too little turban colour on the head (9 of them 0%: turned away or hidden; the rest 0.1-3%,
  just under the 3% threshold).
- 4: colour there, but it failed the "2x the background beside the head" test.
- 1: YOLO did not box him at all.

Lowering the head-colour threshold is a trade-off (same 132 frames):

| Threshold | Found | Wrong person | False alarm |
|---|---:|---:|---:|
| 3% (now) | 73.1% | 0% | 7.1% |
| 2% | 77.9% | 0% | 10.7% |
| 1% | 81.7% | 1.0% | 14.3% |
| 0.5% | 84.6% | 1.0% | 28.6% |

- **Fix:** keep 3% (never the wrong person) and let **M06 tracking** keep the same person through the frames where the
  turban is not seen. Note: these thresholds were set on the same frames we test on; tuning them to these numbers
  would be fitting the test set, so we report the trade-off instead.

## Problem 3: without the turban the hybrid finds nobody
154124 (20 frames): 0% found, 0% wrong (it picks nobody, the safe failure). Colour only is wrong 100%.
- **Fix (M06):** tracking (ByteTrack / BoT-SORT + Kalman) + re-identification by appearance, or a printed ArUco marker
  (also gives the distance to the user).

## Problem 4: the hybrid's 2 false alarms = a hand in front of the lens
154848 frames 00114 and 00152: YOLO calls the hand a person and the pink skin passes as the turban colour.
- **Fix:** ignore "people" boxes that fill almost the whole frame (one line in `hybrid_user`).

## Problem 5: limits of the test
One place, one day, 152 frames; the dark test is darkened copies, not a real low-light flight; frames are 1 s apart,
so the 1-second fallback is barely tested. These match the 3 questions for Gabi (plan part 7).
