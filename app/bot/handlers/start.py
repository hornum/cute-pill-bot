from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.service.user_service import get_or_create_user
from app.config import HELP_COMMAND_TEXT as HELP_TEXT
import app.bot.keyboards as kb


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user = await get_or_create_user(message.chat.id, message.from_user.id, message.from_user.username)

    await message.reply(
        f"Привет, {message.from_user.first_name}!\n\n"
        f"Этот бот будет присылать тебе напоминания о приёме таблеток.\n\n"
        f"Чтобы начать, добавь хотя бы одну таблетку командой /add или через кнопки меню.\n\n"
        f"❗️❗️ ВАЖНО: "
        f"Сейчас в боте отсутствует выбор часового пояса, поэтому все напоминания работают по МОСКОВСКОМУ ВРЕМЕНИ\n\n"
        f"Основные команды:\n\n{HELP_TEXT}",
        reply_markup=kb.main_menu
    )

@router.message(Command('help'))
async def bot_help(message: Message):
    await message.reply(HELP_TEXT)