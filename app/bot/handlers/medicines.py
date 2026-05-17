from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from app.bot.states import AddMedicine, EditMedicine
from app.service.pill_service import get_medicines_and_reminders_list, create_medicine_and_reminder, get_medicine_by_id, \
    delete_medicine, is_less_than_10_reminders, get_reminder_with_time, edit_med_and_reminder
import app.bot.keyboards as kb
from app.service.reminder_service import get_time_without_sec, parse_reminder_time

router = Router()


@router.message(or_f(Command("list"), F.text == 'Список таблеток'))
async def list_medicines(message: Message):
    try:
        medicines_list = await get_medicines_and_reminders_list(message.from_user.id)
    except ValueError as error:
        await message.answer(str(error))
        return

    await message.answer(f"💊 Ваши таблетки\nВыберите для управления",
                        reply_markup=kb.medicines_list_kb(medicines_list))

@router.callback_query(F.data == "back_to_list")
async def on_back_to_list(callback: CallbackQuery):
    try:
        medicines_list = await get_medicines_and_reminders_list(callback.from_user.id)
    except ValueError as error:
        await callback.message.edit_text(str(error))
        return

    await callback.message.edit_text(f"💊 Ваши таблетки\nВыберите для управления",
                        reply_markup=kb.medicines_list_kb(medicines_list))


@router.callback_query(F.data.startswith("med:"))
async def on_med_selection(callback: CallbackQuery):
    med_id = int(callback.data.split(":")[1])
    med_with_time = await get_reminder_with_time(med_id)
    await callback.message.edit_text(text=f"Что хотите сделать?\n\n"
                                          f"Название: {med_with_time["name"]}\n"
                                          f"Дозировка: {med_with_time['dosage']}\n"
                                          f"Время приёма: {med_with_time['time']}",
                                     reply_markup=kb.medicines_actions_kb(med_id))
    await callback.answer()


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
        medicine, reminder = await create_medicine_and_reminder(
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
        f"Время напоминания: Ежедневно, {get_time_without_sec(reminder.reminder_time)}",
        reply_markup=kb.main_menu
    )
    await state.clear()


@router.callback_query(F.data.startswith("delete:"))
async def on_delete_medicine(callback: CallbackQuery):
    med_id = int(callback.data.split(":")[1])
    medicine = await get_medicine_by_id(med_id)
    await callback.message.edit_text(f"Вы действительно хотите удалить {medicine.name} - {medicine.dosage}?",
                                     reply_markup=kb.delete_confirmation_kb(med_id))

@router.callback_query(F.data.startswith("conf_delete:"))
async def on_conf_delete_medicine(callback: CallbackQuery):
    med_id = int(callback.data.split(":")[1])
    await delete_medicine(med_id)
    await callback.message.edit_text("Таблетка удалена 👌")

@router.callback_query(F.data.startswith("edit_med:"))
async def on_edit_med(callback: CallbackQuery, state: FSMContext):
    med_id = int(callback.data.split(":")[1])
    await callback.message.edit_text("Что вы хотите изменить?", reply_markup=kb.change_menu_kb(med_id))
    await callback.answer()

@router.callback_query(F.data.startswith("change:"))
async def on_edit_choice(callback: CallbackQuery, state: FSMContext):
    field_to_change = callback.data.split(":")[1]
    med_id = int(callback.data.split(":")[2])

    msg_texts = {
        "name": "Введите новое название: ",
        "dosage": "Введите новую дозировку: ",
        "time": "Введите новое время: ",
    }

    await state.update_data(field=field_to_change, med_id=med_id)
    await state.set_state(EditMedicine.waiting_for_value)
    await callback.message.edit_text(msg_texts[field_to_change])
    await callback.answer()

@router.message(EditMedicine.waiting_for_value)
async def edit_medicine(message: Message, state: FSMContext):
    data = await state.get_data()
    field_to_change = data['field']
    med_id = int(data['med_id'])
    value = message.text.strip()

    new_values_list = await edit_med_and_reminder(medicine_id=med_id, change_param=field_to_change, value=value)

    await message.answer(text="Напоминание изменено!\n\n"
                                 f"{new_values_list['name']}\n"
                              f"{new_values_list['dosage']}"
                              f"\n{get_time_without_sec(new_values_list['time'])}")
    await state.clear()

