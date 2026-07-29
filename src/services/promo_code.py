from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import PromoCode
from src.enums import PromoCodeActivationStatus
from src.repos.alchemy import PromoCodeRepo

from src.types import (
    PromoCodeActivationResultDTO,
    PromoCodeDTO,
    PromoCodeUpdateUsedCountDTO,
)
from src.types.promocode import PromoCodeNameDTO

__all__ = ["PromoCodeService"]


class PromoCodeService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = PromoCodeRepo(session=session)

    async def get(self, data: PromoCodeNameDTO) -> PromoCodeDTO | None:
        now = datetime.now(timezone.utc)
        promo_code = await self._repo.get_active(code=data.code, now=now)

        if promo_code is None:
            return None

        return PromoCodeDTO.model_validate(obj=promo_code)

    async def activate(self, data: PromoCodeNameDTO, telegram_id: int) -> PromoCodeActivationResultDTO:
        now = datetime.now(timezone.utc)

        async with self._session.begin():
            promo_code = await self._repo.get_active_for_update(code=data.code, now=now)

            if promo_code is None:
                return PromoCodeActivationResultDTO(status=PromoCodeActivationStatus.NOT_FOUND)

            if self._has_invalid_reward(promo_code=promo_code):
                return PromoCodeActivationResultDTO(status=PromoCodeActivationStatus.INVALID_REWARD)

            if not await self._can_user_activate(promo_code=promo_code, telegram_id=telegram_id):
                return PromoCodeActivationResultDTO(status=PromoCodeActivationStatus.ALREADY_USED)

            user_updated = await self._repo.add_user_tokens(
                telegram_id=telegram_id,
                tokens=promo_code.tokens_amount,
            )

            if not user_updated:
                return PromoCodeActivationResultDTO(status=PromoCodeActivationStatus.USER_NOT_FOUND)

            self._repo.increment_used_count(promo_code=promo_code)
            self._repo.add_usage(promocode_id=promo_code.id, user_id=telegram_id)

            return PromoCodeActivationResultDTO(
                status=PromoCodeActivationStatus.ACTIVATED,
                promo_code=PromoCodeDTO.model_validate(obj=promo_code),
                tokens_amount=promo_code.tokens_amount,
            )

    async def update(self, data):
        pass

    async def update_used_count(self, data: PromoCodeUpdateUsedCountDTO) -> PromoCodeDTO:
        filters = [PromoCode.id == data.id]
        promo_code = await self._repo.update(
            filters=filters,
            obj={"used_count": PromoCode.used_count + data.used_count},
        )
        return PromoCodeDTO.model_validate(obj=promo_code)

    @staticmethod
    def _has_invalid_reward(promo_code: PromoCode) -> bool:
        return promo_code.tokens_amount is None or promo_code.tokens_amount <= 0

    async def _can_user_activate(self, promo_code: PromoCode, telegram_id: int) -> bool:
        if promo_code.max_uses_per_user is None:
            return True

        user_uses_count = await self._repo.count_user_usages(
            promocode_id=promo_code.id,
            user_id=telegram_id,
        )
        return user_uses_count < promo_code.max_uses_per_user
