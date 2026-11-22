# Open-vocabulary check on the 22.11 clips (186 frames, one every 3 s)
Reference for the COCO classes = YOLO11l at 1280 px (estimate, not hand labels).

| model | ms/frame | person: found % (extra) | bicycle: found % (extra) | car: found % (extra) | motorcycle: found % (extra) | electric scooter boxes | baby stroller boxes |
|---|---|---|---|---|---|---|---|
| yolo11n (COCO) | 49 | 67% (8) | 31% (3) | 52% (198) | 12% (7) | no class | no class |
| YOLO-World v2 s | 131 | 84% (23) | 36% (0) | 20% (12) | 4% (7) | 0 | 0 |
| YOLOE-11s | 142 | 83% (31) | 29% (3) | 29% (32) | 23% (12) | 3 | 9 |

Reference counts: person 128, bicycle 102, car 853, motorcycle 26
Scooter / stroller boxes must be checked by eye in crops_<model>.jpg (no reference exists).