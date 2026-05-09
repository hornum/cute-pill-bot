from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, )


delete_confirmation = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅"), KeyboardButton(text="❌")]
], resize_keyboard=True, one_time_keyboard=True)
