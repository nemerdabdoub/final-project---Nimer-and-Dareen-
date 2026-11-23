"""
m06_track.py - Project 3760, milestone M06 (due 7.12): user TRACKING on recorded drone videos.

M05 found THE user in single frames: YOLO finds people, the turban colour on a head picks the user, and a
1-second fallback keeps the same person when the colour is lost. M06 replaces that fallback by a TRACKER:
YOLO11n + ByteTrack (or BoT-SORT) gives every person an ID that stays the same from frame to frame, so once the
turban has identified the user, the user stays known while the turban is hidden (head turned, blur, far away).

Rules for picking the user in every processed frame:
  1. colour   : the hybrid finds the turban on a head -> that person is the user, remember his track ID
  2. track    : no turban, but the remembered ID is still in the picture -> same person, still the user
                (at most MAX_HOLD seconds without seeing the turban again, then it stops trusting the ID)
  3. none     : neither -> no user in this frame (the drone would hover, not guess)
  If the colour picks a DIFFERENT ID than the remembered one, that is counted as a "re-identification"
  (the tracker had lost or swapped him; the colour corrects it).

The same run also computes the OLD M05 method (colour + 1-second fallback) on the same detections, so the two
can be compared on exactly the same frames, and a DRY-RUN distance controller: from the user's box it prints the
command the drone would get (turn left/right, forward/back, hold). Nothing is sent to the drone.

Once: python -m pip install lap   (the trackers need it)

Use (from 1_CODE):
  python m06_track.py VIDEO                         YOLO11n + ByteTrack, every 2nd frame
  python m06_track.py VIDEO --tracker botsort       BoT-SORT instead (has re-identification by appearance)
  python m06_track.py VIDEO --step 1 --seconds 60   every frame, only the first 60 s
  python m06_track.py VIDEO --model yolo11n_drone.pt   the fine-tuned model

Output in 3_EVIDENCE/m06_tracking/: <clip>_<tracker>.mp4 (green USER by colour, yellow USER by track,
blue others with their ID, the controller command at the bottom), <clip>_<tracker>_frames.csv (one row per
processed frame) and <clip>_<tracker>_summary.txt (the numbers below).
"""
import argparse
import csv
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m05                                     # same turban colour, head check, hand filter and CONF as in M05

OUT = Path(__file__).resolve().parent.parent / "3_EVIDENCE" / "m06_tracking"
MAX_HOLD = 10.0          # seconds the tracker may keep the user without seeing the turban again
OLD_FALLBACK = 1.0       # the M05 fallback: at most about 1 second
# dry-run distance controller (first version, to be tuned in flight tests)
TARGET_H = 0.45          # wanted user height as a fraction of the frame height (about 3-4 m away)
H_BAND = 0.08            # +- this around the target = "hold" (no forward/back)
X_BAND = 0.15            # user centre within +-15% of the frame centre = no turning


def controller(box, W, H):
    """The command the drone would get for this user box (dry run)."""
    if box is None:
        return "hover (no user)"
    x1, y1, x2, y2 = box
    x_err = ((x1 + x2) / 2 - W / 2) / (W / 2)          # -1 = far left, +1 = far right
    h_frac = (y2 - y1) / H
    parts = []
    if x_err < -X_BAND:
        parts.append("turn left")
    elif x_err > X_BAND:
        parts.append("turn right")
    if h_frac < TARGET_H - H_BAND:
        parts.append("forward")
    elif h_frac > TARGET_H + H_BAND:
        parts.append("back")
    return " + ".join(parts) if parts else "hold"


