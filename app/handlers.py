from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.reply(f"Привет, {message.from_user.first_name}!")

@router.message(Command('help'))
async def help(message: Message):
    await message.reply('/help - Показать команды\n'
                        '/start - Приветствие с именем\n'
                        '/add - Пока просто принимает текст')

@router.message(Command('add'))
async def add(message: Message):
    await message.reply('Введите название таблетки')
