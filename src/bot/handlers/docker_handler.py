import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

from bot.system.controlador_docker import DockerController

logger = logging.getLogger(__name__)

# Estados propios del módulo Docker
DOCKER_ROUTES = 20

# Instancia global del controlador
docker = DockerController()


# ================================
#         MENÚ DOCKER
# ================================

def docker_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Listar contenedores", callback_data="docker_list")],
        [InlineKeyboardButton("Detalles por ID", callback_data="docker_info")],
        [InlineKeyboardButton("Iniciar por ID", callback_data="docker_start")],
        [InlineKeyboardButton("Detener por ID", callback_data="docker_stop")],
        [InlineKeyboardButton("Reiniciar por ID", callback_data="docker_restart")],
        [InlineKeyboardButton("Volver al menú", callback_data="main_menu")]
    ])


async def docker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "🐳 **Menú Docker:**",
            reply_markup=docker_menu_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🐳 **Menú Docker:**",
            reply_markup=docker_menu_keyboard(),
            parse_mode="Markdown"
        )

    return DOCKER_ROUTES


# ================================
#      LISTAR CONTENEDORES
# ================================

async def docker_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        containers = docker.list_containers()
        text = "\n".join([
            f"- `{c['id'][:12]}` | {c['name']} | {c['status']}"
            for c in containers
        ]) or "No hay contenedores."

        await query.edit_message_text(
            f"🐳 **Contenedores:**\n\n{text}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Error:\n```\n{e}\n```", parse_mode="Markdown")

    await query.message.reply_text("🐳 Volver:", reply_markup=docker_menu_keyboard())
    return DOCKER_ROUTES


# ================================
#        DETALLES POR ID
# ================================

async def docker_info_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["awaiting_docker_info"] = True
    await query.edit_message_text("🔍 Envíame el **ID** del contenedor:")

    return DOCKER_ROUTES


async def docker_info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("awaiting_docker_info"):
        return DOCKER_ROUTES

    container_id = update.message.text.strip()
    context.user_data["awaiting_docker_info"] = False

    try:
        info = docker.container_info(container_id)
        await update.message.reply_text(
            f"📄 **Información:**\n```\n{info}\n```",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{e}")

    await update.message.reply_text("🐳 Menú Docker:", reply_markup=docker_menu_keyboard())
    return DOCKER_ROUTES


# ================================
#         AÑADIR AL CONV HANDLER
# ================================

def docker_handlers():
    return [
        CallbackQueryHandler(docker_menu, pattern="^docker_menu$"),
        CallbackQueryHandler(docker_list, pattern="^docker_list$"),
        CallbackQueryHandler(docker_info_request, pattern="^docker_info$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, docker_info),
    ]