def main():
    ap = argparse.ArgumentParser(description="M06: track THE user in a recorded drone video")
    ap.add_argument("video")
    ap.add_argument("--model", default="yolo11n.pt")
    ap.add_argument("--tracker", default="bytetrack",
                    choices=["bytetrack", "botsort", "ocsort", "deepocsort", "fasttrack", "tracktrack"],
                    help="any tracker shipped with Ultralytics 8.4 (see ultralytics/cfg/trackers)")
    ap.add_argument("--step", type=int, default=2, help="process every Nth frame (1 = all)")
    ap.add_argument("--seconds", type=float, default=0, help="only the first N seconds (0 = whole video)")
    a = ap.parse_args()
    try:
        import lap  # noqa: F401  (needed by the ultralytics trackers)
    except ImportError:
        sys.exit("The tracker needs one extra package. Run:  python -m pip install lap   then start again.")

    model = m05.load_model(a.model)
    cap = cv2.VideoCapture(a.video)
    if not cap.isOpened():
        sys.exit(f"Cannot open {a.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    proc_fps = fps / a.step
    hold_max = max(1, round(MAX_HOLD * proc_fps))
    old_max = max(1, round(OLD_FALLBACK * proc_fps))
    OUT.mkdir(parents=True, exist_ok=True)
    stem = f"{Path(a.video).stem}_{a.tracker}"
    writer = None
    rows = []
    user_id, since_colour = None, 0
    old_last, old_run = None, 0
    new_count = {"colour": 0, "track": 0, "none": 0}
    old_count = {"colour": 0, "fallback": 0, "none": 0}
    reids, gaps, gap, longest_gap = 0, 0, 0, 0
    i = n = 0
    while True:
        ok, fr = cap.read()
        if not ok or (a.seconds and i >= a.seconds * fps):
            break
        if i % a.step:
            i += 1
            continue
        H, W = fr.shape[:2]
        r = model.track(fr, persist=True, classes=[0], conf=m05.CONF, tracker=f"{a.tracker}.yaml", verbose=False)[0]
        boxes = r.boxes.xyxy.cpu().numpy().astype(int).tolist()
        ids = r.boxes.id.cpu().numpy().astype(int).tolist() if r.boxes.id is not None else [None] * len(boxes)
        mask = m05.turban_mask(fr)
        by_colour = m05.hybrid_user(mask, boxes)

        # ---- NEW (M06): colour, else the remembered track ID
        user, src = None, "none"
        if by_colour is not None:
            k = max(range(len(boxes)), key=lambda j: m05.iou(boxes[j], by_colour))
            new_id = ids[k]
            if user_id is not None and new_id is not None and new_id != user_id:
                reids += 1
            user_id, since_colour, user, src = new_id, 0, boxes[k], "colour"
        elif user_id is not None and user_id in ids and since_colour < hold_max:
            user, src = boxes[ids.index(user_id)], "track"
            since_colour += 1
        else:
            since_colour += 1
        new_count[src] += 1
        if user is None:
            gap += 1
        else:
            if gap:
                gaps += 1
                longest_gap = max(longest_gap, gap)
            gap = 0

        # ---- OLD (M05): colour, else the 1-second overlap fallback
        old_user, old_src = by_colour, "colour" if by_colour is not None else "none"
        if old_user is None and old_last is not None and old_run < old_max:
            near = [b for b in boxes if m05.iou(b, old_last) >= 0.3]
            if len(near) == 1:
                old_user, old_src = near[0], "fallback"
        old_run = old_run + 1 if old_src == "fallback" else 0
        old_last = old_user
        old_count[old_src] += 1

        cmd = controller(user, W, H)
        rows.append([i, round(i / fps, 2), src, user_id if user is not None else "", *(user or ["", "", "", ""]),
                     old_src, cmd])

        # ---- picture
        for b, tid in zip(boxes, ids):
            if user is not None and b == user:
                continue
            cv2.rectangle(fr, tuple(b[:2]), tuple(b[2:]), (255, 120, 0), 2)
            m05.label_box(fr, f"person {tid}", b[0], b[1], (255, 120, 0), 0.55)
        if user is not None:
            col = (0, 220, 0) if src == "colour" else (0, 200, 255)
            cv2.rectangle(fr, tuple(user[:2]), tuple(user[2:]), col, 3)
            m05.label_box(fr, f"USER id {user_id} ({src})", user[0], user[1], col, 0.75)
        cv2.putText(fr, f"M06 {a.model.replace('.pt', '')} + {a.tracker} + turban   t={i / fps:5.1f}s", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(fr, f"command: {cmd}", (10, H - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        if writer is None:
            writer = cv2.VideoWriter(str(OUT / f"{stem}.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), proc_fps, (W, H))
        writer.write(fr)
        i += 1
        n += 1
        if n % 100 == 0:
            print(f"  {i / fps:5.0f} s done ...")
    cap.release()
    if writer:
        writer.release()
    if gap:
        gaps += 1
        longest_gap = max(longest_gap, gap)

    with open(OUT / f"{stem}_frames.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "time_s", "new_source", "user_id", "x1", "y1", "x2", "y2", "old_source", "command"])
        w.writerows(rows)
    tot = max(1, n)
    pct = lambda d, k: 100 * d[k] / tot
    lines = [
        f"M06 tracking: {Path(a.video).name}, {a.model} + {a.tracker}, every {a.step}. frame ({proc_fps:.1f}/s), {n} frames, {n / proc_fps:.0f} s",
        "",
        f"NEW (M06, colour + tracker): user known in {100 - pct(new_count, 'none'):.0f}% of frames "
        f"(colour {pct(new_count, 'colour'):.0f}%, kept by the tracker {pct(new_count, 'track'):.0f}%, none {pct(new_count, 'none'):.0f}%)",
        f"OLD (M05, colour + 1 s fallback): user known in {100 - pct(old_count, 'none'):.0f}% of frames "
        f"(colour {pct(old_count, 'colour'):.0f}%, fallback {pct(old_count, 'fallback'):.0f}%, none {pct(old_count, 'none'):.0f}%)",
        f"re-identifications by colour (tracker had lost or swapped him): {reids}",
        f"gaps without a user: {gaps}, longest {longest_gap / proc_fps:.1f} s",
        "",
        "Check by eye in the video: every yellow 'USER (track)' box must be the actor. A yellow box on someone else = a",
        "tracker swap (write down the time). That count is the M06 'wrong person' number.",
    ]
    (OUT / f"{stem}_summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nSaved in {OUT}: {stem}.mp4, {stem}_frames.csv, {stem}_summary.txt")


if __name__ == "__main__":
    main()
