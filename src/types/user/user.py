from src.types.base import ImmutableDTO
from src.types.user.user_settings import UserSettingsBaseDTO

__all__ = ["UserResponseIdDTO", "UserDTO", "UserCreateDTO"]


class UserResponseIdDTO(ImmutableDTO):
    telegram_id: int


class UserDTO(UserResponseIdDTO):
    username: str | None
    first_name: str | None
    last_name: str | None
    token_balance: int
    tokens_spent: int

    settings: UserSettingsBaseDTO | None


class UserCreateDTO(UserResponseIdDTO):
    username: str | None
    first_name: str | None
    last_name: str | None
