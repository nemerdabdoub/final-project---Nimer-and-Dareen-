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

## Correction for the FIELD (live, phone cabled to the laptop) - added 25.11 15:10
- **Live is slower than offline:** the live chain adds phone -> USB -> video decoding. Measured with YOLO11n on charger:
  31.7 FPS offline vs **27.8 FPS live** (A6, 14:24) = about -12%.
- **Estimated live on battery:** YOLO11n ~20 FPS, **YOLO11m ~18 FPS** -> 11m should still pass 15 FPS but with less margin;
  the live B4 check on battery decides (if < 15 -> 11n).
- **The laptop also charges the S10 over the cable** (~5 W, ~8-10% of the 60 Wh battery per hour) -> heavy work
  ~50-55 min from 100%. Tips: S10 at 100% before leaving, unplug it when not flying, lid closed between tests.
