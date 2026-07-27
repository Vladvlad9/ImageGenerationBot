from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from src.database.alchemy.mixins import LifecycleMixin
from src.database.alchemy.models.base import Base

__all__ = ["Payment"]


class Payment(Base, LifecycleMixin):
    __table_args__ = (
        CheckConstraint("amount >= 0", name="amount_payment_valid"),
    )

    id: Mapped[UUID] = mapped_column(
        SQLUUID,
        insert_default=uuid7,
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="CASCADE"),
        index=True,
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending",
                                        nullable=False)  # pending, paid, failed, canceled, refunded
    provider: Mapped[str] = mapped_column(String(32), nullable=False)  # stripe, yookassa, paypal, telegram
    provider_payment_id: Mapped[str] = mapped_column(String(128), unique=True)

    description: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["User"] = relationship(
        "User",
        back_populates="payments",
    )

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, status={self.status})>"
        )

    def __str__(self) -> str:
        return f"Payment id={self.id}, status={self.status}, amount={self.amount} {self.currency}"
