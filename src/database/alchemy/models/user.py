from sqlalchemy import BigInteger, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.alchemy.mixins import LifecycleMixin, SoftDeleteMixin
from src.database.alchemy.models.base import Base

__all__ = ["User"]


class User(Base, LifecycleMixin, SoftDeleteMixin):
    __table_args__ = (
        CheckConstraint("length(username) >= 5", name="username_valid"),
    )

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(32))

    first_name: Mapped[str | None] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))

    token_balance: Mapped[int] = mapped_column(default=0)
    tokens_spent: Mapped[int] = mapped_column(default=0)
