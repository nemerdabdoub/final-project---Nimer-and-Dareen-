"""
m05_head_area_test.py - Project 3760: fix for "the red-shirt man is picked as the user".

Cause (seen 25.11): the turban is looked for in the TOP 35% of each person box. For a person far away (small box) or a
person in a red shirt, that top 35% contains the SHIRT, so red shirt = "turban". Anatomy: the head is ~1/8 of a standing
person's height (~12%); with the turban on top ~15-20%. So the head area should be ~20%, not 35%.
The value 0.20 is chosen from anatomy BEFORE looking at results (no tuning on these test frames); 0.35 = old.
Measures on the same 403 hand-labelled frames: hybrid user pick (right / wrong person / false alarm / frames correct)
and the user score (AUC, red-shirt boxes). Writes M05_data/results/head_area_25.11/summary.md
"""
from pathlib import Path

import cv2
import numpy as np

import m05
from m05 import turban_mask, hybrid_user, iou
from m05_userpick_allvideos import framesets, user_box, load_detector, judge
from m05_user_score_hist import auc
from user_score import user_scores

HEADS = [0.35, 0.20]
OUT = Path(__file__).resolve().parent.parent / "M05_data" / "results" / "head_area_25.11"


def main():
    model = load_detector("yolo11n.pt")
    cache = []
    for s, items in framesets().items():
        for it in items:
            img = cv2.imread(str(it[0]))
            cache.append((Path(it[0]).name, img, user_box(it, img), m05.people_of(model, img), turban_mask(img)))
    lines = ["# Head area for the turban check: 35% (old) vs 20% (anatomy) - YOLO11n, 403 hand-labelled frames", "",
             "| head area | user found | wrong person | false alarms | frames correct | user-score AUC | user median | others >= 0.5 | max score of the red-shirt man (session 1) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for hp in HEADS:
        m05.HEAD_PART = hp
        out = {"right": 0, "wrong": 0, "missed": 0, "alarm": 0, "none": 0}
        pu, po, red = [], [], []
        for name, img, u, people, mask in cache:
            out[judge(u, box=hybrid_user(mask, people))] += 1
            for b, v in zip(people, user_scores(mask, people)):
                if u is not None and iou(b, u) >= m05.IOU_MATCH:
                    pu.append(v)
                else:
                    po.append(v)
                    if name.startswith("143404"):
                        red.append(v)
        nu = out["right"] + out["wrong"] + out["missed"]
        nn = out["alarm"] + out["none"]
        lines.append(f"| {hp:.0%} | {out['right']}/{nu} ({100 * out['right'] / nu:.1f}%) | {out['wrong']} | {out['alarm']}/{nn} | "
                     f"{100 * (out['right'] + out['none']) / (nu + nn):.1f}% | {auc(pu, po):.3f} | {np.median(pu):.2f} | "
                     f"{100 * np.mean(np.array(po) >= 0.5):.1f}% | {max(red) if red else 0:.2f} |")
        print(lines[-1], flush=True)
    m05.HEAD_PART = 0.35
    lines += ["", "0.20 chosen from anatomy before the run (head ~1/8 of body height + turban). Confirm on the new crossing clips."]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
