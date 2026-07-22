from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alchemy.mixins import LifecycleMixin
from src.database.alchemy.models.base import Base

__all__ = ["UserSettings"]


class UserSettings(Base, LifecycleMixin):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
        index=True,
    )

    image_aspect_ratio: Mapped[str] = mapped_column(String(16), default="1:1")
    image_quality: Mapped[str] = mapped_column(String(16), default="auto")
    language: Mapped[str] = mapped_column(String(8), default="ru")
    notify_on_finish: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="settings",
    )
