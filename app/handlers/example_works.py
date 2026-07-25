from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile

from app.buttons.inline_keyboard import back_keyboard
from settings import settings
from src.enums import ButtonCallback
from src.storage.storage import StorageAppWrite

router = Router(name="example_works")


@router.callback_query(F.data == ButtonCallback.EXAMPLE_WORKS)
async def example_works(callback: CallbackQuery):
    storage = StorageAppWrite(bucket_id=settings.STORAGE.BUCKET_ID)

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=await storage.get_file_view(file_id="6a6490de00141f42474e"),
            filename="generated.png",
        ),
        caption="Ты можешь использовать этот стиль\n"
                "Пришли изображение своего героя",
        reply_markup=back_keyboard()
    )
