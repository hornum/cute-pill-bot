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
        f"Привет, {user.username}!\n\nЧто этот бот может:\n\n{HELP_TEXT}",
        reply_markup=kb.main_menu
    )

@router.message(Command('help'))
async def bot_help(message: Message):
    await message.reply(HELP_TEXT)