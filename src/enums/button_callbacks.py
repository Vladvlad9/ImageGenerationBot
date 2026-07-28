from enum import StrEnum

__all__ = ['ButtonCallback']


class ButtonCallback(StrEnum):
    GENERATE = "generate"
    HELP = "help"
    PROFILE = "profile"
    BACK = "back"
    QUALITY = "quality"
    FORMAT = "format"

    TEST_CHAT_GPT = "test_chat_gpt"
    EXAMPLE_WORKS = "example_works"
    PAYMENTS = "payments"

    TELEGRAM = "telegram_stars"
    CRYPTO = "crypto_payments"
    PROMO_CODE = "promo_code"
    DONATIONALERTS = "donationalerts"
