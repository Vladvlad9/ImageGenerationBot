import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from aiogram import Bot

from settings import settings
from src.chatGPT.image_service import build_image_generation_service
from src.enums import ImageAspectRatio, ImageQuality
from src.services.user import UserServices
from src.storage.storage import StorageAppWrite

__all__ = [
    "ImageGenerationFailedError",
    "NotEnoughTokensError",
    "StyleImageGenerationResult",
    "StyleImageGenerationService",
]

logger = logging.getLogger(__name__)


class NotEnoughTokensError(Exception):
    def __init__(self, current_balance: int, required_balance: int) -> None:
        self.current_balance = current_balance
        self.required_balance = required_balance
        super().__init__(
            f"Not enough tokens: current={current_balance}, required={required_balance}"
        )


class ImageGenerationFailedError(Exception):
    """Raised when generation fails after tokens were already spent.

    Carries whether the refund itself succeeded so the handler can tell
    the user accurately (refund failure is rare but must not be silently
    reported as "your tokens are back" if it isn't true).
    """

    def __init__(
            self,
            original_error: Exception,
            refunded: bool,
            remaining_token_balance: int | None = None,
    ) -> None:
        self.original_error = original_error
        self.refunded = refunded
        self.remaining_token_balance = remaining_token_balance
        super().__init__(str(original_error))


@dataclass(frozen=True)
class StyleImageGenerationResult:
    image_bytes: bytes
    usage: Any | None
    cost_usd: float | None
    remaining_token_balance: int | None


class StyleImageGenerationService:
    def __init__(
            self,
            bot: Bot,
            user_service: UserServices,
            storage: StorageAppWrite | None = None,
            image_generator_factory: Callable = build_image_generation_service,
    ) -> None:
        self._bot = bot
        self._user_service = user_service
        self._storage = storage or StorageAppWrite(bucket_id=settings.STORAGE.BUCKET_ID)
        self._image_generator_factory = image_generator_factory

    async def generate(
            self,
            telegram_id: int,
            telegram_photo_file_id: str,
            style_file_id: str,
            style_prompt: str | None,
    ) -> StyleImageGenerationResult:
        user = await self._user_service.get(telegram_id=telegram_id)

        remaining_token_balance = await self._spend_generation_tokens(telegram_id=telegram_id)
        if remaining_token_balance is None:
            await self._raise_insufficient_tokens(telegram_id=telegram_id)

        try:
            user_image_bytes = await self._download_telegram_photo(file_id=telegram_photo_file_id)
            style_image_bytes = await self._storage.get_file_view(file_id=style_file_id)

            image_generator = self._image_generator_factory(
                aspect_ratio=self._get_user_aspect_ratio(user=user),
                quality=self._get_user_image_quality(user=user),
            )
            image_bytes = await image_generator.edit_with_style(
                image_bytes=user_image_bytes,
                style_image_bytes=style_image_bytes,
                style_prompt=style_prompt,
            )
        except Exception as error:
            refunded_balance = await self._safe_refund_generation_tokens(telegram_id=telegram_id)
            raise ImageGenerationFailedError(
                original_error=error,
                refunded=refunded_balance is not None,
                remaining_token_balance=refunded_balance,
            ) from error

        return StyleImageGenerationResult(
            image_bytes=image_bytes,
            usage=image_generator.last_usage,
            cost_usd=image_generator.last_cost_usd,
            remaining_token_balance=remaining_token_balance,
        )

    async def _download_telegram_photo(self, file_id: str) -> bytes:
        image_io = await self._bot.download(file_id)
        if image_io is None:
            raise RuntimeError("Не удалось скачать фото пользователя.")

        return image_io.getvalue()

    @staticmethod
    def _get_user_aspect_ratio(user: Any | None) -> str:
        if user and user.settings:
            return user.settings.image_aspect_ratio

        return ImageAspectRatio.ONE_TO_ONE

    @staticmethod
    def _get_user_image_quality(user: Any | None) -> str:
        if user and user.settings:
            return user.settings.image_quality

        return ImageQuality.LOW

    async def _raise_insufficient_tokens(self, telegram_id: int) -> None:
        # Re-fetch the balance for an accurate message: the atomic UPDATE
        # already told us it wasn't enough, this is purely for display.
        user = await self._user_service.get(telegram_id=telegram_id)
        token_balance = user.token_balance if user and user.token_balance is not None else 0
        raise NotEnoughTokensError(
            current_balance=token_balance,
            required_balance=settings.GPT.MIN_STYLE_IMAGE_GENERATION_TOKENS,
        )

    async def _spend_generation_tokens(self, telegram_id: int) -> int | None:
        return await self._user_service.spend_tokens(
            telegram_id=telegram_id,
            tokens=settings.GPT.MIN_STYLE_IMAGE_GENERATION_TOKENS,
        )

    async def _safe_refund_generation_tokens(self, telegram_id: int) -> int | None:
        try:
            return await self._user_service.refund_tokens(
                telegram_id=telegram_id,
                tokens=settings.GPT.MIN_STYLE_IMAGE_GENERATION_TOKENS,
            )
        except Exception:
            # Never let a refund failure mask the real (generation) error -
            # log it and let the caller report refunded=False instead.
            logger.exception(
                "Failed to refund tokens after failed generation: telegram_id=%s",
                telegram_id,
            )
            return None
