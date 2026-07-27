from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alchemy.mixins import LifecycleMixin, SoftDeleteMixin, IDMixin
from src.database.alchemy.models.base import Base

__all__ = ["User"]


class User(Base, IDMixin, LifecycleMixin, SoftDeleteMixin):
    __table_args__ = (
        CheckConstraint("length(username) >= 5", name="username_valid"),
    )

    username: Mapped[str | None] = mapped_column(String(32))

    first_name: Mapped[str | None] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))

    token_balance: Mapped[int] = mapped_column(default=0)
    tokens_spent: Mapped[int] = mapped_column(default=0)

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    settings: Mapped["UserSettings | None"] = relationship(
        "UserSettings",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
