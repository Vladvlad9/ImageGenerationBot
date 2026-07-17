from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.buttons.inline_keyboard import start_keyboard
from src.enums.button_callbacks import ButtonCallback

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start_command(message: Message):
    await message.answer(
        "🥳 Добро пожаловать!",
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == ButtonCallback.BACK)
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "Welcome!",
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == ButtonCallback.HELP)
async def show_help(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Нажмите «Сгенерировать картинку» и отправьте описание изображения.",
    )
