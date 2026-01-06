import json
import logging
from pathlib import Path
from telegram.ext import ContextTypes
from telegram import Update

# === RUTA PORTABLE, MULTIPLATAFORMA ===
# ruta: src/config/allowed_users.json

BASE_DIR = Path(__file__).resolve().parents[2]       # <-- carpeta /src
CONFIG_FILE = BASE_DIR /"bot"/ "config" / "allowed_users.json"

logger = logging.getLogger(__name__)

def load_allowed_users() -> set:
    if not CONFIG_FILE.exists():
        logger.warning(f"[WARNING] No se encontró {CONFIG_FILE}. Se permitirán todos los usuarios.")
        return set()

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return set(data.get("allowed_usernames", []))
    except Exception as e:
        logging.error(f"[ERROR] No se pudo cargar allowed_users.json: {e}")
        return set()


ALLOWED_USERNAMES = load_allowed_users()


def restricted(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        username = update.effective_user.username

        if username not in ALLOWED_USERNAMES:
            await update.effective_message.reply_text(
                "🚫 No tienes permiso para usar este bot."
            )
            return  # No ejecuta la función original

        return await func(update, context, *args, **kwargs)

    return wrapper