# Flight tests for the tracking milestone (due 7.12) — one test at a time, in order

## SIMPLE NAMES (use these)
| # | name | what happens |
|---|---|---|
| 1 | **STOP TEST** | emergency land button (FORCE_LAND.bat) — table part done ✓ 25.11; real part = while hovering |
| 2 | **TABLE TEST** | drone on the table, follow program watches, sends nothing — done ✓ 25.11 |
| 3 | **TURN TEST** | drone in the air only TURNS to face the user |
| 4 | **DISTANCE TEST** | user walks away / comes back, drone moves forward / back |
| 5 | **FOLLOW TEST** | turn + distance together: drone follows the user anywhere, 60 s |
| 6 | **SIDE TEST** | follow + sideways sliding (new mode, after FOLLOW TEST works) |
| 7 | **CROSS TEST** | follow while someone walks in front of the user |
| 8 | **DELAY TEST** | drone turns by itself 10 times, we measure the delay |
| 9 | **RECORD** | just film clips for later (crossings, turn away, from above) |

---
(details below: T0 = STOP TEST, T1 = TABLE TEST, T2 = TURN TEST, T3 = DISTANCE TEST, T4 = FOLLOW TEST, T5 = CROSS TEST, T6 = DELAY TEST, T7 = RECORD)


**Why this order:** each test adds ONE new thing, so if something goes wrong we know what caused it. Never skip ahead.
**What the drone can do today:** TURN (yaw) to keep the user centred + move FORWARD / BACK to keep the distance (`--forward`).
It does **NOT** move sideways yet (that is M07). So "follow wherever I go" = turn toward her + close the distance.
**Rule:** Claude asks before every step that moves the drone. Battery > 40% to start, land at 30% (the script stops itself at 30%).
Pilot = at the laptop with the S10 in hand. User = turban, 4 m in front. Sun behind the drone.
Command start (PowerShell): `cd "C:\Users\LOREN\Desktop\final-project---Nimer-and-Dareen-\1_CODE"; & 'C:\Users\LOREN\venvs\gpu\Scripts\python.exe' run_with_adb.py ...`

| # | test | command end (`run_with_adb.py ...`) | user does | why | PASS if |
|---|---|---|---|---|---|
| T0 | pre-flight + FORCE LAND table test | `/start_ready` · double-click `FORCE_LAND.bat` (drone on the table) | — | the emergency stop must work before any autonomous flight | red STOP screen appears |
| T1 | follow DRY on the table | `m06_follow.py --live --dry --seconds 30` | walks left / right | detection + user lock + commands, nothing sent | FOLLOWING, yaw sign right |
| T2 | **turn only** (flying) | `m06_follow.py --live --max-yaw 0.2 --seconds 40` | walks slowly in an ARC around the drone (same distance) | first autonomous axis; nothing else can go wrong | drone turns to keep her centred; stops turning when centred |
| T3 | **distance only feel** (flying) | `m06_follow.py --live --forward --max-yaw 0.2 --seconds 30` | walks STRAIGHT away 3 m, waits, comes back | adds forward/back | drone moves toward her, stops at ~3–4 m; backs off when she comes close |
| T4 | **full follow = what Nimer expected** (flying) | `m06_follow.py --live --forward --max-yaw 0.2` (until landing) | walks anywhere slowly: away, diagonal, around | turn + distance together = follows her direction | keeps her in view and at distance for 60 s (work-plan req. 4) |
| T5 | follow + crossing (flying) | same as T4 | a passer-by crosses in front | the M06 question: same user kept? | USER box never jumps to the passer-by |
| T6 | delay + turn rate (hover) | `command_delay_test.py --auto 10` · `--pulse 2 --deflect 0.2/0.3/0.4 --auto 2` | stays out of view | numbers to tune the controller | 10 delay values, 3 turn rates |
| T7 | raw clips for the test set (record) | `record_video.py 0 <name>` | crossings, turn away, from above | M06 hold-out data | clip saved |

After each flying test: land → say "done" → Claude reads the CSV and says PASS / FAIL + why, before the next test.
Not yet: sideways moves (M07), delay predictor (`--predict`, only after an emulator test), colour (`--colour`, after T5).
