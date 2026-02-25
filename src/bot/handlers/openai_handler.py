import json
import logging
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from bot.constants.states import OPENAI_ROUTES
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

async def openai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Si viene de botón
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        # Si viene del comando /openai
        message = update.message

    context.user_data["state"] = OPENAI_ROUTES

    await message.reply_text(
        openai_menu_message(),
        reply_markup=openai_menu_keyboard()
    )

    return OPENAI_ROUTES

def openai_menu_message():
    return "Choose OpenAI action:"

def openai_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('chat', callback_data='chat')],
    ])

async def openai_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Si estamos esperando texto para chat, redirigir a función de chat
    if context.user_data.get("awaiting_chat", False) and text.find("/") == -1  :
        return await openai_chat(update, context)

    # Si llega texto sin esperarlo → ignorar elegantemente
    await update.message.reply_text(
        "⚠️ No estoy esperando texto ahora.\n"
        "Usa el menú OpenAI 👉",
        reply_markup=openai_menu_keyboard()
    )

    return  context.user_data.get("state")

async def openai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """El usuario escribe al chat con openAI."""
    if not context.user_data.get("awaiting_chat", False):
        return context.user_data.get("state")

    message = update.message.text.strip()

    try:
       #answer
       answer = await  openai_manager.chat(message)
       await update.message.reply_text(f"{answer}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al conectar con OpenAI:\n{e}")

    return context.user_data.get("state")