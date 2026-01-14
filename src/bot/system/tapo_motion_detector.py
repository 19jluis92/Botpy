import cv2
import time
import logging
from typing import Optional, Tuple


class MotionDetector:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        name: str,
        rtsp_url: str,
        min_area: int = 8000,
        cooldown: int = 30,
        reconnect_delay: int = 5,
        warmup_time: int = 15,
        roi: Optional[Tuple[int, int, int, int]] = None
    ):
        self.name = name
        self.rtsp_url = rtsp_url
        self.min_area = min_area
        self.cooldown = cooldown
        self.reconnect_delay = reconnect_delay
        self.warmup_time = warmup_time
        self.roi = roi

        self.cap = None
        self.last_motion_time = 0
        self.sent_boot_image = False

        self.fail_count = 0
        self.max_fails = 5

        # 🧠 Warm-up SOLO UNA VEZ
        self.warmup_until = time.time() + self.warmup_time

        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=False
        )

        self._connect(initial=True)

    # =============================
    #         RTSP
    # =============================
    def _connect(self, initial=False):
        if self.cap:
            self.cap.release()

        self.logger.info(f"🔌 Conectando RTSP: {self.name}")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        time.sleep(self.reconnect_delay)

        # ❗️ NO tocar warmup ni boot en reconexión

    def _reconnect(self):
        self.logger.warning(f"♻️ Reconectando cámara... {self.name}")
        try:
            self.cap.release()
        except Exception:
            pass
        time.sleep(self.reconnect_delay)
        self._connect()

    # =============================
    #      MOTION DETECTION
    # =============================
    def read(self):
        if not self.cap or not self.cap.isOpened():
            self._reconnect()
            return None, False, False

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.fail_count += 1
            if self.fail_count >= self.max_fails:
                self.fail_count = 0
                self._reconnect()
            return None, False, False
        else:
            self.fail_count = 0

        frame = cv2.resize(frame, (640, 360))
        now = time.time()

        # 🧠 Warm-up REAL
        if now < self.warmup_until:
            self.subtractor.apply(
                cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                learningRate=-1
            )
            return frame, False, False

        # 📸 Snapshot SOLO UNA VEZ
        if not self.sent_boot_image:
            self.sent_boot_image = True
            self.logger.info(f"🚨 Camara en linea {self.name} (BOOT)")
            return frame, False, True

        # ROI
        work_frame = frame
        if self.roi:
            x, y, w, h = self.roi
            work_frame = frame[y:y + h, x:x + w]

        gray = cv2.cvtColor(work_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        fgmask = self.subtractor.apply(gray, learningRate=0)

        _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel, 2)
        fgmask = cv2.dilate(fgmask, kernel, 2)

        contours, _ = cv2.findContours(
            fgmask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:
            if cv2.contourArea(cnt) < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            if w < 50 or h < 50:
                continue

            if now - self.last_motion_time < self.cooldown:
                return frame, False, False

            self.last_motion_time = now
            self.logger.info(f"🚨 Movimiento detectado en {self.name}")
            return frame, True, False

        return frame, False, False
