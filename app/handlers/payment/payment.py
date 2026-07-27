from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard.payment import payment_keyboard
from src.enums import ButtonCallback

router = Router(name="payment")


@router.callback_query(F.data == ButtonCallback.PAYMENTS)
async def payment_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите способ оплаты",
        reply_markup=payment_keyboard()
    )
