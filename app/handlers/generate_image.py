from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.buttons.inline_keyboard import ImageGenerationKeyboard
from app.states import ImageStates
from settings import settings
from src.chatGPT.image_service import ImageGenerationService
from src.enums.button_callbacks import ButtonCallback
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
async def order(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="📖 Пишите запрос на любом языке:\n"
             "– Эта модель понимает конкретно каждое ваше слово: на русском, на английском и любом языке\n"
             "– Попросите её, например, создать постер с приглашением на мероприятие (укажите всю информацию о нём)\n\n"
             "⚙️ Настройки:\n"
             "Качество: 1K\n"
             "Формат фото: 1:1\n\n"
             "🔹 Баланса хватит на 1 запрос. 1 фото = 6,900 токенов.",
        reply_markup=build_inline_keyboard(
            keyboard=ImageGenerationKeyboard(),
        )
    )
    await state.set_state(ImageStates.prompt)


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
