from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from src.enums import PromoCodeActivationStatus
from src.types.base import ImmutableDTO

__all__ = [
    "PromoCodeResponseIdDTO",
    "PromoCodeDTO",
    "PromoCodeCreateDTO",
    "PromoCodeUpdateDTO",
    "PromoCodeActivationResultDTO",
    "PromoCodeUsageResponseIdDTO",
    "PromoCodeUsageDTO",
    "PromoCodeUsageCreateDTO",
    "PromoCodeNameDTO",
    "PromoCodeUpdateUsedCountDTO",
]


def normalize_promo_code(value: str) -> str:
    return str(value).strip().lower()


class PromoCodeNameDTO(ImmutableDTO):
    code: str = Field(
        ...,
        min_length=3,
        max_length=64,
        description="Уникальный код"
    )

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str | None) -> str:
        if value is None:
            return ""

        return normalize_promo_code(value=value)


class PromoCodeResponseIdDTO(ImmutableDTO):
    id: UUID


class PromoCodeUpdateUsedCountDTO(PromoCodeResponseIdDTO):
    used_count: int = Field(default=1, ge=1)


class PromoCodeDTO(PromoCodeResponseIdDTO):
    code: str
    status: str
    tokens_amount: int | None
    max_uses: int | None
    used_count: int
    max_uses_per_user: int | None
    starts_at: datetime | None
    expires_at: datetime | None


class PromoCodeActivationResultDTO(ImmutableDTO):
    status: PromoCodeActivationStatus
    promo_code: PromoCodeDTO | None = None
    tokens_amount: int = 0


class PromoCodeCreateDTO(ImmutableDTO):
    code: str
    status: str = "active"
    tokens_amount: int | None = None
    max_uses: int | None = None
    max_uses_per_user: int | None = 1
    starts_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return normalize_promo_code(value=value)


class PromoCodeUpdateDTO(ImmutableDTO):
    code: str | None = None
    status: str | None = None
    tokens_amount: int | None = None
    max_uses: int | None = None
    used_count: int | None = None
    max_uses_per_user: int | None = None
    starts_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_promo_code(value=value)


class PromoCodeUsageResponseIdDTO(ImmutableDTO):
    id: UUID


class PromoCodeUsageDTO(PromoCodeUsageResponseIdDTO):
    promocode_id: UUID
    user_id: int


class PromoCodeUsageCreateDTO(ImmutableDTO):
    promocode_id: UUID
    user_id: int
