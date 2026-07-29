from aiogram.types import SuccessfulPayment
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import TelegramStarsPaymentStatus
from src.repos.alchemy import PaymentRepo
from src.types import TelegramStarsPaymentResultDTO
from src.types.payment_package import TOKEN_PACKAGES_BY_PAYLOAD

__all__ = ["TelegramStarsService"]


class TelegramStarsService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = PaymentRepo(session=session)

    async def apply_payment(
        self,
        telegram_id: int,
        payment: SuccessfulPayment,
    ) -> TelegramStarsPaymentResultDTO:
        package = TOKEN_PACKAGES_BY_PAYLOAD.get(payment.invoice_payload)

        if (
            payment.currency != "XTR"
            or package is None
            or payment.total_amount != package.stars
        ):
            return TelegramStarsPaymentResultDTO(status=TelegramStarsPaymentStatus.INVALID_PAYMENT)

        try:
            async with self._session.begin():
                provider_payment_id = payment.telegram_payment_charge_id
                existing_payment = await self._repo.get_by_provider_payment_id(
                    provider_payment_id=provider_payment_id
                )

                if existing_payment is not None:
                    return TelegramStarsPaymentResultDTO(status=TelegramStarsPaymentStatus.DUPLICATE)

                new_balance = await self._repo.add_user_tokens(
                    telegram_id=telegram_id,
                    tokens=package.tokens,
                )

                if new_balance is None:
                    return TelegramStarsPaymentResultDTO(status=TelegramStarsPaymentStatus.USER_NOT_FOUND)

                self._repo.add_telegram_stars_payment(
                    user_id=telegram_id,
                    amount=payment.total_amount,
                    provider_payment_id=provider_payment_id,
                    description=f"Покупка {package.tokens} токенов за Telegram Stars",
                )

                return TelegramStarsPaymentResultDTO(
                    status=TelegramStarsPaymentStatus.APPLIED,
                    tokens=package.tokens,
                    balance=new_balance,
                )
        except IntegrityError:
            await self._session.rollback()
            return TelegramStarsPaymentResultDTO(status=TelegramStarsPaymentStatus.DUPLICATE)
