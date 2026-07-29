from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import PromoCode, PromoCodeUsage, User
from src.repos.alchemy import BaseRepo

__all__ = ["PromoCodeRepo"]


class PromoCodeRepo(BaseRepo[PromoCode]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=PromoCode)

    async def get_active(self, code: str, now: datetime) -> PromoCode | None:
        return await self._session.scalar(
            select(PromoCode).where(*self._active_filters(code=code, now=now))
        )

    async def get_active_for_update(self, code: str, now: datetime) -> PromoCode | None:
        return await self._session.scalar(
            select(PromoCode)
            .where(*self._active_filters(code=code, now=now))
            .with_for_update()
        )

    async def count_user_usages(self, promocode_id: UUID, user_id: int) -> int:
        return await self._session.scalar(
            select(func.count(PromoCodeUsage.id)).where(
                PromoCodeUsage.promocode_id == promocode_id,
                PromoCodeUsage.user_id == user_id,
            )
        )

    async def add_user_tokens(self, telegram_id: int, tokens: int) -> bool:
        result = await self._session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(token_balance=User.token_balance + tokens)
            .returning(User.telegram_id)
        )
        return result.scalar_one_or_none() is not None

    def add_usage(self, promocode_id: UUID, user_id: int) -> None:
        self._session.add(
            PromoCodeUsage(
                promocode_id=promocode_id,
                user_id=user_id,
            )
        )

    @staticmethod
    def increment_used_count(promo_code: PromoCode, amount: int = 1) -> None:
        promo_code.used_count += amount

    @staticmethod
    def _active_filters(code: str, now: datetime) -> tuple:
        return (
            PromoCode.code == code,
            PromoCode.status == "active",
            or_(PromoCode.starts_at.is_(None), PromoCode.starts_at <= now),
            or_(PromoCode.expires_at.is_(None), PromoCode.expires_at >= now),
            or_(
                PromoCode.max_uses.is_(None),
                PromoCode.used_count < PromoCode.max_uses,
            ),
        )
