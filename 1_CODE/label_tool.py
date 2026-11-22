"""
label_tool.py - Project 3760, M05: correct the suggested labels, frame by frame, in one window.

  python label_tool.py nimer      your half   (M05_data/to_label_Nimer)
  python label_tool.py dareen     Dareen's half (M05_data/to_label_Dareen)

It opens each frame with the suggested boxes already drawn and saves YOUR corrected labels straight into
M05_data/labels/ (YOLO format, same file names), every time you move to another frame. No upload, no export.
Run it again later and it continues from what you already saved.

  green = user (the man in the turban, class 0)     blue = person (everyone else, class 1)     yellow = selected

MOUSE   left-click a box   select it            left-drag on the image   draw a NEW box (it starts as person)
        right-click a box  delete it
KEYS    u  selected box -> user (only one user per frame: any other user becomes person)
        p  selected box -> person
        x  delete the selected box
        n / Space / ->   save, next frame         b / <-   save, previous frame
        j  jump to the first frame not saved yet  h  show / hide this help on the image
        q / Esc  save and quit
Rules: the turban man is ALWAYS user, even when the turban is hidden. Delete boxes that are not people
(hands close to the camera, the mural, app buttons). Add any person that has no box.
"""
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent.parent / "M05_data"
OUT = ROOT / "labels"
HALVES = {"nimer": ROOT / "to_label_Nimer", "dareen": ROOT / "to_label_Dareen"}
COLOURS = {0: (0, 200, 0), 1: (230, 140, 0)}      # BGR: user green, person blue
SELECTED = (0, 230, 255)
NAMES = {0: "user", 1: "person"}
MAX_W, MAX_H = 1500, 850                           # window fits a laptop screen
KEY_LEFT, KEY_RIGHT = 2424832, 2555904             # arrow keys from cv2.waitKeyEx on Windows


def load_labels(path):
    """YOLO lines -> [[cls, x, y, w, h], ...] (normalised 0-1)"""
    boxes = []
    if path.exists():
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) == 5:
                boxes.append([int(parts[0])] + [float(v) for v in parts[1:]])
    return boxes


