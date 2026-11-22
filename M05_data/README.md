# M05_data: shared M05 data (through git, small files only)

| Folder | What | Who |
|---|---|---|
| `frames/` | all 152 frames (161951: 61, 154848: 40, 161825: 31, 154124: 20 without the actor) | done 22.11 |
| `to_label_Dareen/` | `1_images` (81 frames: 161951 + 154124) and `2_labels` (suggested labels + `labels.txt`) | Dareen corrects |
| `to_label_Nimer/` | `1_images` (71 frames: 154848 + 161825) and `2_labels` (suggested labels + `labels.txt`) | Nimer corrects |
| `labels/` | the CORRECTED YOLO `.txt` files, both halves together (152 when done) | both, by Sun 14:00 |
| `results/` | the CSV tables from `python m05.py run ...` | both |

Labelling in makesense.ai: upload `1_images`, "Load labels from file" = `2_labels/labels.txt` (user = 0, person = 1),
Actions > Import Annotations > YOLO > all files in `2_labels`. Fix the boxes, then Actions > Export Annotations > YOLO zip,
and put the `.txt` files in `labels/`.

Before running a check: copy `frames/` and `labels/` into `3_EVIDENCE/m05_user_detection/` (m05.py reads from there).
Never put videos or `*.pt` model files here.
