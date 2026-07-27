from .payment import router as payment_router
from .telegram_star import router as telegram_star_router
from .promocode import router as promo_code_router
from .crypto import router as crypto_router

__all__ = [
    'payment_router',
    'telegram_star_router',
    'promo_code_router',
    'crypto_router',
]
