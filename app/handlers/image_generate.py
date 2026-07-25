from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.buttons.inline_keyboard import ImageGenerationKeyboard
from app.states import ImageStates
from src.chatGPT.image_service import build_image_generation_service
from src.enums import ImageAspectRatio
from src.enums.button_callbacks import ButtonCallback
from src.enums.image_quality import ImageQuality
from src.services.image_storage import store_generated_image
from src.services.user import UserServices
from src.types import ImageGenerationProtocol, InlineKeyboardProtocol

router = Router(name="generate_image")


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
async def order(callback: CallbackQuery, state: FSMContext, service: UserServices):
    user = await service.get(telegram_id=callback.from_user.id)

    # rich_message = InputRichMessage(
    #     html=rich_msg(image_quality=user.settings.image_quality, image_aspect_ratio=user.settings.image_aspect_ratio)
    # )
    # await callback.message.delete()
    # await callback.message.answer_rich(
    #     rich_message=rich_message,
    #     reply_markup=build_inline_keyboard(keyboard=ImageGenerationKeyboard())
    # )

    await callback.message.edit_text(
        text="📖 Пишите запрос на любом языке:\n"
             "– Эта модель понимает конкретно каждое ваше слово: на русском, на английском и любом языке\n"
             "– Попросите её, например, создать постер с приглашением на мероприятие (укажите всю информацию о нём)\n\n"
             "⚙️ Настройки:\n"
             f"Качество: {user.settings.image_aspect_ratio}\n"
             f"Формат фото: {user.settings.image_quality}\n\n"
             f"🔹 Баланса хватит на 1 запрос. 1 фото = 6,900 токенов.",
        reply_markup=build_inline_keyboard(keyboard=ImageGenerationKeyboard())
    )

    await state.set_state(ImageStates.prompt)


# TODO переделать
@router.message(ImageStates.prompt)
async def prompt(message: Message, state: FSMContext, service: UserServices):
    prompt_text = message.text or ""
    if not prompt_text.strip():
        await message.answer("Опиши изображение текстом, пожалуйста.")
        return

    user = await service.get(telegram_id=message.from_user.id)
    aspect_ratio = user.settings.image_aspect_ratio if user and user.settings else ImageAspectRatio.ONE_TO_ONE
    image_quality = user.settings.image_quality if user and user.settings else ImageQuality.LOW

    await message.delete()
    status_message = await message.answer("Генерирую изображение...")

    try:
        image_generator = build_image_generation_service(
            aspect_ratio=aspect_ratio,
            quality=image_quality,
        )
        image_bytes = await generate_image_bytes(
            image_generator=image_generator,
            prompt=prompt_text,
        )
    except Exception as e:
        print(f"ERROR: {e}")
        await status_message.edit_text(
            "Не получилось сгенерировать изображение через ChatGPT. Попробуй другой запрос чуть позже.",
            reply_markup=build_inline_keyboard(keyboard=ImageGenerationKeyboard())
        )
        await state.clear()
        return

    stored_image = None
    try:
        stored_image = await store_generated_image(
            image_bytes=image_bytes,
            telegram_id=message.from_user.id,
            prompt=prompt_text,
        )
    except Exception:
        stored_image = None

    caption = "Готово."
    if stored_image and stored_image.public_url:
        caption = f"{caption}\n{stored_image.public_url}"
    elif stored_image:
        caption = f"{caption}\nСохранено в Backblaze B2: {stored_image.object_key}"

    await message.answer_photo(
        photo=BufferedInputFile(
            file=image_bytes,
            filename="generated.png",
        ),
        caption=caption,
    )
    await status_message.delete()

    await state.clear()
