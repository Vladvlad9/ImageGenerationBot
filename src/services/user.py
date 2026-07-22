from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.alchemy.models import User, UserSettings
from src.repos.alchemy import UserRepo
from src.types.user import UserCreateDTO, UserDTO

__all__ = ["UserServices"]

from src.types.user.user_settings import UserSettingsCreateDTO


class UserServices:
    def __init__(self, session: AsyncSession):
        self._repo = UserRepo(session=session)

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
