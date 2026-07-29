from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import Style
from src.repos.alchemy import BaseRepo

__all__ = ["StyleRepo"]


class StyleRepo(BaseRepo[Style]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Style)

    async def get_by_file_id(self, file_id: str) -> Style | None:
        return await self._session.scalar(
            select(Style)
            .where(
                Style.file_id == file_id,
                Style.deleted_at.is_(None),
            )
        )

    async def get_list(self) -> list[Style]:
        result = await self._session.scalars(
            select(Style)
            .where(Style.deleted_at.is_(None))
            .order_by(Style.created_at)
        )
        return list(result.all())
