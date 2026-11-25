# Digital twin results (25.11 evening) - `1_CODE/twin.py`, clip walk_60s (Nimer walking, hover), 70 s from second 60
Model: delay 0.5 s, turn 90 deg/s at full stick, lag 0.3 s, view 60 % of 118 deg, controller 15 Hz. Same frames every run.

**Validation:** twin with the flight settings: 50.3 % followed / 0.22 off-centre vs the real FOLLOW TEST: 55 % / 0.26 -> close.

| max turn | search turn | predictor | clothes learning | user followed | off-centre | yaw flips/min |
|---|---|---|---|---|---|---|
| 0.2 | no | no | no | 48.9 % | 0.28 | 5.1 |
| 0.2 | yes | no | no | 50.3 % | 0.25 | 5.1 |
| 0.3 | no | no | no | 48.9 % | 0.26 | 5.1 |
| 0.3 | yes | no | no | 50.3 % | 0.22 | 5.1 |
| 0.4 | no | no | no | 49.0 % | 0.25 | 5.1 |
| 0.4 | yes | no | no | 50.4 % | 0.22 | 5.1 |
| 0.3 | yes | yes | no | 50.3 % | 0.23 | 5.1 |
| 0.4 | yes | yes | no | 50.3 % | 0.23 | 5.1 |
| **0.3** | **yes** | **no** | **yes** | **82.6 %** | **0.21** | 9.4 |

**Findings:** people are in view ~97 % but the USER is locked only ~50 % -> the bottleneck is RECOGNITION (turban not seen),
not turning. Turn 0.3 vs 0.4 and the predictor change nothing; the search turn helps a little (0.28 -> 0.22).
**Clothes learning lifts "user followed" 50 % -> 82.6 %.** Caveat: mostly one person in this clip (clothes cannot be confused);
confirm in flight + on a crossing clip. Setting for the next flight: turn 0.3 + search + clothes learning (= AUTO_TESTS now).

## Crossing clip (session 1 with the red-shirt passer-by, first 60 s), 26.11
| clothes learning | user followed | off-centre | people in view |
|---|---|---|---|
| no | 62.7 % | 0.33 | 68 % |
| yes | 64.7 % | 0.28 | 68 % |
Small gain here (most of the missing % = nobody in view). "Followed" does not say WHO was followed: next step = compare the
twin's locked box with the hand labels of session 1 (Nimer labelled it) to count wrong-person frames.

## Right / wrong person vs Nimer's hand labels — whole session 1 clip (151 labelled frames), 26.11
| clothes learning | right | wrong person | missed (in view) | user outside view | correct "nobody" | false pick |
|---|---|---|---|---|---|---|
| no | 28 | 1 | 12 | 12 | 98 | 0 |
| yes | 29 | 1 | 11 | 12 | 98 | 0 |
User in view: right 68 % → 71 %, wrong 2.4 %, 0 false picks in 98 empty frames. Outdoors the turban is visible, so clothes
learning adds little here; its big gain (50 → 83 %) was on the indoor clip where the turban colour was not seen.
