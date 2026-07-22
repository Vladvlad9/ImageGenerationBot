from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard
from src.enums.button_callbacks import ButtonCallback
from src.services.user import UserServices

router = Router(name="profile")


@router.callback_query(F.data == ButtonCallback.PROFILE)
async def profile(callback: CallbackQuery, service: UserServices):
    user = await service.get(telegram_id=callback.from_user.id)

    await callback.message.edit_text(
        text=f"📊 Мой профиль\n\n "
             f"👤 Имя: {user.username}\n\n"
             f"🔹 Баланс: {user.token_balance} токенов\n"
             f"🔸 Потрачено: {user.tokens_spent} токенов",
        reply_markup=back_keyboard(),
    )
