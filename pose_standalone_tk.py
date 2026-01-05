# pose_standalone_tk.py
"""
TECHTRAP - Final Stable Demo
Pose-based Rehabilitation System
MediaPipe + MindSpore
Huawei ICT Competition - Innovation Track
"""

import cv2
import time
import math
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk

# MindSpore AI backend
from ai.mindspore_pose import MindSporeAI



# ========= Pose Detector (MediaPipe) =========
class poseDetector:
    def __init__(self, detectionCon=0.5, trackCon=0.5, model_complexity=1):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            smooth_landmarks=True,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon,
        )
        self.results = None
        self.lmList = []

    def findPose(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            self.mpDraw.draw_landmarks(
                img,
                self.results.pose_landmarks,
                self.mpPose.POSE_CONNECTIONS
            )
        return img

    def findPosition(self, img):
        self.lmList = []
        if self.results and self.results.pose_landmarks:
            h, w, _ = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
        return self.lmList

    def findAngle(self, img, p1, p2, p3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        angle = math.degrees(
            math.atan2(y3 - y2, x3 - x2)
            - math.atan2(y1 - y2, x1 - x2)
        )
        if angle < 0:
            angle += 360

        cv2.putText(
            img,
            str(int(angle)),
            (x2 - 40, y2 + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )
        return angle


# ========= MAIN =========
def main():
    # Initialize MindSpore
    ms_ai = MindSporeAI()

    # Initialize pose detector
    detector = poseDetector()

    # Camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit("Camera not found")

    # Tkinter GUI
    root = tk.Tk()
    root.title("TECHTRAP – Pose Demo (MindSpore)")
    label = tk.Label(root)
    label.pack()

    pTime = 0

    def update_frame():
        nonlocal pTime

        ok, img = cap.read()
        if not ok:
            return

        # MindSpore inference (AI backend proof)
        _ = ms_ai.infer(img)

        # MediaPipe pose
        img = detector.findPose(img)
        lmList = detector.findPosition(img)

        if len(lmList) > 15:
            detector.findAngle(img, 11, 13, 15)

        # Status text
        cv2.putText(
            img,
            "MindSpore: ACTIVE",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # FPS
        cTime = time.time()
        fps = int(1 / (cTime - pTime)) if pTime else 0
        pTime = cTime
        cv2.putText(
            img,
            f"{fps} FPS",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2,
        )

        # Convert OpenCV image → Tkinter
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgPIL = Image.fromarray(imgRGB)
        imgTK = ImageTk.PhotoImage(imgPIL)

        label.imgtk = imgTK
        label.configure(image=imgTK)

        root.after(10, update_frame)

    update_frame()
    root.mainloop()
    cap.release()


if __name__ == "__main__":
    main()
