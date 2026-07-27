from aiogram import Router

from .start import router as start_router
from .profile import router as profile_router
from .help import router as help_router
from .image_aspect_ratio import router as image_aspect_ratio_router
from .image_quality import router as image_quality_router
from .example_works import router as example_works_router

router = Router(name='root')

router.include_router(start_router)
router.include_router(profile_router)
router.include_router(help_router)
router.include_router(image_aspect_ratio_router)
router.include_router(image_quality_router)
router.include_router(example_works_router)
