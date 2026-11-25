# Head area for the turban check: 35% (old) vs 20% (anatomy) - YOLO11n, 403 hand-labelled frames

| head area | user found | wrong person | false alarms | frames correct | user-score AUC | user median | others >= 0.5 | max score of the red-shirt man (session 1) |
|---|---|---|---|---|---|---|---|---|
| 35% | 115/164 (70.1%) | 3 | 0/239 | 87.8% | 0.914 | 0.85 | 2.2% | 0.99 |
| 20% | 123/164 (75.0%) | 2 | 0/239 | 89.8% | 0.919 | 0.97 | 2.2% | 0.98 |

0.20 chosen from anatomy before the run (head ~1/8 of body height + turban). Confirm on the new crossing clips.

## Red-shirt fix on session 1 (60 s, `m06_follow.py`), USER track ID per second (her = 2, red-shirt man = 4, 1 = man in front of her at the start)
| rule | s0-2 | s3-8 | s9-11 | s12-18 | ID switches |
|---|---|---|---|---|---|
| old sticky rule, head 35% (M05) | 1 1 2 | 2 2 2 2 2 2 | **4 4 4** | 2 ... | 10 |
| old sticky rule, head 20% | 1 1 2 | 2 2 2 2 2 2 | 2 **4 4** | 2 ... | 9 |
| **guarded switch + head 20% (new default)** | 1 1 1 | 2 2 2 2 2 2 | **2 2 2** | 2 ... | **3** |
| guarded + head 20% + `--colour` | 1 1 1 | 1 1 1 1 1 1 | 2 2 2 | 2 ... | 3 |
- New default: **the red-shirt man never gets the USER box**; switches 10 -> 3. Cost: the start stays 1 s longer on the man standing
  in front of her (his box holds her turban).
- With `--colour` the start is stuck 9 s on that man: the automatic enrolment learned the merged box, and the guard then refuses to
  switch away while "he" scores high. Lesson: enrol on a CLEAR view (E key, user alone) - as in the field-day checklist.
- One clip, and it was looked at before -> confirm on the new crossing clips (hold-out).
