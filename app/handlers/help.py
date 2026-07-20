from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard
from src.enums.button_callbacks import ButtonCallback

router = Router(name="help")


@router.callback_query(F.data == ButtonCallback.HELP)
async def show_help(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Нажмите «Сгенерировать картинку» и отправьте описание изображения.",
        reply_markup=back_keyboard(),
    )
