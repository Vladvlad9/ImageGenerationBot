from sqlalchemy.ext.asyncio import AsyncSession

from src.services.promo_code import PromoCodeService
from src.enums import PromoCodeActivationStatus
from src.types import (
    PromoCodeDTO,
    PromoCodeNameDTO,
)

__all__ = ["PromoCodeServiceController"]


class PromoCodeServiceController:
    def __init__(self, session: AsyncSession):
        self.promo_code_controller = PromoCodeService(session=session)

    async def get(self, data: PromoCodeNameDTO) -> PromoCodeDTO | None:
        return await self.promo_code_controller.get(data=data)

    async def activate(self, data: PromoCodeNameDTO, telegram_id: int) -> str:
        result = await self.promo_code_controller.activate(data=data, telegram_id=telegram_id)

        if result.status == PromoCodeActivationStatus.ACTIVATED:
            text = (
                f"Вы активировали промокод: <b>{data.code}</b>\n\n"
                f"✅ Начислено токенов: <b>{result.tokens_amount}</b>"
            )
        elif result.status == PromoCodeActivationStatus.ALREADY_USED:
            text = ("😔 Промокод уже использован\n\n"
                    "❗️ Вы уже активировали этот промокод максимальное количество раз")
        elif result.status == PromoCodeActivationStatus.INVALID_REWARD:
            text = ("😔 Промокод временно недоступен\n\n"
                    "❗️ Для него не настроено количество токенов")
        elif result.status == PromoCodeActivationStatus.USER_NOT_FOUND:
            text = ("😔 Не удалось начислить токены\n\n"
                    "❗️ Пользователь не найден")
        else:
            text = ("😔 Промокод не найден\n\n"
                    "❗️ Промокод не существует или он был активирован ранее")

        return text
