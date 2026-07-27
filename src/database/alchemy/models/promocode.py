from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alchemy.mixins import IDMixin, LifecycleMixin
from src.database.alchemy.models.base import Base

__all__ = ["PromoCode", "PromoCodeUsage"]


class PromoCode(Base, IDMixin, LifecycleMixin):
    __table_args__ = (
        CheckConstraint("used_count >= 0", name="promocode_used_count_valid"),
        CheckConstraint("max_uses IS NULL OR max_uses > 0", name="promocode_max_uses_valid"),
        CheckConstraint(
            "max_uses_per_user IS NULL OR max_uses_per_user > 0",
            name="promocode_max_uses_per_user_valid",
        ),
        CheckConstraint(
            "tokens_amount IS NULL OR tokens_amount > 0",
            name="promocode_tokens_amount_valid",
        ),
    )

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)  # сам код, например START100
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)  # active, inactive, expired.

    tokens_amount: Mapped[int | None] = mapped_column(Integer)  # сколько токенов начислить

    max_uses: Mapped[int | None] = mapped_column(Integer)  # общий лимит активаций
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # сколько раз уже активировали
    max_uses_per_user: Mapped[int | None] = mapped_column(Integer,
                                                          default=1)  # сколько раз один пользователь может активировать этот код

    starts_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))  # с какого времени работает
    expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))  # когда истекает

    usages: Mapped[list["PromoCodeUsage"]] = relationship(
        "PromoCodeUsage",
        back_populates="promocode",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<PromoCode(id={self.id}, code={self.code}, "
            f"type={self.type}, status={self.status})>"
        )

    def __str__(self) -> str:
        return f"PromoCode code={self.code}, status={self.status}"


class PromoCodeUsage(Base, IDMixin, LifecycleMixin):
    promocode_id: Mapped[UUID] = mapped_column(  # какой промокод использовали
        SQLUUID,
        ForeignKey("promo_code.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(  # кто использовал
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="CASCADE"),
        index=True,
    )

    promocode: Mapped["PromoCode"] = relationship(
        "PromoCode",
        back_populates="usages",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="promocode_usages",
    )

    def __repr__(self) -> str:
        return (
            f"<PromoCodeUsage(id={self.id}, promocode_id={self.promocode_id}, "
            f"user_id={self.user_id})>"
        )
