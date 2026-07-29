from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.buttons.inline_keyboard import back_keyboard
from src.enums.button_callbacks import ButtonCallback

router = Router(name="help")


@router.callback_query(F.data == ButtonCallback.HELP)
async def show_help(callback: CallbackQuery):
    await callback.message.edit_text(
        text="ℹ️ Как пользоваться ботом\n\n"
             "Открыть «Примеры работ», выбрать стиль и отправить свое изображение, чтобы бот обработал его в похожем стиле.\n"
             "Дождись генерации — готовое изображение придет прямо в чат.\n"
             "Готовое изображение хранится только у тебя в бота. Если очистишь историю все пропадет\n\n"
             "💰 Для генерации используются токены. Баланс можно посмотреть в профиле.",
        reply_markup=back_keyboard(),
    )
