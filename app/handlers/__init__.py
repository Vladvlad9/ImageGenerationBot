from aiogram import Router

from .start import router as start_router
from .profile import router as profile_router
from .help import router as help_router
from .image_aspect_ratio import router as image_aspect_ratio_router
from .image_quality import router as image_quality_router
from .example_works import router as example_works_router
from .payment import payment_router
from .payment import telegram_star_router
from .payment import promo_code_router
from .payment import crypto_router
from .payment import refund_router
from .payment import donation_alerts_router

router = Router(name='root')

router.include_router(start_router)
router.include_router(profile_router)
router.include_router(help_router)
router.include_router(image_aspect_ratio_router)
router.include_router(image_quality_router)
router.include_router(example_works_router)
router.include_router(payment_router)
router.include_router(telegram_star_router)
router.include_router(promo_code_router)
router.include_router(crypto_router)
router.include_router(refund_router)
router.include_router(donation_alerts_router)
