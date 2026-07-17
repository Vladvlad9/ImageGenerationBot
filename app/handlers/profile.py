from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard
from src.enums.button_callbacks import ButtonCallback

router = Router(name="profile")


@router.callback_query(F.data == ButtonCallback.PROFILE)
async def profile(callback: CallbackQuery):
    username: str = callback.from_user.username
    token: int = 0

    await callback.message.delete()
    await callback.message.answer(
        text=f"📊 Мой профиль\n\n "
             f"👤 Имя: {username}\n"
             f"🔹 Баланс: {token} токенов\n\n"
             f"🔸 Потрачено: {token} токенов",
        reply_markup=back_keyboard(),
    )
