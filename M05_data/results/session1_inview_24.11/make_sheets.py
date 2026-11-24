# Session 1 in-view labelling helper.
# Samples ~1 frame/s, makes numbered contact sheets from the ORIGINAL video (no boxes -> unbiased labels),
# and reads the detector's decision for the same frames from the demo video's drawn box colours.
import csv, sys
from pathlib import Path
import cv2
import numpy as np

orig, demo, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
STEP_DEMO = 8            # demo = every 3rd original frame at 8.33 fps -> 8 demo frames ~= 0.96 s
W, H, COLS, ROWS = 300, 169, 5, 4

cd, co = cv2.VideoCapture(str(demo)), cv2.VideoCapture(str(orig))
n = int(cd.get(cv2.CAP_PROP_FRAME_COUNT))
rows, tiles = [], []
for idx, k in enumerate(range(0, n, STEP_DEMO)):
    cd.set(cv2.CAP_PROP_POS_FRAMES, k); ok, fd = cd.read()
    co.set(cv2.CAP_PROP_POS_FRAMES, 3 * k); ok2, fo = co.read()
    if not (ok and ok2):
        break
    b, g, r = [fd[:, :, c].astype(int) for c in range(3)]
    green = int(((b < 60) & (g > 190) & (r < 60)).sum())                # USER box (0,220,0)
    kept = int(((b < 60) & (g > 170) & (g < 230) & (r > 220)).sum())    # USER (kept) box (0,200,255)
    blue = int(((b > 220) & (g > 90) & (g < 150) & (r < 40)).sum())     # person box (255,120,0)
    decision = "colour" if green > 300 else "kept" if kept > 300 else "none"
    rows.append({"idx": idx, "demo_frame": k, "orig_frame": 3 * k, "t_s": round(3 * k / 25, 1),
                 "detector": decision, "other_people_drawn": int(blue > 300)})
    t = cv2.resize(fo, (W, H))
    cv2.rectangle(t, (0, 0), (70, 26), (0, 0, 0), -1)
    cv2.putText(t, str(idx), (4, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    tiles.append(t)

per = COLS * ROWS
for s in range(0, len(tiles), per):
    chunk = tiles[s:s + per] + [np.zeros((H, W, 3), np.uint8)] * (per - len(tiles[s:s + per]))
    grid = np.vstack([np.hstack(chunk[r * COLS:(r + 1) * COLS]) for r in range(ROWS)])
    cv2.imwrite(str(out / f"sheet_{s // per:02d}.jpg"), grid, [cv2.IMWRITE_JPEG_QUALITY, 85])

with open(out / "detector.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "frames,", (len(tiles) + per - 1) // per, "sheets")
print({d: sum(r["detector"] == d for r in rows) for d in ("colour", "kept", "none")})
