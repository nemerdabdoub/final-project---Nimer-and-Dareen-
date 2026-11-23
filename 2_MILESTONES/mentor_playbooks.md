# Mentor playbooks (read live by the Mentor panel, `tools/mentor`)

What a supervisor like Gabi would tell you at each kind of work, written down so it is there when he is not.
The panel guesses which process you are in from what you and Claude do (commands, files, your messages) and shows
that playbook. Edit freely: keep the format (`## id | Title`, then `When:`, `Why:`, `Steps:`, `Gabi asks:`, `Traps:`,
`Done when:`). Order matters: the first playbook whose `When:` word matches wins. Longer background:
`4_DOCUMENTS/ADVISOR_GUIDE.md` and `4_DOCUMENTS/How_to_run_this_project_mentor_guide.pdf`.

## Principles
- Every number needs three things: what data, what rule, compared with what. A number alone convinces nobody.
- Fix the weakest link of the whole loop (camera → detect → track → decide → move), not the part you like most.
- Write the question and the pass line BEFORE you run anything. Afterwards it is too easy to move the line.
- Never tune on your test data. Keep a hold-out set and touch it once, at the end.
- Small steps you can undo: one change, one test, one commit, one line in UPDATES.md.
- A failure you understand is a result. Write it down with the reason; examiners love honest failures.
- If you cannot explain it on one slide to a smart friend, you do not understand it yet. Simplify.
- Safety beats schedule. A crashed drone costs weeks; a postponed flight costs a day.
- The approved work plan is the contract: quote its exact words when you claim something is done.
- When stuck for more than 45 minutes, stop, write down what you know and what you tried, and ask.

## lost | Feeling lost: where are we and what next?
When: feel lost, feeling lost, we are lost, i'm lost, im lost, confused, overwhelmed, what now, what next, where are we, don't know what, everything is new, אבוד, מה עכשיו
Why: Feeling lost is normal in a first real project. The cure is always the same: the map, then ONE next step.
Steps:
1. Look at the map: M02-M05 done, M06 tracking due 7.12, then control, then guiding to a target.
2. Open 2_MILESTONES/mentor_plan.md: the first unticked task is your next step. Only that one.
3. Say the milestone's question in one sentence (M06: does the tracker keep the SAME user, and what does the drone do when unsure?).
4. Pick a task that fits in 2 hours. If it does not fit, split it.
5. Agree with your partner who does what today; write it in UPDATES.md.
6. At the end of the day: one commit, one line of what you learned.
Gabi asks:
- What is the question of this milestone, in one sentence?
- What did you finish since we last met, and what is the evidence?
- What is blocking you?
Traps:
- Doing many things at once and finishing none.
- Polishing slides or tools instead of the hardest open problem.
- Waiting for the perfect plan before starting. Start small, then correct.
Done when: you can say the next task, who does it, and how you will know it worked.

## flight | Flight test with the drone
When: flight_test, takeoff, take off, land, record_video, drone_interface, connection_test, latency_test, send_speeds, hover, fly
Why: Flights are expensive and risky. A flight is an experiment: plan it on paper so every minute in the air answers a question.
Steps:
1. Write the goal of this flight in one line and what you will measure (e.g. take-off from code works 3 of 3 times).
2. Checklist: battery > 40%, open space, no people under the path, phone in hand, DJI Fly in Manual Control.
3. Test on the ground first: run the script with the drone off or not armed; check prints and the camera window.
4. Decide the abort rule before take-off: Ctrl+C, then land by hand on the phone.
5. Record everything: screen video + terminal log into 3_EVIDENCE/<date>/.
6. One change per flight. If two things changed and it failed, you learned nothing.
7. After landing: write 3 lines (what worked, what failed, next) in the milestone note while you remember.
Gabi asks:
- What was the goal of this flight and did you reach it?
- What is your stop / abort procedure, and did you test it?
- How many repetitions? Did it work every time or once?
- Where is the video and the log?
Traps:
- Flying to "see what happens" without a question.
- Changing code at the field without testing it on the ground first.
- One lucky success reported as "works". Repeat it.
- Low battery or wind making a good algorithm look bad.
Done when: the goal line is answered with numbers (n of n), and the video + log are saved and linked in the note.

