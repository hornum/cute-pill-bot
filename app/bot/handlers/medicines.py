from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.bot.states import AddMedicine, DeleteMedicine
from app.service.pill_service import get_medicines_and_reminders_list, create_medicine_and_reminder, get_medicine_by_id, \
    delete_medicine, is_less_than_10_reminders, get_reminder_with_time
import app.bot.keyboards as kb

router = Router()


@router.message(or_f(Command("list"), F.text == 'Список таблеток'))
async def list_medicines(message: Message):
    medicines_list = await get_medicines_and_reminders_list(message.from_user.id)

    if not medicines_list:
        await message.answer("Вы пока не добавили таблетки")
        return

    lines = []

    for medicine in medicines_list:
        lines.append(f"ID: {medicine["id"]}, {medicine["name"]} - {medicine["dosage"]}\n"
                     f"Время приёма: {medicine["reminder_time"]};")

    answer_text = "\n------\n".join(lines)

    await message.answer(f"Ваши таблетки:\n\n{answer_text}")


@router.message(or_f(Command('add'), F.text == '➕ Добавить таблетку'))
async def add_medicine_start(message: Message, state: FSMContext):
    if await is_less_than_10_reminders(message.from_user.id):
        await message.reply('Введите название таблетки:', reply_markup=ReplyKeyboardRemove())
        await state.set_state(AddMedicine.waiting_for_name)
    else:
        await message.reply("Вы достигли максимума таблеток! (10 штук)\nСперва удалите другую таблетку.")

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
        f"Время напоминания: Ежедневно, {time_text}",
        reply_markup=kb.main_menu
    )
    await state.clear()


@router.message(or_f(Command('delete'), F.text == '🗑 Удалить таблетку'))
async def delete_medicine_start(message: Message, state: FSMContext):
    await message.reply('Введите ID таблетки, которую хотите удалить.'
                        'Посмотреть ID можно в списке таблеток  командой /list',
                        reply_markup=ReplyKeyboardRemove()
                        )
    await state.set_state(DeleteMedicine.waiting_for_id)


@router.message(DeleteMedicine.waiting_for_id)
async def delete_medicine_confirmation(message: Message, state: FSMContext):

    medicine_id = message.text.replace('ID', '').replace('id', '').strip()

    try:
        medicine_id = int(medicine_id)
    except ValueError:
        await message.answer("Неверный формат ID! Введите число.")
        return

    medicine = await get_medicine_by_id(medicine_id)

    if not medicine:
        await message.answer("Таблетка с этим ID не найдена, введите корректный ID.")
        return

    await state.update_data(medicine_id=medicine_id)

    await message.answer(f"Вы действительно хотите удалить таблетку?\n{medicine.name}, {medicine.dosage}?"
                         f"\n\nВыберите на клавиатуре или отправьте смайлик ✅/❌",
                         reply_markup=kb.delete_confirmation
                         )

    await state.set_state(DeleteMedicine.waiting_for_confirmation)

@router.message(DeleteMedicine.waiting_for_confirmation)
async def delete_medicine_confirmation(message: Message, state: FSMContext):
    answer = message.text

    if answer == "✅":
        data = await state.get_data()
        await delete_medicine(data["medicine_id"])
        await message.answer("Таблетка удалена!", reply_markup=kb.main_menu)

    elif answer == "❌":
        await state.clear()
        await message.answer("Окей! Удаление отменено.", reply_markup=kb.main_menu)
