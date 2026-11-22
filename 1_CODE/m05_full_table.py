"""m05_full_table.py - ONE table for every method on ONE computer: accuracy (tables A and B), speed and CPU load.
Methods: colour only, YOLO11n / YOLOv12n / YOLO26n alone, and the hybrid (YOLO + turban colour) with each.
Run from 1_CODE (close other programs, charger in):   python m05_full_table.py
Needs 3_EVIDENCE/m05_user_detection/frames and labels (all 152 corrected). Saves m05_full_comparison.csv/.md there.

Frame sets (as decided 22.11): finding people (table A) on all labelled frames; finding THE user (table B) on the
frames where the actor wears the turban (all except clip 154124). Speed and CPU are measured over all frames.
CPU % = share of the WHOLE processor used while the method runs (100% = every core busy); cores = how many cores'
worth of work it used on average. The whole Python process uses about 0.7-1.0 GB of RAM."""
import csv, os, platform, sys, time
sys.argv = ["m05"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2, psutil
import m05
from ultralytics import YOLO

E = m05.ROOT
frames = m05.frames_in(E / "frames")
imgs = {p: cv2.imread(str(p)) for p in frames}
gts = {p: m05.read_labels(E / "labels", p, imgs[p].shape) for p in frames}
frames = [p for p in frames if gts[p] is not None]
marker = [p for p in frames if not p.name.startswith("154124")]
H = imgs[frames[0]].shape[0]
proc, ncpu = psutil.Process(), psutil.cpu_count()


def judge(gt, box=None, point=None):
    users = gt[0]
    if users:
        u = users[0]
        if box is not None:
            return "right" if m05.iou(box, u) >= m05.IOU_MATCH else "wrong"
        if point is not None:
            return "right" if u[0] <= point[0] <= u[2] and u[1] <= point[1] <= u[3] else "wrong"
        return "missed"
    return "alarm" if (box is not None or point is not None) else "none"


def run(step, k):
    """step(img) -> (people or None, pick box or None, pick point or None). Times every frame; returns stats."""
    views = {p: m05.darken(imgs[p], k) for p in frames}          # darkening is not timed
    out = {}
    c0, w0 = proc.cpu_times(), time.perf_counter()
    for p in frames:
        out[p] = step(views[p])
    wall = time.perf_counter() - w0
    c1 = proc.cpu_times()
    cpu = (c1.user - c0.user) + (c1.system - c0.system)
    s = {"FPS": len(frames) / wall, "ms/frame": 1000 * wall / len(frames),
         "CPU % of laptop": 100 * cpu / (wall * ncpu), "cores used": cpu / wall}
    # table A (finding people), all labelled frames
    if out[frames[0]][0] is not None:
        tp = fp = fn = btp = bn = 0
        for p in frames:
            g = gts[p][0] + gts[p][1]
            a, b, c = m05.match(out[p][0], g)
            tp, fp, fn = tp + a, fp + b, fn + c
            big = [q for q in g if q[3] - q[1] >= m05.BIG_PERSON * H]
            btp += m05.match(out[p][0], big)[0]; bn += len(big)
        s["detection % (all people)"] = 100 * tp / max(1, tp + fn)
        s["detection % (people > 1/4 height)"] = 100 * btp / max(1, bn)
        s["precision %"] = 100 * tp / max(1, tp + fp)
    # table B (finding THE user), turban frames
    res = [judge(gts[p], out[p][1], out[p][2]) for p in marker]
    wu = [r for r in res if r in ("right", "wrong", "missed")]
    wo = [r for r in res if r in ("alarm", "none")]
    s["user found %"] = 100 * wu.count("right") / max(1, len(wu))
    s["wrong person %"] = 100 * wu.count("wrong") / max(1, len(wu))
    s["false alarm %"] = 100 * wo.count("alarm") / max(1, len(wo))
    s["frames correct %"] = 100 * (wu.count("right") + wo.count("none")) / max(1, len(res))
    return s


rows = []
print(f"{len(frames)} frames ({len(marker)} with the turban marker) on {platform.node()}, {ncpu} logical cores")
for k in m05.BRIGHTNESS:
    rows.append({"method": "colour only", "brightness": k,
                 **run(lambda im: (None, None, m05.colour_only_user(m05.turban_mask(im))), k)})
    print(f"  colour only  {k}  done")
for m in m05.MODELS:
    model = YOLO(m)
    model(imgs[frames[0]], verbose=False)                      # warm-up, not timed
    name = m[:-3]

    def alone(im):
        ppl = m05.people_of(model, im)
        return ppl, (max(ppl, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])) if ppl else None), None

    def hybrid(im):
        ppl = m05.people_of(model, im)
        return ppl, m05.hybrid_user(m05.turban_mask(im), ppl), None

    for k in m05.BRIGHTNESS:
        rows.append({"method": f"{name} only (biggest person)", "brightness": k, **run(alone, k)})
        rows.append({"method": f"hybrid {name} + colour", "brightness": k, **run(hybrid, k)})
        print(f"  {name}  {k}  done")

cols = ["method", "brightness", "detection % (all people)", "detection % (people > 1/4 height)", "precision %",
        "user found %", "wrong person %", "false alarm %", "frames correct %",
        "FPS", "ms/frame", "CPU % of laptop", "cores used"]
fmt = lambda v: "-" if v is None else (f"{v:.1f}" if isinstance(v, float) and v not in m05.BRIGHTNESS else str(v))
order = sorted(rows, key=lambda r: (r["brightness"] != 1.0, r["method"].startswith("hybrid"),
                                    not r["method"].startswith("colour"), r["method"]))
with open(E / "m05_full_comparison.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in order:
        w.writerow([fmt(r.get(c)) for c in cols])
import subprocess
try:
    cpu_name = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
                              capture_output=True, text=True, timeout=60).stdout.strip() or platform.processor()
except Exception:
    cpu_name = platform.processor()
with open(E / "m05_full_comparison.md", "w", encoding="utf-8") as f:
    f.write(f"Full comparison on one laptop ({cpu_name}, {ncpu} logical cores, CPU only). "
            f"Table A metrics on {len(frames)} frames, table B on {len(marker)} turban frames.\n\n")
    f.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
    for r in order:
        f.write("| " + " | ".join(fmt(r.get(c)) for c in cols) + " |\n")
print(open(E / "m05_full_comparison.md", encoding="utf-8").read())
