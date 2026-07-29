from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.buttons.inline_keyboard import start_keyboard
from src.enums.button_callbacks import ButtonCallback
from src.services import UserServices

router = Router(name="start")


START_TEXT = (
    "🎨 Я бот для генерации изображений с помощью GPT Image.\n\n"
    "Выбери пример работы, а я помогу превратить ее "
    "в готовую картинку. Можно настроить формат, качество и посмотреть свой "
    "профиль с балансом токенов."
)


@router.message(CommandStart())
async def cmd_start_command(message: Message, service: UserServices):
    user = await service.get(telegram_id=message.from_user.id)
    if not user:
        await service.create(data=await service.user_data(message=message))

    await message.answer(
        text=START_TEXT,
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == ButtonCallback.BACK)
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        text=START_TEXT,
        reply_markup=start_keyboard()
    )
