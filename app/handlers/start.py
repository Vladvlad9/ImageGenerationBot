from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.buttons.inline_keyboard import start_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start_command(message: Message):
    await message.answer(
        "Welcome",
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == "back")
async def back_to_start(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        "Welcome!",
        reply_markup=start_keyboard()
    )
