import asyncio
import os
import time
import json
from pathlib import Path
import logging
from bot.system.controlador_tapo import TapoController
from bot.system.tapo_motion_detector import MotionDetector


class TapoManager:
    logger = logging.getLogger(__name__)

    def __init__(self, bot=None, chat_id=None):
        self.bot = bot
        self.chat_id = chat_id
        self.cameras = {}
        self.detectors = []

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

            detector = MotionDetector(
                name=cam["name"],
                rtsp_url=cam["rtsp"],
                min_area=8000,
                cooldown=30,
                warmup_time=15
            )

            self.cameras[cam["name"]] = controller
            self.detectors.append({
                "name": cam["name"],
                "controller": controller,
                "detector": detector,
                "last_sent": 0,
                "min_interval": 60
            })

    # =============================
    #       MONITOR LOOP
    # =============================
    async def monitor_loop(self):
        await asyncio.sleep(10)  # Espera inicial
        while True:
            for cam in self.detectors:
                try:
                    frame, motion, boot = cam["detector"].read()

                    now = time.time()

                    if now - cam["last_sent"] < cam["min_interval"]:
                        self.logger.info(f" {cam['name']} el intervalo no ha pasado, saltando...")
                        self.logger.debug(f" {cam['name']} el intervalo no ha pasado, saltando...last_sent:{ cam['last_sent']} now:{now}")
                        continue

                    if frame is None:
                        self.logger.error(f" {cam['name']} el frame es None, saltando...")
                        continue
                
                    # 📸 Snapshot al iniciar cámara
                    if boot:
                        self.logger.info(f" {cam['name']} enviando notificación: INICIO")
                        image = cam["controller"].save_frame(frame)
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=f"📸 Cámara {cam['name']} iniciada"
                        )
                        await self.bot.send_photo(
                            chat_id=self.chat_id,
                            photo=open(image, "rb")
                        )
                        cam["last_sent"] = now
                    # 🚨 Movimiento detectado
                    if motion:
                        self.logger.info(f" {cam['name']} enviando notificación: MOVIMIENTO")
                        image = cam["controller"].save_frame(frame)

                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=f"🚨 Movimiento detectado en {cam['name']}"
                        )
                        await self.bot.send_photo(
                            chat_id=self.chat_id,
                            photo=open(image, "rb")
                        )
                        cam["last_sent"] = now
                
                except Exception as e:
                    self.logger.error(f"Error en {cam['name']} enviando notificación: {e}")
            await asyncio.sleep(1)
            # 🧹 Limpieza cada 5 minutos
            now = time.time()
            if now - self.last_cleanup > 300:
                self.cleanup_folder("captures"+cam["name"], 300)
                self.last_cleanup = now

            await asyncio.sleep(1)

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
                image = cam["controller"].save_frame(frame)
                return image
        return None
