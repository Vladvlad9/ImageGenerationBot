from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard

router = Router(name="generate_image")


@router.callback_query(F.data == "generate")
async def order(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Введите промпт",
        reply_markup=back_keyboard()
    )
