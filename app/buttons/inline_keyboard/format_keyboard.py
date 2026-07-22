from aiogram import types

from app.buttons.constants import ButtonText
from app.buttons.inline_keyboard.builder import Button, InlineKeyboard
from src.enums import ImageAspectRatio, ButtonCallback

__all__ = ['format_keyboard']


def _format_button_text(aspect_ratio: ImageAspectRatio, current_aspect_ratio: str) -> str:
    if aspect_ratio == current_aspect_ratio:
        return f"✅ {aspect_ratio}"

    return aspect_ratio


def format_keyboard(current_aspect_ratio: str = ImageAspectRatio.ONE_TO_ONE) -> types.InlineKeyboardMarkup:
    return InlineKeyboard(
        buttons=[
            [
                Button(
                    text=_format_button_text(ImageAspectRatio.AUTO, current_aspect_ratio),
                    callback_data=ImageAspectRatio.AUTO,
                ),
            ],
            [
                Button(
                    text=_format_button_text(ImageAspectRatio.ONE_TO_ONE, current_aspect_ratio),
                    callback_data=ImageAspectRatio.ONE_TO_ONE,
                ),
                Button(
                    text=_format_button_text(ImageAspectRatio.TWO_TO_THREE, current_aspect_ratio),
                    callback_data=ImageAspectRatio.TWO_TO_THREE,
                ),
            ],
            [
                Button(
                    text=_format_button_text(ImageAspectRatio.THREE_TO_TWO, current_aspect_ratio),
                    callback_data=ImageAspectRatio.THREE_TO_TWO,
                ),
                Button(
                    text=_format_button_text(ImageAspectRatio.THREE_TO_FOUR, current_aspect_ratio),
                    callback_data=ImageAspectRatio.THREE_TO_FOUR,
                ),
            ],
            [
                Button(
                    text=_format_button_text(ImageAspectRatio.FOUR_TO_THREE, current_aspect_ratio),
                    callback_data=ImageAspectRatio.FOUR_TO_THREE,
                ),
                Button(
                    text=_format_button_text(ImageAspectRatio.NINE_TO_SIXTEEN, current_aspect_ratio),
                    callback_data=ImageAspectRatio.NINE_TO_SIXTEEN,
                ),
            ],
            [
                Button(
                    text=_format_button_text(ImageAspectRatio.SIXTEEN_TO_NINE, current_aspect_ratio),
                    callback_data=ImageAspectRatio.SIXTEEN_TO_NINE,
                ),
            ],
            [
                Button(text=ButtonText.BACK, callback_data=ButtonCallback.GENERATE),
            ],
        ],
    ).build()