def save_labels(path, boxes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{c} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n" for c, x, y, w, h in boxes))


def to_pixels(b, W, H):
    _, x, y, w, h = b
    return int((x - w / 2) * W), int((y - h / 2) * H), int((x + w / 2) * W), int((y + h / 2) * H)


def from_pixels(cls, x1, y1, x2, y2, W, H):
    x1, x2 = sorted((max(0, min(W, x1)), max(0, min(W, x2))))
    y1, y2 = sorted((max(0, min(H, y1)), max(0, min(H, y2))))
    return [cls, (x1 + x2) / 2 / W, (y1 + y2) / 2 / H, (x2 - x1) / W, (y2 - y1) / H]


def box_at(boxes, px, py, W, H):
    """index of the smallest box containing the point, or None"""
    best, area = None, None
    for i, b in enumerate(boxes):
        x1, y1, x2, y2 = to_pixels(b, W, H)
        if x1 <= px <= x2 and y1 <= py <= y2:
            a = (x2 - x1) * (y2 - y1)
            if area is None or a < area:
                best, area = i, a
    return best


def main():
    who = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if who not in HALVES:
        sys.exit(__doc__)
    images = sorted((HALVES[who] / "1_images").glob("*.jpg"))
    suggested = HALVES[who] / "2_labels"
    if not images:
        sys.exit(f"No frames in {HALVES[who] / '1_images'}: git pull first")

    state = {"i": 0, "boxes": [], "sel": None, "drag": None, "now": None, "dirty": False, "help": True}
    first_unsaved = next((k for k, p in enumerate(images) if not (OUT / (p.stem + ".txt")).exists()), 0)
    state["i"] = first_unsaved

    def open_frame():
        p = images[state["i"]]
        mine = OUT / (p.stem + ".txt")
        state["img"] = cv2.imread(str(p))
        state["boxes"] = load_labels(mine if mine.exists() else suggested / (p.stem + ".txt"))
        state["sel"], state["dirty"] = None, False
        H, W = state["img"].shape[:2]
        state["scale"] = min(1.0, MAX_W / W, MAX_H / H)

    def save():
        p = images[state["i"]]
        save_labels(OUT / (p.stem + ".txt"), state["boxes"])

    def on_mouse(event, mx, my, flags, _):
        s = state["scale"]
        H, W = state["img"].shape[:2]
        px, py = int(mx / s), int(my / s)
        if event == cv2.EVENT_LBUTTONDOWN:
            state["drag"], state["now"] = (px, py), (px, py)
        elif event == cv2.EVENT_MOUSEMOVE and state["drag"]:
            state["now"] = (px, py)
        elif event == cv2.EVENT_LBUTTONUP and state["drag"]:
            (x0, y0), state["drag"] = state["drag"], None
            if abs(px - x0) > 6 and abs(py - y0) > 6:
                state["boxes"].append(from_pixels(1, x0, y0, px, py, W, H))
                state["sel"], state["dirty"] = len(state["boxes"]) - 1, True
            else:
                state["sel"] = box_at(state["boxes"], px, py, W, H)
        elif event == cv2.EVENT_RBUTTONDOWN:
            k = box_at(state["boxes"], px, py, W, H)
            if k is not None:
                state["boxes"].pop(k)
                state["sel"], state["dirty"] = None, True

    def draw():
        img = state["img"].copy()
        H, W = img.shape[:2]
        for k, b in enumerate(state["boxes"]):
            x1, y1, x2, y2 = to_pixels(b, W, H)
            col = SELECTED if k == state["sel"] else COLOURS.get(b[0], (0, 0, 255))
            cv2.rectangle(img, (x1, y1), (x2, y2), col, 4 if k == state["sel"] else 3)
            cv2.putText(img, NAMES.get(b[0], str(b[0])), (x1 + 4, max(70, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, col, 2, cv2.LINE_AA)
        if state["drag"] and state["now"]:
            cv2.rectangle(img, state["drag"], state["now"], SELECTED, 2)
        saved = sum((OUT / (p.stem + ".txt")).exists() for p in images)
        users = sum(b[0] == 0 for b in state["boxes"])
        people = sum(b[0] == 1 for b in state["boxes"])
        mark = "saved" if (OUT / (images[state['i']].stem + '.txt')).exists() and not state["dirty"] else "not saved yet"
        bar = (f"{state['i'] + 1}/{len(images)}  {images[state['i']].stem}   user {users}  person {people}"
               f"   [{mark}]   done {saved}/{len(images)}")
        cv2.rectangle(img, (0, 0), (W, 50), (0, 0, 0), -1)
        cv2.putText(img, bar, (12, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2, cv2.LINE_AA)
        if users > 1:
            cv2.putText(img, "more than one user!", (W - 360, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (0, 0, 255), 2)
        if state["help"]:
            lines = ["click = select   drag = new box   right-click = delete",
                     "u = user   p = person   x = delete selected",
                     "n/Space/-> = next   b/<- = back   j = first unsaved   q = save+quit   h = hide help"]
            for k, t in enumerate(lines):
                y = H - 20 - 34 * (len(lines) - 1 - k)
                cv2.putText(img, t, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 5, cv2.LINE_AA)
                cv2.putText(img, t, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        s = state["scale"]
        return cv2.resize(img, (int(W * s), int(H * s))) if s < 1 else img

    win = f"M05 labels - {who}"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, on_mouse)
    open_frame()
    while True:
        cv2.imshow(win, draw())
        key = cv2.waitKeyEx(30)
        if key == -1:
            if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:      # window closed with the X
                save()
                break
            continue
        ch = chr(key).lower() if 0 <= key < 256 else ""
        sel = state["sel"]
        if ch == "u" and sel is not None:
            for b in state["boxes"]:
                if b[0] == 0:
                    b[0] = 1
            state["boxes"][sel][0], state["dirty"] = 0, True
        elif ch == "p" and sel is not None:
            state["boxes"][sel][0], state["dirty"] = 1, True
        elif ch == "x" and sel is not None:
            state["boxes"].pop(sel)
            state["sel"], state["dirty"] = None, True
        elif ch in ("n", " ") or key == KEY_RIGHT:
            save()
            if state["i"] < len(images) - 1:
                state["i"] += 1
                open_frame()
        elif ch == "b" or key == KEY_LEFT:
            save()
            if state["i"] > 0:
                state["i"] -= 1
                open_frame()
        elif ch == "j":
            save()
            state["i"] = next((k for k, p in enumerate(images) if not (OUT / (p.stem + ".txt")).exists()), state["i"])
            open_frame()
        elif ch == "h":
            state["help"] = not state["help"]
        elif ch == "q" or key == 27:
            save()
            break
    cv2.destroyAllWindows()
    saved = sum((OUT / (p.stem + ".txt")).exists() for p in images)
    print(f"Saved {saved} of {len(images)} frames into {OUT}")
    if saved == len(images):
        print("Your half is done. Tell Claude: labels done")


if __name__ == "__main__":
    main()
