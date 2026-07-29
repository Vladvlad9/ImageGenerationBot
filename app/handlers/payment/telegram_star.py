from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard.payment import telegram_stars_keyboard
from app.service.telegram_stars import TelegramStarsServiceController
from src.enums import ButtonCallback
from src.types.payment_package import TOKEN_PACKAGES_BY_CALLBACK, TOKEN_PACKAGES_BY_PAYLOAD

router = Router(name='telegram_stars')


def _generation_label(generations: int) -> str:
    if generations % 10 == 1 and generations % 100 != 11:
        return "генерация"
    if 2 <= generations % 10 <= 4 and not 12 <= generations % 100 <= 14:
        return "генерации"
    return "генераций"


@router.callback_query(F.data == ButtonCallback.TELEGRAM)
async def telegram_stars(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите пакет генераций",
        reply_markup=telegram_stars_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.in_(TOKEN_PACKAGES_BY_CALLBACK.keys()))
async def buy_tokens(callback: CallbackQuery):
    package = TOKEN_PACKAGES_BY_CALLBACK[callback.data]
    formatted_tokens = f"{package.tokens:,}".replace(",", " ")
    generation_title = f"{package.generations} {_generation_label(package.generations)}"

    await callback.message.answer_invoice(
        title=generation_title,
        description=f"{generation_title} для изображений. На баланс начислится {formatted_tokens} токенов.",
        payload=package.payload,
        currency="XTR",
        prices=[
            LabeledPrice(label=generation_title, amount=package.stars),
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
