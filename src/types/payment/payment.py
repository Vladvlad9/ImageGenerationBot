from uuid import UUID

from src.enums import TelegramStarsPaymentStatus
from src.types.base import ImmutableDTO

__all__ = [
    "PaymentResponseIdDTO",
    "PaymentDTO",
    "PaymentCreateDTO",
    "TelegramStarsPaymentResultDTO",
]


class PaymentResponseIdDTO(ImmutableDTO):
    id: UUID


class PaymentDTO(PaymentResponseIdDTO):
    user_id: int
    amount: int
    currency: str
    status: str
    provider: str
    provider_payment_id: str
    description: str


class PaymentCreateDTO(ImmutableDTO):
    user_id: int
    amount: int
    currency: str
    status: str
    provider: str
    provider_payment_id: str
    description: str


class TelegramStarsPaymentResultDTO(ImmutableDTO):
    status: TelegramStarsPaymentStatus
    tokens: int = 0
    balance: int | None = None
