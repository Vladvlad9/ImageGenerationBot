from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import UserSettings
from src.repos.alchemy import UserSettingsRepo

from src.types.user import UserSettingsBaseDTO, UserSettingsUpdateDTO

__all__ = ["UserSettingsServices"]


class UserSettingsServices:
    def __init__(self, session: AsyncSession):
        self._repo = UserSettingsRepo(session=session)

    async def get(self, telegram_id: int):
        pass

    async def insert(self, telegram_id: int):
        pass

    async def update(self, telegram_id: int, data: UserSettingsUpdateDTO):
        filters = [UserSettings.telegram_id == telegram_id]
        obj = data.model_dump(exclude_unset=True, exclude_none=True)

        settings_user = await self._repo.update(obj=obj, filters=filters)
        return UserSettingsBaseDTO.model_validate(obj=settings_user)
