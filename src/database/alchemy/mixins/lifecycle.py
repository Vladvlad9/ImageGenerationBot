from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import declarative_mixin, Mapped, mapped_column
from sqlalchemy.sql.functions import now

__all__ = ["LifecycleMixin"]


@declarative_mixin
class LifecycleMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        insert_default=now,
        nullable=False,
        comment="Date of created",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        insert_default=now,
        nullable=False,
        comment="Date of last updated",
    )
