# Material for the end-of-semester-A (mid-project) presentation

Collected here so the presentation can reuse finished slides. Running log of results: `../mid_project_presentation_log.md`.

## M05 user detection (22.11): `M05_User_Detection_full_deck_22.11.pptx` / `.pdf` (16 slides)
The full deck. For the meeting on 23.11 a short version was used: `../M05_for_Gabi_23.11_short.pptx` (slides 1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 16).

| # | Slide | Reuse in the semester presentation |
|---|---|---|
| 1 | Finding THE user from a drone (title) | title / opening picture |
| 2 | M03 closed: the drone flies from our code | progress part |
| 3 | The M05 question + 4 requirements | **yes**: frames the main problem |
| 4 | Data: 152 frames, checked by hand | **yes**: method |
| 5 | Three ways to pick the user | **yes** |
| 6 | Our design: how the hybrid decides (5 steps) | **yes**: the core design slide |
| 7 | Key result: wrong person 36.5% → 0% | **yes**: main result |
| 8 | What it looks like (colour picks a sofa, hybrid picks the actor) | **yes** |
| 9 | Three YOLO models vs the 90% target | yes |
| 10 | All 8 detectors, accuracy vs speed | **yes**: engineering trade-off |
| 11 | **All results in one table** (7 methods: detection, precision, user found, wrong person, false alarm, frames correct, FPS) | **yes**: the full comparison |
| 12 | Final choice: YOLO11n + turban colour | **yes** |
| 13 | Where it fails, and why (small / cut-off people) | **yes**: limits and what we tried |
| 14 | Fine-tuning: a painting is not a person | yes: extra experiment (update with the final run) |
| 15 | Earlier projects in this line (DJI Tello) | **yes**: related work |
| 16 | Next: M06 tracking + questions | replace with the newest status |

Update before the presentation: numbers from the final runs, the new filming (bicycle / following distance), M06 results.
