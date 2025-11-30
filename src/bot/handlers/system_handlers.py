from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot.system.controlador_sistema import SistemaController
from bot.constants.states import SYSTEM_ROUTES

sistema = SistemaController()


def system_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖥 Info del sistema", callback_data="sys_info")],
        [InlineKeyboardButton("📊 Uso CPU/RAM/Disco", callback_data="sys_usage")],
        [InlineKeyboardButton("🌡 Temperatura", callback_data="sys_temp")],
        [InlineKeyboardButton("📡 IPs", callback_data="sys_ips")],
        [InlineKeyboardButton("🔁 Reiniciar", callback_data="sys_reboot")],
        [InlineKeyboardButton("⛔ Apagar", callback_data="sys_shutdown")],
        [InlineKeyboardButton("⬅ Main Menu", callback_data="0")],
    ])


async def system_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚙️ **Menú del Sistema**", reply_markup=system_menu_keyboard(), parse_mode="Markdown")
    return SYSTEM_ROUTES


async def system_info(update, context):
    query = update.callback_query
    await query.answer()

    info = sistema.get_system_info()
    text = "\n".join([f"• *{k}:* {v}" for k, v in info.items()])

    await query.edit_message_text(f"🖥 **Información del sistema:**\n\n{text}", parse_mode="Markdown")
    await query.message.reply_text("⚙️ Menú del Sistema:", reply_markup=system_menu_keyboard())
    return SYSTEM_ROUTES


async def system_usage(update, context):
    query = update.callback_query
    await query.answer()

    usage = sistema.get_usage()
    text = (
        f"💽 **Uso actual:**\n\n"
        f"CPU: {usage['cpu_percent']}%\n"
        f"RAM: {usage['ram_percent']}%\n"
        f"Disco: {usage['disk_percent']}%"
    )

    await query.edit_message_text(text, parse_mode="Markdown")
    await query.message.reply_text("⚙️ Menú del Sistema:", reply_markup=system_menu_keyboard())
    return SYSTEM_ROUTES


async def system_temp(update, context):
    query = update.callback_query
    await query.answer()

    temp = sistema.get_temperature()
    if temp is None:
        msg = "🌡 No disponible (solo en Raspberry con `vcgencmd`)."
    else:
        msg = f"🌡 **Temperatura:** {temp}°C"

    await query.edit_message_text(msg, parse_mode="Markdown")
    await query.message.reply_text("⚙️ Menú del Sistema:", reply_markup=system_menu_keyboard())
    return SYSTEM_ROUTES


async def system_ips(update, context):
    query = update.callback_query
    await query.answer()

    local = sistema.get_ip_local()
    public = sistema.get_ip_public()

    msg = f"📡 **Direcciones IP:**\n\n🌐 Local: `{local}`\n🌍 Pública: `{public}`"
    await query.edit_message_text(msg, parse_mode="Markdown")
    await query.message.reply_text("⚙️ Menú del Sistema:", reply_markup=system_menu_keyboard())
    return SYSTEM_ROUTES


async def system_reboot(update, context):
    query = update.callback_query
    await query.answer()

    msg = sistema.reboot()
    await query.edit_message_text(msg)
    return SYSTEM_ROUTES


async def system_shutdown(update, context):
    query = update.callback_query
    await query.answer()

    msg = sistema.shutdown()
    await query.edit_message_text(msg)
    return SYSTEM_ROUTES
