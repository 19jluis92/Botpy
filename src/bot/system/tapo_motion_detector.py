import cv2
import time
import logging
from typing import Optional, Tuple

class MotionDetector:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        rtsp_url: str,
        min_area: int = 8000,
        cooldown: int = 30,
        reconnect_delay: int = 5,
        warmup_time: int = 15,
        roi: Optional[Tuple[int, int, int, int]] = None
    ):
        """
        :param rtsp_url: RTSP URL
        :param min_area: área mínima de movimiento
        :param cooldown: segundos entre alertas
        :param reconnect_delay: segundos antes de reconectar
        :param warmup_time: tiempo de aprendizaje inicial
        :param roi: (x, y, w, h) región de interés
        """
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

        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=False
        )

        self._connect()

    # =============================
    #         RTSP
    # =============================
    def _connect(self):
        if self.cap:
            self.cap.release()

        self.logger.info(f"🔌 Conectando RTSP: {self.rtsp_url}")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        time.sleep(1)

        self.start_time = time.time()
        self.sent_boot_image = False

    def _reconnect(self):
        self.logger.warning("♻️ Reconectando cámara...")
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
        if not ret:
            self._reconnect()
            return None, False, False

        # 📸 Snapshot inicial
        if not self.sent_boot_image:
            self.sent_boot_image = True
            return frame, False, True

        # ROI
        work_frame = frame
        if self.roi:
            x, y, w, h = self.roi
            work_frame = frame[y:y+h, x:x+w]

        gray = cv2.cvtColor(work_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        elapsed = time.time() - self.start_time
        learning_rate = -1 if elapsed < self.warmup_time else 0

        fgmask = self.subtractor.apply(gray, learningRate=learning_rate)

        # 🧼 Limpieza
        _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel, iterations=2)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)

        if elapsed < self.warmup_time:
            return frame, False, False

        contours, _ = cv2.findContours(
            fgmask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            if w < 50 or h < 50:
                continue

            now = time.time()
            if now - self.last_motion_time < self.cooldown:
                return frame, False, False

            self.last_motion_time = now
            return frame, True, False

        return frame, False, False

    # =============================
    #          CLEANUP
    # =============================
    def release(self):
        if self.cap:
            self.cap.release()
