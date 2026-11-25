# Classic body cues vs the turban (YOLO11n boxes, 350 boxes: 147 user / 203 other, clips with an enrolment: 4)

| cue | ROC AUC | median user | median other | CPU ms / box |
|---|---|---|---|---|
| turban (today) | 0.928 | 0.87 | 0.00 | <1 |
| body colour shades | 0.846 | 0.67 | 0.36 | 0.13 |
| body shape / edges (HOG) | 0.759 | 0.48 | 0.38 | 0.74 |
| turban + colour | 0.978 | 0.72 | 0.18 | sum |
| turban + colour + shape | 0.976 | 0.64 | 0.26 | sum |

Other people with turban score >= 0.9 (the red-shirt problem) - what the body cues say:
| frame | turban | colour | shape | turban+colour |
|---|---|---|---|---|
| 143404_recording_session1_00000.jpg | 0.93 | 0.65 | 0.68 | 0.79 |
| 143404_recording_session1_00200.jpg | 0.98 | 0.44 | 0.37 | 0.71 |
| 143404_recording_session1_00250.jpg | 0.99 | 0.51 | 0.61 | 0.75 |
| 143404_recording_session1_00300.jpg | 0.97 | 0.27 | 0.50 | 0.62 |

For comparison, the user's median colour similarity = 0.67.
Enrolment = first 5 frames per clip with a turban score >= 0.8 (live-style). Not tuned on these frames.
