# Filming session 22.11.2026: outside the Medical Faculty (bike racks), new drone footage for M05 test + M06

Purpose: new clips the M05 detector never saw (honest test) and the first footage for M06 tracking
(people moving, crossing, bikes). Recorded from the drone camera with `record_video.py`.
Weather: clear, about 23 °C, some wind; a calmer spot was chosen near the bike racks.

| Clip (on Dareen's laptop, `3_EVIDENCE/2026-11-22/`) | Start | Length | Size | Notes |
|---|---|---|---|---|
| `143404_recording_session1.mp4` | 14:34 | about 5 min | 450 MB | first session |
| `144943_recording_session2.mp4` | 14:49 | almost 5 min | 276 MB | drone at **7-8 m height, next to trees**; battery **59% → 14%** |

## Battery (measured)
- Session 2: 59% → 14% in almost 5 minutes = about **9% per minute** at 7-8 m in light wind
  → a full battery gives roughly **11 minutes** of such flight (far less than DJI's still-air figure).
- **Lesson:** land at **30%** (not 14%), especially near trees or in wind: the drone needs reserve to come back.
  For the next session: plan clips of 3-4 minutes per battery and bring all batteries charged.

## What the height means for the data
- At 7-8 m people look small in the frame: good for testing/teaching **small and far people** (the M05 weak point),
  but it is **not** the following view (planned: 1.5-2 m height, 3-6 m away). Future M06 control tests need that lower view.

## Still to fill in (shot log)
- What happens when in each clip (walk / distance / crowd / bike / no turban), with times. Who wore the turban.
- Which clips are **test-only** (never used for training): decide before any training.

## Next
1. Scan both clips with `python m06_track.py <clip>` (user found by colour / kept by the tracker / none).
2. Pick test-only clips; extract about 1 frame/s from the rest for labelling if more training data is needed.
