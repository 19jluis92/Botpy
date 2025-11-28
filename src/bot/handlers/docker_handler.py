from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def docker_menu_message():
    return "Choose Docker action:"

def docker_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('List containers', callback_data='m2_1')],
        [InlineKeyboardButton('Execute by Id', callback_data='m2_2')],
        [InlineKeyboardButton('Main menu', callback_data=str(0))]
    ])

async def docker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(docker_menu_message(), reply_markup=docker_menu_keyboard())
    return 2
