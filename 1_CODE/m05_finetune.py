"""m05_finetune.py - teach YOLO11n our drone scenes (paintings / statues / mural are NOT people), same speed.
Training frames come ONLY from the 6 clips of 20.11 that the M05 test never used, plus the 20.10 classroom drone clip
(split every other second between the halves); the 152 test frames stay test-only.

Run from 1_CODE:
  python m05_finetune.py extract        ~270 frames (1 per second) from the 6 unused clips
  python m05_finetune.py prelabel       suggested boxes (YOLO11l) + split into two halves in M05_data/train/
  python m05_finetune.py label dareen   correct your half in Nimer's label_tool (same keys), saved to M05_data/train/labels
  python m05_finetune.py label nimer
  python m05_finetune.py train          fine-tune yolo11n on the corrected labels -> 1_CODE/yolo11n_drone.pt (not in git)
  python m05_finetune.py train 15 gentle   keep the 80-class head, freeze the backbone, small learning rate
                                           -> 1_CODE/yolo11n_drone_gentle.pt
Labelling rule for training: box EVERY real person (user or person, both fine); NO box on paintings, statues, the mural,
hands at the lens or app buttons - leaving them empty is exactly what teaches the model they are not people."""
import shutil, sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CLIPS = REPO / "3_EVIDENCE" / "2026-11-20"
TRAIN = REPO / "M05_data" / "train"
RAW = REPO / "3_EVIDENCE" / "m05_user_detection" / "train_frames"        # all extracted frames (laptop only)
HALVES = {"dareen": ["162603_recording_test60", "160733_recording_test10"],
          "nimer": ["152950_connection_test_video", "153832_connection_test_video",
                    "161703_connection_test_video", "161723_recording_test30"]}
TEST_CLIPS = ("161951", "154848", "161825", "154124")                   # never used for training
# shared clip from another day and room (drone camera, people in ~1/3 of it): every other second to each half
SHARED = {"1621_drone_view_classroom_flight_REALTIME": REPO / "3_EVIDENCE" / "2026-10-20"}


def clip_path(stem):
    return SHARED.get(stem, CLIPS) / f"{stem}.mp4"


def owner(path, who, clips):
    """does this extracted frame belong to `who`'s half?"""
    for stem in SHARED:
        if path.name.startswith(stem):
            k = sorted(p.name for p in RAW.glob(stem + "_*.jpg")).index(path.name)
            return k % 2 == (0 if who == "dareen" else 1)
    return path.name.startswith(tuple(clips))


def extract():
    RAW.mkdir(parents=True, exist_ok=True)
    total = 0
    for stem in [s for clips in HALVES.values() for s in clips] + list(SHARED):
            assert not stem.startswith(TEST_CLIPS), stem
            cap = cv2.VideoCapture(str(clip_path(stem)))
            every = max(1, round(cap.get(cv2.CAP_PROP_FPS) or 25))     # 1 frame per second
            i = n = 0
            while True:
                ok, fr = cap.read()
                if not ok:
                    break
                if i % every == 0:
                    cv2.imwrite(str(RAW / f"{stem}_{i:05d}.jpg"), fr); n += 1
                i += 1
            print(f"{stem}: {n} frames"); total += n
    print(f"{total} training frames in {RAW}")


def prelabel():
    sys.argv = ["m05"]
    sys.path.insert(0, str(HERE))
    import m05
    from ultralytics import YOLO
    model = YOLO(m05.PRELABEL_MODEL)
    for who, clips in HALVES.items():
        img_dir, lab_dir = TRAIN / f"to_label_{who.capitalize()}" / "1_images", TRAIN / f"to_label_{who.capitalize()}" / "2_labels"
        img_dir.mkdir(parents=True, exist_ok=True); lab_dir.mkdir(parents=True, exist_ok=True)
        n = 0
        for p in sorted(RAW.glob("*.jpg")):
            if not owner(p, who, clips):
                continue
            img = cv2.imread(str(p)); h, w = img.shape[:2]
            people = m05.people_of(model, img)
            user = m05.hybrid_user(m05.turban_mask(img), people)
            lines = []
            for b in people:
                c = 0 if user is not None and m05.iou(b, user) > 0.9 else 1
                lines.append(f"{c} {(b[0]+b[2])/2/w:.6f} {(b[1]+b[3])/2/h:.6f} {(b[2]-b[0])/w:.6f} {(b[3]-b[1])/h:.6f}")
            shutil.copy2(p, img_dir / p.name)
            (lab_dir / (p.stem + ".txt")).write_text("\n".join(lines))
            n += 1
        (lab_dir / "labels.txt").write_text("user\nperson\n")
        print(f"{who}: {n} frames with suggested labels in {img_dir.parent}")
    (TRAIN / "labels").mkdir(parents=True, exist_ok=True)


