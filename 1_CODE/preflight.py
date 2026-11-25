"""
preflight.py - Project 3760: READ-ONLY pre-flight check (Nimer 25.11). Never moves the drone, never presses anything.

    python preflight.py          (or /start_ready in Claude Code)

Checks: phone connected by ADB, real drone (DRONE_SIM empty), no leftover FORCE_LAND flag, DJI Fly screen recognised
(Take Off circle = on the ground, ready), drone battery > 40% (read from the ring), laptop battery / charger, free disk.
Exit code 0 = all required checks passed, 1 = something failed (do not fly).
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PHONE = "RF8MB2CG6SE"
results = []


def check(name, ok, detail, required=True):
    results.append((name, ok, detail, required))
    mark = "OK  " if ok else ("FAIL" if required else "WARN")
    print(f"[{mark}] {name}: {detail}", flush=True)


def laptop_battery():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "$b = Get-CimInstance Win32_Battery; if ($b) { \"$($b.EstimatedChargeRemaining) $($b.BatteryStatus)\" }"],
                             capture_output=True, text=True, timeout=15).stdout.split()
        if len(out) == 2:
            return int(out[0]), out[1] in ("2", "6", "7", "8", "9")   # 2 = on AC
    except Exception:
        pass
    return None, None


def main():
    print("PRE-FLIGHT CHECK (read only - nothing is pressed)\n", flush=True)
    # 1. simulator off
    sim = os.environ.get("DRONE_SIM", "")
    check("Real drone, not the simulator", not sim, "DRONE_SIM is empty" if not sim else f"DRONE_SIM={sim} -> run: set DRONE_SIM=")
    # 2. no stale force-land flag
    flag = os.path.join(HERE, "FORCE_LAND")
    check("No leftover FORCE_LAND flag", not os.path.exists(flag),
          "clear" if not os.path.exists(flag) else "1_CODE/FORCE_LAND exists -> delete it, or the next script lands at once")
    # 3. phone by ADB
    adb = os.path.join(HERE, "adb.exe")
    try:
        out = subprocess.run([adb if os.path.exists(adb) else "adb", "devices"], capture_output=True, text=True, timeout=20).stdout
        lines = [l for l in out.splitlines()[1:] if l.strip()]
        phone_ok = any(l.startswith(PHONE) and l.strip().endswith("device") for l in lines)
        detail = f"{PHONE} connected" if phone_ok else ("no phone listed - cable the S10, allow USB debugging" if not lines else
                                                       "listed: " + "; ".join(lines) + " (unauthorized? accept on the phone)")
    except Exception as e:
        phone_ok, detail = False, f"adb failed: {e}"
    check("Control phone (ADB)", phone_ok, detail)
    # 4-5. DJI Fly screen + drone battery (only if phone ok and not sim)
    if phone_ok and not sim:
        try:
            sys.path.insert(0, HERE)
            os.chdir(HERE)
            from drone_interface import Drone
            with Drone() as d:
                frame, t0 = None, time.time()
                while frame is None and time.time() - t0 < 10:
                    frame = d.screen(); time.sleep(0.3)
                ground = d.on_ground_ready(frame)
                check("DJI Fly ready on the ground", bool(ground), d.describe_screen(frame))
                pct, how = d.battery_info(frame)
                check("Drone battery > 40%", pct is not None and pct > 40,
                      f"{pct}% ({how})" if pct is not None else f"unknown ({how}) - check on the phone")
        except Exception as e:
            check("DJI Fly screen", False, f"could not read the phone screen: {e}")
    else:
        check("DJI Fly screen + drone battery", False, "skipped (needs the phone connected and DRONE_SIM empty)")
    # 6. laptop
    pct, ac = laptop_battery()
    if pct is None:
        check("Laptop power", True, "no battery info (desktop or unknown)", required=False)
    else:
        check("Laptop power", pct >= 50 or ac, f"{pct}%{' on charger' if ac else ' on battery'}", required=False)
    free = shutil.disk_usage(HERE).free / 1e9
    check("Free disk >= 20 GB", free >= 20, f"{free:.0f} GB free", required=False)
    # by hand
    print("\nBY HAND (cannot be checked by code): phone in hand · Manual Control · big open space, nobody under the drone ·"
          " wind < 20 km/h · force land table-tested today")
    failed = [r for r in results if r[3] and not r[1]]
    print("\n" + ("READY: all checks passed. Start the flight script yourself (record_video.py, T = take off, L = land)."
                  if not failed else f"NOT READY: {len(failed)} check(s) failed - do NOT fly."))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
