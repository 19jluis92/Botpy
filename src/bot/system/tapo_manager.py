import asyncio
from pathlib import Path
from time import time
from bot.system.controlador_tapo import TapoController
from bot.system.tapo_motion_detector import MotionDetector
import json

class TapoManager:
    def __init__(self, bot=None, chat_id=None):
        self.bot = bot
        self.chat_id = chat_id
        self.cameras = {}
        self.detectors = []
        BASE_DIR = Path(__file__).resolve().parents[2]       # <-- carpeta /src
        config_path = BASE_DIR /"bot"/ "config" / "tapo_cameras.json"
        self.load(config_path)
        

    def load(self, path):
        with open(path) as f:
            data = json.load(f)
        
        for cam in data["cameras"]:
            self.cameras[cam["name"]] = TapoController(
                cam["name"],
                cam["rtsp"]
            )
        
        for cam in data["cameras"]:
            self.detectors.append({
                "name": cam["name"],
                "controller": TapoController(cam["name"], cam["rtsp"]),
                "detector": MotionDetector(cam["rtsp"]),
                "cooldown": 0
            })
    
    def capture_all(self):
        results = {}
        for name, cam in self.cameras.items():
            results[name] = cam.capture_image()
        return results

    def capture_zone(self, zone_name):
        
        for name, cam in self.cameras.items():
            if zone_name.lower() in name.lower():
                return cam.capture_image()
        return None

    async def monitor_loop(self):
        while True:
            for cam in self.detectors:
                frame, motion = cam["detector"].read()

                if motion and time() > cam["cooldown"]:
                    cam["cooldown"] = time() + 30  # 30s anti-spam

                    image = cam["controller"].capture_image()

                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=f"🚨 Movimiento detectado en {cam['name']}"
                    )

                    await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=open(image, "rb")
                    )

            await asyncio.sleep(1)
