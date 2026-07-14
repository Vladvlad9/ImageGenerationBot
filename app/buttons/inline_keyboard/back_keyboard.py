from aiogram import types

__all__ = ["back_keyboard"]


def back_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
