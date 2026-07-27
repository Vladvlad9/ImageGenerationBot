from uuid import UUID
from sqlalchemy import UUID as SQLUUID
from uuid_utils import uuid7
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["IDMixin"]


class IDMixin:
    id: Mapped[UUID] = mapped_column(
        SQLUUID,
        insert_default=uuid7,
        primary_key=True,
        unique=True
    )
