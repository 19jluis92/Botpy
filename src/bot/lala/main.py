import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ConversationHandler,CallbackQueryHandler, CallbackContext, TypeHandler,InlineQueryHandler, filters, MessageHandler, ApplicationBuilder, ApplicationBuilder, ContextTypes, CommandHandler
from uuid import uuid4
from optparse import OptionParser
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define Stages
START_ROUTES, ACTIONS_ROUTES , END_ROUTES = range(3)

# Callback data
START,NGROK, DOCKER, OPTION3,ROKU, END = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    await  update.message.reply_text("I'm a Lala-bot, please talk to me!")
    await  update.message.reply_text("User "+ user.first_name)
    await  update.message.reply_text(main_menu_message(),
                         reply_markup=main_menu_keyboard())
    return START_ROUTES

async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User on start_over function.")
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    await  query.message.reply_text("I'm a Lala-bot, please talk to me!")
    await  query.message.reply_text(main_menu_message(),
                         reply_markup=main_menu_keyboard())
    return START_ROUTES

def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')

############################ Menu Ngrok actions #########################################
async def ngrok_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User on ngrok_menu function.")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text = ngrok_menu_message(),
        reply_markup=ngrok_menu_keyboard()
    )
    return START_ROUTES

############################ Menu Docker actions #########################################
async def docker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User on docker_menu function.")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text = docker_menu_message(),
        reply_markup=docker_menu_keyboard()
    )
    return START_ROUTES

############################ Menu Docker actions #########################################
async def docker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User on roku_menu function.")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text = roku_menu_message(),
        reply_markup=roku_menu_keyboard()
    )
    return START_ROUTES

############################ Keyboards #########################################
def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Ngrok', callback_data=str(NGROK))],
              [InlineKeyboardButton('Docker', callback_data=str(DOCKER))],
              [InlineKeyboardButton('Melate', callback_data=str(OPTION3))],
              [InlineKeyboardButton('Roku', callback_data=str(ROKU))],
              [InlineKeyboardButton('End conversation', callback_data=str(END))]]
  return InlineKeyboardMarkup(keyboard)

def ngrok_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Active URLs', callback_data='m1_1')],
              [InlineKeyboardButton('status', callback_data='m1_2')],
              [InlineKeyboardButton('Main menu', callback_data=str(START))]]
  return InlineKeyboardMarkup(keyboard)

def docker_menu_keyboard():
  keyboard = [[InlineKeyboardButton('List containers', callback_data='m2_1')],
              [InlineKeyboardButton('Execute command by Id', callback_data='m2_2')],
              [InlineKeyboardButton('Main menu', callback_data=str(START))]]
  return InlineKeyboardMarkup(keyboard)

def roku_menu_keyboard():
  keyboard = [[InlineKeyboardButton('define ip', callback_data='m4_1')],
              [InlineKeyboardButton('encender', callback_data='m4_2')],
              [InlineKeyboardButton('apagar', callback_data='m4_3')],
              [InlineKeyboardButton('volumen', callback_data='m4_4')],
              [InlineKeyboardButton('aplicacion', callback_data='m4_5')],
              [InlineKeyboardButton('Main menu', callback_data=str(START))]]
  return InlineKeyboardMarkup(keyboard)

def exit_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Yess', callback_data=str(END))],
              [InlineKeyboardButton('Noo', callback_data=str(START))]]
  return InlineKeyboardMarkup(keyboard)

############################# Messages #########################################
def main_menu_message():
  return 'Choose the option in main menu:'

def ngrok_menu_message():
  return 'Choose the Ngrok action:'

def docker_menu_message():
  return 'Choose the Docker action:'

def roku_menu_message():
  return 'Choose the Roku TV action:'

def exit_menu_message():
  return 'Are you sure?'

############################# Exit menus #########################################
async def exit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("User on exit_menu function.")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text = exit_menu_message(),
        reply_markup=exit_menu_keyboard()
    )
    return END_ROUTES

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    logger.info("User  on end function.")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token('7344595591:AAGlWr7gUllCQjfclhn7JykGjinby8_QDuY').build()
    
    #asyncio.run(main())
    start_handler = CommandHandler('start', start)
    
    #application.add_handler(echo_handler)
    #application.add_handler(caps_handler)
    #application.add_handler(start_handler)
    #application.add_handler(inline_caps_handler)
    #application.add_handler(TypeHandler(Update, callback))
    #application.add_handler(CallbackQueryHandler(option1, pattern='option1'))
    
    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(START) + "$"),
                CallbackQueryHandler(ngrok_menu, pattern="^" + str(NGROK) + "$"),
                CallbackQueryHandler(docker_menu, pattern="^" + str(DOCKER) + "$"),
                CallbackQueryHandler(exit_menu, pattern="^" + str(END) + "$"),
            ],
            ACTIONS_ROUTES: [
                CallbackQueryHandler(ngrok_menu, pattern="^" + str(NGROK) + "$"),
                CallbackQueryHandler(docker_menu, pattern="^" + str(DOCKER) + "$"),
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(START) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)
    
    application.add_error_handler(error)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)