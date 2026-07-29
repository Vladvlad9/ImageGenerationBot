from enum import StrEnum

__all__ = ["TelegramStarsPaymentStatus"]


class TelegramStarsPaymentStatus(StrEnum):
    APPLIED = "applied"
    DUPLICATE = "duplicate"
    INVALID_PAYMENT = "invalid_payment"
    USER_NOT_FOUND = "user_not_found"
