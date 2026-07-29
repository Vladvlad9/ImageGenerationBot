from src.types.base import ImmutableDTO
from src.types.user.user_settings import UserSettingsBaseDTO

__all__ = ["UserResponseIdDTO", "UserDTO", "UserCreateDTO", "UserUpdateDTO"]


class UserResponseIdDTO(ImmutableDTO):
    telegram_id: int


class UserDTO(UserResponseIdDTO):
    username: str | None
    first_name: str | None
    last_name: str | None
    token_balance: int | None
    tokens_spent: int | None

    settings: UserSettingsBaseDTO | None


class UserCreateDTO(UserResponseIdDTO):
    username: str | None
    first_name: str | None
    last_name: str | None
    token_balance: int | None


class UserUpdateDTO(UserResponseIdDTO):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    token_balance: int | None = None
