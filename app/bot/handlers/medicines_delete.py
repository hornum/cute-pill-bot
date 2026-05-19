from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.service.medicine_service import get_medicine_by_id, delete_medicine
import app.bot.keyboards as kb


router = Router()


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