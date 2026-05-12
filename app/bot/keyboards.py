from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, )


delete_confirmation = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅"), KeyboardButton(text="❌")]
], resize_keyboard=True, one_time_keyboard=True)

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить таблетку")],
    [KeyboardButton(text="Список таблеток"), KeyboardButton(text="🗑 Удалить таблетку")]
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
