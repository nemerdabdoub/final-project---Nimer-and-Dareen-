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
