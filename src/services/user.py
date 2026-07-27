from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.alchemy.models import User, UserSettings
from src.repos.alchemy import UserRepo
from src.types.user import UserCreateDTO, UserDTO
from src.types.user.user_settings import UserSettingsCreateDTO

__all__ = ["UserServices"]


class UserServices:
    def __init__(self, session: AsyncSession):
        self._repo = UserRepo(session=session)

    @staticmethod
    async def user_data(message: Message) -> UserCreateDTO:
        return UserCreateDTO(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )

    @staticmethod
    async def update_token_balance(current_balance: int, new_balance: int) -> int:
        return current_balance - new_balance

    async def get(self, telegram_id: int) -> UserDTO | None:
        filters = [User.telegram_id == telegram_id]
        options = [joinedload(User.settings)]
        user = await self._repo.get(filters=filters, options=options)
        if user is None:
            return None

        return UserDTO.model_validate(obj=user)

    async def create(self, data: UserCreateDTO):
        try:
            settings_data = UserSettingsCreateDTO()

            user = User(
                **data.model_dump(),
                settings=UserSettings(**settings_data.model_dump()),
            )
            user = await self._repo.add(obj=user)
            return UserDTO.model_validate(obj=user)
        except IntegrityError as e:
            print(e)
            # raise InternalServerError(name="User")

    async def update(self):
        pass

    async def delete(self):
        pass

    async def spend_tokens(self, telegram_id: int, tokens: int) -> int | None:
        if tokens <= 0:
            return None

        return await self._repo.spend_tokens(
            telegram_id=telegram_id,
            tokens=tokens,
        )
