# M05 session notes, 22.11 (Dareen's laptop, with Claude Code)

For Nimer: what was done tonight, the results, and what is next.

## 1. Install check: works
- `git pull` first. The only update was CLAUDE.md, which now says to commit and push after each finished change.
- `python m05.py` (from 1_CODE) prints the help text (STEP 1 to STEP 4).
- Separate import test: Python 3.14.8, ultralytics 8.4.216, torch 2.15.0 (CPU), OpenCV 5.0.0. All load.

## 2. Frames extracted: done
Command from `M05_YOLO_comparison_23.11.md` (extract, every 25 / 38 / 25 / 75 frames):

| Clip | Frames |
|---|---|
| 161951_recording_test60.mp4 | 61 |
| 154848_connection_test_video.mp4 | 40 |
| 161825_recording_test30.mp4 | 31 |
| 154124_connection_test_video.mp4 (no actor) | 20 |
| **Total** | **152** (22 MB) |

Saved in `3_EVIDENCE/m05_user_detection/frames/`. This matches the plan exactly.
Checked one frame (161951_..._00750.jpg): the actor in the red turban is clear. Also visible:
- the red mural on the left (the case where colour alone should fail);
- the DJI Fly on-screen buttons and timer. They are not people; just ignore them when labelling.

## 3. Suggested labels (prelabel): done
`python m05.py prelabel` downloaded yolo11l.pt (49 MB) and labelled all 152 frames. Output:
`3_EVIDENCE/m05_user_detection/labels_suggested/` = 152 `.txt` files + `classes.txt` (`user`, `person`).

| Clip | Frames | "user" boxes | "person" boxes | Frames with no box | Who corrects |
|---|---|---|---|---|---|
| 161951 | 61 | 46 | 83 | 2 | Dareen |
| 154124 (no actor) | 20 | 0 | 42 | 0 | Dareen |
| 154848 | 40 | 23 | 65 | 1 | **Nimer** |
| 161825 | 31 | 12 | 14 | 5 | **Nimer** |

- Good sign: the clip without the actor got **0** "user" boxes.
- These are only suggestions. About 50 frames with the actor do not have him marked as `user` yet
  (turban hidden or small), and some people may be missing. That is what the hand correction fixes.

## 4. Next steps
**Nimer: correct your half** (frames starting with **154848** and **161825**, 71 frames, about 35-45 min):
1. makesense.ai (no account) or Roboflow, new object-detection project.
2. Upload your frames + the matching `.txt` files from `labels_suggested` + `classes.txt` (from Drive).
3. The turban man = `user` (class 0); everyone else = `person` (class 1). Add missing people, delete wrong boxes.
4. Export in YOLO format into the shared `labels` folder on Drive.

**Dareen:** upload m05.py, frames and labels_suggested to Drive, then correct the 161951 + 154124 half (81 frames).
After both halves are in `3_EVIDENCE/m05_user_detection/labels/`: C1 `python m05.py run colour`, then the YOLO checks.

## 5. GitHub plugin error in the Claude app (optional, not needed for M05)
Popup: "Couldn't reconnect github: Authorization header is badly formatted".
- Cause: the plugin logs in with the Windows variable `GITHUB_PERSONAL_ACCESS_TOKEN`, and that variable is not set,
  so it sends an empty key. Normal `git pull` / `git push` are not affected.
- Fix (each person on their own laptop; never paste the token in a chat or a file):
  1. github.com, Settings, Developer settings, Personal access tokens, Fine-grained tokens, Generate new token.
     Only this repo; Contents, Issues, Pull requests = Read and write; 90 days.
  2. Windows search "environment variables", "Edit environment variables for your account", User variables, New:
     name `GITHUB_PERSONAL_ACCESS_TOKEN`, value = the token.
  3. Close the Claude app completely (also from the tray) and open it again. The popup should be gone.

## 6. Open question for Nimer
`1_CODE/detect_user.py` and `1_CODE/fix_video_speed.py` are staged on Dareen's laptop but **not committed**.
Are they yours? Tell Dareen whether to push them.
