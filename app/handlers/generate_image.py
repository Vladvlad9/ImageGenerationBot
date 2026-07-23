from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputRichMessage, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard import ImageGenerationKeyboard
from app.buttons.inline_keyboard.format_keyboard import format_keyboard, quality_keyboard
from src.enums import ImageAspectRatio
from src.enums.button_callbacks import ButtonCallback
from src.enums.image_quality import ImageQuality
from src.services.user import UserServices
from src.services.user_settings import UserSettingsServices
from src.types import ImageGenerationProtocol, InlineKeyboardProtocol
from src.types.user import UserSettingsUpdateDTO

router = Router(name="generate_image")


def rich_msg(image_quality: str, image_aspect_ratio: str) -> str:
    ORDER_RICH_HTML = f"""
    <h1>📖 Пишите запрос на любом языке:</h1>

    <p>
      – Эта модель понимает конкретно каждое ваше слово: на русском, на английском и любом языке
    </p>

    <p>
      – Попросите её, например, создать постер с приглашением на мероприятие (укажите всю информацию о нём)
    </p>

    <table bordered striped>
      <caption>⚙️ Настройки:</caption>
      <tr>
        <th>Качество</th>
        <th>Формат фото</th>
      </tr>
      <tr>
        <td>{image_quality}</td>
        <td>{image_aspect_ratio}</td>
      </tr>
    </table>

    <details>
      <summary>Баланс?</summary>
      <p>
        🔹 Баланса хватит на 1 запрос. 1 фото = 6,900 токенов.
      </p>
    </details>
    """
    return ORDER_RICH_HTML


async def generate_image_bytes(
        image_generator: ImageGenerationProtocol,
        prompt: str,
) -> bytes:
    return await image_generator.generate(prompt=prompt)


def build_inline_keyboard(
        keyboard: InlineKeyboardProtocol,
):
    return keyboard.build()


@router.callback_query(F.data == ButtonCallback.GENERATE)
async def order(callback: CallbackQuery, service: UserServices):
    user = await service.get(telegram_id=callback.from_user.id)

    rich_message = InputRichMessage(
        html=rich_msg(image_quality=user.settings.image_quality, image_aspect_ratio=user.settings.image_aspect_ratio)
    )
    await callback.message.delete()
    await callback.message.answer_rich(
        rich_message=rich_message,
        reply_markup=build_inline_keyboard(keyboard=ImageGenerationKeyboard())
    )

    # await callback.message.edit_text(
    #     text="📖 Пишите запрос на любом языке:\n"
    #          "– Эта модель понимает конкретно каждое ваше слово: на русском, на английском и любом языке\n"
    #          "– Попросите её, например, создать постер с приглашением на мероприятие (укажите всю информацию о нём)\n\n"
    #          "⚙️ Настройки:\n"
    #          f"Качество: {user.settings.image_quality}\n"
    #          f"Формат фото: {user.settings.image_aspect_ratio}\n\n"
    #          "🔹 Баланса хватит на 1 запрос. 1 фото = 6,900 токенов.",
    #     reply_markup=build_inline_keyboard(
    #         keyboard=ImageGenerationKeyboard(),
    #     )
    # )
    # await state.set_state(ImageStates.prompt)


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


@router.callback_query(F.data == ButtonCallback.QUALITY)
async def quality(callback: CallbackQuery, service: UserServices):
    user = await service.get(telegram_id=callback.from_user.id)
    current_quality = user.settings.image_quality if user and user.settings else ImageQuality.LOW

    await callback.message.edit_text(
        text="📐 Выберите формат создаваемого фото в GPT Image\n\n"
             "auto: автоматически подберет нужный формат\n",
        reply_markup=quality_keyboard(current_aspect_quality=current_quality)
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
