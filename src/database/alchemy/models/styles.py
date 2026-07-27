from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.alchemy.mixins import LifecycleMixin, SoftDeleteMixin
from src.database.alchemy.models.base import Base

__all__ = ["Style"]


class Style(Base, LifecycleMixin, SoftDeleteMixin):
    file_id: Mapped[str] = mapped_column(String(32), primary_key=True, unique=True, index=True)

    caption: Mapped[str | None] = mapped_column(String(1024))
    prompt: Mapped[str | None] = mapped_column(String(5024))
