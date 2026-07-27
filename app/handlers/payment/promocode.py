from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard
from src.enums import ButtonCallback

router = Router(name='promo_code')


@router.callback_query(F.data == ButtonCallback.PROMO_CODE)
async def promo_code(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Введите промокод",
        reply_markup=back_keyboard(callback_data=ButtonCallback.PAYMENTS)
    )
