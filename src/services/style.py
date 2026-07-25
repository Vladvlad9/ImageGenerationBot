from sqlalchemy.ext.asyncio import AsyncSession

from src.repos.alchemy import StyleRepo

__all__ = ["StyleServices"]


class StyleServices:
    def __init__(self, session: AsyncSession):
        self._repo = StyleRepo(session=session)

    async def get_list(self):
        return await self._repo.get_list()
