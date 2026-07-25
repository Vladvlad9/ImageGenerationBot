from aiogram import types

from app.buttons.constants import ButtonText
from src.enums import ButtonCallback

__all__ = ["style_pagination_keyboard"]


def style_pagination_keyboard(current_index: int, total: int) -> types.InlineKeyboardMarkup:
    buttons: list[list[types.InlineKeyboardButton]] = []

    if total > 1:
        navigation_buttons: list[types.InlineKeyboardButton] = []

        if current_index > 0:
            navigation_buttons.append(
                types.InlineKeyboardButton(
                    text="<-",
                    callback_data=f"{ButtonCallback.EXAMPLE_WORKS}:{current_index - 1}",
                )
            )

        navigation_buttons.append(
            types.InlineKeyboardButton(
                text=f"{current_index + 1}/{total}",
                callback_data=f"{ButtonCallback.EXAMPLE_WORKS}:noop",
            )
        )

        if current_index < total - 1:
            navigation_buttons.append(
                types.InlineKeyboardButton(
                    text="->",
                    callback_data=f"{ButtonCallback.EXAMPLE_WORKS}:{current_index + 1}",
                )
            )

        buttons.append(navigation_buttons)

    buttons.append(
        [
            types.InlineKeyboardButton(
                text=ButtonText.BACK,
                callback_data=ButtonCallback.BACK,
            )
        ]
    )

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
