from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard.payment import telegram_stars_keyboard
from app.service.telegram_stars import TelegramStarsServiceController
from src.enums import ButtonCallback
from src.types.payment_package import TOKEN_PACKAGES_BY_CALLBACK, TOKEN_PACKAGES_BY_PAYLOAD

router = Router(name='telegram_stars')


@router.callback_query(F.data == ButtonCallback.TELEGRAM)
async def telegram_stars(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите пакет токенов",
        reply_markup=telegram_stars_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.in_(TOKEN_PACKAGES_BY_CALLBACK.keys()))
async def buy_tokens(callback: CallbackQuery):
    package = TOKEN_PACKAGES_BY_CALLBACK[callback.data]
    formatted_tokens = f"{package.tokens:,}".replace(",", " ")

    await callback.message.answer_invoice(
        title=f"{formatted_tokens} токенов",
        description=f"Покупка {formatted_tokens} токенов для генерации изображений",
        payload=package.payload,
        currency="XTR",
        prices=[
            LabeledPrice(label=f"{formatted_tokens} токенов", amount=package.stars),
        ],
        provider_token="",
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    package = TOKEN_PACKAGES_BY_PAYLOAD.get(query.invoice_payload)

    if query.currency != "XTR" or package is None or query.total_amount != package.stars:
        await query.answer(ok=False, error_message="Не удалось проверить платеж.")
        return

    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, session: AsyncSession):
    payment = message.successful_payment

    if message.from_user is None:
        return

    service = TelegramStarsServiceController(session=session)
    text = await service.apply_payment(
        telegram_id=message.from_user.id,
        payment=payment,
    )

    if text is not None:
        await message.answer(text)
