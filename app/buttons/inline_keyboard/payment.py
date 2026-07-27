from aiogram import types

from app.buttons.constants import ButtonText
from app.buttons.inline_keyboard import InlineKeyboard, Button
from src.enums import ButtonCallback

__all__ = ["payment_keyboard"]


def payment_keyboard() -> types.InlineKeyboardMarkup:
    return InlineKeyboard(
        buttons=[
            [
                Button(text=ButtonText.TELEGRAM, callback_data=ButtonCallback.TELEGRAM),
            ],
            [
                Button(text=ButtonText.CRYPTO, callback_data=ButtonCallback.CRYPTO),
            ],
            [
                Button(text=ButtonText.PROMO_CODE, callback_data=ButtonCallback.PROMO_CODE),
            ],
            [
                Button(text=ButtonText.BACK, callback_data=ButtonCallback.BACK),
            ]
        ],
    ).build()
