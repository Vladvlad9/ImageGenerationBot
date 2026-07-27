from aiogram import types

from app.buttons.constants import ButtonText
from app.buttons.inline_keyboard.builder import Button, InlineKeyboard
from src.enums.button_callbacks import ButtonCallback

__all__ = ['start_keyboard']


def start_keyboard() -> types.InlineKeyboardMarkup:
    return InlineKeyboard(
        buttons=[
            [
                Button(text=ButtonText.EXAMPLE_WORKS, callback_data=ButtonCallback.EXAMPLE_WORKS),
            ],
            [
                Button(text=ButtonText.HELP, callback_data=ButtonCallback.HELP),
                Button(text=ButtonText.PROFILE, callback_data=ButtonCallback.PROFILE),
            ],
            [
                Button(text=ButtonText.PAYMENTS, callback_data=ButtonCallback.PAYMENTS),
            ]
        ],
    ).build()
