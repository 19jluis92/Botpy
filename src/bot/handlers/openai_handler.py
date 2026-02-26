import json
import logging
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from bot.system.controlador_openai import OpenAIManager

logger = logging.getLogger(__name__)

openai_manager = None  # Variable global para almacenar la instancia de OpenAIManager

async def openai_start():
    """Inicializar conexión con OpenAI."""
    # Cargar configuración de OpenAI desde archivo JSON
    logger.info(f"openai_start called")
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'openai.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Crear instancia de OpenAIManager con la configuración
    global openai_manager
    openai_manager = OpenAIManager(
        ip_config=config.get("ip"),
        port_config=config.get("port"),
        api_key=config.get("api_key"),
        model_config=config.get("model")
    )

    logger.info(f"openai_manager created: {openai_manager}")
    # Conectar a OpenAI
    try:
        await openai_manager.connect()
        logger.info("Connected to OpenAI successfully.")
    except Exception as e:
        logger.error(f"Error connecting to OpenAI: {e}")


async def openai_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global openai_manager
    logger.info("openai_text_router called")

    if update.message.text.startswith("/"):
        logger.info("openai_text_router message ignored starts with /")
        return context.user_data.get("state")
    
    if not openai_manager:
        logger.info("openai_text_router message ignored because openai_manager is not initialized")
        return context.user_data.get("state")

    try:
        user_message = update.message.text

        logger.info("openai_text_router sending user_message: " + user_message)

        response = await openai_manager.chat(user_message)

        logger.info("openai_text_router  response: " + response)

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"AI error: {e}")
        await update.message.reply_text("⚠️ Error con IA")

    # regresar al estado donde estaba el usuario
    return context.user_data.get("state")

async def openai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """El usuario escribe al chat con openAI."""
    message = update.message.text.strip()

    try:
       #answer
       answer = await  openai_manager.chat(message)
       await update.message.reply_text(f"{answer}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al conectar con OpenAI:\n{e}")

    return context.user_data.get("state")