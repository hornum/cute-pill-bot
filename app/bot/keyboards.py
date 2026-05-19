from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, )


main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить таблетку"), KeyboardButton(text="Список таблеток")],
], resize_keyboard=True)

add_more_time_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить ещё время", callback_data="add_more_time")],
    [InlineKeyboardButton(text="✅ Готово", callback_data="finish_times")],
])

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

def medicines_actions_kb(med_id: int, is_active: bool) -> InlineKeyboardMarkup:
    if is_active:
        change_status_str = "Отключить напоминания ❌"
    else:
        change_status_str = "Включить напоминания ✅"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить напоминание", callback_data=f"edit_med:{med_id}")],

        [InlineKeyboardButton(text=change_status_str, callback_data=f"change_active_status:{med_id}")],

        [InlineKeyboardButton(text="Удалить таблетку", callback_data=f"delete:{med_id}"),
        InlineKeyboardButton(text="Назад к списку", callback_data=f"back_to_list")],
    ])


def delete_confirmation_kb(med_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅", callback_data=f"conf_delete:{med_id}"),
         InlineKeyboardButton(text="❌", callback_data=f"back_to_list")],
    ])


def change_menu_kb(med_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Название", callback_data=f"change:name:{med_id}"),],
        [InlineKeyboardButton(text="💊 Дозировку", callback_data=f"change:dosage:{med_id}")],
        [InlineKeyboardButton(text="⏰ Время приёма", callback_data=f"change:time:{med_id}")],
    ])
