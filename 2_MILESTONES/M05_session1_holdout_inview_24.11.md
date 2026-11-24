# Session 1 hold-out: user found when in view (24.11, Nimer + Claude)

**Clip:** `3_EVIDENCE/2026-11-22/143404_recording_session1.mp4` (22.11, Med Faculty, DJI Fly screen recording, 5 min,
25 fps). Never used for tuning. The user wears a **red head covering** (brighter than the purple-red turban we tuned on),
white jacket, jeans. Other people: a man in front of her at the start, a **passer-by in a red shirt**, people far away.

**Method.** Detector: hybrid YOLO11n + turban colour, `python m05.py video <clip> yolo11n.pt` (conf 0.25, every 3rd frame,
1 s fallback). Sample: every 8th demo frame ≈ 1 frame/s → **313 frames**. Labels by eye (Claude, from the original video
without boxes, so not biased by the detector): **Y** = user in view with head visible (97), **P** = partly (sleeve/hand
close-up or head cut at the frame edge, 27), **N** = not in view (189). Then each detector pick checked by eye: user or
wrong person. Files: `M05_data/results/session1_inview_24.11/` (labels CSV + `make_sheets.py` + `score.py`).
Caveat: one labeller (Claude); Dareen or Nimer should spot-check ~30 frames, as on 23.11 (126/129 agreement then).

## Results (95% Wilson CI)

| Frames | n | User picked correctly | Wrong person | No pick |
|---|---|---|---|---|
| Y – user in view, head visible | 97 | **83 (85.6%, 77.2–91.2)** | **8 (8.2%, 4.2–15.4)** | 6 (6.2%) |
| P – partly in view | 27 | 6 (22.2%) | 0 | 21 |
| N – user not in view | 189 | – | **0 false picks (0%, 0–2.0)** | 189 |

So the raw "29% turban / 70% none" from the demo run was mostly the user being out of view (189/313 frames).

## What went wrong (all 8 wrong-person frames are in the first 13 s)
- **Frames 0–1: occlusion.** A man stands in front of her; the colour pixels of her head fall inside his box → his box is
  called USER. (Same "overlapping boxes" problem as the 23.11 talking point.)
- **Frames 7–12: red-shirt passer-by.** A man in a red shirt walks across; his shirt passes the colour test while she is
  partly hidden → he becomes USER for 6 s. Same failure as the 22.11 new clips (5 wrong = man in red shirt).
- **Misses (6, frames 110–113, 118–119):** she is far and at the bottom edge; YOLO gives no person box for her.

## What it means / next
- Colour marker generalises to a different red: 85.6% correct when in view on a never-tuned outdoor clip, 0 false picks
  in 189 empty frames.
- The weak spot is **identity, not detection**: red clothing on another person and occlusion. Fixes for M06:
  (1) tracker ID (BoT-SORT) — keep her ID from frames 2–6 instead of re-choosing every frame; (2) the hybrid already
  checks only the top `HEAD_PART` of each box, but for a small far person that strip still reaches the shirt →
  test a smaller `HEAD_PART` for small boxes, or require the colour blob above the shoulder line; (3) at a crossing (two boxes overlap) do not switch.
- Re-run this same scoring after each fix → before/after on the same 313 frames.