def label(who):
    import label_tool                                       # Nimer's tool, pointed at the training folders
    label_tool.OUT = TRAIN / "labels"
    label_tool.HALVES = {"nimer": TRAIN / "to_label_Nimer", "dareen": TRAIN / "to_label_Dareen"}
    label_tool.OUT.mkdir(parents=True, exist_ok=True)
    sys.argv = ["label_tool", who]
    label_tool.main()


def train(epochs=50, gentle=False):
    """gentle = keep YOLO11n's 80-class head (person stays class 0, nothing re-initialised), freeze the first 10 layers
    (the backbone that already sees people), small learning rate. The first, plain run (1 class, all layers) forgot
    part of what it knew about people: detection 85.4% -> 77.1% on the 152 test frames."""
    from ultralytics import YOLO
    import random
    ds = REPO / "3_EVIDENCE" / "m05_user_detection" / "finetune_dataset"
    run = "yolo11n_drone_gentle" if gentle else "yolo11n_drone"
    if ds.exists():
        shutil.rmtree(ds)
    labels = sorted((TRAIN / "labels").glob("*.txt"))
    if not labels:
        sys.exit("No corrected labels in M05_data/train/labels yet")
    imgs = {p.stem: p for p in TRAIN.glob("to_label_*/1_images/*.jpg")}
    random.seed(0); random.shuffle(labels)
    n_val = max(1, len(labels) // 7)                        # ~15% of the TRAINING clips to watch over-fitting
    for k, lab in enumerate(labels):
        part = "val" if k < n_val else "train"
        (ds / "images" / part).mkdir(parents=True, exist_ok=True); (ds / "labels" / part).mkdir(parents=True, exist_ok=True)
        shutil.copy2(imgs[lab.stem], ds / "images" / part / imgs[lab.stem].name)
        rows = [l.split() for l in lab.read_text().splitlines() if l.strip()]
        (ds / "labels" / part / lab.name).write_text("\n".join("0 " + " ".join(r[1:5]) for r in rows))   # user + person -> person
    model = YOLO(str(HERE / "yolo11n.pt"))
    names = model.names if gentle else {0: "person"}           # gentle: the same 80 COCO classes, person = 0
    (ds / "data.yaml").write_text(f"path: {ds.as_posix()}\ntrain: images/train\nval: images/val\nnames:\n"
                                  + "".join(f"  {k}: {v}\n" for k, v in names.items()))
    extra = dict(freeze=10, optimizer="AdamW", lr0=0.0005, warmup_epochs=1) if gentle else {}
    model.train(data=str(ds / "data.yaml"), epochs=epochs, imgsz=640, batch=16, device="cpu", workers=0,
                project=str(ds.parent / "finetune_runs"), name=run, exist_ok=True, plots=False, verbose=False, **extra)
    best = ds.parent / "finetune_runs" / run / "weights" / "best.pt"
    shutil.copy2(best, HERE / f"{run}.pt")
    print(f"Saved {HERE / (run + '.pt')} ({len(labels) - n_val} train / {n_val} val frames)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "extract":
        extract()
    elif cmd == "prelabel":
        prelabel()
    elif cmd == "label" and len(sys.argv) > 2 and sys.argv[2].lower() in HALVES:
        label(sys.argv[2].lower())
    elif cmd == "train":
        train(int(sys.argv[2]) if len(sys.argv) > 2 else 50, gentle="gentle" in sys.argv[3:])
    else:
        sys.exit(__doc__)
