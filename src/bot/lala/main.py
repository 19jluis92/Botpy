import logging
import json
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
from bot.utils.auth import restricted
from dotenv import load_dotenv
import sys, os
from jproperties import Properties
load_dotenv()
from bot.system.controlador_roku import RokuController
from bot.system.controlador_melate import MelateController
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Estados
START_ROUTES,NGROK_ROUTES, MELATE_ROUTES, DOCKER_ROUTES, ROKU_ROUTES, END_ROUTES = range(6)

# callback_data
START, NGROK, DOCKER, MELATE, ROKU, END = range(6)

# Controlador Roku
roku = RokuController()

# Controlador Melate
melate = MelateController()


#######################################################
#                     START
#######################################################
@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    await update.message.reply_text("I'm Lala-Bot!")
    await update.message.reply_text(main_menu_message(), reply_markup=main_menu_keyboard())

    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(main_menu_message(), reply_markup=main_menu_keyboard())
    return START_ROUTES


#######################################################
#                     MENÚS
#######################################################

async def ngrok_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(ngrok_menu_message(), reply_markup=ngrok_menu_keyboard())
    return START_ROUTES


async def docker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(docker_menu_message(), reply_markup=docker_menu_keyboard())
    return START_ROUTES

async def melate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(melate_menu_message(), reply_markup=melate_menu_keyboard())
    return MELATE_ROUTES


async def roku_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


#######################################################
#                     KEYBOARDS
#######################################################

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Ngrok', callback_data=str(NGROK))],
        [InlineKeyboardButton('Docker', callback_data=str(DOCKER))],
        [InlineKeyboardButton('Melate', callback_data=str(MELATE))],
        [InlineKeyboardButton('Roku', callback_data=str(ROKU))],
        [InlineKeyboardButton('End conversation', callback_data=str(END))]
    ])


def ngrok_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Active URLs', callback_data='m1_1')],
        [InlineKeyboardButton('Status', callback_data='m1_2')],
        [InlineKeyboardButton('Main menu', callback_data=str(START))]
    ])


def docker_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('List containers', callback_data='m2_1')],
        [InlineKeyboardButton('Execute by Id', callback_data='m2_2')],
        [InlineKeyboardButton('Main menu', callback_data=str(START))]
    ])

def melate_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Dame el numero', callback_data='m3_1')],
        [InlineKeyboardButton('Main menu', callback_data=str(START))]
    ])


def roku_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Define IP', callback_data='m4_1')],
        [InlineKeyboardButton('Encender', callback_data='m4_2')],
        [InlineKeyboardButton('Apagar', callback_data='m4_3')],
        [InlineKeyboardButton('Volumen', callback_data='m4_4')],
        [InlineKeyboardButton('Aplicación', callback_data='m4_5')],
        [InlineKeyboardButton('Mostrar Aplicaciones', callback_data='m4_6')],
        [InlineKeyboardButton('Mostrar Información de TV', callback_data='m4_7')],
        [InlineKeyboardButton('Main menu', callback_data=str(START))]
    ])


#######################################################
#                     MESSAGES
#######################################################

def main_menu_message():
    return "Choose the option:"

def ngrok_menu_message():
    return "Choose the Ngrok action:"

def docker_menu_message():
    return "Choose Docker action:"

def melate_menu_message():
    return "Choose Melate action:"

def roku_menu_message():
    return "Choose Roku action:"


#######################################################
#                     EXIT
#######################################################

async def exit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data=str(END))],
            [InlineKeyboardButton("No", callback_data=str(START))]
        ])
    )
    return END_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("See you soon!")
    return ConversationHandler.END


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

    try:
        await roku.volume_up()  # ajusta según quieras
        msg = "🔊 Volumen ajustado"
    except Exception as e:
        msg = f"❌ Error con el volumen:\n{e}"

    await query.edit_message_text(msg)
    await query.message.reply_text("📺 Menú Roku:", reply_markup=roku_menu_keyboard())
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

    # Si llega texto sin esperarlo → ignorar elegantemente
    await update.message.reply_text(
        "⚠️ No estoy esperando texto ahora.\n"
        "Usa el menú Roku 👉",
        reply_markup=roku_menu_keyboard()
    )

    return ROKU_ROUTES

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
    return MELATE_ROUTES


#######################################################
#                     MAIN
#######################################################

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      CommandHandler("roku", roku_menu),],
        states={
            START_ROUTES: [
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
                CallbackQueryHandler(ngrok_menu, pattern=f"^{NGROK}$"),
                CallbackQueryHandler(docker_menu, pattern=f"^{DOCKER}$"),
                CallbackQueryHandler(melate_menu, pattern=f"^{MELATE}$"),
                CallbackQueryHandler(roku_menu, pattern=f"^{ROKU}$"),
                CallbackQueryHandler(exit_menu, pattern=f"^{END}$"),
                CommandHandler("roku", roku_menu),
            ],
            NGROK_ROUTES: [
                #CallbackQueryHandler(roku_define_ip, pattern="^m4_1$"),
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
            ],
            DOCKER_ROUTES: [
                #CallbackQueryHandler(roku_define_ip, pattern="^m4_1$"),
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
            ],
            MELATE_ROUTES: [
                CallbackQueryHandler(melate_get_number, pattern="^m3_1$"),
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
            ],
            ROKU_ROUTES: [
                CallbackQueryHandler(roku_define_ip, pattern="^m4_1$"),
                CallbackQueryHandler(roku_power_on,  pattern="^m4_2$"),
                CallbackQueryHandler(roku_power_off, pattern="^m4_3$"),
                CallbackQueryHandler(roku_volume,    pattern="^m4_4$"),
                CallbackQueryHandler(roku_open_app,  pattern="^m4_5$"),
                CallbackQueryHandler(roku_get_apps,  pattern="^m4_6$"),
                CallbackQueryHandler(roku_get_status, pattern="^m4_7$"),
                # 🔥 IMPORTANTE: Handlers para texto (IP y AppID)
                MessageHandler(filters.TEXT & ~filters.COMMAND, roku_text_router),

                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
            ],

            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
                CallbackQueryHandler(end, pattern=f"^{END}$"),
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()
