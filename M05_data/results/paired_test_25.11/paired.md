# Paired test (McNemar, exact) on the same 403 hand-labelled frames, hybrid = + turban

| comparison | both right | only the bigger right | only YOLO11n right | both wrong | difference | p-value | verdict |
|---|---|---|---|---|---|---|---|
| yolo11m vs yolo11n | 354 | 7 | 0 | 42 | +1.7 pts | 0.016 | real difference |
| yolo26m vs yolo11n | 352 | 7 | 2 | 42 | +1.2 pts | 0.180 | could be luck (not significant) |

Only the frames where ONE model is right and the other wrong decide the test.
