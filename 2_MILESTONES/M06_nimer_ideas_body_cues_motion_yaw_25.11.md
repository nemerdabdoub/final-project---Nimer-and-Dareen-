# Nimer's ideas, tested: colour shades, body edges, pixel motion, CPU vs GPU, and the automatic turning (yaw) loop (25.11)

Question: besides the turban, can classic image cues (colour shades, body outline/edges, pixel movement) tell THE user from
other people - and are they cheap enough for the CPU? And how should the drone turn by itself to keep the user in view?

## 1. Measured: body colour and body edges vs the turban
`1_CODE/m05_body_cues.py` on the same hand-labelled frames (YOLO11n boxes). Live-style **enrolment**: per clip, the body of
the first 5 boxes with turban score >= 0.8 = the user's template ("this is me" at take-off). Every box is then compared to it.
Results: `M05_data/results/body_cues_25.11/summary.md` (350 boxes: 147 user / 203 other; clip 144943 skipped - no clear turban frame).

| cue | what it measures | ROC AUC | median user | median other | CPU ms / box |
|---|---|---|---|---|---|
| turban (today) | turban colour on the head | 0.928 | 0.87 | 0.00 | < 1 |
| body colour shades | hue x saturation histogram of the clothes | 0.846 | 0.67 | 0.36 | 0.13 |
| body shape / edges (HOG-style) | directions of the body's outlines | 0.759 | 0.48 | 0.38 | 0.74 |
| **turban + colour** | average of the two | **0.978** | 0.72 | 0.18 | ~1 |
| turban + colour + shape | average of three | 0.976 | 0.64 | 0.26 | ~2 |

**What it means**
- **Colour shades help a lot when added to the turban**: AUC 0.928 → **0.978** (fewer high-scoring strangers), for ~0.1 ms per box
  on the CPU. Alone it is weaker than the turban (strangers can wear similar colours).
- **Body edges/outline add nothing** on top (0.976): people's outlines look alike from a drone; the outline changes with every step.
- **Red-shirt passer-by:** turban alone 0.93–0.99 → turban + colour 0.62–0.79. Better, but still near the user's median (0.72),
  partly because in session 1 the enrolment itself picked up the red shirt (he was the first "turban" in the clip). Lesson:
  **enrol on a clear, close view of the user at take-off**, not on the first coloured box.
- Honest limits: one set of frames, simple averages (no weights fitted), the enrolment uses frames from the same clips.
  Re-test on the new crossing clips (hold-out).

## 2. Pixel movement (optical flow) - what it is good for, and what not
Optical flow = how each patch of pixels moved between two frames (Lucas-Kanade / Farneback in OpenCV; CPU, ~2–10 ms per frame
at low resolution).
- **Not an identity cue**: two walking people move the same way. (Gait recognition exists but needs long sequences and big data.)
- **Useful for:** (a) keeping the user's box between YOLO runs (cheap tracking on CPU if YOLO runs only every 2nd–3rd frame),
  (b) **ego-motion**: when the drone turns, the whole picture shifts - flow of the background measures how much the drone
  really turned (a free check of the yaw loop and of the command delay), (c) seeing who is moving TOWARD the user (crossing warning).
- The trackers we use already do (a) with a Kalman motion model (+ camera-motion compensation in BoT-SORT, which is optical flow inside).
→ Verdict: **no new identity cue; keep it in mind for ego-motion and the delay check.**

## 3. CPU or GPU?
| part | CPU | GPU |
|---|---|---|
| YOLO11n detection | ~30 FPS short / ~8–10 FPS when the laptop slows itself | ~50+ FPS |
| YOLO11m detection | ~6 FPS (fails) | ~45 FPS |
| turban + colour + edge cues | < 2 ms per box - **CPU is enough** | no gain (too small to move to the GPU) |
| optical flow (low res) | 2–10 ms per frame | not needed |
| deep re-ID network (OSNet etc.) | 10–20 ms per box | 2–4 ms per box |
**Nimer is right for the classic cues: they are CPU-cheap.** The neural network (YOLO) is what needs the GPU.
Plan: GPU for YOLO, CPU for the colour cues + controller - they run side by side.

## 4. The automatic turning (yaw) loop - how it works and how to make it good
`1_CODE/m06_follow.py` already has a first version. In words: **error → angle → stick**.
1. **Error:** x_err = (box centre − picture centre) / half the width, from −1 (far left) to +1 (far right).
2. **Angle:** the user is about x_err × (HFOV / 2) to the side. DJI Neo spec HFOV ≈ 118° (wide; check on the mirrored view by
   turning the drone 90° and counting). x_err = 0.5 ≈ 30° off-centre.
3. **Stick:** yaw = K × x_err, with a **dead band** (|x_err| < 0.15 → 0, no jitter), a **max** (0.25), and a **rate limit**
   (stick changes ≤ 0.05 per frame, no jerks). Not FOLLOWING → yaw 0 at once (hover).

**Why it can wobble: the delay.** The picture we steer on is ~0.3 s old (video 256 ms + detection 34 ms) + the command delay
(measured tomorrow). If K is too big, the drone overshoots, sees the user on the other side, turns back → oscillation.
Fixes, in order:
- small K first (0.3–0.5), raise slowly; keep the dead band;
- **D term (damping)**: yaw = K·x_err + D·(change of x_err) → brakes before overshooting;
- **predict ahead**: the tracker knows the user's speed across the picture → steer on where she WILL be after the delay
  (x + v·delay), a simple delay compensation (Smith-predictor idea).

**How to measure it (standard control metrics, from tomorrow's B5 CSV):** step test = user steps 2 m sideways and stops →
**rise time** (s to get her back to centre), **overshoot** (% past the centre), **settling time**, **steady error**, and
**% of time in the dead band**. Before/after each change of K or D. That is how an examiner expects a controller to be shown.

## 5. Recommendation
1. Add **body colour** to the user score (turban + colour) - CPU, ~0.1 ms, AUC 0.928 → 0.978. Enrol at take-off on a clear view.
2. Skip body edges as an identity cue; use optical flow only for ego-motion / delay checks if needed.
3. Keep YOLO on the GPU, cues + controller on the CPU.
4. Yaw loop: start P-only small K tomorrow, log it, then add D + prediction and compare with the step-test metrics.
5. Still to try (M06): YOLO pose to find the REAL head (fixes the red-shirt-in-head-area bug at the source) and a deep re-ID
   body score (BoT-SORT `with_reid`) - compare on the crossing clips against turban + colour.
