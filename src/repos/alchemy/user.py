from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import User
from src.repos.alchemy import BaseRepo

__all__ = ["UserRepo"]


class UserRepo(BaseRepo[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=User)

    async def spend_tokens(self, telegram_id: int, tokens: int) -> int | None:
        try:
            result = await self._session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(
                    token_balance=User.token_balance - tokens,
                    tokens_spent=User.tokens_spent + tokens,
                )
                .returning(User.token_balance)
            )
            await self._session.commit()
            return result.scalar_one_or_none()
        except Exception:
            await self._session.rollback()
            raise
