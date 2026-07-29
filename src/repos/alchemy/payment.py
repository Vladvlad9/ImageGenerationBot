from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import Payment, User
from src.repos.alchemy import BaseRepo

__all__ = ["PaymentRepo"]


class PaymentRepo(BaseRepo[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Payment)

    async def get_by_provider_payment_id(self, provider_payment_id: str) -> Payment | None:
        return await self._session.scalar(
            select(Payment).where(Payment.provider_payment_id == provider_payment_id)
        )

    async def add_user_tokens(self, telegram_id: int, tokens: int) -> int | None:
        result = await self._session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(token_balance=User.token_balance + tokens)
            .returning(User.token_balance)
        )
        return result.scalar_one_or_none()

    def add_telegram_stars_payment(
        self,
        user_id: int,
        amount: int,
        provider_payment_id: str,
        description: str,
    ) -> None:
        self._session.add(
            Payment(
                user_id=user_id,
                amount=amount,
                currency="XTR",
                status="paid",
                provider="telegram_stars",
                provider_payment_id=provider_payment_id,
                description=description,
            )
        )
