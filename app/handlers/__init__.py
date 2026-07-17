from aiogram import Router

from .start import router as start_router
from .generate_image import router as generate_image_router
from .profile import router as profile_router

router = Router(name='root')
router.include_router(start_router)
router.include_router(generate_image_router)
router.include_router(profile_router)
