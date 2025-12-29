import cv2
import time

class MotionDetector:
    def __init__(self, rtsp_url, min_area=5000):
        self.cap = cv2.VideoCapture(rtsp_url)
        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )
        self.min_area = min_area

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, False

        fgmask = self.subtractor.apply(frame)

        contours, _ = cv2.findContours(
            fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        motion = False
        for cnt in contours:
            if cv2.contourArea(cnt) > self.min_area:
                motion = True
                break

        return frame, motion

    def release(self):
        self.cap.release()
