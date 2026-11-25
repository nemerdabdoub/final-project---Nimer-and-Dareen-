"""
record_loop.py - record clip after clip without typing: clip_01, clip_02, ... each until Esc, the next starts by itself.
Ctrl+C in the terminal (or Esc twice quickly / close) = stop the loop. Each clip: take off -> scene -> land -> Esc.
  python record_loop.py            names field_01, field_02, ...
  python record_loop.py walk       names walk_01, walk_02, ...
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
base = sys.argv[1] if len(sys.argv) > 1 else "field"
k = 1
try:
    while True:
        name = f"{base}_{k:02d}"
        print(f"\n===== CLIP {name}: REC window opens - take off, film, land, then Esc. Ctrl+C here = stop the loop =====\n")
        subprocess.run([sys.executable, os.path.join(HERE, "run_with_adb.py"), "record_video.py", "0", name], cwd=HERE)
        k += 1
        print("next clip in 3 s ... (Ctrl+C now to stop)")
        time.sleep(3)
except KeyboardInterrupt:
    print(f"\nLoop stopped. {k - 1} clip(s) recorded in 3_EVIDENCE\\<today>\\")
