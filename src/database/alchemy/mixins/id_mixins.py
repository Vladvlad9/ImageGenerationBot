from uuid_utils import uuid7

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["IDMixin"]


class IDMixin:
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid7)
