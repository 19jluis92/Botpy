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
from bot.handlers.roku_handlers import (
    roku_menu,
    roku_menu_keyboard,
    roku_define_ip,
    roku_power_on,
    roku_power_off,
    roku_volume,
    roku_open_app,
    set_roku_app_id,
    roku_get_apps,
    roku_get_status,
    set_roku_ip,
    roku_text_router
)
from bot.handlers.ngrok_handlers import (
    ngrok_active_urls,
    ngrok_status,
    ngrok_menu_keyboard,
    ngrok_menu,
)
from bot.handlers.melate_handler import (
    melate_get_number,
    melate_menu_keyboard,
    melate_menu
)
from bot.handlers.docker_handler import (
    docker_info,
    docker_info_request,
    docker_list,
    docker_menu,
    docker_menu_keyboard,
)
from bot.handlers.system_handlers import (
    system_menu,
    system_info,
    system_usage,
    system_temp,
    system_ips,
    system_reboot,
    system_shutdown,
    system_wireless_restart,
    system_wlan_restart,
    system_wireless_sleep,
    system_wlan_sleep,
)
from bot.utils.auth import restricted
from dotenv import load_dotenv
import sys, os
from jproperties import Properties
load_dotenv()
from bot.system.controlador_roku import RokuController
from bot.system.controlador_melate import MelateController
from bot.system.controlador_ngrok import NgrokController

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Estados
START_ROUTES,NGROK_ROUTES, DOCKER_ROUTES,MELATE_ROUTES, ROKU_ROUTES, SYSTEM_ROUTES, END_ROUTES = range(7)

# callback_data
START, NGROK, DOCKER, MELATE, ROKU, SYSTEM, END = range(7)


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
#                     KEYBOARDS
#######################################################

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Ngrok', callback_data=str(NGROK))],
        [InlineKeyboardButton('Docker', callback_data=str(DOCKER))],
        [InlineKeyboardButton('Melate', callback_data=str(MELATE))],
        [InlineKeyboardButton('Roku', callback_data=str(ROKU))],
        [InlineKeyboardButton('Sistema', callback_data=str(SYSTEM_ROUTES))],
        [InlineKeyboardButton('End conversation', callback_data=str(END))]
    ])


#######################################################
#                     MESSAGES
#######################################################

def main_menu_message():
    return "Choose the option:"


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
#                     MAIN
#######################################################

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      CommandHandler("roku", roku_menu),
                      CommandHandler("melate", melate_menu),
                      CommandHandler("docker", docker_menu),],
        states={
            START_ROUTES: [
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
                CallbackQueryHandler(ngrok_menu, pattern=f"^{NGROK}$"),
                CallbackQueryHandler(docker_menu, pattern=f"^{DOCKER}$"),
                CallbackQueryHandler(melate_menu, pattern=f"^{MELATE}$"),
                CallbackQueryHandler(roku_menu, pattern=f"^{ROKU}$"),
                CallbackQueryHandler(system_menu, pattern=f"^{SYSTEM_ROUTES}$"),
                CallbackQueryHandler(exit_menu, pattern=f"^{END}$"),
                CommandHandler("roku", roku_menu),
            ],
            NGROK_ROUTES: [
                CallbackQueryHandler(ngrok_active_urls, pattern="^m1_1$"),
                CallbackQueryHandler(ngrok_status, pattern="^m1_2$"),
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
            ],
            MELATE_ROUTES: [
                CallbackQueryHandler(melate_get_number, pattern="^m3_1$"),
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
            ],
            DOCKER_ROUTES: [
                CallbackQueryHandler(docker_menu, pattern="^docker_menu$"),
                CallbackQueryHandler(docker_list, pattern="^docker_list$"),
                CallbackQueryHandler(docker_info_request, pattern="^docker_info$"),
                CallbackQueryHandler(start_over, pattern=f"^{START}$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, docker_info),
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
            SYSTEM_ROUTES: [
                CallbackQueryHandler(system_info, pattern="^sys_info$"),
                CallbackQueryHandler(system_usage, pattern="^sys_usage$"),
                CallbackQueryHandler(system_temp, pattern="^sys_temp$"),
                CallbackQueryHandler(system_ips, pattern="^sys_ips$"),
                CallbackQueryHandler(system_wireless_restart, pattern="^sys_wireless_restart$"),
                CallbackQueryHandler(system_wlan_restart, pattern="^sys_wlan_restart$"),
                CallbackQueryHandler(system_wireless_sleep, pattern="^sys_wireless_sleep$"),
                CallbackQueryHandler(system_wlan_sleep, pattern="^sys_wlan_sleep$"),
                CallbackQueryHandler(system_reboot, pattern="^sys_reboot$"),
                CallbackQueryHandler(system_shutdown, pattern="^sys_shutdown$"),
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
