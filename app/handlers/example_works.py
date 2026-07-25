from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.pagination import style_pagination_keyboard
from settings import settings
from src.enums import ButtonCallback
from src.services.style import StyleServices
from src.storage.storage import StorageAppWrite

router = Router(name="example_works")


@router.callback_query(F.data == ButtonCallback.EXAMPLE_WORKS)
async def example_works(callback: CallbackQuery, session: AsyncSession):
    service = StyleServices(session=session)
    await show_example_work(callback=callback, service=service, index=0, is_new_message=True)


@router.callback_query(F.data.startswith(f"{ButtonCallback.EXAMPLE_WORKS}:"))
async def paginate_example_works(callback: CallbackQuery, session: AsyncSession):
    page = callback.data.rsplit(":", maxsplit=1)[-1]
    if page == "noop":
        await callback.answer()
        return

    service = StyleServices(session=session)
    await show_example_work(callback=callback, service=service, index=int(page), is_new_message=False)


async def show_example_work(
        callback: CallbackQuery,
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
    storage = StorageAppWrite(bucket_id=settings.STORAGE.BUCKET_ID)
    photo = BufferedInputFile(
        file=await storage.get_file_view(file_id=style.file_id),
        filename="generated.png",
    )
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
