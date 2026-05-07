from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states import AddMedicine
from app.service.pill_service import create_medicine_and_reminder
from app.service.user_service import get_or_create_user


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user = await get_or_create_user(message.chat.id, message.from_user.id, message.from_user.username)
    await message.reply(f"Привет, {user.username}!")

@router.message(Command('help'))
async def help(message: Message):
    await message.reply('/help - Показать команды\n'
                        '/start - Приветствие с именем\n'
                        '/add - Добавить таблетку')

@router.message(Command('add'))
async def add_medicine_start(message: Message, state: FSMContext):
    await message.reply('Введите название таблетки:')
    await state.set_state(AddMedicine.waiting_for_name)

@router.message(AddMedicine.waiting_for_name)
async def process_medicine_name(message: Message, state: FSMContext):
    name = message.text.strip().title()
    if len(name) < 2:
        await message.answer("Название слишком короткое. Введите название таблетки ещё раз:")
        return
    await state.update_data(name=name)

    await message.answer("Введите дозировку. Например: 1 таблетка, 500 мг, 2 капсулы:")
    await state.set_state(AddMedicine.waiting_for_dosage)

@router.message(AddMedicine.waiting_for_dosage)
async def process_medicine_dosage(message: Message, state: FSMContext):
    dosage = message.text.strip()
    await state.update_data(dosage=dosage)

    await message.answer("Введите время приёма в формате ЧЧ:ММ. Например: 09:00")
    await state.set_state(AddMedicine.waiting_for_time)


@router.message(AddMedicine.waiting_for_time)
async def process_medicine_time(message: Message, state: FSMContext):
    time_text = message.text.strip()
    data = await state.get_data()

    try:
        medicine = await create_medicine_and_reminder(
            tg_id = message.from_user.id,
            pill_name = data['name'],
            dose = data['dosage'],
            str_time = time_text
        )
    except ValueError as error:
        await message.answer(str(error))
        return

    await message.answer(
        f"Готово! Добавлена:\n\n"
        f"Таблетка: {medicine.name}\n"
        f"Дозировка: {medicine.dosage}\n"
        f"Время напоминания: Ежедневно, {time_text}"
    )
    await state.clear()
