# M03 - Control from code (due Monday 9.11)

## Status (21.11)
- DONE 7.11: dry run of every command; take-off and hover from code; landing from code (two-step landing, 15:44 and the filmed run at 15:50).
- DONE 12.11: the six moves in flight (`python flight_test.py moves 0.3 0.5`, 19:04): forward, backward, right, left, rotate right, rotate left, then landing from code (landed about 7 s after the start of the landing; battery 69% -> 66%). Log: 3_EVIDENCE/2026-11-12/190414_flight_test_log.txt
- Check line in the plan: 10 of 10 movement commands work + a short video. Up/down are in the dry run; fill in the table below from the 12.11 video.

| Move | Did it move? | Right direction? | Notes |
| --- | --- | --- | --- |
| forward |  |  |  |
| backward |  |  |  |
| right |  |  |  |
| left |  |  |  |
| rotate right |  |  |  |
| rotate left |  |  |  |

## Before every flight
- Open space, nobody close, nothing above. Battery 50% or more (never below 40%).
- Phone in your hand, DJI Fly in Manual Control, no orange warning.
- Close any other program that uses the phone (scrcpy_demo, latency_test).
- Film with your own phone.

## Commands
- `python flight_test.py dry` - no drone; checks where the code touches the phone
- `python flight_test.py hover` - take off from code, you land by hand
- `python flight_test.py cycle` - take off, hover, land from code
- `python flight_test.py moves 0.3 0.5` - six moves, then land from code (never above 0.4)
- `python flight_test.py land` - the drone is hovering: land it from code

## If something fails
- Ctrl+C: sticks released, the drone hovers. Land by hand.
- Take-off from code does nothing: check settings.txt (TAKEOFF 539,1447), that DJI Fly is in front, in Manual Control, that the phone is awake.

## How to run the flight tests (step-by-step notes from 7.11)

### Before every flight
- Open space, nobody close, nothing above. Battery 50% or more (never below 40%).
- Phone in your hand, DJI Fly in Manual Control, no orange warning.
- Close any other program that uses the phone (scrcpy_demo, latency_test).
- Film with your own phone.

### Step 0 - dry run (no drone, no space needed)
Drone OFF. Phone: Developer options > Show taps + Pointer location; open a blank page (Chrome: about:blank).
OPEN_TERMINAL_HERE.bat, then:   python flight_test.py dry
Compare each touch with the coordinates the script prints (within a few pixels). Take a screenshot: SCREENSHOT.bat dry_pointer
This checks the code against settings.txt. It does not prove the drone obeys.

### Step A - hover from code (needs a big open space: about 2.5 x 2.5 m clear)
OPEN_TERMINAL_HERE.bat, then:   python flight_test.py hover        (or  cycle  for take-off + landing from code)
It asks ONE question (YES). It logs the drone battery before and after by itself, with a picture of the ring (check that the number matches the app the first time). Wait for 'Takeoff permitted' on the phone first; the code now checks the screen and says if the app is not ready.
Expected: it takes off, hovers about 5 seconds, then YOU land by hand (hold Land).
Write down: did it take off? how high? steady?

### Step B - six small moves
(7.11 result: push 0.1-0.2 for 0.4-0.5 s moved the Neo only a few cm. Next: moves 0.3 0.5, then moves 0.3 0.8. Stop when each move is clearly visible but stays within about 30-50 cm.)
python flight_test.py moves      (gentle: push 0.1 for 0.4 s; then it lands from code). If the moves are too small to see: python flight_test.py moves 0.15 0.5, then 0.2 0.5 ... (never above 0.4). Stop raising it as soon as each move is clearly visible but stays within about 30-50 cm.
Fill in:

| Move | Did it move? | Right direction? | Notes |
| --- | --- | --- | --- |
| forward |  |  |  |
| backward |  |  |  |
| right |  |  |  |
| left |  |  |  |
| rotate right |  |  |  |
| rotate left |  |  |  |

### Step C - landing from code
Take off by hand (tap and hold Take Off), let it hover, then:   python flight_test.py land
Expected: the script holds the Land button about 2.5 s, looks at the screen, and taps OK only if the dark pop-up is there. It prints what happened and saves a screenshot of the screen.
Watch the drone: if it is not landing within about 4 seconds, hold Land / tap OK yourself and write it down.
If it does not land: land by hand. Landing from code stays switched off in our plans until it works twice.

### If something fails
- Ctrl+C: sticks released, the drone hovers. Land by hand.
- Take-off from code does nothing: check settings.txt (TAKEOFF 539,1447), that DJI Fly is in front, that the phone is awake.
- A move goes the wrong way or is far too strong: stop, write it down, send it to Claude with the log file.

### What to show Gabi
1. The video. 2. The table above. 3. The log files in 3_EVIDENCE\<date>\ (every step with its time). 4. The honest status of each function.

### Minimum if time runs short
Step A (hover from code) with a video, and the table for the moves you did. Say what is left and when.
