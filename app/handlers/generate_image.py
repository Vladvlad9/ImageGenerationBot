from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.buttons.inline_keyboard import ImageGenerationKeyboard
from app.buttons.inline_keyboard.format_keyboard import format_keyboard
from app.states import ImageStates
from settings import settings
from src.chatGPT.image_service import ImageGenerationService
from src.enums.button_callbacks import ButtonCallback
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
    await callback.message.edit_text(
        text="📖 Пишите запрос на любом языке:\n"
             "– Эта модель понимает конкретно каждое ваше слово: на русском, на английском и любом языке\n"
             "– Попросите её, например, создать постер с приглашением на мероприятие (укажите всю информацию о нём)\n\n"
             "⚙️ Настройки:\n"
             f"Качество: {user.settings.image_quality}\n"
             f"Формат фото: {user.settings.image_aspect_ratio}\n\n"
             "🔹 Баланса хватит на 1 запрос. 1 фото = 6,900 токенов.",
        reply_markup=build_inline_keyboard(
            keyboard=ImageGenerationKeyboard(),
        )
    )
    await state.set_state(ImageStates.prompt)


@router.callback_query(F.data == ButtonCallback.FORMAT)
async def format_img(callback: CallbackQuery, service: UserServices):
    user = await service.get(telegram_id=callback.from_user.id)
    current_aspect_ratio = user.settings.image_aspect_ratio if user and user.settings else "1:1"

    await callback.message.edit_text(
        text="📐 Выберите формат создаваемого фото в GPT Image\n\n"
             "auto: автоматически подберет нужный формат",
        reply_markup=format_keyboard(current_aspect_ratio=current_aspect_ratio)
    )


@router.message(ImageStates.prompt)
async def prompt(message: Message, state: FSMContext):
    await state.update_data(prompt=message.text.lower())
    # await message.delete()
    await message.answer(
        text="Идет генерация...",
        # reply_markup=make_row_keyboard(available_food_sizes)
    )

    img = ImageGenerationService(
        api_key=settings.GPT.API_KEY,
        model=settings.GPT.MODEL,
        size=settings.GPT.SIZE,
    )
    prmpt = "Черно-белая манга: одинокий самурай стоит в поле красных ликорисов, кинематографичная композиция"
    image_bytes = await generate_image_bytes(
        image_generator=img,
        prompt=prmpt,
    )

    with open("result.png", "wb") as file:
        file.write(image_bytes)

    print("Картинка сохранена как result.png")
    await state.clear()
