# Whole M06 pipeline speed (YOLO + BoT-SORT + turban/user score + controller), GPU (RTX 5050), 25.11 14:40
Offline on 120 s of session 1 (`m06_follow.py --video ... --seconds 120`), laptop battery % logged in the CSV.

| model | power | FPS median | FPS last 30 s | laptop battery |
|---|---|---|---|---|
| YOLO11n | charger | 31.7 | 30.6 | 100% |
| YOLO11m | charger | 28.8 | 27.7 | 100% |
| YOLO11n | battery | 23.1 | 14.9 (dip) | 100 -> 96% |
| YOLO11m | battery | 20.7 | 21.3 | 95 -> 91% |

- On battery ~25-30% slower. YOLO11m keeps ~21 FPS on battery -> passes the ">= 15 FPS on battery" rule (offline; live check in B4).
- Battery: ~4% per 2.5 min of heavy work -> ~1-1.5 h from full. Plug in whenever possible.
- With the paired test (11m better, p = 0.016) -> **YOLO11m is the choice unless the live B4 run drops below 15 FPS.**
