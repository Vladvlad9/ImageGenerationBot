from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import User
from src.repos.alchemy import UserRepo
from src.types.user import UserCreateDTO, UserDTO

__all__ = ["UserServices"]


class UserServices:
    def __init__(self, session: AsyncSession):
        self._repo = UserRepo(session=session)

    async def get(self, telegram_id: int):
        return await self._repo.get(filters=[User.telegram_id == telegram_id])

    async def create(self, data: UserCreateDTO):
        try:
            user = await self._repo.insert(obj=data.model_dump())
            return UserDTO.model_validate(obj=user)
        except IntegrityError as e:
            print(e)
            # raise InternalServerError(name="Create_Car")

    async def update(self):
        pass

    async def delete(self):
        pass
