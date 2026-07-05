import sys
import types


def _install_module(name, module):
    sys.modules[name] = module

# ------------------
# Modulos simulados
# ------------------

# cv2
cv2 = types.ModuleType("cv2")

class VideoCapture:
    def __init__(self, url):
        self.url = url
        self._opened = True

    def isOpened(self):
        return True

    def read(self):
        return True, b"frame"

    def release(self):
        pass


def resize(frame, size):
    return frame


def imwrite(path, frame):
    open(path, "wb").close()
    return True

cv2.VideoCapture = VideoCapture
cv2.resize = resize
cv2.imwrite = imwrite
_install_module("cv2", cv2)

# ultralytics
ultralytics = types.ModuleType("ultralytics")

class YOLO:
    def __init__(self, model):
        self.model = model

    def __call__(self, frame, conf, imgsz, verbose):
        return []

ultralytics.YOLO = YOLO
_install_module("ultralytics", ultralytics)

# docker
docker = types.ModuleType("docker")

def from_env():
    raise RuntimeError("Docker no disponible")

docker.from_env = from_env
_install_module("docker", docker)

# rokuecp
rokuecp = types.ModuleType("rokuecp")

class Roku:
    def __init__(self, ip):
        self.ip = ip

    async def update(self):
        return None

    async def remote(self, command):
        return None

    async def launch(self, app_id):
        return None

    async def _get_apps(self):
        return []

    async def _get_device_info(self):
        return {}

rokuecp.Roku = Roku
_install_module("rokuecp", rokuecp)

# openai
openai = types.ModuleType("openai")

class AsyncOpenAI:
    def __init__(self, base_url, api_key, timeout, max_retries, http_client):
        self.chat = types.SimpleNamespace(
            completions=types.SimpleNamespace(
                create=lambda **kwargs: types.SimpleNamespace(
                    choices=[types.SimpleNamespace(
                        message=types.SimpleNamespace(content="ok")
                    )]
                )
            )
        )

openai.AsyncOpenAI = AsyncOpenAI
_install_module("openai", openai)

# httpx
httpx = types.ModuleType("httpx")

class AsyncClient:
    def __init__(self, proxies, trust_env):
        pass

httpx.AsyncClient = AsyncClient
_install_module("httpx", httpx)

# psutil
psutil = types.ModuleType("psutil")

def cpu_percent(interval=None):
    return 1.0


def virtual_memory():
    return types.SimpleNamespace(percent=2.0)


def disk_usage(path):
    return types.SimpleNamespace(percent=3.0)

psutil.cpu_percent = cpu_percent
psutil.virtual_memory = virtual_memory
psutil.disk_usage = disk_usage
_install_module("psutil", psutil)

# telegram
telegram = types.ModuleType("telegram")

class InlineKeyboardButton:
    def __init__(self, text, callback_data):
        self.text = text
        self.callback_data = callback_data


class InlineKeyboardMarkup:
    def __init__(self, keyboard):
        self.keyboard = keyboard


telegram.InlineKeyboardButton = InlineKeyboardButton
telegram.InlineKeyboardMarkup = InlineKeyboardMarkup
telegram.Update = object
_install_module("telegram", telegram)

# telegram.ext
telegram_ext = types.ModuleType("telegram.ext")

class ContextTypes:
    DEFAULT_TYPE = object

telegram_ext.ContextTypes = ContextTypes
_install_module("telegram.ext", telegram_ext)
