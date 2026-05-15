from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, )


delete_confirmation = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅"), KeyboardButton(text="❌")]
], resize_keyboard=True, one_time_keyboard=True)

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить таблетку"), KeyboardButton(text="Список таблеток")],
], resize_keyboard=True)

def pill_confirmation(reminder_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принял", callback_data=f"taken:{reminder_id}"),
        InlineKeyboardButton(text="❌ Пропустить приём", callback_data=f"skipped:{reminder_id}")
    ],
    [
        InlineKeyboardButton(text="⏳ Отложить на 15 минут", callback_data=f"snooze:{reminder_id}")
    ]]
    )

def medicines_list_kb(medicines: list) -> InlineKeyboardMarkup:
    buttons = []

    for medicine in medicines:
        buttons.append([
            InlineKeyboardButton(
                text=f"{medicine["name"]} - {medicine["dosage"]}", callback_data=f"med:{medicine["id"]}")
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def medicines_actions_kb(med_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить время", callback_data=f"edit_time:{med_id}")
         ,InlineKeyboardButton(text="Удалить таблетку", callback_data=f"delete:{med_id}")],
        [InlineKeyboardButton(text="Назад к списку", callback_data=f"back_to_list")],
    ])

def delete_confirmation_kb(med_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅", callback_data=f"conf_delete:{med_id}"),
         InlineKeyboardButton(text="❌", callback_data=f"back_to_list")],
    ])