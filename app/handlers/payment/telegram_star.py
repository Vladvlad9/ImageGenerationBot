from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message

from app.buttons.inline_keyboard.payment import telegram_stars_keyboard
from src.enums import ButtonCallback
from src.services import UserServices
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
    if query.currency != "XTR" or query.invoice_payload not in TOKEN_PACKAGES_BY_PAYLOAD:
        await query.answer(ok=False, error_message="Не удалось проверить платеж.")
        return

    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, service: UserServices):
    payment = message.successful_payment
    package = TOKEN_PACKAGES_BY_PAYLOAD.get(payment.invoice_payload)

    if payment.currency != "XTR" or package is None:
        return

    new_balance = await service.add_tokens(
        telegram_id=message.from_user.id,
        tokens=package.tokens,
    )
    if new_balance is None:
        await message.answer("Оплата прошла успешно, но не удалось начислить токены. Напишите в поддержку.")
        return

    formatted_tokens = f"{package.tokens:,}".replace(",", " ")
    formatted_balance = f"{new_balance:,}".replace(",", " ")
    await message.answer(
        "Оплата прошла успешно.\n\n"
        f"Начислено: {formatted_tokens} токенов\n"
        f"Баланс: {formatted_balance} токенов"
    )
