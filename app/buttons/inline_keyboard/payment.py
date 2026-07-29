from aiogram import types

from app.buttons.constants import ButtonText
from app.buttons.inline_keyboard import InlineKeyboard, Button
from src.enums import ButtonCallback
from src.types.payment_package import TOKEN_PACKAGES

__all__ = ["payment_keyboard", "telegram_stars_keyboard"]


def _generation_label(generations: int) -> str:
    if generations % 10 == 1 and generations % 100 != 11:
        return "генерация"
    if 2 <= generations % 10 <= 4 and not 12 <= generations % 100 <= 14:
        return "генерации"
    return "генераций"


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
              Button(text=ButtonText.DONATIONALERTS, callback_data=ButtonCallback.DONATIONALERTS),
            ],
            [
                Button(text=ButtonText.PROMO_CODE, callback_data=ButtonCallback.PROMO_CODE),
            ],
            [
                Button(text=ButtonText.BACK, callback_data=ButtonCallback.BACK),
            ]
        ],
    ).build()


def telegram_stars_keyboard() -> types.InlineKeyboardMarkup:
    return InlineKeyboard(
        buttons=[
            [
                Button(
                    text=(
                        f"{package.generations} {_generation_label(package.generations)} "
                        f"- {package.stars} ⭐"
                    ),
                    callback_data=package.callback_data,
                )
            ]
            for package in TOKEN_PACKAGES
        ] + [
            [
                Button(text=ButtonText.BACK, callback_data=ButtonCallback.PAYMENTS),
            ]
        ],
    ).build()
