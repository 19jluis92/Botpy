from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot.system.controlador_melate import MelateController

melate = MelateController()
def melate_menu_message():
    return "Choose Melate action:"

async def melate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(melate_menu_message(), reply_markup=melate_menu_keyboard())
    return 3


def melate_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Dame el numero', callback_data='m3_1')],
        [InlineKeyboardButton('Main menu', callback_data=str(0))]
    ])



# ========================
#   MELATE — DAME UN NUMERO
# ========================

async def melate_get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        msg = await melate.get_recommended_number()
    except Exception as e:
        msg = f"❌ Error al obtener el numero:\n{e}"

    await query.edit_message_text(msg, parse_mode="Markdown")
    await query.message.reply_text("Numero recomendado:", reply_markup=melate_menu_keyboard())
    return 3
