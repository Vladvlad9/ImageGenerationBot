from typing import Protocol

from aiogram.types import InlineKeyboardMarkup


class InlineKeyboardProtocol(Protocol):
    def build(self) -> InlineKeyboardMarkup:
        ...