## experiment | Running an experiment or a comparison
When: m05.py run, m06_track, compare, comparison, benchmark, evaluate, accuracy, fps, results, .csv, table
Why: An experiment is how you turn an opinion ("YOLO11n is better") into evidence an examiner accepts.
Steps:
1. Write the question, the metric and the pass line first (e.g. user kept in >= 90% of frames).
2. Fix the data: which clips, which labels, which frames. Same data for every method you compare.
3. Name the baseline: what you compare against (M05 hybrid, or "no tracking").
4. Change ONE thing at a time; keep everything else fixed (model, image size, thresholds).
5. Run, save the CSV with a date in its name, keep the exact command in the note.
6. Look at the failures, not just the average: open 5 wrong frames and say why each failed.
7. Write the result as: number, compared with baseline, on what data, and what it means for the next step.
Gabi asks:
- Compared with what? On which data, how many frames?
- Was this data used for tuning? (If yes, the number is too optimistic.)
- Where does it fail, and why?
- Is the difference real or noise? (Few frames → small differences mean nothing.)
Traps:
- Tuning thresholds on the same frames you report.
- Comparing methods on different clips or different labels.
- Reporting only the average and hiding the failure cases.
- Forgetting speed: an accurate method at 3 FPS is useless on the drone.
Done when: one table (method × metric) on fixed data, a baseline row, the command to reproduce it, and 3 lines of meaning.

## data | Collecting and labelling data
When: label, labels, prelabel, extract, frames, filming, film, clip, dataset, test_22.11, roboflow, makesense
Why: The labels define what "correct" means. Bad labels make every later number wrong, quietly.
Steps:
1. Write the labelling rules before you start (who is user, who is person, what gets no box) and keep them in the note.
2. Film for the question: for M06 film crossings on purpose (someone walks past the user, both directions, near and far).
3. Split the data at once: training/tuning vs hold-out test. Never move frames between them later.
4. Pre-labels are a draft: check every frame by eye, do not just accept them.
5. Check agreement: both partners label the same 10-20 frames and compare; fix the rules where you disagree.
6. Run the checker (e.g. `python m05_newclips.py check`) and push the labels in small batches.
Gabi asks:
- How many frames, from how many clips and conditions (light, distance, crowd)?
- Who labelled, with what rules, and did you check agreement?
- Is the test set separate from what you tuned on?
Traps:
- Accepting the model's pre-labels: then you test the model against itself.
- All data from one place and one day: the result does not generalise.
- Too few hard cases (crossings, far people, low light) in the test set.
Done when: rules written, labels checked and pushed, train/test split recorded, frame counts in the note.

## control | Designing the drone controller (follow the user)
When: controller, proportional, dead band, deadband, rate limit, pid, follow, distance, yaw, m06 control, command delay
Why: The controller closes the loop. With ~290 ms video delay plus the command delay, a fast controller will oscillate.
Steps:
1. Measure the delays first: video (~290 ms known) and command → movement (from a video). Write them down.
2. Start with the simplest controller: box centre → yaw, box height → forward/back. Proportional only.
3. Add a dead band (do nothing for small errors) and a rate limit (no sudden big commands).
4. Define the states: FOLLOWING, UNSURE (hold position), LOST (hover, then land or search slowly).
5. Run it OFFLINE on recorded videos and plot the commands. They must be smooth and sensible.
6. Ground test (commands printed, drone not flying), then hover-only, then slow following. One step per session.
Gabi asks:
- What are the delays in your loop, and how does your controller handle them?
- What does the drone do when it loses the user or is unsure?
- What are the gains, and how did you choose them?
- What limits the speed for safety?
Traps:
- Tuning gains in the air before trying them on recorded video.
- No dead band: the drone twitches all the time.
- Following the wrong person after a crossing because there is no UNSURE state.
Done when: delays measured, offline plots look smooth, states defined with actions, and a hover-only test passed safely.

## decision | From results to a decision
When: winner, decide, decision, choose, choice, which model, final choice, trade-off
Why: Engineering is choosing under limits. Gabi grades the reasoning more than the choice.
Steps:
1. List the options you really tested (not the ones you only read about).
2. Write the criteria with weights: accuracy, wrong-person rate, speed (FPS), simplicity, risk.
3. Put the numbers in one table, on the same data.
4. Choose, and write the price you pay (what the winner is worse at).
5. Write what would make you change your mind (e.g. if far people matter more, try 800 px).
6. Record it in the decision log with the date and both names.
Gabi asks:
- Why this one and not the second best?
- What do you lose with this choice?
- Under what conditions would you choose differently?
Traps:
- Choosing by habit or by what is newest.
- Hiding the weaknesses of the winner.
- Deciding alone: both partners must agree and be able to defend it.
Done when: one table, one choice, its price, and a dated line in the decision log that both of you agree with.

## meeting | Preparing a meeting with Gabi
When: gabi, meeting, slides, deck, pptx, talking points, presentation, supervisor
Why: A meeting is short. Come with evidence and questions, leave with decisions.
Steps:
1. One sentence: what we promised last time, and what we did.
2. Three key numbers, each with its comparison and data (say them out loud once before).
3. One demo, opened and paused at the right second.
4. The failures and what you learned from them.
5. 2-4 concrete questions where you need his decision (not "is it OK?" but "A or B, because...").
6. After the meeting: write his answers and the new tasks in UPDATES.md within the hour.
Gabi asks:
- What did you promise, and what did you deliver?
- What does not work yet, and what is your plan?
- What do you need from me?
Traps:
- Too many slides, no clear message.
- Numbers without comparison or data size.
- Not writing down what he said: a week later you will both remember differently.
Done when: you can give the 3-minute story without slides, and the questions are written.

