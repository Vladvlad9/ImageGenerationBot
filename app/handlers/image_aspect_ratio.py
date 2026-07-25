from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard.format_keyboard import format_keyboard
from src.enums import ButtonCallback, ImageAspectRatio
from src.services import UserServices, UserSettingsServices
from src.types.user import UserSettingsUpdateDTO

router = Router(name="image_aspect_ratio")


@router.callback_query(F.data == ButtonCallback.FORMAT)
async def format_img(callback: CallbackQuery, service: UserServices):
    user = await service.get(telegram_id=callback.from_user.id)
    current_aspect_ratio = user.settings.image_aspect_ratio if user and user.settings else ImageAspectRatio.ONE_TO_ONE

    await callback.message.edit_text(
        text="📐 Выберите формат создаваемого фото в GPT Image\n\n"
             "auto: автоматически подберет нужный формат\n"
             "1:1: идеально подходит для профильных фото в соцсетях, таких как VK, Telegram и т.д\n"
             "2:3: хорошо подходит для печатных фотографий, но также может использоваться для пинов на Pinterest\n"
             "3:2: широко используемый формат для фотографий, подходит для постов в Telegram, VK, и др.\n"
             "3:4: широко используемый формат для фотографий, карточек товаров и т.д.\n"
             "4:3: Традиционный формат для видео; подходит для просмотра на стандартных экранах компьютеров\n"
             "9:16: оптимальный формат для Stories в Telegram или вертикальных видео на YouTube\n"
             "16:9: стандартный формат для видео, идеален для YouTube, VK и др.\n",
        reply_markup=format_keyboard(current_aspect_ratio=current_aspect_ratio)
    )


@router.callback_query(F.data.in_([aspect_ratio.value for aspect_ratio in ImageAspectRatio]))
async def set_format_img(callback: CallbackQuery, session: AsyncSession):
    aspect_ratio = callback.data
    settings_service = UserSettingsServices(session=session)
    await settings_service.update(
        telegram_id=callback.from_user.id,
        data=UserSettingsUpdateDTO(image_aspect_ratio=aspect_ratio),
    )

    await callback.message.edit_reply_markup(
        reply_markup=format_keyboard(current_aspect_ratio=aspect_ratio),
    )
    await callback.answer(text=f"Формат фото: {aspect_ratio}")
