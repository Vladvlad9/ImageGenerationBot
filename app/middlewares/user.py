from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.config import alchemy_db_connection
from src.services.user import UserServices


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        async with alchemy_db_connection.session_maker() as session:
            data["session"] = session
            data["service"] = UserServices(session=session)
            return await handler(event, data)
