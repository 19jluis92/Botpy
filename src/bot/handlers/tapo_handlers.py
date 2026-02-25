import logging
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from bot.constants.states import TAPO_ROUTES
from bot.system.tapo_object_detector import ObjectDetector

logger = logging.getLogger(__name__)

async def tapo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Accediendo al menú Tapo")
    context.user_data["state"] = TAPO_ROUTES
    keyboard = [
        [InlineKeyboardButton("📸 Ver Entrada", callback_data="tapo_snapshot_entrada")],
        [InlineKeyboardButton("📸 Ver patio", callback_data="tapo_snapshot_patio")],
        [InlineKeyboardButton("📸 Habilitar Detección", callback_data="tapo_motion_detector_on")],
        [InlineKeyboardButton("📸 Desactivar Detección", callback_data="tapo_motion_detector_off")],
        [InlineKeyboardButton("📸 Habilitar/Desactivar Entrada", callback_data="tapo_motion_detector_entrada")],
        [InlineKeyboardButton("📸 Habilitar/Desactivar patio", callback_data="tapo_motion_detector_patio")],
        [InlineKeyboardButton('Main menu', callback_data='0')]
    ]

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "📷 Cámaras Tapo",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TAPO_ROUTES

async def tapo_snapshot_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"tapo_snapshot_entrada called")
    query = update.callback_query
    await query.answer()
    try:

        path = context.application.bot_data["tapo_manager"].capture_zone("Entrada")
        if path is None:
                await query.message.reply_text(
                "❌ No se pudo conectar con la cámara de la entrada."
                )
        else:
            await query.message.reply_photo(
                photo=open(path, "rb"),
                caption=f"📷 Cámara: Entrada"
                )
        
        delete_image(path)
    except Exception as e:
        logger.error(f"tapo_snapshot_entrada exception:\n{e}")
        await query.edit_message_text(f"❌ Error al capturar imagen:\n{e}")

async def tapo_motion_detector_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"tapo_motion_detector_off called")
    query = update.callback_query
    await query.answer()
    try:
        context.application.bot_data["tapo_manager"].notifications_enabled = False
        context.application.bot_data["tapo_manager"].detectors[1]["enabled"] = False
        context.application.bot_data["tapo_manager"].detectors[0]["enabled"] = False
        await query.message.reply_text("🔕 Notificaciones de detección DESACTIVADAS")
    except Exception as e:
        logger.error(f"tapo_motion_detector_off exception:\n{e}")
        await query.edit_message_text(f"❌ Error al DESACTIVADAR:\n{e}")

async def tapo_motion_detector_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"tapo_motion_detector_on called")
    query = update.callback_query
    await query.answer()
    try:
        context.application.bot_data["tapo_manager"].notifications_enabled = True
        context.application.bot_data["tapo_manager"].detectors[1]["enabled"] = True
        context.application.bot_data["tapo_manager"].detectors[0]["enabled"] = True
        context.application.bot_data["tapo_manager"].reset()
        await query.message.reply_text("🔔 Notificaciones de detección ACTIVADAS")
    except Exception as e:
        logger.error(f"tapo_motion_detector_on exception:\n{e}")
        await query.edit_message_text(f"❌ Error al encender:\n{e}")

async def tapo_motion_detector_patio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"tapo_motion_detector_patio called")
    query = update.callback_query
    await query.answer()
    try:
        state = context.application.bot_data["tapo_manager"].detectors[1]["enabled"]
        context.application.bot_data["tapo_manager"].detectors[1]["enabled"] = not state
        await query.edit_message_text(f"✅ Detección de Patio {'ACTIVADA' if not state else 'DESACTIVADA'}")
    except Exception as e:
        logger.error(f"tapo_motion_detector_patio exception:\n{e}")
        await query.edit_message_text(f"❌ Error al Activar/Desactivar patio:\n{e}")

async def tapo_motion_detector_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"tapo_motion_detector_entrada called")
    query = update.callback_query
    await query.answer()
    try:
        state = context.application.bot_data["tapo_manager"].detectors[0]["enabled"]
        context.application.bot_data["tapo_manager"].detectors[0]["enabled"] = not state
        await query.edit_message_text(f"✅ Detección de Entrada {'ACTIVADA' if not state else 'DESACTIVADA'}")
    except Exception as e:
        logger.error(f"tapo_motion_detector_entrada exception:\n{e}")
        await query.edit_message_text(f"❌ Error al Activar/Desactivar entrada:\n{e}")

async def tapo_snapshot_patio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"tapo_snapshot_patio called")
    query = update.callback_query
    await query.answer()
    try:

        path = context.application.bot_data["tapo_manager"].capture_zone("Patio")
        if path is None:
                await query.message.reply_text(
                "❌ No se pudo conectar con la cámara del patio."
                )
        else:
            await query.message.reply_photo(
                photo=open(path, "rb"),
                caption=f"📷 Cámara: Patio"
                )
        
        delete_image(path)
    except Exception as e:
        logger.error(f"tapo_snapshot_patio exception:\n{e}")
        await query.edit_message_text(f"❌ Error al capturar imagen:\n{e}")


def delete_image(path: str):
    # borrar después de enviar
    if os.path.exists(path):
        os.remove(path)
