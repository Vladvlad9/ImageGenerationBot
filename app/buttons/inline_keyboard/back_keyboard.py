from aiogram import types

from app.buttons.constants import ButtonText
from app.buttons.inline_keyboard.builder import Button, InlineKeyboard
from src.enums.button_callbacks import ButtonCallback

__all__ = ["back_keyboard"]


def back_keyboard() -> types.InlineKeyboardMarkup:
    return InlineKeyboard(
        buttons=[
            [
                Button(text=ButtonText.BACK, callback_data=ButtonCallback.BACK),
            ],
        ],
    ).build()
