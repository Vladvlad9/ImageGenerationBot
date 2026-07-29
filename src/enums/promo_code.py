from enum import StrEnum

__all__ = ["PromoCodeActivationStatus"]


class PromoCodeActivationStatus(StrEnum):
    ACTIVATED = "activated"
    NOT_FOUND = "not_found"
    ALREADY_USED = "already_used"
    INVALID_REWARD = "invalid_reward"
    USER_NOT_FOUND = "user_not_found"
