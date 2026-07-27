from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.pagination import style_pagination_keyboard
from app.states import ImageStates
from settings import settings
from src.chatGPT.image_service import (
    build_image_generation_service,
    format_image_generation_cost,
    format_image_generation_tokens,
)
from src.enums import ImageAspectRatio, ImageQuality
from src.enums import ButtonCallback
from src.services.style import StyleServices
from src.services.user import UserServices
from src.storage.storage import StorageAppWrite

router = Router(name="example_works")


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
) -> None:
    state_data = await state.get_data()
    style_file_id = state_data.get("style_file_id")
    style_prompt = state_data.get("style_prompt")

    if not style_file_id:
        await state.clear()
        await message.answer("Сначала выбери стиль в разделе «Стили работ».")
        return

    user = await service.get(telegram_id=message.from_user.id)
    aspect_ratio = user.settings.image_aspect_ratio if user and user.settings else ImageAspectRatio.ONE_TO_ONE
    image_quality = user.settings.image_quality if user and user.settings else ImageQuality.LOW

    status_message = await message.answer("Генерирую изображение в выбранном стиле...")

    try:
        user_photo = message.photo[-1]
        user_image_io = await bot.download(user_photo.file_id)
        if user_image_io is None:
            raise RuntimeError("Не удалось скачать фото пользователя.")

        storage = StorageAppWrite(bucket_id=settings.STORAGE.BUCKET_ID)
        style_image_bytes = await storage.get_file_view(file_id=style_file_id)

        image_generator = build_image_generation_service(
            aspect_ratio=aspect_ratio,
            quality=image_quality,
        )
        image_bytes = await image_generator.edit_with_style(
            image_bytes=user_image_io.getvalue(),
            style_image_bytes=style_image_bytes,
            style_prompt=style_prompt,
        )
        cost_usd = image_generator.last_cost_usd
        usage = image_generator.last_usage
    except Exception as e:
        print(f"ERROR: {e}")
        await status_message.edit_text(
            "Не получилось обработать изображение через ChatGPT. Попробуй чуть позже."
        )
        return

    await message.answer_photo(
        photo=BufferedInputFile(
            file=image_bytes,
            filename="generated.png",
        ),
        caption=(
            f"Готово."
            f"{format_image_generation_tokens(usage)}"
            f"{format_image_generation_cost(cost_usd)}"
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
        style_prompt=style.prompt,
    )
    await state.set_state(ImageStates.style_photo)

    storage = StorageAppWrite(bucket_id=settings.STORAGE.BUCKET_ID)
    photo = await storage.get_file_url(file_id=style.file_id)
    caption = style.caption or (
        "Ты можешь использовать этот стиль\n"
        "Пришли изображение своего героя"
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
