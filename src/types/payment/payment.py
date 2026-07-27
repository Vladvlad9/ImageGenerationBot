from uuid import UUID

from src.types.base import ImmutableDTO

__all__ = ["PaymentResponseIdDTO", "PaymentDTO", "PaymentCreateDTO"]


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
