from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot.states import AddMedicine, EditMedicine
from app.service.pill_service import edit_med_and_reminder
import app.bot.keyboards as kb
from app.service.reminder_service import get_time_without_sec, delete_all_reminders


router = Router()


@router.callback_query(F.data.startswith("edit_med:"))
async def on_edit_med(callback: CallbackQuery, state: FSMContext):
    med_id = int(callback.data.split(":")[1])
    await callback.message.edit_text("Что вы хотите изменить?", reply_markup=kb.change_menu_kb(med_id))
    await callback.answer()

@router.callback_query(F.data.startswith("change:time:"))
async def on_edit_times(callback: CallbackQuery, state: FSMContext):
    med_id = int(callback.data.split(":")[2])
    await delete_all_reminders(med_id)
    await state.clear()
    await state.update_data(med_id=med_id, times=[], editing=True)
    await state.set_state(AddMedicine.waiting_for_time)
    await callback.message.edit_text("Введите новое время приёма в формате ЧЧ:ММ:")
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
                              f"\n{get_time_without_sec(new_values_list['time'])}", reply_markup=kb.main_menu_kb)
    await state.clear()
