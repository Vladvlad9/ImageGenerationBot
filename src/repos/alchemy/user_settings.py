from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import UserSettings
from src.repos.alchemy import BaseRepo

__all__ = ["UserSettingsRepo"]


class UserSettingsRepo(BaseRepo[UserSettings]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=UserSettings)
