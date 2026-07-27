from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["TelegramIDMixin"]


class TelegramIDMixin:
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)
