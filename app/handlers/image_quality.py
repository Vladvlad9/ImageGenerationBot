from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard import quality_keyboard
from src.enums import ButtonCallback, ImageQuality
from src.services import UserServices, UserSettingsServices
from src.types.user import UserSettingsUpdateDTO

router = Router(name="image_quality")


@router.callback_query(F.data == ButtonCallback.QUALITY)
async def quality(callback: CallbackQuery, service: UserServices):
    user = await service.get(telegram_id=callback.from_user.id)
    current_quality = user.settings.image_quality if user and user.settings else ImageQuality.LOW

    await callback.message.edit_text(
        text="📐 Выберите формат создаваемого фото в GPT Image\n\n"
             "auto: автоматически подберет нужный формат\n",
        reply_markup=quality_keyboard(current_aspect_quality=current_quality)
    )


@router.callback_query(F.data.in_([aspect_quality.value for aspect_quality in ImageQuality]))
async def set_quality_img(callback: CallbackQuery, session: AsyncSession):
    aspect_quality = callback.data
    settings_service = UserSettingsServices(session=session)
    await settings_service.update(
        telegram_id=callback.from_user.id,
        data=UserSettingsUpdateDTO(image_quality=aspect_quality),
    )

    await callback.message.edit_reply_markup(
        reply_markup=quality_keyboard(current_aspect_quality=aspect_quality),
    )
    await callback.answer(text=f"Качество фото: {aspect_quality}")
