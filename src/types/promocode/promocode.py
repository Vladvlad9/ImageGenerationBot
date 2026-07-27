from datetime import datetime
from uuid import UUID

from src.types.base import ImmutableDTO

__all__ = [
    "PromoCodeResponseIdDTO",
    "PromoCodeDTO",
    "PromoCodeCreateDTO",
    "PromoCodeUpdateDTO",
    "PromoCodeUsageResponseIdDTO",
    "PromoCodeUsageDTO",
    "PromoCodeUsageCreateDTO",
]


class PromoCodeResponseIdDTO(ImmutableDTO):
    id: UUID


class PromoCodeDTO(PromoCodeResponseIdDTO):
    code: str
    status: str
    tokens_amount: int | None
    max_uses: int | None
    used_count: int
    max_uses_per_user: int | None
    starts_at: datetime | None
    expires_at: datetime | None


class PromoCodeCreateDTO(ImmutableDTO):
    code: str
    status: str = "active"
    tokens_amount: int | None = None
    max_uses: int | None = None
    max_uses_per_user: int | None = 1
    starts_at: datetime | None = None
    expires_at: datetime | None = None


class PromoCodeUpdateDTO(ImmutableDTO):
    code: str | None = None
    status: str | None = None
    tokens_amount: int | None = None
    max_uses: int | None = None
    used_count: int | None = None
    max_uses_per_user: int | None = None
    starts_at: datetime | None = None
    expires_at: datetime | None = None


class PromoCodeUsageResponseIdDTO(ImmutableDTO):
    id: UUID


class PromoCodeUsageDTO(PromoCodeUsageResponseIdDTO):
    promocode_id: UUID
    user_id: int


class PromoCodeUsageCreateDTO(ImmutableDTO):
    promocode_id: UUID
    user_id: int
