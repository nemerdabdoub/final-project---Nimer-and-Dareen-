"""
user_score.py - Project 3760: a USER SCORE (0..1) for every person box = "how much does this person look like OUR user?"

YOLO's number on a box is the DETECTION confidence ("is this a person?") - it is high for everyone, user or not.
This score answers the IDENTITY question ("is this person the user?"), like a re-identification / match score:
the user should get close to 1, everybody else close to 0.

It is built from the same two measurements the hybrid rule already uses (m05.hybrid_user):
  frac     = share of the head area (top 35% of the box) that is turban-coloured
  contrast = frac / share of turban colour just beside the head (a red wall or car behind = low contrast)
  score    = S(frac / 0.03) * S(contrast / 2),   S(r) = r^3 / (1 + r^3)
  -> at the hybrid's own thresholds (3% of the head, 2x contrast) each factor is 0.5;
     a clear turban (>= 6% and >= 4x) gives > 0.8; no turban colour gives ~0.
  A box that fills the frame (hand at the lens filter of M05) gets 0.
It is a SCORE, not a calibrated probability (that would need fitting on labelled data).
"""
import numpy as np

import m05


def _s(r):
    r3 = r ** 3
    return r3 / (1.0 + r3)


def turban_parts(mask, box):
    """(frac, side_frac) for one person box, exactly as in m05.hybrid_user; None if the hand filter rejects it."""
    H, W = mask.shape[:2]
    x1, y1, x2, y2 = [int(v) for v in box]
    if x2 - x1 > m05.MAX_USER_W * W and y2 - y1 > m05.MAX_USER_H * H:
        return None
    hy2 = y1 + max(1, int((y2 - y1) * m05.HEAD_PART))
    head = mask[max(0, y1):hy2, max(0, x1):x2]
    if not head.size:
        return None
    frac = float((head > 0).mean())
    sw = max(4, (x2 - x1) // 2)
    side = np.concatenate([mask[max(0, y1):hy2, max(0, x1 - sw):max(0, x1)].ravel(),
                           mask[max(0, y1):hy2, min(W, x2):min(W, x2 + sw)].ravel()])
    side_frac = float((side > 0).mean()) if side.size else 0.0
    return frac, side_frac


def user_score(mask, box):
    p = turban_parts(mask, box)
    if p is None:
        return 0.0
    frac, side_frac = p
    if frac <= 0:
        return 0.0
    contrast = frac / max(side_frac, 1e-3)
    return float(_s(frac / m05.MIN_HEAD_FRACTION) * _s(contrast / m05.CONTRAST))


def user_scores(mask, boxes):
    return [user_score(mask, b) for b in boxes]
