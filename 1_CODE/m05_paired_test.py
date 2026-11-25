"""
m05_paired_test.py - Project 3760: is hybrid YOLO11m (or YOLO26m) REALLY better than hybrid YOLO11n?

Same 403 hand-labelled frames and rules as m05_userpick_allvideos.py. A frame is "correct" when the hybrid picks the
user (IoU >= 0.5) in a frame with the user, or picks nobody in a frame without the user.
McNemar (exact): only the frames where ONE model is right and the other wrong count. If those split about evenly,
the difference can be luck. p < 0.05 = the difference is real.

  python m05_paired_test.py          (GPU env recommended: C:\\Users\\LOREN\\venvs\\gpu\\Scripts\\python.exe)
Writes M05_data/results/paired_test_25.11/paired.md
"""
from math import comb
from pathlib import Path

import cv2

import m05
from m05 import turban_mask, hybrid_user
from m05_userpick_allvideos import framesets, user_box, load_detector, judge

MODELS = ["yolo11n.pt", "yolo11m.pt", "yolo26m.pt"]
OUT = Path(__file__).resolve().parent.parent / "M05_data" / "results" / "paired_test_25.11"


def mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def main():
    frames = []
    for s, items in framesets().items():
        for it in items:
            img = cv2.imread(str(it[0]))
            frames.append((img, user_box(it, img)))
    correct = {}
    for det in MODELS:
        model = load_detector(det)
        res = []
        for img, u in frames:
            out = judge(u, box=hybrid_user(turban_mask(img), m05.people_of(model, img)))
            res.append(out in ("right", "none"))
        correct[det.replace(".pt", "")] = res
        print(det, f"{100 * sum(res) / len(res):.1f}% correct", flush=True)

    base = "yolo11n"
    lines = [f"# Paired test (McNemar, exact) on the same {len(frames)} hand-labelled frames, hybrid = + turban", "",
             "| comparison | both right | only the bigger right | only YOLO11n right | both wrong | difference | p-value | verdict |",
             "|---|---|---|---|---|---|---|---|"]
    for other in [m for m in correct if m != base]:
        a, o = correct[base], correct[other]
        both = sum(x and y for x, y in zip(a, o))
        only_o = sum(y and not x for x, y in zip(a, o))
        only_a = sum(x and not y for x, y in zip(a, o))
        none = sum(not x and not y for x, y in zip(a, o))
        p = mcnemar_p(only_o, only_a)
        diff = 100 * (only_o - only_a) / len(a)
        verdict = "real difference" if p < 0.05 else "could be luck (not significant)"
        lines.append(f"| {other} vs {base} | {both} | {only_o} | {only_a} | {none} | {diff:+.1f} pts | {p:.3f} | {verdict} |")
    lines += ["", "Only the frames where ONE model is right and the other wrong decide the test."]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "paired.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
