
## clip 143404: 301 frames, 0 signal lost, 301 analysed
reference (yolo11l.pt @ 1280px): 307 people, 95 big (> 1/4 height), 10 on a bike, 368 bikes; frames with people: 180
| model | agrees with reference: all % | big % | riders % | extra boxes (not in ref) | extra on a bike | bikes found | ms/frame |
|---|---|---|---|---|---|---|---|
| yolo11n | 66.4 | 100.0 | 80.0 | 24 | 1 | 134 / 368 | 49 |
| yolo12n | 64.2 | 100.0 | 90.0 | 19 | 3 | 172 / 368 | 61 |
| yolo26n | 65.8 | 98.9 | 90.0 | 27 | 1 | 154 / 368 | 47 |
| yolo11n_drone_gentle | 59.3 | 92.6 | 80.0 | 31 | 4 | 0 / 368 | 48 |
turban: colour-only says 'user' in 156 frames, hybrid in 88 frames (check each in hybrid_user_picks.jpg / colour_only_alarms.jpg)

## clip 144943: 296 frames, 42 signal lost, 254 analysed
reference (yolo11l.pt @ 1280px): 90 people, 27 big (> 1/4 height), 1 on a bike, 26 bikes; frames with people: 51
| model | agrees with reference: all % | big % | riders % | extra boxes (not in ref) | extra on a bike | bikes found | ms/frame |
|---|---|---|---|---|---|---|---|
| yolo11n | 66.7 | 100.0 | 100.0 | 6 | 0 | 7 / 26 | 49 |
| yolo12n | 72.2 | 100.0 | 100.0 | 9 | 0 | 15 / 26 | 61 |
| yolo26n | 66.7 | 100.0 | 0.0 | 6 | 0 | 5 / 26 | 47 |
| yolo11n_drone_gentle | 56.7 | 100.0 | 100.0 | 3 | 0 | 0 / 26 | 48 |
turban: colour-only says 'user' in 67 frames, hybrid in 0 frames (check each in hybrid_user_picks.jpg / colour_only_alarms.jpg)

## clip all: 597 frames, 42 signal lost, 555 analysed
reference (yolo11l.pt @ 1280px): 397 people, 122 big (> 1/4 height), 11 on a bike, 394 bikes; frames with people: 231
| model | agrees with reference: all % | big % | riders % | extra boxes (not in ref) | extra on a bike | bikes found | ms/frame |
|---|---|---|---|---|---|---|---|
| yolo11n | 66.5 | 100.0 | 81.8 | 30 | 1 | 141 / 394 | 49 |
| yolo12n | 66.0 | 100.0 | 90.9 | 28 | 3 | 187 / 394 | 61 |
| yolo26n | 66.0 | 99.2 | 81.8 | 33 | 1 | 159 / 394 | 47 |
| yolo11n_drone_gentle | 58.7 | 94.3 | 81.8 | 34 | 4 | 0 / 394 | 48 |
turban: colour-only says 'user' in 223 frames, hybrid in 88 frames (check each in hybrid_user_picks.jpg / colour_only_alarms.jpg)