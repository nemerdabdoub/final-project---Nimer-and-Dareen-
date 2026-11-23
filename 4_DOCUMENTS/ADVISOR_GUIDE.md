# Advisor's guide for Project 3760: the map, the method, and what to expect

How an experienced supervisor would guide this project, step by step. Read it at the start of each milestone.
Both Claudes use it: every step gets an **"Advisor's view"** (why it matters, what comes next, risks, what an examiner will ask).

## 1. The map: where the project is going
| Phase | What it proves | Status |
|---|---|---|
| M02-M03 | We control the drone from our code (take-off, moves, landing) | done |
| M04 | Approved work plan with measurable requirements | done |
| M05 | We can find THE user in a frame (YOLO11n + turban) | done 23.11 |
| **M06 (7.12)** | We keep the same user over time (tracking) and turn his position into commands | **now** |
| Dec-Jan | **First closed loop:** camera → detect → decide → command → drone moves, live | the biggest step |
| Mid-project presentation (Jan, upload by 20.1) | Working detection + tracking, first live following, plan for semester B | material collected |
| Semester B | Guiding the user to a target, field tests, final report and presentation | |

**The one big open design question:** how does the system know **where the target is** and which way to guide?
(a marker at the target, a known map / GPS point, a route recorded in advance, or the user points?) Decide it early:
it shapes M07+ and the semester-B work. Bring 2-3 options with pros/cons to the supervisor.

## 2. The method: every milestone, the same 7 steps
1. **Question and success numbers first.** Write the requirement as a number before coding ("user identified in >= 90% of frames").
2. **Baseline first.** The simplest thing that could work, measured. Every improvement is compared with it.
3. **One change at a time.** Otherwise you never know what helped.
4. **Hold out test data.** Clips never used for tuning or training; final numbers only on them.
5. **Evidence for every claim.** Log, table, video, file path. If it is not recorded, it did not happen.
6. **Decide and write why** (half a page): options, numbers, choice, trade-off. (M05_engineering_journey is a good example.)
7. **State the limits.** Where it fails and why; what you would do next. Examiners trust results more when you know their limits.

## 3. Engineering principles for this drone
- **Measure the whole loop, not only the model.** The model runs at ~30 FPS, but the loop has ~290 ms delay (phone mirroring).
  At walking speed (~1.4 m/s) the user moves ~0.4 m per loop: fine at 3-4 m distance, so keep commands gentle (small gains).
- **When unsure, hover.** No user, two overlapping candidates, or a lost track → hold position, never guess. Safety beats coverage.
- **Integration is where projects fail.** Build a rough end-to-end version early, even if it only turns toward the user.
- **Dry run before live.** Show commands on screen first; then a hovering drone with commands; then slow following; then real use.
- **Field tests need a protocol:** spotter, open space, battery >= 40% start / land at 30% (~11 min per battery measured 22.11),
  shot list, shot log with times, test-only clips decided before training.
- **Keep the design simple until the numbers say otherwise.** One detector + marker + tracker; no model ensembles.

## 4. Working with the supervisor
- Come with **decisions, not open questions**: "we plan X because Y; any objection?"
- After every meeting send a **4-line email**: what we showed, what was decided, next step + date, open questions. It records agreement.
- 1-2 concrete questions per meeting; bring the evidence (table, short video).
- If there is no answer in a few days: proceed with the plan you wrote and say so.

## 5. Working as a pair
- Clear ownership per task (who is responsible, not just who helps); one person owns integration each milestone.
- Short sync twice a week (10 min): done / next / blocked. UPDATES.md is the written version.
- Split the interesting work too: both of you should be able to explain every part at the presentation.

## 6. What examiners will ask (prepare one sentence each)
- Why this approach and not the alternatives? (engineering considerations)
- How exactly did you measure, on what data, and is the test fair?
- Where does it fail, and what did you do about it?
- What is the delay of the whole system and is it safe?
- What would you do with 3 more months?

## 7. M06 now: definition of done (7.12)
- User **identified** in >= 90% of frames in the lab clips (closes requirement 1), with the tracker.
- ID swaps counted by eye on the crossing scenes; behaviour while boxes overlap = hold.
- ByteTrack vs BoT-SORT compared; choice written with numbers.
- Dry-run controller shown on video; first **hovering** test where the commands are only displayed.
- One-page "M06 journey" (problems, actions, evidence, choice), like M05.
