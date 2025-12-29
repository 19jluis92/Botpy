import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from bot.constants.states import TAPO_ROUTES
from bot.system.tapo_manager import TapoManager

async def tapo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📸 Ver Entrada", callback_data="tapo_snapshot_entrada")],
        [InlineKeyboardButton("📸 Ver patio", callback_data="tapo_snapshot_patio")]
    ]

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "📷 Cámaras Tapo",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TAPO_ROUTES

async def tapo_snapshot_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tapo_manager = TapoManager()
    query = update.callback_query
    await query.answer()
    try:

        path = tapo_manager.capture_zone("Entrada")

        await query.message.reply_photo(
            photo=open(path, "rb"),
            caption=f"📷 Cámara: Entrada"
            )
        
        delete_image(path)
    except Exception as e:
        await query.edit_message_text(f"❌ Error al capturar imagen:\n{e}")

async def tapo_snapshot_patio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tapo_manager = TapoManager()
    query = update.callback_query
    await query.answer()
    try:

        path = tapo_manager.capture_zone("Patio")

        await query.message.reply_photo(
            photo=open(path, "rb"),
            caption=f"📷 Cámara: Patio"
            )
        
        delete_image(path)
    except Exception as e:
        await query.edit_message_text(f"❌ Error al capturar imagen:\n{e}")


def delete_image(path: str):
    # borrar después de enviar
    if os.path.exists(path):
        os.remove(path)
