from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.buttons.constants import ButtonText
from src.enums import ButtonCallback

router = Router(name='telegram_stars')


@router.callback_query(F.data == ButtonCallback.TELEGRAM)
async def buy_tokens(callback: CallbackQuery):
    # builder = InlineKeyboardBuilder()
    # builder.button(text="Оплатить", pay=True)
    # builder.button(text=ButtonText.BACK, callback_data=ButtonCallback.PAYMENTS)
    # builder.adjust(1)

    await callback.message.delete()
    await callback.message.answer_invoice(
        title="Пакет токенов",
        description="10 000 токенов для генерации изображений",
        payload="tokens_10000",
        currency="XTR",
        prices=[
            LabeledPrice(label="10 000 токенов", amount=10),
        ],
        provider_token="",
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment

    if payment.currency != "XTR":
        return

    if payment.invoice_payload == "tokens_10000":
        # Тут начислить пользователю 10_000 токенов
        # telegram_id = message.from_user.id
        pass

    await message.answer("Оплата прошла успешно. Токены начислены.")
