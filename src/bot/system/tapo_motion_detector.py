import logging
import cv2
import time

class MotionDetector:
    logger = logging.getLogger(__name__)
    
    def __init__(
        self,
        rtsp_url: str,
        min_area: int = 5000,
        cooldown: int = 30,
        reconnect_delay: int = 5
    ):
        """
        :param rtsp_url: URL RTSP de la cámara
        :param min_area: Área mínima para detectar movimiento
        :param cooldown: Segundos entre alertas
        :param reconnect_delay: Segundos antes de reintentar RTSP
        """
        self.rtsp_url = rtsp_url
        self.min_area = min_area
        self.cooldown = cooldown
        self.reconnect_delay = reconnect_delay

        self.last_motion_time = 0
        self.cap = None

        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=False
        )

        self._connect()

    # =============================
    #       RTSP CONNECTION
    # =============================
    def _connect(self):
        if self.cap:
            self.cap.release()

        self.logger.info("🔌 Conectando a cámara RTSP...")
        self.cap = cv2.VideoCapture(self.rtsp_url)

        # Da tiempo a RTSP de estabilizar
        time.sleep(1)

    def _reconnect(self):
        self.logger.info("♻️ Reintentando conexión RTSP...")
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
        """
        :return: (frame, motion_detected)
        """
        if not self.cap or not self.cap.isOpened():
            self._reconnect()
            return None, False

        ret, frame = self.cap.read()

        if not ret:
            self._reconnect()
            return None, False

        fgmask = self.subtractor.apply(frame)

        contours, _ = cv2.findContours(
            fgmask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        motion = any(
            cv2.contourArea(cnt) > self.min_area
            for cnt in contours
        )

        # =============================
        #        COOLDOWN
        # =============================
        if motion:
            now = time.time()
            if now - self.last_motion_time < self.cooldown:
                return frame, False

            self.last_motion_time = now
            return frame, True

        return frame, False

    # =============================
    #         CLEANUP
    # =============================
    def release(self):
        if self.cap:
            self.cap.release()
