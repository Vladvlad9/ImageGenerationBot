from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard import start_keyboard
from src.enums.button_callbacks import ButtonCallback
from src.services.user import UserServices

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start_command(message: Message, session: AsyncSession):
    user = await UserServices(session=session).get(message.from_user.id)
    if user:
        await message.answer(
            text="🥳 Добро пожаловать!",
            reply_markup=start_keyboard()
        )
    else:
        await message.answer("Тебя нету в БД")




@router.callback_query(F.data == ButtonCallback.BACK)
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(
        text="🥳 Добро пожаловать!",
        reply_markup=start_keyboard()
    )
