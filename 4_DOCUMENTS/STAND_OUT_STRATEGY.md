# How we stand out: engineering strategy until the final exam (Project 3760)

Written 23.11.2026 for Nimer, Dareen and both Claude sessions. **Read it before every milestone, presentation and report.**
Sources: the course Moodle files (syllabus, opening meeting 20.10.2026, mid-presentation guidelines, timetable) and the
two earlier project books on this topic (on Dareen's laptop, `Downloads`; not in git, they are other students' work).

## 1. Why this matters

We are the **third** team to do "a drone that guides a user to a target" with Gabi. The examiner and Gabi have already
seen a working demo twice. **"It works" will not stand out. Measured, defensible engineering will.**

How the grade is built (timetable 2026-27):

| Item | Weight | Who grades | When |
|---|---|---|---|
| Work plan | 10% | project office | 12.11.2026 (done) |
| Mid-project presentation (10 min, max 10 slides) | 20% | project office | Jan-Feb 2027 |
| Supervisor, semester A | 5% | Gabi | Jan-Feb 2027 |
| Test-procedures document | 5% | project office | 28.3.2027 |
| Supervisor: fit for the project exhibition | 5% | Gabi | before final |
| **Final presentation: examiner** | **25%** | examiner | Jul-Aug 2027 |
| **Supervisor, final** | **30%** | Gabi | Jul-Aug 2027 |

Course rules that decide points:
- Final presentation: 25 min (demo at most 5 min) + ~10 min questions; **both** present. Judged on knowledge, content,
  presenting to engineers, and actual work scope: **"work not shown clearly and in detail gets no points."**
- AI is allowed, but we must **say exactly what was done with AI** (mid-presentation: one slide, per block of the block
  diagram) and be ready for technical questions **especially on AI-made parts**.
- Quantitative requirements (at least 3) follow the project all the way; **the project is judged by meeting them**.
  Recommended: **use the same metrics as earlier work**, and compare with it.
- Slides: few words, more graphs, diagrams and results; formal presentation of the algorithms; no code on slides.
- Poster: selected projects go to the exhibition and compete for prizes, judged by staff and industry.
- The faculty's project site (EE section) expects: a **comprehensive literature survey**, planned experiments,
  **analysis of results including statistical analysis**, conclusions and future research directions.
  So our CIs, baselines and a short related-work section (earlier teams + papers: ByteTrack, BoT-SORT, YOLO) count directly.

## 2. What the earlier teams did (so we do not repeat it, and can compare with it)

| | Team A: Fridman & Adda (Winter 2026) | Team B: Qasem Ali & Atallah (project 2720) | **Us** |
|---|---|---|---|
| Drone | DJI Tello (open SDK, Wi-Fi) | DJI Tello | **DJI Neo, no SDK: controlled by mirroring the phone app** (harder, measured delay) |
| Who is the user | typed by hand (enter the track ID) | red shirt, HSV colour | **automatic: YOLO11n + head-colour marker, then tracking** |
| Detection | YOLO11 sizes benchmarked for FPS | YOLO | **8 detectors compared on hand labels (accuracy + FPS)** |
| Tracking | ByteTrack + template matching re-ID | YOLO tracking, wait when lost | M06: tracker + marker re-confirmation + states |
| Control | hysteresis | PD visual servoing | M06+: P/PD **designed around the measured loop delay** |
| Planning | RRT* (tuned, ~5 plans/s) | RRT (95% success, 140 ms) | later milestones |
| **How results were measured** | "from empirical observations" | 30 runs counted by eye; they write the numbers "should not be interpreted as formal dataset-based accuracy metrics" | **per-frame metrics on hand-labelled ground truth, hold-out test set, baselines, confidence intervals** |

Their own future-work lists: remote (out-of-sight) target with memory/map, and obstacles to the drone itself.

## 3. Our edge: eight things to show at every stage

1. **Measured, not observed.** Every claim = number + data size + baseline + uncertainty.
   Example: wrong person 3/164 = 1.8% (95% CI 0.6-5.2%), false alarms 0/239 (95% CI 0-1.6%).
   Team B's 93.3% user detection is 28/30 runs: 95% CI 79-98%, too wide to compare methods. Say this politely.
2. **Honest test data.** Hand labels with written rules, a hold-out set never used for tuning, labelled by both of us.
3. **Baselines and ablations.** Every improvement is shown against the version without it (colour only / YOLO only /
   hybrid; tracker vs no tracker; with vs without re-confirmation).
4. **The loop as a system.** A delay budget (video 256 ms + detection 34 ms ≈ 290 ms + command delay, M06) and a
   controller designed and tested **offline on recorded video first**. Neither earlier team measured their loop delay.
5. **Identity you can trust.** Count **ID swaps on crossing scenes** and wrong-person follows: the exact failure team A
   only described ("ByteTrack assigns a new ID"). Define FOLLOWING / UNSURE / LOST with a safe action for each.
6. **Safety engineering.** Written flight checklist, abort tested, fail-safe states, a small FMEA table (failure → effect →
   detection → action). Examiners from industry notice this.
7. **Requirement trace.** Exact words of the approved work plan → test → result → status, kept up to date. It is the
   backbone of the mid presentation, the test-procedures document and the final book.
8. **Decisions with trade-offs, documented.** A decision log: options tested, criteria, numbers, the price of the
   choice, what would change our mind. Plus: every AI-made part listed per block and understood by both of us.

## 4. Stand-out moves per milestone

| Milestone | The usual way | Our way (what to show) |
|---|---|---|
| M05 detection (done) | "YOLO detects the user" | 8 detectors on 403 hand-labelled frames, wrong-person + false alarms, low-light test, failure analysis |
| M06 tracking (7.12) | "tracking works" | ID swaps / 10 crossings, % user kept vs M05 baseline on the **same** clips, states with actions, hold-out crossing set |
| Control | tune gains in the air | measured command delay, offline replay on video, step-response plot, dead band + rate limit justified by numbers |
| Guidance / path | "the path is shown" | planning success rate + time vs parameters, compared with teams A/B numbers (RRT 95%, 140 ms) |
| Test procedures (28.3) | a list of tests | every requirement → procedure → pass line → result table; reproducible commands |
| Poster | photos + text | one system diagram, one comparison table vs earlier work, one striking plot, the delay budget |
| Final | long demo | 3-minute story, ≤5-min demo with a planned failure case handled safely, numbers with CIs, AI-use slide |

## 5. Checklist for every result, slide or report section

- [ ] Number + **compared with what** + **on what data (how many frames/runs)** + uncertainty (CI or repeats).
- [ ] Which requirement of the approved work plan it serves (exact words).
- [ ] The failure cases shown, with the reason.
- [ ] Reproducible: the command, the data version, the date.
- [ ] What was done with AI, and can **both** of us explain it without notes?
- [ ] One graph instead of a paragraph. No code on slides.
- [ ] Where this beats the earlier teams' way, said in one line.

## 6. Risks to the "stand out" goal

- Too much tooling and slides, too little drone. Mitigation: each week one measured step on the real system.
- Overclaiming. Mitigation: CIs and honest limits. Examiners trust teams that state limits.
- One partner knows a part the other cannot defend. Mitigation: swap and explain each other's part weekly.
- AI-made parts we cannot explain. Mitigation: before pushing AI-made code or numbers, one of us explains it back.
