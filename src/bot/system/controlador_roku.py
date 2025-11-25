from rokuecp import Roku

class RokuController:
    def __init__(self):
        self.ip = None
        self.roku = None

    async def connect(self):
        if not self.ip:
            raise RuntimeError("No IP definida para Roku")

        if not self.roku:
            self.roku = Roku(self.ip)

        # Necesario para actualizar datos del dispositivo
        await self.roku.update()

    def set_ip(self, ip: str):
        self.ip = ip

    async def power_on(self):
        await self.connect()
        # Encendido = enviar "Home" porque PowerOn no existe
        await self.roku.control.keypress("Home")

    async def power_off(self):
        await self.connect()
        await self.roku.control.keypress("PowerOff")

    async def volume_up(self, steps=1):
        await self.connect()
        for _ in range(steps):
            await self.roku.control.keypress("VolumeUp")

    async def volume_down(self, steps=1):
        await self.connect()
        for _ in range(steps):
            await self.roku.control.keypress("VolumeDown")

    async def launch_app(self, app_id: str):
        await self.connect()
        await self.roku.control.launch(app_id)
