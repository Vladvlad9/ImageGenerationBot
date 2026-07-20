from collections.abc import AsyncIterator

from uuid_utils import uuid7

from sqlalchemy import URL, NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

__all__ = ["AlchemyDBConnection"]


class AlchemyDBConnection:
    def __init__(self, url: URL | str):
        self.url = url
        self.engine: AsyncEngine = create_async_engine(
            url=self.url,
            pool_recycle=0,
            poolclass=NullPool,
            query_cache_size=0,
            connect_args={
                "prepared_statement_name_func": lambda: f"__asyncpg_{uuid7()}__",
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "command_timeout": 30,
            },
            execution_options={"isolation_level": "READ COMMITTED"},
        )
        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_maker() as session:
            yield session

    async def close(self) -> None:
        await self.engine.dispose()
