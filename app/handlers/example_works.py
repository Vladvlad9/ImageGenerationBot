import logging

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard import back_keyboard
from app.buttons.pagination import style_pagination_keyboard
from app.states import ImageStates
from settings import settings
from src.chatGPT.image_service import format_image_generation_tokens, format_image_generation_cost
from src.enums import ButtonCallback
from src.services.style import StyleServices
from src.services.style_image_generation import (
    ImageGenerationFailedError,
    NotEnoughTokensError,
    StyleImageGenerationService,
)
from src.services.user import UserServices
from src.storage.storage import StorageAppWrite

router = Router(name="example_works")
logger = logging.getLogger(__name__)


def format_remaining_token_balance(balance: int | None) -> str:
    if balance is None:
        return ""

    return f"\nОстаток баланса: {balance} токенов"


@router.callback_query(F.data == ButtonCallback.EXAMPLE_WORKS)
async def example_works(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    service = StyleServices(session=session)
    await show_example_work(callback=callback, state=state, service=service, index=0, is_new_message=True)


@router.callback_query(F.data.startswith(f"{ButtonCallback.EXAMPLE_WORKS}:"))
async def paginate_example_works(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    page = callback.data.rsplit(":", maxsplit=1)[-1]
    if page == "noop":
        await callback.answer()
        return

    service = StyleServices(session=session)
    await show_example_work(callback=callback, state=state, service=service, index=int(page), is_new_message=False)


@router.message(ImageStates.style_photo, F.photo)
async def generate_image_by_style(
        message: Message,
        state: FSMContext,
        bot: Bot,
        service: UserServices,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()
    style_file_id = state_data.get("style_file_id")

    if not style_file_id:
        await state.clear()
        await message.answer("Сначала выбери стиль в разделе «Стили работ».")
        return

    style_service = StyleServices(session=session)
    style = await style_service.get_by_file_id(file_id=style_file_id)
    if style is None:
        await state.clear()
        await message.answer("Выбранный стиль больше недоступен. Выбери другой стиль.")
        return

    status_message = await message.answer(
        "Генерирую изображение: сначала переношу стиль, затем меняю персонажа..."
    )

    try:
        user_photo = message.photo[-1]
        generation_service = StyleImageGenerationService(
            bot=bot,
            user_service=service,
        )
        result = await generation_service.generate(
            telegram_id=message.from_user.id,
            telegram_photo_file_id=user_photo.file_id,
            style_file_id=style_file_id,
            style_prompt=style.prompt,
        )
    except NotEnoughTokensError as e:
        await status_message.edit_text(
            "Недостаточно токенов для генерации.\n"
            f"Минимум для запроса: {e.required_balance} токенов.\n"
            f"Твой баланс: {e.current_balance} токенов.",
            reply_markup=back_keyboard()
        )
        return
    except ImageGenerationFailedError as e:
        logger.exception(
            "Image generation failed: telegram_id=%s",
            message.from_user.id,
        )
        if e.refunded:
            text = (
                "Не получилось обработать изображение через ChatGPT. "
                "Токены за этот запрос вернули на баланс — попробуй ещё раз чуть позже."
                f"{format_remaining_token_balance(e.remaining_token_balance)}"
            )
        else:
            text = (
                "Не получилось обработать изображение через ChatGPT, а вернуть токены "
                "на баланс тоже не вышло. Напиши в поддержку — разберёмся вручную."
            )
        await status_message.edit_text(text, reply_markup=back_keyboard())
        return
    except Exception as e:
        logger.exception("Unexpected error in generate_image_by_style: telegram_id=%s", message.from_user.id)
        await status_message.edit_text(
            "Не получилось обработать изображение через ChatGPT. Попробуй чуть позже."
        )
        return

    await message.answer_photo(
        photo=BufferedInputFile(
            file=result.image_bytes,
            filename="generated.png",
        ),
        caption=(
            f"Готово.\n\n"
            f"Изображение хранится только у тебя в боте, "
            f"после 'Очистки истории' все изображения ПРОПАДУТ.\n\n"
            f"{format_image_generation_tokens(result.usage)}"
            f"{format_image_generation_cost(result.cost_usd)}"
            f"{format_remaining_token_balance(result.remaining_token_balance)}"
        ),
    )
    await status_message.delete()


@router.message(ImageStates.style_photo)
async def ask_style_photo(message: Message) -> None:
    await message.answer("Пришли изображение, которое нужно сделать в выбранном стиле.")


async def show_example_work(
        callback: CallbackQuery,
        state: FSMContext,
        service: StyleServices,
        index: int,
        is_new_message: bool,
) -> None:
    styles = await service.get_list()
    if not styles:
        if is_new_message:
            await callback.message.delete()

        await callback.answer()
        await callback.message.answer(
            text="Пока нет добавленных стилей работ.",
            reply_markup=style_pagination_keyboard(current_index=0, total=0),
        )
        return

    index = max(0, min(index, len(styles) - 1))
    style = styles[index]

    await state.update_data(
        style_file_id=style.file_id,
    )
    await state.set_state(ImageStates.style_photo)

    storage = StorageAppWrite(bucket_id=settings.STORAGE.BUCKET_ID)
    photo = await storage.get_file_url(file_id=style.file_id)

    caption = style.caption or (
        "<b>Использовать этот стиль</b>\n"
        "⬇️Пришли изображение своего героя⬇️\n\n"
        f"Генерация займет {settings.GPT.MIN_STYLE_IMAGE_GENERATION_TOKENS:,.0f} токенов\n"
    )
    reply_markup = style_pagination_keyboard(current_index=index, total=len(styles))

    if is_new_message:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
        )
    else:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=caption),
            reply_markup=reply_markup,
        )

    await callback.answer()
