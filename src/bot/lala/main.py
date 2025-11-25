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
    CommandHandler
)
from dotenv import load_dotenv
# Load .env file
load_dotenv()
import sys, os
print("\n>> RUTAS DE PYTHON (sys.path):")
for p in sys.path:
    print("   ", p)

from bot.system.controlador_roku import RokuController

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Estados
START_ROUTES, ACTIONS_ROUTES, END_ROUTES = range(3)

# callback_data
START, NGROK, DOCKER, OPTION3, ROKU, END = range(6)

# Instancia global del controlador Roku
roku = RokuController()


#########################################
#              START
#########################################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    await update.message.reply_text("I'm Lala-Bot!")
    await update.message.reply_text(main_menu_message(),
                                    reply_markup=main_menu_keyboard())

    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(main_menu_message(),
                                   reply_markup=main_menu_keyboard())
    return START_ROUTES


#########################################
#              MENÚS
#########################################

async def ngrok_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=ngrok_menu_message(),
        reply_markup=ngrok_menu_keyboard()
    )
    return START_ROUTES


async def docker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=docker_menu_message(),
        reply_markup=docker_menu_keyboard()
    )
    return START_ROUTES


# ESTA ES LA FUNCIÓN QUE ESTABA MAL
async def roku_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=roku_menu_message(),
        reply_markup=roku_menu_keyboard()
    )
    return START_ROUTES


#########################################
#           KEYBOARDS
#########################################

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('Ngrok', callback_data=str(NGROK))],
        [InlineKeyboardButton('Docker', callback_data=str(DOCKER))],
        [InlineKeyboardButton('Melate', callback_data=str(OPTION3))],
        [InlineKeyboardButton('Roku', callback_data=str(ROKU))],
        [InlineKeyboardButton('End conversation', callback_data=str(END))]
    ]
    return InlineKeyboardMarkup(keyboard)


def ngrok_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Active URLs', callback_data='m1_1')],
        [InlineKeyboardButton('status', callback_data='m1_2')],
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
        [InlineKeyboardButton('Main menu', callback_data=str(START))]
    ])


#########################################
#           MESSAGES
#########################################

def main_menu_message():
    return 'Choose the option:'


def ngrok_menu_message():
    return 'Choose the Ngrok action:'


def docker_menu_message():
    return 'Choose Docker action:'


def roku_menu_message():
    return 'Choose Roku action:'


#########################################
#           EXIT
#########################################

async def exit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("Are you sure?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data=str(END))],
        [InlineKeyboardButton("No", callback_data=str(START))]
    ]))
    return END_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("See you soon!")
    return ConversationHandler.END


#########################################
#             MAIN
#########################################

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
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
                CallbackQueryHandler(end, pattern=f"^{END}$"),
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()
