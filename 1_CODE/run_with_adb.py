"""
run_with_adb.py - start any drone script with 1_CODE (where adb.exe lives) on the PATH.
The lab's scrcpy.py calls plain "adb"; in a fresh terminal Windows can't find it ("FileNotFoundError: [WinError 2]").
  python run_with_adb.py record_video.py 0.5 indoor_test
  python run_with_adb.py m06_follow.py --live --dry
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = HERE + os.pathsep + os.environ.get("PATH", "")
os.chdir(HERE)
sys.path.insert(0, HERE)
if len(sys.argv) < 2:
    sys.exit(__doc__)
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(os.path.join(HERE, script), run_name="__main__")
