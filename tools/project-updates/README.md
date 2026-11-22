# Project updates panel (Claude Code)

A live panel beside the Claude chat in VS Code. It shows whether this laptop is in sync with GitHub,
the files changed on this laptop that are not committed yet, and the last 20 pushes by Nimer and Dareen
with their files, and the M05 false alarms from every result table. Click a file to open it in VS Code. It refreshes every 5 seconds and checks GitHub
every 2 minutes. It finds git (also GitHub Desktop's git) and VS Code on any laptop by itself.

## Install (once, in the Claude chat)

```
/plugin install project-updates --marketplace nemerdabdoub/final-project---Nimer-and-Dareen-
```

Answer `y` to add the marketplace, then pick a scope. Reopen the panel any time with `/updates`.

