import logging
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
from dotenv import load_dotenv
import sys, os

load_dotenv()

# Debug: rutas python
print("\n>> RUTAS DE PYTHON (sys.path):")
for p in sys.path:
    print("   ", p)

from bot.system.controlador_roku import RokuController

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Estados
START_ROUTES, ROKU_ROUTES, END_ROUTES = range(3)

# callback_data
START, NGROK, DOCKER, OPTION3, ROKU, END = range(6)

# Controlador Roku
roku = RokuController()


#######################################################
#                     START
#######################################################

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


async def roku_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["roku_state"] = None

    await query.edit_message_text(roku_menu_message(), reply_markup=roku_menu_keyboard())
    return ROKU_ROUTES


#######################################################
#                     KEYBOARDS
#######################################################

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Ngrok', callback_data=str(NGROK))],
        [InlineKeyboardButton('Docker', callback_data=str(DOCKER))],
        [InlineKeyboardButton('Melate', callback_data=str(OPTION3))],
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


#######################################################
#                     ACCIONES ROKU
#######################################################

async def roku_define_ip(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data["roku_state"] = "await_ip"
    await query.edit_message_text("📺 Envíame la IP de tu Roku TV:")

    return ROKU_ROUTES


async def set_roku_ip(update, context):
    ip = update.message.text.strip()
    roku.set_ip(ip)

    context.user_data["roku_state"] = None

    await update.message.reply_text(f"✅ IP configurada: {ip}")
    await update.message.reply_text(roku_menu_message(), reply_markup=roku_menu_keyboard())

    return ROKU_ROUTES


async def roku_power_on(update, context):
    query = update.callback_query
    await query.answer()

    await roku.power_on()
    await query.edit_message_text("🔌 TV Roku ENCENDIDA")

    return ROKU_ROUTES


async def roku_power_off(update, context):
    query = update.callback_query
    await query.answer()

    await roku.power_off()
    await query.edit_message_text("🛑 TV Roku APAGADA")

    return ROKU_ROUTES


async def roku_volume(update, context):
    query = update.callback_query
    await query.answer()

    await roku.volume_up()
    await query.edit_message_text("🔊 Volumen +")

    return ROKU_ROUTES


async def roku_open_app(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data["roku_state"] = "await_app"
    await query.edit_message_text("📺 Envíame el ID de la aplicación:")

    return ROKU_ROUTES


async def set_roku_app_id(update, context):
    app_id = update.message.text.strip()
    await roku.launch_app(app_id)

    context.user_data["roku_state"] = None

    await update.message.reply_text(f"▶️ Lanzando app: {app_id}")
    await update.message.reply_text(roku_menu_message(), reply_markup=roku_menu_keyboard())

    return ROKU_ROUTES


async def roku_get_apps(update, context):
    query = update.callback_query
    await query.answer()

    apps = await roku.get_apps()
    await query.edit_message_text(str(apps))

    return ROKU_ROUTES


async def roku_get_status(update, context):
    query = update.callback_query
    await query.answer()

    info = await roku.roku.query.device_info()
    await query.edit_message_text(str(info))

    return ROKU_ROUTES


#######################################################
#        ROUTER de TEXTO (SOLO para Roku)
#######################################################

async def roku_text_router(update, context):
    state = context.user_data.get("roku_state")

    if state == "await_ip":
        return await set_roku_ip(update, context)

    if state == "await_app":
        return await set_roku_app_id(update, context)

    await update.message.reply_text(" Usa los botones del menú Roku.")
    return ROKU_ROUTES


#######################################################
#                     MAIN
#######################################################

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
                CallbackQueryHandler(ngrok_menu, pattern=f"^{NGROK}$"),
                CallbackQueryHandler(docker_menu, pattern=f"^{DOCKER}$"),
                CallbackQueryHandler(roku_menu, pattern=f"^{ROKU}$"),
                CallbackQueryHandler(exit_menu, pattern=f"^{END}$"),
            ],

            ROKU_ROUTES: [
                CallbackQueryHandler(roku_define_ip, pattern="^m4_1$"),
                CallbackQueryHandler(roku_power_on,  pattern="^m4_2$"),
                CallbackQueryHandler(roku_power_off, pattern="^m4_3$"),
                CallbackQueryHandler(roku_volume,    pattern="^m4_4$"),
                CallbackQueryHandler(roku_open_app,  pattern="^m4_5$"),
                CallbackQueryHandler(roku_get_apps,  pattern="^m4_6$"),
                CallbackQueryHandler(roku_get_status, pattern="^m4_7$"),

                # Fallback texto exclusivo de Roku
                MessageHandler(filters.TEXT & ~filters.COMMAND, roku_text_router),
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
