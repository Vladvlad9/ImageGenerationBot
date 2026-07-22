from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.buttons.inline_keyboard import start_keyboard
from src.enums.button_callbacks import ButtonCallback
from src.services.user import UserServices
from src.types.user import UserCreateDTO

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start_command(message: Message, service: UserServices):
    user = await service.get(telegram_id=message.from_user.id)
    if not user:
        user_data = UserCreateDTO(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )
        await service.create(data=user_data)

    await message.answer(
        text="🥳 Добро пожаловать!",
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == ButtonCallback.BACK)
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(
        text="🥳 Добро пожаловать!",
        reply_markup=start_keyboard()
    )
