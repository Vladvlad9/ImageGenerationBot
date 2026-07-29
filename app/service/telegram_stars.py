from aiogram.types import SuccessfulPayment
from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import TelegramStarsPaymentStatus
from src.services import TelegramStarsService

__all__ = ["TelegramStarsServiceController"]


class TelegramStarsServiceController:
    def __init__(self, session: AsyncSession):
        self.telegram_stars_controller = TelegramStarsService(session=session)

    async def apply_payment(self, telegram_id: int, payment: SuccessfulPayment) -> str | None:
        result = await self.telegram_stars_controller.apply_payment(
            telegram_id=telegram_id,
            payment=payment,
        )

        if result.status == TelegramStarsPaymentStatus.APPLIED:
            formatted_tokens = f"{result.tokens:,}".replace(",", " ")
            formatted_balance = f"{result.balance:,}".replace(",", " ")
            return (
                "Оплата прошла успешно.\n\n"
                f"Начислено: {formatted_tokens} токенов\n"
                f"Баланс: {formatted_balance} токенов"
            )

        if result.status == TelegramStarsPaymentStatus.DUPLICATE:
            return None

        if result.status == TelegramStarsPaymentStatus.USER_NOT_FOUND:
            return "Оплата прошла успешно, но не удалось начислить токены. Напишите в поддержку."

        return "Не удалось проверить платеж. Напишите в поддержку."
