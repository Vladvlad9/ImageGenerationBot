from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard
from src.enums import ButtonCallback

router = Router(name='crypto')


@router.callback_query(F.data == ButtonCallback.CRYPTO)
async def crypto(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Реквизиты:\n"
             "1.\n"
             "2.\n",
        reply_markup=back_keyboard(callback_data=ButtonCallback.PAYMENTS)
    )
