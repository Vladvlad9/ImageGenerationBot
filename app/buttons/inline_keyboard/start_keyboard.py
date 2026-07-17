from aiogram import types

from app.buttons.constants import ButtonCallback, ButtonText
from app.buttons.inline_keyboard.builder import Button, InlineKeyboard

__all__ = ['start_keyboard']


def start_keyboard() -> types.InlineKeyboardMarkup:
    return InlineKeyboard(
        buttons=[
            [
                Button(text=ButtonText.GENERATE, callback_data=ButtonCallback.GENERATE),
            ],
            [
                Button(text=ButtonText.HELP, callback_data=ButtonCallback.HELP),
                Button(text=ButtonText.PROFILE, callback_data=ButtonCallback.PROFILE),
            ],
        ],
    ).build()
