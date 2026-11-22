"""m05_newclips.py - labelling for the NEW clips filmed 22.11 outside the Medical Faculty (bikes).

These frames are TEST-ONLY: never train on them. They give an honest check of what we tuned on the 20.11 frames
(the hand filter, the head-colour threshold) and later of M06 tracking.

Run from 1_CODE:
  python m05_newclips.py prepare        (Dareen, who has the clips) extract 1 frame every 2 s, draft labels with
                                        YOLO11l + turban colour, split into two halves in M05_data/test_22.11/ -> push
  python m05_newclips.py label nimer    correct your half in label_tool (same keys), saved to M05_data/test_22.11/labels
  python m05_newclips.py label dareen
  python m05_newclips.py check          both halves done? classes 0/1 only, values 0-1, at most one user per frame

Labelling rule (TEST labels, same as the M05 test): user = the actor in the turban, ALWAYS (also when the turban is
hidden); person = every other real person, also small and far ones; NO box on bikes, statues, posters, hands at the
lens or app buttons. A frame with nobody stays empty.
"""
import shutil, sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CLIPS = REPO / "3_EVIDENCE" / "2026-11-22"
STEMS = ["143404_recording_session1", "144943_recording_session2"]
EVERY_S = 2                                                               # 1 frame every 2 seconds
RAW = REPO / "3_EVIDENCE" / "m05_user_detection" / "newclips_22.11_frames"  # all extracted frames (laptop only)
SET = REPO / "M05_data" / "test_22.11"                                    # shared through git (small jpgs + txt)
HALF_DIRS = {"nimer": SET / "to_label_Nimer", "dareen": SET / "to_label_Dareen"}


def extract():
    RAW.mkdir(parents=True, exist_ok=True)
    total = 0
    for stem in STEMS:
        path = CLIPS / f"{stem}.mp4"
        if not path.exists():
            sys.exit(f"Missing {path}: run this on the laptop that has the 22.11 clips (Dareen's).")
        cap = cv2.VideoCapture(str(path))
        every = max(1, round((cap.get(cv2.CAP_PROP_FPS) or 25) * EVERY_S))
        i = n = 0
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            if i % every == 0:
                cv2.imwrite(str(RAW / f"{stem}_{i:05d}.jpg"), fr, [cv2.IMWRITE_JPEG_QUALITY, 88])
                n += 1
            i += 1
        print(f"{stem}: {n} frames")
        total += n
    print(f"{total} frames in {RAW}")


def prelabel():
    sys.argv = ["m05"]
    sys.path.insert(0, str(HERE))
    import m05
    from ultralytics import YOLO
    model = YOLO(m05.PRELABEL_MODEL)                                     # yolo11l: bigger than the tested models
    frames = sorted(RAW.glob("*.jpg"))
    counts = {w: 0 for w in HALF_DIRS}
    for d in HALF_DIRS.values():
        (d / "1_images").mkdir(parents=True, exist_ok=True)
        (d / "2_labels").mkdir(parents=True, exist_ok=True)
    for k, p in enumerate(frames):
        who = "nimer" if k % 2 == 0 else "dareen"                          # every other frame: both see both clips
        img = cv2.imread(str(p))
        h, w = img.shape[:2]
        people = m05.people_of(model, img)
        user = m05.hybrid_user(m05.turban_mask(img), people)
        lines = []
        for b in people:
            c = 0 if user is not None and m05.iou(b, user) > 0.9 else 1
            lines.append(f"{c} {(b[0]+b[2])/2/w:.6f} {(b[1]+b[3])/2/h:.6f} {(b[2]-b[0])/w:.6f} {(b[3]-b[1])/h:.6f}")
        shutil.copy2(p, HALF_DIRS[who] / "1_images" / p.name)
        (HALF_DIRS[who] / "2_labels" / (p.stem + ".txt")).write_text("\n".join(lines))
        counts[who] += 1
    for d in HALF_DIRS.values():
        (d / "2_labels" / "labels.txt").write_text("user\nperson\n")
    (SET / "labels").mkdir(parents=True, exist_ok=True)
    (SET / "labels" / ".gitkeep").touch()
    print(f"Halves: nimer {counts['nimer']} frames, dareen {counts['dareen']} frames, in {SET}")
    print("Now push M05_data/test_22.11 (frames are small; the videos stay on this laptop).")


def label(who):
    import label_tool                                                     # Nimer's tool, pointed at this set
    label_tool.OUT = SET / "labels"
    label_tool.HALVES = HALF_DIRS
    label_tool.OUT.mkdir(parents=True, exist_ok=True)
    sys.argv = ["label_tool", who]
    label_tool.main()


def check():
    out = SET / "labels"
    for who, d in HALF_DIRS.items():
        imgs = sorted(p.stem for p in (d / "1_images").glob("*.jpg"))
        done = [s for s in imgs if (out / f"{s}.txt").exists()]
        bad, multi, boxes, users, empty = 0, 0, 0, 0, 0
        for s in done:
            rows = [r.split() for r in (out / f"{s}.txt").read_text().splitlines() if r.strip()]
            bad += sum(len(r) != 5 or r[0] not in ("0", "1") or not all(0 <= float(v) <= 1 for v in r[1:]) for r in rows)
            u = sum(r[0] == "0" for r in rows)
            multi += u > 1
            users += u
            boxes += len(rows)
            empty += not rows
        print(f"{who}: {len(done)}/{len(imgs)} labelled · {boxes} boxes ({users} user) · {empty} empty · "
              f"bad lines {bad} · frames with >1 user {multi}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prepare":
        extract()
        prelabel()
    elif cmd == "extract":
        extract()
    elif cmd == "prelabel":
        prelabel()
    elif cmd == "label" and len(sys.argv) > 2 and sys.argv[2].lower() in HALF_DIRS:
        label(sys.argv[2].lower())
    elif cmd == "check":
        check()
    else:
        print(__doc__)
