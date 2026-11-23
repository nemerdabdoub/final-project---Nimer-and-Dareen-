# Mentor coach panel (Claude Code)

A second panel beside the Claude chat, next to Nimer's **Project updates** panel. It acts as a stand-in supervisor:

- **Guesses which process you are in** (feeling lost, flight test, experiment, labelling, controller, decision,
  meeting with Gabi, writing, code, debugging, working as a pair, new milestone) from your messages and from the
  commands Claude runs and the files it edits. Your own messages count more than Claude's commands for 10 minutes.
- **Shows that playbook:** why it matters, the steps, what Gabi will ask, the traps, and when it is done, plus the
  current milestone, days left and the next open task from `2_MILESTONES/mentor_plan.md`, and one principle per hour.
- **Ask the mentor buttons** send a question to Claude: "Where are we? What is the ONE next step?", "Review what we
  just did, like Gabi would", "Practice: ask us Gabi's hardest questions", "Plan our next 2 hours",
  "Explain the idea behind this simply".
- **Tells Claude the current process**, so the Advisor's view in the chat uses the same playbook.

The advice lives in `2_MILESTONES/mentor_playbooks.md` (plain Markdown). Edit it to change what the mentor says;
the panel reloads it every 15 s. Nothing here runs git or changes files.

## Commands

- `/mentor`: open the panel
- `/mentor flight` (or any playbook id): pin a process so it does not switch
- `/mentor auto`: follow your work automatically again

## Install

Once this folder is in the marketplace file, `/plugin install mentor-coach --marketplace nemerdabdoub/final-project---Nimer-and-Dareen-`.
In a session where `/plugin` is not available, Claude can link the folder into the session's mods folder (as done on Dareen's laptop, 23.11).
