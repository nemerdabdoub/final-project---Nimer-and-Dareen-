"""
m05_user_score_hist.py - Project 3760: does the USER SCORE separate the user from everybody else?

On the same 403 hand-labelled frames as the final M05 table: YOLO finds people, every detected box gets a user score
(user_score.py). A box counts as "user" if it overlaps the hand-labelled user box (IoU >= 0.5), else "other person".
Outputs (M05_data/results/user_score_25.11/):
  histogram.png   two histograms: user boxes vs other people (the picture Gabi asked for)
  summary.md      ROC AUC (1 = perfect separation, 0.5 = coin flip), medians, how many cross a 0.5 line,
                  highest-scoring OTHER people (the dangerous ones) and lowest-scoring users
  hard_cases.jpg  crops: the 6 highest-scoring other people and the 6 lowest-scoring users

  python m05_user_score_hist.py [yolo11n.pt]
"""
import sys
from pathlib import Path

import cv2
import numpy as np

import m05
from m05 import turban_mask, iou
from m05_userpick_allvideos import framesets, user_box, load_detector
from user_score import user_scores

OUT = Path(__file__).resolve().parent.parent / "M05_data" / "results" / "user_score_25.11"


def auc(pos, neg):
    """probability that a random user box scores higher than a random other box (ties = half)"""
    pos, neg = np.asarray(pos), np.asarray(neg)
    if not len(pos) or not len(neg):
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + 0.5 * eq) / (len(pos) * len(neg)))


def crop(img, b, size=160):
    x1, y1, x2, y2 = [int(v) for v in b]
    c = img[max(0, y1):max(y1 + 1, y2), max(0, x1):max(x1 + 1, x2)]
    h, w = c.shape[:2]
    k = size / max(h, w)
    c = cv2.resize(c, (max(1, int(w * k)), max(1, int(h * k))))
    out = np.full((size, size, 3), 255, np.uint8)
    out[:c.shape[0], :c.shape[1]] = c
    return out


def main():
    det = sys.argv[1] if len(sys.argv) > 1 else "yolo11n.pt"
    model = load_detector(det)
    users, others = [], []              # (score, frame path, box)
    n_frames = n_user_frames = top_is_user = 0
    for s, items in framesets().items():
        for it in items:
            img = cv2.imread(str(it[0]))
            u = user_box(it, img)
            people = m05.people_of(model, img)
            sc = user_scores(turban_mask(img), people)
            n_frames += 1
            if u is not None:
                n_user_frames += 1
            best = int(np.argmax(sc)) if sc else None
            for k, (b, v) in enumerate(zip(people, sc)):
                is_user = u is not None and iou(b, u) >= m05.IOU_MATCH
                (users if is_user else others).append((v, str(it[0]), b))
                if is_user and k == best:
                    top_is_user += 1
    pu = np.array([v for v, _, _ in users])
    po = np.array([v for v, _, _ in others])
    A = auc(pu, po)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    bins = np.linspace(0, 1, 21)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=130)
    ax.hist(po, bins=bins, color="#8a8f98", alpha=0.85, label=f"other people (n={len(po)})")
    ax.hist(pu, bins=bins, color="#2f9e44", alpha=0.85, label=f"the user (n={len(pu)})")
    ax.set_yscale("log")
    ax.set_xlabel("user score (0 = not the user, 1 = surely the user)")
    ax.set_ylabel("number of person boxes (log scale)")
    ax.set_title(f"User score: the user vs other people - {len(pu) + len(po)} boxes in {n_frames} hand-labelled frames, "
                 f"{det.replace('.pt', '')}\nROC AUC = {A:.3f}", fontsize=11)
    ax.axvline(0.5, color="#c92a2a", ls="--", lw=1)
    ax.text(0.51, ax.get_ylim()[1] * 0.5, "0.5", color="#c92a2a")
    ax.grid(axis="y", alpha=0.3)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"histogram_{det.replace('.pt', '')}.png")

    hi_o = sorted(others, key=lambda r: -r[0])[:6]
    lo_u = sorted(users, key=lambda r: r[0])[:6]
    tiles = []
    for rows in (hi_o, lo_u):
        row = []
        for v, p, b in rows:
            t = crop(cv2.imread(p), b)
            cv2.putText(t, f"{v:.2f}", (4, 154), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            row.append(t)
        while len(row) < 6:
            row.append(np.full((160, 160, 3), 255, np.uint8))
        tiles.append(np.hstack(row))
    cv2.imwrite(str(OUT / f"hard_cases_{det.replace('.pt', '')}.jpg"), np.vstack(tiles))

    def pct(a, cond):
        return 100 * float(np.mean(cond(a))) if len(a) else float("nan")
    lines = [f"# User score: does it separate the user from other people? ({det}, {n_frames} hand-labelled frames)", "",
             "YOLO's box number = detection confidence (is it a person?). The USER SCORE = is it OUR user? (`1_CODE/user_score.py`)", "",
             "| | the user | other people |", "|---|---|---|",
             f"| detected person boxes | {len(pu)} | {len(po)} |",
             f"| median user score | {np.median(pu):.2f} | {np.median(po):.3f} |",
             f"| score >= 0.5 | {pct(pu, lambda a: a >= 0.5):.1f}% | {pct(po, lambda a: a >= 0.5):.1f}% |",
             f"| score < 0.05 | {pct(pu, lambda a: a < 0.05):.1f}% | {pct(po, lambda a: a < 0.05):.1f}% |", "",
             f"**ROC AUC = {A:.3f}** (1 = every user box scores above every other box; 0.5 = coin flip).",
             f"When the user is detected, she has the highest score in the frame in {top_is_user}/{len(pu)} frames.", "",
             "Highest-scoring OTHER people (the risk: someone who looks like the user):"]
    lines += [f"- {v:.2f}  {Path(p).name}" for v, p, _ in hi_o]
    lines += ["", "Lowest-scoring USER boxes (turban hidden / far / dark):"]
    lines += [f"- {v:.2f}  {Path(p).name}" for v, p, _ in lo_u]
    lines += ["", f"Pictures: `histogram_{det.replace('.pt', '')}.png`, `hard_cases_{det.replace('.pt', '')}.jpg` "
              "(top row = highest other people, bottom row = lowest users)."]
    (OUT / f"summary_{det.replace('.pt', '')}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
