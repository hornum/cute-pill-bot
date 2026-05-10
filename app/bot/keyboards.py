from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, )


delete_confirmation = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅"), KeyboardButton(text="❌")]
], resize_keyboard=True, one_time_keyboard=True)

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить таблетку")],
    [KeyboardButton(text="Список таблеток"), KeyboardButton(text="🗑 Удалить таблетку")]
], resize_keyboard=True)