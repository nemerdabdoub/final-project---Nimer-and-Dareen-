# User score: does it separate the user from other people? (yolo11n.pt, 403 hand-labelled frames)

YOLO's box number = detection confidence (is it a person?). The USER SCORE = is it OUR user? (`1_CODE/user_score.py`)

| | the user | other people |
|---|---|---|
| detected person boxes | 152 | 227 |
| median user score | 0.85 | 0.000 |
| score >= 0.5 | 76.3% | 2.2% |
| score < 0.05 | 15.8% | 94.7% |

**ROC AUC = 0.914** (1 = every user box scores above every other box; 0.5 = coin flip).
When the user is detected, she has the highest score in the frame in 147/152 frames.

Highest-scoring OTHER people (the risk: someone who looks like the user):
- 0.99  143404_recording_session1_00250.jpg
- 0.98  143404_recording_session1_00200.jpg
- 0.97  143404_recording_session1_00300.jpg
- 0.93  143404_recording_session1_00000.jpg
- 0.81  161951_recording_test60_00775.jpg
- 0.41  161951_recording_test60_01375.jpg

Lowest-scoring USER boxes (turban hidden / far / dark):
- 0.00  161825_recording_test30_00025.jpg
- 0.00  161825_recording_test30_00050.jpg
- 0.00  161825_recording_test30_00075.jpg
- 0.00  161825_recording_test30_00100.jpg
- 0.00  161825_recording_test30_00500.jpg
- 0.00  161951_recording_test60_00025.jpg

Pictures: `histogram_yolo11n.png`, `hard_cases_yolo11n.jpg` (top row = highest other people, bottom row = lowest users).

## What the hard cases show (by eye, 25.11)
- **Top 3 "other people" (0.97-0.99) = the red-shirt passer-by in session 1.** He is far, so his box is small and the
  "head" area (top 35% of the box) contains his red SHIRT. The colour rule cannot tell a red shirt under a head from a turban on it.
- 0.93 / 0.81 / 0.41 = boxes of people standing next to / in front of the user whose box includes her turban.
- Lowest users (0.00) = clip 161825 where her head (turban) is cut off at the top of the picture (label rule: the actor is ALWAYS user).
- In the follow demo (`demo_frame_redshirt_locked.jpg`) the tracker LOCKED on the red-shirt man at the start (USER 0.99) while the
  real user scored 0.84 -> in a live loop the drone would turn toward the wrong person. **This is the main M06 risk.**
- Fix ideas (to test on the NEW crossing clips, not tuned on these test frames): head area relative to box width (top ~20%),
  require skin/face below the red, or an appearance (re-ID) score learned when the turban is clear.
