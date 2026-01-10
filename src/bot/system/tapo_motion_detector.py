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
        min_area: int = 12000,
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
        self.start_time = time.time()
        self.last_motion_time = 0
        self.sent_boot_image = False

        self.fail_count = 0
        self.max_fails = 5

        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=25,
            detectShadows=True
        )

        self._connect()

    # =============================
    #         RTSP
    # =============================
    def _connect(self):
        if self.cap:
            self.cap.release()

        self.logger.info(f"🔌 Conectando RTSP: {self.name}")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        time.sleep(self.reconnect_delay)

        self.ignore_until = time.time() + self.warmup_time
        self.start_time = time.time()
        self.sent_boot_image = False

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
            return None, False, False # ❌ NO enviar

        ret, frame = self.cap.read()
        if not ret:
            self.fail_count += 1
            if self.fail_count >= self.max_fails:
                self._reconnect()
                self.fail_count = 0
            return None, False, False
        else:
            self.fail_count = 0

        now = time.time()
        frame = cv2.resize(frame, (640, 360))

        if now < self.ignore_until:
            return frame, False, False

        if not self.sent_boot_image:
            self.sent_boot_image = True
            self.logger.info(f"🚨 Camara en linea {self.name} (BOOT)")
            return frame, False, True

        # ROI
        work_frame = frame
        if self.roi:
            x, y, w, h = self.roi
            work_frame = frame[y:y+h, x:x+w]

        gray = cv2.cvtColor(work_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        fgmask = self.subtractor.apply(gray)

        # 🔥 eliminar sombras (gris)
        _, fgmask = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel, iterations=2)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)

        # ☀️ filtro de cambio global (sol)
        motion_ratio = cv2.countNonZero(fgmask) / fgmask.size
        if motion_ratio > 0.25:
            self.logger.debug(f"{self.name} cambio global detectado (luz)")
            return frame, False, False

        contours, _ = cv2.findContours(
            fgmask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:
            area = cv2.contourArea(cnt)
            self.logger.debug(f"🚨 Validando movimiento en {self.name} area:{area}")
            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            if w < 50 or h < 50:
                continue

            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            if hull_area == 0:
                continue

            solidity = area / hull_area
            if solidity < 0.4:
                continue

            if now - self.last_motion_time < self.cooldown:
                return frame, False, False

            self.last_motion_time = now
            self.logger.info(f"🚨 Movimiento detectado en {self.name}")
            return frame, True, False

        return frame, False, False

    def capture_zone(self):
        if not self.cap or not self.cap.isOpened():
            self._reconnect()
            return None

        ret, frame = self.cap.read()
        if not ret:
            self._reconnect()
            return None

        frame = cv2.resize(frame, (640, 360))
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
