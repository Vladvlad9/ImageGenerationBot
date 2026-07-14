from aiogram import types

__all__ = ['start_keyboard']


def start_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Сгенерировать картинку", callback_data="generate")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
