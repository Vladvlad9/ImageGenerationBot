from aiogram import types

from app.buttons.constants import ButtonText
from app.buttons.inline_keyboard.builder import Button, InlineKeyboard
from src.enums import ImageAspectRatio, ButtonCallback

__all__ = ['format_keyboard', 'quality_keyboard']

from src.enums.image_quality import ImageQuality


def _format_button_text(aspect_ratio: ImageAspectRatio, current_aspect_ratio: str) -> str:
    if aspect_ratio == current_aspect_ratio:
        return f"✅ {aspect_ratio}"

    return aspect_ratio


def _quality_button_text(aspect_quality: ImageQuality, current_aspect_quality: str) -> str:
    if aspect_quality == current_aspect_quality:
        return f"✅ {aspect_quality}"

    return aspect_quality


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
                    text=_format_button_text(ImageAspectRatio.TWO_TO_ONE, current_aspect_ratio),
                    callback_data=ImageAspectRatio.TWO_TO_ONE,
                ),
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


def quality_keyboard(current_aspect_quality: str) -> types.InlineKeyboardMarkup:
    return InlineKeyboard(
        buttons=[
            [
                Button(
                    text=_quality_button_text(ImageQuality.LOW, current_aspect_quality),
                    callback_data=ImageQuality.LOW,
                ),

                Button(
                    text=_quality_button_text(ImageQuality.MEDIUM, current_aspect_quality),
                    callback_data=ImageQuality.MEDIUM,
                ),

                Button(
                    text=_quality_button_text(ImageQuality.HIGH, current_aspect_quality),
                    callback_data=ImageQuality.HIGH,
                ),
            ],
            [
                Button(text=ButtonText.BACK, callback_data=ButtonCallback.GENERATE),
            ]
        ]
    ).build()
