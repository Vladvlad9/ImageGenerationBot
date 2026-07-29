from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard
from settings import settings
from src.enums import ButtonCallback

router = Router(name="donationalerts")


@router.callback_query(F.data == ButtonCallback.DONATIONALERTS)
async def donation_alerts_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Донат\n"
             f"{settings.DONATIONALERTS.LINK}\n\n"
             f"Укажи в нике свой username - <b>{callback.from_user.username}</b>\n"
             f"После успешного доната я пришлю тебе промокод на активацию токенов",
        reply_markup=back_keyboard(ButtonCallback.PAYMENTS)
    )
