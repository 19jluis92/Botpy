import cv2
import time
import logging
import math
from ultralytics import YOLO
from typing import Optional, Tuple, List


class ObjectDetector:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        name: str,
        rtsp_url: str,
        model: str = "yolov8n.pt",
        detect_classes: Optional[List[str]] = None,
        conf_threshold: float = 0.45,
        reconnect_delay: int = 5,
        warmup_time: int = 10,
        roi: Optional[Tuple[int, int, int, int]] = None,
        position_tolerance: int = 80,
        area_tolerance: float = 0.5,
        static_lock_time: int = 20   # ⏸️ segundos para bloquear objeto
    ):
        self.name = name
        self.rtsp_url = rtsp_url
        self.conf_threshold = conf_threshold
        self.reconnect_delay = reconnect_delay
        self.warmup_time = warmup_time
        self.roi = roi

        self.detect_classes = detect_classes or ["person", "car", "dog", "cat"]

        self.position_tolerance = position_tolerance
        self.area_tolerance = area_tolerance
        self.static_lock_time = static_lock_time

        self.tracked_objects = []

        self.cap = None
        self.model = YOLO(model)

        self.start_time = time.time()
        self.fail_count = 0
        self.max_fails = 5

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

        self.start_time = time.time()
        self.fail_count = 0

    def _reconnect(self):
        self.logger.warning(f"♻️ Reconectando cámara... {self.name}")
        try:
            self.cap.release()
        except Exception:
            pass

        time.sleep(self.reconnect_delay)
        self._connect()

    # =============================
    #      OBJECT DETECTION
    # =============================
    def read(self):
        if not self.cap or not self.cap.isOpened():
            self._reconnect()
            return None, False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.fail_count += 1
            if self.fail_count >= self.max_fails:
                self._reconnect()
            return None, False, None

        self.fail_count = 0
        frame = cv2.resize(frame, (640, 360))

        # 🧠 Warmup
        if time.time() - self.start_time < self.warmup_time:
            return frame, False, None

        work_frame = frame
        roi_offset = (0, 0)
        if self.roi:
            x, y, w, h = self.roi
            work_frame = frame[y:y+h, x:x+w]
            roi_offset = (x, y)

        results = self.model(
            work_frame,
            conf=self.conf_threshold,
            imgsz=640,
            verbose=False
        )

        now = time.time()

        for r in results:
            for box in r.boxes:
                cls_name = r.names[int(box.cls)]

                if cls_name not in self.detect_classes:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2) + roi_offset[0]
                cy = int((y1 + y2) / 2) + roi_offset[1]
                area = (x2 - x1) * (y2 - y1)

                if self._handle_object(cx, cy, area, cls_name, now):
                    continue

                self.logger.info(f"🚨 {self.name}: nuevo {cls_name}")
                return frame, True, cls_name

        self._cleanup_objects(now)
        return frame, False, None

    # =============================
    #      OBJECT TRACKING
    # =============================
    def _handle_object(self, cx, cy, area, cls, now):
        for obj in self.tracked_objects:
            if obj["cls"] != cls:
                continue

            dist = math.hypot(cx - obj["center"][0], cy - obj["center"][1])
            area_diff = abs(area - obj["area"]) / obj["area"]

            if dist < self.position_tolerance and area_diff < self.area_tolerance:
                obj["center"] = (cx, cy)
                obj["area"] = area
                obj["last_seen"] = now

                if not obj["locked"]:
                    if now - obj["static_since"] >= self.static_lock_time:
                        obj["locked"] = True
                        self.logger.info(f"{self.name}: {cls} BLOQUEADO (estático)")

                return True  # mismo objeto → no alertar

        # objeto realmente nuevo
        self.tracked_objects.append({
            "cls": cls,
            "center": (cx, cy),
            "area": area,
            "last_seen": now,
            "static_since": now,
            "locked": False
        })

        return False

    def _cleanup_objects(self, now):
        # elimina solo los que DESAPARECEN
        self.tracked_objects = [
            o for o in self.tracked_objects
            if now - o["last_seen"] < 5
        ]

    # =============================
    #        UTILIDADES
    # =============================
    def capture_zone(self):
        if not self.cap or not self.cap.isOpened():
            self._reconnect()
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return cv2.resize(frame, (640, 360))

    def release(self):
        if self.cap:
            self.cap.release()
