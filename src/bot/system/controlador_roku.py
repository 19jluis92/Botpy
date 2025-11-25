import asyncio
from rokuecp import Roku

class RokuController:
    def __init__(self):
        self.ip = None
        self.roku = None

    async def connect(self):
        if self.ip is None:
            raise RuntimeError("No se ha definido la IP de la Roku")
        self.roku = await Roku.connect(self.ip)

    def set_ip(self, ip: str):
        """Define la IP de la Roku para usar después."""
        self.ip = ip

    async def home(self):
        await self.roku.control.keypress("Home")

    async def power_off(self):
        await self.roku.control.keypress("PowerOff")

    async def volume_up(self, steps: int = 1):
        for _ in range(steps):
            await self.roku.control.keypress("VolumeUp")

    async def volume_down(self, steps: int = 1):
        for _ in range(steps):
            await self.roku.control.keypress("VolumeDown")

    async def get_apps(self):
        return await self.roku.query.apps()

    async def launch_app(self, app_id: str):
        await self.roku.control.launch(app_id)
