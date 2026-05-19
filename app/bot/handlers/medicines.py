from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from app.bot.states import AddMedicine
from app.service.medicine_service import get_medicines_and_reminders_list, create_medicine_and_reminders, \
    is_less_than_10_reminders, get_reminder_with_time
import app.bot.keyboards as kb
from app.service.reminder_service import parse_reminder_time, add_reminders_to_medicine


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
    times_str = ", ".join(r for r in med_with_time["times"])
    med_status_str = "Включены ✅" if med_with_time["is_active"] else "Отключены ❌"
    await callback.message.edit_text(text=f"Что хотите сделать?\n\n"
                                          f"Название: {med_with_time["name"]}\n"
                                          f"Дозировка: {med_with_time['dosage']}\n"
                                          f"Время приёма: {times_str}\n"
                                          f"Статус напоминаний: {med_status_str}",
                                     reply_markup=kb.medicines_actions_kb(med_id, med_with_time["is_active"]))
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
    time_text = message.text.strip().replace('.', ':')

    try:
        parsed_time = parse_reminder_time(time_text)
        output_time = parsed_time.strftime("%H:%M")
    except ValueError as error:
        await message.answer(str(error))
        return

    data = await state.get_data()
    times = data.get("times", [])
    times.append(time_text)
    await state.update_data(times=times)

    await message.answer(
        f"Время {output_time} добавлено! Всего напоминаний: {len(times)}\n"
        f"Хотите добавить ещё одно?",
        reply_markup=kb.add_more_time_kb
    )

    await state.set_state(AddMedicine.waiting_for_more_time)


@router.callback_query(F.data == "add_more_time")
async def on_add_more_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите следующее время в формате ЧЧ:ММ")
    await state.set_state(AddMedicine.waiting_for_time)
    await callback.answer()

@router.callback_query(F.data == "finish_times")
async def on_finish_times(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    times = data["times"]
    editing = data.get("editing", False)

    if editing:
        med_id = data["med_id"]
        reminders = await add_reminders_to_medicine(med_id, times)
        times_str = ", ".join(r.reminder_time.strftime("%H:%M") for r in reminders)
        await callback.message.edit_text(f"✅ Время обновлено: {times_str}")
        await callback.message.answer("Выберите действие:", reply_markup=kb.main_menu_kb)

    else:
        try:
            medicine, reminders = await create_medicine_and_reminders(
                tg_id=callback.from_user.id,
                pill_name=data["name"],
                dose=data["dosage"],
                times=times
            )
        except ValueError as error:
            await callback.message.edit_text(str(error))
            return

        times_str = ", ".join(r.reminder_time.strftime("%H:%M") for r in reminders)
        await callback.message.edit_text(
            f"✅ Готово! Добавлена:\n\n"
            f"Таблетка: {medicine.name}\n"
            f"Дозировка: {medicine.dosage}\n"
            f"Время напоминаний: {times_str}"
        )
        await callback.message.answer("Выберите действие:", reply_markup=kb.main_menu_kb)

    await callback.answer()
    await state.clear()
