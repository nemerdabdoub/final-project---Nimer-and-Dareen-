# M05 - Engineering considerations: alternatives we looked at

Short notes for the report and for the meeting with Gabi. Our baseline: **YOLO finds the people, the turban colour on the head picks the user (hybrid)**.

## 1. Alternatives to YOLO for finding people

| Detector | What it is | Compared with YOLO on our laptops (no GPU) |
|---|---|---|
| RT-DETR | Transformer-based real-time detector (runs with the same ultralytics library) | Similar or better accuracy, but much slower on a CPU (a few frames per second) |
| MobileNet-SSD / EfficientDet-Lite | Light detectors made for phones | Fast, but less accurate for small or partly hidden people seen from a drone |
| MediaPipe (Google) | Person / pose detection | Very fast on a CPU, but made for one or a few people close to the camera |
| HOG + SVM (classic OpenCV) | Pre-deep-learning person detector | Misses people who are not upright and facing the camera |
| Faster R-CNN | Two-stage detector | Accurate, but too slow for live drone control on a laptop |

**Decision:** YOLO, because it gives the best balance of speed and accuracy on a laptop without a GPU, and the drone needs real-time reactions. Possible later check: add RT-DETR to `m05.py` as one non-YOLO comparison.

## 2. Alternatives to the colour marker for knowing WHICH person is the user

| Option | Better than colour | Weaker | Effort |
|---|---|---|---|
| Printed marker (ArUco / AprilTag) | Nothing else in the scene looks like it; also gives the distance and angle to the user (useful for the M06 distance controller) | Must face the camera; needs about 15-20 cm at a few metres; motion blur | Low (built into OpenCV) |
| Tracking (ByteTrack / BoT-SORT + Kalman filter) | Keeps the same ID on the same person between frames; replaces the 1-second fallback; handles people crossing | Does not identify the user by itself; needs a first identification | Planned for M06 |
| Re-identification by appearance | No marker at all: learns the user's look at the start | Confused by similar clothes; heavier on a laptop | Medium (often part of BoT-SORT) |
| Face recognition | - | A drone sees heads from above or behind; privacy | Not chosen |
| Text-prompt detectors ("person with a red turban") | Flexible | Slow without a GPU, less reliable | Not chosen |

## 3. Platform: Crazyflie instead of the DJI Neo
Considered in November. Not chosen for now: no assembled drone available, no camera on it (the AI-deck would have to be ordered), a payload limit of about 40 g, and the AI-deck camera is 320x320 greyscale. We continue with the DJI Neo.

## What we say on Monday
"Our baseline is YOLO + colour marker. We also considered non-YOLO detectors (RT-DETR, MobileNet-SSD, MediaPipe): YOLO gives the best speed/accuracy balance on a laptop without a GPU. Next, M06 adds tracking, and we are considering a printed ArUco marker, which also gives the distance to the user, as an alternative to the colour."
