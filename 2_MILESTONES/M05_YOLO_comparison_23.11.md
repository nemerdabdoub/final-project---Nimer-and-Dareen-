# M05 - User detection: compare YOLO versions (due Monday 23.11)

You do NOT need the drone for most of this: use the flight videos you already have (3_EVIDENCE\2026-10-20).

1. Install Ultralytics:   python -m pip install ultralytics    (and check the versions of YOLO that exist in the OFFICIAL Ultralytics documentation: YOLO11, YOLOv12, YOLO26)
2. Cut frames out of the flight videos. Label about 200 frames: the user (person). Tools: CVAT or Roboflow.
3. Run each YOLO version on the same labelled frames. Measure: detection rate (the plan asks for 90% in the lab) and speed (frames per second on your laptop).
4. One results table + one short video with the detections. Write the winner and why.
5. Also compare with the colour-marker idea (the plan asks: colour marker vs YOLO).
6. Save the table, the video and the labelled set in 3_EVIDENCE\<date>\.
Present it to Gabi on 23.11. Keep the AI log up to date (5_LOGS\Project_logs.xlsx, sheet AI log).

## Update 21.11
Use `1_CODE/m05_yolo_compare.py` and follow `4_DOCUMENTS/Project_3493_Plan_until_Gabi_23.11.pdf`.
Label with two classes in Roboflow: `user` (0) and `other` (1). Design for the system: YOLO finds people, the colour marker picks the user (`hybrid` mode).
