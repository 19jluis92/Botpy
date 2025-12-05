from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot.system.controlador_ngrok import NgrokController
from bot.constants.states import NGROK_ROUTES

ngrok = NgrokController()

def ngrok_menu_message():
    return "Choose the Ngrok action:"

async def ngrok_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Si viene de botón
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        # Si viene del comando /ngrok
        message = update.message

    context.user_data["ngrok_state"] = None

    await message.reply_text(
        ngrok_menu_message(),
        reply_markup=ngrok_menu_keyboard()
    )

    return NGROK_ROUTES


def ngrok_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Active URLs', callback_data='m1_1')],
        [InlineKeyboardButton('Status', callback_data='m1_2')],
        [InlineKeyboardButton('Main menu', callback_data='0')]
    ])



# ========================
#   NGROK — LISTAR URLS ACTIVAS
# ========================

async def ngrok_active_urls(update, context):
    query = update.callback_query
    await query.answer()

    try:
        urls = ngrok.get_public_urls()
        if not urls:
            msg = "❌ No hay túneles activos."
        else:
            msg = "🌐 **Ngrok URLs activas:**\n\n" + "\n".join(f"- {u}" for u in urls)

    except Exception as e:
        msg = f"⚠️ Error obteniendo URLs:\n{e}"

    await query.edit_message_text(msg, parse_mode="Markdown")
    return NGROK_ROUTES

# ========================
#   NGROK — STATUS
# ========================

async def ngrok_status(update, context):
    query = update.callback_query
    await query.answer()

    try:
        status = ngrok.list_tunnels()
        msg = f"📊 **Ngrok Status:**\n```\n{status}\n```"
    except Exception as e:
        msg = f"⚠️ Error obteniendo status:\n{e}"

    await query.edit_message_text(msg, parse_mode="Markdown")
    return NGROK_ROUTES



