from aiogram import types

from app.buttons.constants import ButtonText
from app.buttons.inline_keyboard.builder import Button, InlineKeyboard
from src.enums.button_callbacks import ButtonCallback

__all__ = ["ImageGenerationKeyboard", "img_gen_keyboard"]


class ImageGenerationKeyboard:
    def build(self) -> types.InlineKeyboardMarkup:
        return InlineKeyboard(
            buttons=[
                [
                    Button(text=ButtonText.QUALITY, callback_data=ButtonCallback.QUALITY),
                    Button(text=ButtonText.FORMAT, callback_data=ButtonCallback.FORMAT),
                ],
                [
                    Button(text=ButtonText.BACK, callback_data=ButtonCallback.BACK),
                ],
            ],
        ).build()


def img_gen_keyboard() -> types.InlineKeyboardMarkup:
    return ImageGenerationKeyboard().build()
