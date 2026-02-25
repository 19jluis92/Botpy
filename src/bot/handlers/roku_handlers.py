
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot.system.controlador_roku import RokuController
from bot.constants.states import ROKU_ROUTES
import json

roku = RokuController()

def roku_menu_message():
    return "Choose Roku action:"


async def roku_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = ROKU_ROUTES
    # Si viene de botón
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        # Si viene del comando /roku
        message = update.message

    context.user_data["roku_state"] = None

    await message.reply_text(
        roku_menu_message(),
        reply_markup=roku_menu_keyboard()
    )

    return ROKU_ROUTES


def roku_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Define IP', callback_data='m4_1')],
        [InlineKeyboardButton('Encender', callback_data='m4_2')],
        [InlineKeyboardButton('Apagar', callback_data='m4_3')],
        [InlineKeyboardButton('Volumen', callback_data='m4_4')],
        [InlineKeyboardButton('Aplicación', callback_data='m4_5')],
        [InlineKeyboardButton('Mostrar Aplicaciones', callback_data='m4_6')],
        [InlineKeyboardButton('Mostrar Información de TV', callback_data='m4_7')],
        [InlineKeyboardButton('Main menu', callback_data='0')]
    ])

# ========================
#   ROKU — DEFINIR IP
# ========================

async def roku_define_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """El usuario presiona 'Define IP' → pedir IP."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("📡 Envíame la IP de tu Roku TV:")
    context.user_data["awaiting_ip"] = True

    return ROKU_ROUTES


async def set_roku_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """El usuario escribe la IP → guardar, conectar y regresar al menú Roku."""
    if not context.user_data.get("awaiting_ip", False):
        return ROKU_ROUTES

    ip = update.message.text.strip()
    roku.set_ip(ip)
    context.user_data["awaiting_ip"] = False

    await update.message.reply_text(f"🔧 IP configurada: {ip}\nIntentando conectar...")

    try:
        await roku.connect()
        await update.message.reply_text("✅ Conectado correctamente a Roku.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al conectar con Roku:\n{e}")

    await update.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES



# ========================
#   ROKU — ENCENDER
# ========================

async def roku_power_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await roku.power_on()
        msg = "🔌 TV Roku **ENCENDIDA**"
    except Exception as e:
        msg = f"❌ Error al encender:\n{e}"

    await query.edit_message_text(msg)
    await query.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES



# ========================
#   ROKU — APAGAR
# ========================

async def roku_power_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await roku.power_off()
        msg = "🔌 TV Roku **APAGADA**"
    except Exception as e:
        msg = f"❌ Error al apagar:\n{e}"

    await query.edit_message_text(msg)
    await query.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES



# ========================
#   ROKU — AJUSTAR VOLUMEN
# ========================

async def roku_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("📺 Envíame el *Volumen*:")
    context.user_data["awaiting_roku_volume"] = True
    return ROKU_ROUTES


async def set_roku_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_roku_volume", False):
        return ROKU_ROUTES

    volumen_value =int( update.message.text.strip())
    context.user_data["awaiting_roku_volume"] = False

    try:
        if volumen_value >=1:
            await roku.volume_up(volumen_value)  # ajusta según quieras
        else:
            await roku.volume_down(abs(volumen_value))  # ajusta según quieras
        msg = "🔊 Volumen ajustado"
    except Exception as e:
        msg = f"❌ Error con el volumen:\n{e}"

    await update.message.reply_text(msg, parse_mode="Markdown")
    await update.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES



# ========================
#   ROKU — ABRIR APLICACIÓN
# ========================

async def roku_open_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("📺 Envíame el *ID de la aplicación*:")
    context.user_data["awaiting_appId"] = True
    return ROKU_ROUTES


async def set_roku_app_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_appId", False):
        return ROKU_ROUTES

    app_id = update.message.text.strip()
    context.user_data["awaiting_appId"] = False

    try:
        await roku.launch_app(app_id)
        msg = f"📺 Aplicación lanzada: `{app_id}`"
    except Exception as e:
        msg = f"❌ No se pudo abrir la aplicación:\n{e}"

    await update.message.reply_text(msg, parse_mode="Markdown")
    await update.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES



# ========================
#   ROKU — LISTAR APPS
# ========================

async def roku_get_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        apps = await roku.get_apps()
        pretty = "\n".join([
            f"- {a.get('#text', 'Sin nombre')} (ID: {a.get('@id', 'N/A')})"
            for a in apps
        ])
        msg = f"📦 **Aplicaciones instaladas:**\n\n{pretty}"
    except Exception as e:
        msg = f"❌ Error al obtener aplicaciones:\n{e}"

    await query.edit_message_text(msg, parse_mode="Markdown")
    await query.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES



# ========================
#   ROKU — STATUS DEL DISPOSITIVO
# ========================

async def roku_get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        info = await roku.get_device_info()
        keys = ["friendly-model-name", "model-name", "power-mode"]
        filtered = {k: info[k] for k in keys if k in info}
        pretty = json.dumps(filtered, indent=4)
        msg = f"📺 **Información del dispositivo:**\n\n{pretty}"
    except Exception as e:
        msg = f"❌ Error al obtener información:\n{e}"

    await query.edit_message_text(msg, parse_mode="Markdown")
    await query.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES

async def roku_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Si estamos esperando IP
    if context.user_data.get("awaiting_ip", False):
        return await set_roku_ip(update, context)

    # Si estamos esperando un AppID
    if context.user_data.get("awaiting_appId", False):
        return await set_roku_app_id(update, context)
    
    # Si estamos esperando un Volumen
    if context.user_data.get("awaiting_roku_volume", False):
        return await set_roku_volume(update, context)

    # Si llega texto sin esperarlo → ignorar elegantemente
    await update.message.reply_text(
        "⚠️ No estoy esperando texto ahora.\n"
        "Usa el menú Roku 👉",
        reply_markup=roku_menu_keyboard()
    )

    return ROKU_ROUTES
