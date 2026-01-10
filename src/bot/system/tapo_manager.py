import asyncio
import os
import time
import json
from pathlib import Path
import logging
from bot.system.controlador_tapo import TapoController
from bot.system.tapo_object_detector import ObjectDetector


class TapoManager:
    logger = logging.getLogger(__name__)

    def __init__(self, bot=None, chat_id=None):
        self.bot = bot
        self.chat_id = chat_id
        self.cameras = {}
        self.detectors = []
        self.notifications_enabled = True  # 🔔 GLOBAL

        base_dir = Path(__file__).resolve().parents[2]
        config_path = base_dir / "bot" / "config" / "tapo_cameras.json"

        self.last_cleanup = 0
        self.load(config_path)

    # =============================
    #          LOAD
    # =============================
    def load(self, path):
        with open(path) as f:
            data = json.load(f)

        for cam in data["cameras"]:
            controller = TapoController(
                cam["name"],
                cam["rtsp"]
            )

            # detector = MotionDetector(
            #     name=cam["name"],
            #     rtsp_url=cam["rtsp"],
            #     min_area=cam["area"],
            #     cooldown=30,
            #     warmup_time=15
            # )

            detector = ObjectDetector(
                name=cam["name"],
                rtsp_url=cam["rtsp"],
                detect_classes=["person", "dog"],#detect_classes=["person", "car", "dog"],
                warmup_time=10,
                roi=None,  # opcional desde JSON,
                position_tolerance=90,
                area_tolerance=0.6,
                static_lock_time=20
            )
            
            self.cameras[cam["name"]] = controller
            self.detectors.append({
                "name": cam["name"],
                "controller": controller,
                "detector": detector,
                "last_sent": 0,
                "min_interval": 60,
                "enabled": True
            })

    # =============================
    #       MONITOR LOOP
    # =============================

    #Deprecated too sensible pixel by pixel works with tapo_motion_detector.py
    # async def monitor_loop(self):
    #     await asyncio.sleep(10)

    #     while True:
    #         now = time.time()

    #         for cam in self.detectors:
    #             try:
    #                 frame, motion, boot = cam["detector"].read()

    #                 if frame is None:
    #                     self.logger.error(f"{cam['name']} frame None, saltando")
    #                     continue

    #                 # 📸 BOOT SIEMPRE TIENE PRIORIDAD
    #                 if boot:
    #                     self.logger.info(f"{cam['name']} enviando BOOT")
    #                     image = cam["controller"].save_frame(frame)

    #                     await self.bot.send_message(
    #                         chat_id=self.chat_id,
    #                         text=f"📸 Cámara {cam['name']} iniciada"
    #                     )
    #                     await self.bot.send_photo(
    #                         chat_id=self.chat_id,
    #                         photo=open(image, "rb")
    #                     )

    #                     cam["last_sent"] = now
    #                     continue  # ⬅️ MUY IMPORTANTE

    #                 # ⏱️ Intervalo anti-spam
    #                 if now - cam["last_sent"] < cam["min_interval"]:
    #                     continue

    #                 # 🚨 Movimiento
    #                 if motion:
    #                     self.logger.info(f"🚨 {cam['name']} enviando MOVIMIENTO")
    #                     image = cam["controller"].save_frame(frame)

    #                     await self.bot.send_message(
    #                         chat_id=self.chat_id,
    #                         text=f"🚨 Movimiento detectado en {cam['name']}"
    #                     )
    #                     await self.bot.send_photo(
    #                         chat_id=self.chat_id,
    #                         photo=open(image, "rb")
    #                     )

    #                     cam["last_sent"] = now

    #             except Exception as e:
    #                 self.logger.error(f"Error en {cam['name']}: {e}")

    #         # 🧹 Limpieza cada 5 min
    #         if now - self.last_cleanup > 300:
    #             for cam in self.detectors:
    #                 self.cleanup_folder("captures"+cam['name'], 300)
    #             self.last_cleanup = now

    #         await asyncio.sleep(1)

    async def monitor_loop(self):
        await asyncio.sleep(5)
        while True:
            now = time.time()

            for cam in self.detectors:
                try:
                    if not self.notifications_enabled or not cam["enabled"]:
                        self.logger.info(f"{cam['name']} detección ignorada (notificaciones apagadas)")
                        await asyncio.sleep(10)
                        continue


                    frame, detected, label =  await asyncio.to_thread(
                    cam["detector"].read
                    )

                    if frame is None:
                        continue

                    if detected:
                        image = cam["controller"].save_frame(frame)
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=f"🚨 {label.upper()} detectado en {cam['name']}"
                        )
                        await self.bot.send_photo(
                            chat_id=self.chat_id,
                            photo=open(image, "rb")
                        )
                        cam["last_sent"] = now
                except Exception as e:
                    self.logger.error(f"Error en {cam['name']}: {e}")
            
            await asyncio.sleep(0.3)
            
            # 🧹 Limpieza cada 5 min
            if now - self.last_cleanup > 300:
                for cam in self.detectors:
                    self.cleanup_folder("captures"+cam['name'], 300)
                self.last_cleanup = now

    # =============================
    #        CLEANUP
    # =============================
    def cleanup_folder(self, folder, max_age_seconds=300):
        if not os.path.exists(folder):
            return

        now = time.time()
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)

            if not os.path.isfile(path):
                continue

            if now - os.path.getmtime(path) > max_age_seconds:
                try:
                    os.remove(path)
                except Exception:
                    pass


    def capture_zone(self, zone_name):

        for cam in self.detectors:
            if zone_name.lower() in cam["name"].lower():
                frame = cam["detector"].capture_zone()
                if frame is None:
                    return None
                image = cam["controller"].save_frame(frame)
                return image
        return None
