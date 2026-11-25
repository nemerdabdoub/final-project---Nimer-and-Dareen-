"""
force_land.py - Project 3760: FORCE LAND for any running drone script (Nimer 25.11).

    python force_land.py            (or /force_land in Claude Code, or double-click FORCE_LAND.bat in the repo root)

How it works: it creates the file 1_CODE/FORCE_LAND. Every script talks to the drone through drone_interface.Drone (or
sim_drone.SimDrone), which checks that file on every frame and every stick command: sticks released, the two-step DJI Fly
landing started (land()), and every later stick command ignored. The script that landed writes the result to
1_CODE/FORCE_LAND_RESULT.txt; this program waits for it and prints it.
If no running script picks it up within 3 s (no script running, or it is stuck), it says so: then LAND BY HAND on the phone.

SAFETY: this is a back-up, not the first choice. The fastest stop is still your thumb on the phone (hold Land / STOP).
Through Claude the command needs a few seconds before it even starts; FORCE_LAND.bat is faster.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FLAG = os.path.join(HERE, "FORCE_LAND")
RESULT = os.path.join(HERE, "FORCE_LAND_RESULT.txt")


def requested():
    return os.path.exists(FLAG)


def clear():
    try:
        os.remove(FLAG)
    except OSError:
        pass


def report(text):
    try:
        with open(RESULT, "w", encoding="utf-8") as f:
            f.write(time.strftime("%H:%M:%S ") + str(text) + "\n")
    except OSError:
        pass


def main():
    try:
        os.remove(RESULT)
    except OSError:
        pass
    with open(FLAG, "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
    print("FORCE LAND sent - waiting for the running drone script ...", flush=True)
    t0 = time.time()
    while time.time() - t0 < 3.0:
        if not requested():                                   # a script took it and is landing now
            print("A running script took it and is LANDING. Watch the drone.", flush=True)
            t1 = time.time()
            while time.time() - t1 < 15 and not os.path.exists(RESULT):
                time.sleep(0.2)
            if os.path.exists(RESULT):
                print("Result:", open(RESULT, encoding="utf-8").read().strip())
            else:
                print("No result after 15 s - CHECK THE DRONE, land by hand if it is still in the air.")
            return 0
        time.sleep(0.05)
    clear()                                                   # do not leave a stale flag that lands the NEXT script
    print("!!! NO running drone script took the FORCE LAND within 3 s (none running, or it is stuck).")
    print("!!! LAND BY HAND ON THE PHONE NOW (DJI Fly: Land, then hold the big Land circle).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