## writing | Writing a summary, report or slides
When: 4_DOCUMENTS, summary, report, docx, write-up, journey, abstract, poster
Why: The report is how the project is judged. Write as you go, not at the end.
Steps:
1. Start from the reader: what must they understand and believe after reading?
2. Structure: problem → requirement → method → result (with numbers) → decision → next step.
3. Every claim gets evidence: a table, a figure, a file in the repo.
4. Quote the approved work plan's exact words when you say a requirement is met.
5. One figure per idea; label axes and units.
6. Let your partner read it cold; fix every place they stop.
Gabi asks:
- Which requirement does this section prove?
- Where is the evidence for this sentence?
- What are the limits of this result?
Traps:
- Describing what you did instead of what you found.
- Claiming "works" without numbers and conditions.
- Two summaries saying different things: keep ONE source of truth.
Done when: every claim has evidence, your partner read it, and it is pushed.

## code | Writing or changing code
When: .py, script, function, refactor, bug fix, def , import
Why: Code is a tool for experiments. Make it simple, repeatable and safe to run again.
Steps:
1. Say in one line what the script must do and how you will check it.
2. Reuse what exists (drone_interface.py, m05.py) instead of copying code.
3. Make the run repeatable: arguments on the command line, outputs with dates, no hidden manual steps.
4. Test on a small input first (one clip, 10 frames) before the full run.
5. Anything that moves the drone: a dry-run mode first, and Ctrl+C must stop it safely.
6. Commit with a clear message; write in UPDATES.md how to run it.
Gabi asks:
- How do you know the code is correct? What did you test it on?
- Can your partner run it on their laptop and get the same numbers?
Traps:
- A script that only works on one laptop (hard-coded paths).
- Editing the same file as your partner at the same time.
- Changing an evaluation script after the results are in, without re-running everything.
Done when: it runs on both laptops, the result can be reproduced from one command, and it is pushed.

## debug | Something does not work
When: traceback, doesn't work, does not work, not working, crash, crashed, failed, broken, stuck, no frames, winerror
Why: Debugging is an experiment too: guess, test, narrow down. Random changes waste days.
Steps:
1. Write down exactly what you expected and what happened (copy the error text).
2. Make it small: the smallest command that still shows the problem.
3. Check the boring things first: is the phone connected (adb devices), right folder, right file, battery, cable.
4. Change one thing at a time and note the result.
5. After 45 minutes with no progress: stop, write what you know and tried, ask your partner or Claude with that text.
6. When fixed: write the cause and the fix in the note, so it never costs you time again.
Gabi asks:
- What exactly fails, and how did you narrow it down?
- What did you try, and what did each try tell you?
Traps:
- Changing many things at once, then not knowing what fixed it.
- Not reading the error message to the end.
- Fixing the symptom (retry until it works) instead of the cause.
Done when: you know the cause, the fix is tested twice, and one line in the note explains it.

## pair | Working as a pair (git, sync, roles)
When: git push, git pull, merge, conflict, UPDATES.md, partner, nimer, dareen, push now
Why: Two people can do twice the work or half, depending on how you sync.
Steps:
1. Pull and read UPDATES.md before you start.
2. Agree who owns which file today; never edit the same file at the same time.
3. Small commits with clear messages; one UPDATES line per finished change.
4. Both must be able to explain every result. Swap and explain each other's part once a week.
5. Disagreements: decide with data, write the decision and the reason.
Gabi asks:
- Who did what?
- Can each of you explain the other's part?
Traps:
- One partner does all the code, the other all the slides: both lose at the exam.
- Big commits at the end of the day that mix many changes.
Done when: GitHub is in sync, UPDATES.md says who does what next, and you both know the current numbers.

## milestone | Starting a new milestone
When: mentor_plan, new milestone, M06, M07, M08, work plan, milestone, definition of done
Why: A milestone without a question and a pass line never ends; with them, it ends on a date.
Steps:
1. Copy the requirement's exact words from the approved work plan.
2. Write the question, the metric and the pass line; agree them with Gabi.
3. List the tasks in mentor_plan.md, each one fitting in half a day.
4. Plan the data (what to film, what to label, what is the hold-out set).
5. Name the risks and a plan B for the biggest one.
6. Put a mid-way check date (halfway to the due date) in UPDATES.md.
Gabi asks:
- What exactly will you show on the due date?
- What is the pass line, and how will you measure it?
- What is the biggest risk, and what is plan B?
Traps:
- Starting to code before the question and metric are clear.
- Underestimating data collection and labelling time.
Done when: question, pass line, task list and risks are in the repo and Gabi agreed.
