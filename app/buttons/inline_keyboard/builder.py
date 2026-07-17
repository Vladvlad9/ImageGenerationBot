from dataclasses import dataclass

from aiogram import types

__all__ = ["Button", "InlineKeyboard"]


@dataclass(frozen=True)
class Button:
    text: str
    callback_data: str


class InlineKeyboard:
    def __init__(self, buttons: list[list[Button]]) -> None:
        self._buttons = buttons

    def build(self) -> types.InlineKeyboardMarkup:
        return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=button.text,
                        callback_data=button.callback_data,
                    )
                    for button in row
                ]
                for row in self._buttons
            ],
        )
