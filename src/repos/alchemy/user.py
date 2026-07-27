from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.models import User
from src.repos.alchemy import BaseRepo

__all__ = ["UserRepo"]


class UserRepo(BaseRepo[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=User)

    async def spend_tokens(self, telegram_id: int, tokens: int) -> int | None:
        """Atomically spend tokens iff the user currently has enough.

        The balance check and the deduction happen in a single UPDATE
        statement, so this is safe under concurrent calls (e.g. a user
        double-tapping "generate"): Postgres serializes concurrent UPDATEs
        on the same row, so only one caller can ever observe
        `token_balance >= tokens` and successfully deduct.

        Returns the new balance, or None if the user doesn't exist or
        doesn't have enough tokens.
        """
        try:
            result = await self._session.execute(
                update(User)
                .where(
                    User.telegram_id == telegram_id,
                    User.token_balance >= tokens,
                )
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

    async def refund_tokens(self, telegram_id: int, tokens: int) -> int | None:
        """Atomically undo a prior spend_tokens() of the same amount.

        Adds tokens back to the balance and reverses tokens_spent, so
        analytics reflect net (not gross) spend. Single UPDATE, so it's
        safe under concurrent calls same as spend_tokens.

        Returns the new balance, or None if the user doesn't exist.
        """
        try:
            result = await self._session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(
                    token_balance=User.token_balance + tokens,
                    tokens_spent=User.tokens_spent - tokens,
                )
                .returning(User.token_balance)
            )
            await self._session.commit()
            return result.scalar_one_or_none()
        except Exception:
            await self._session.rollback()
            raise

    async def add_tokens(self, telegram_id: int, tokens: int) -> int | None:
        """Atomically add purchased tokens to the user's balance.

        Returns the new balance, or None if the user doesn't exist.
        """
        try:
            result = await self._session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(token_balance=User.token_balance + tokens)
                .returning(User.token_balance)
            )
            await self._session.commit()
            return result.scalar_one_or_none()
        except Exception:
            await self._session.rollback()
            raise
