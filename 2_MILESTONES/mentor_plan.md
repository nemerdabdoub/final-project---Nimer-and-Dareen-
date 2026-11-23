# Mentor plan (read live by the Project updates panel)
Tick a task by changing `- [ ]` to `- [x]` and push. The panel shows the current milestone, days left, the next open
tasks and the questions the supervisor will ask. Advice behind it: `4_DOCUMENTS/How_to_run_this_project_mentor_guide.pdf`.

## M06 user tracking
Due: 2026-12-07
Question: Does the tracker keep the SAME user through crossings, and what does the drone do when unsure?
Metric: user kept in >= 90% of frames; ID swaps on crossing scenes <= 1 in 10; 0 wrong-person follows.
Ask: How many ID swaps on crossings? | What does the drone do when UNSURE or LOST? | Same clips as the M05 baseline? | Was the test data used for tuning?

- [ ] Requirement trace table in the repo (exact words of the approved plan -> test -> result -> status)
- [ ] Write the M06 question, metrics and pass lines (above) and agree them with Gabi
- [ ] Film crossing scenes on purpose (someone walks past the user, both directions, close and far)
- [ ] Label the crossing scenes; keep them as the M06 hold-out test set (never tune on them)
- [ ] Tracker states FOLLOWING / UNSURE / LOST in m06_track.py, each with a drone action
- [ ] Turban re-confirms the user after a crossing; no ID switch without the turban
- [ ] Count ID swaps and % user kept: new tracker vs M05 baseline on the same clips
- [ ] Measure the command delay (command sent -> drone starts moving), from a video
- [ ] Proportional controller (box centre -> turn, box height -> distance) with dead band and rate limit
- [ ] Run the controller offline on recorded videos; plot the commands
- [ ] Ground test (commands printed, drone not flying), then hover-only test with the flight checklist
- [ ] One-page M06 summary + decision log + questions for Gabi
