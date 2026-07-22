from src.types.base import ImmutableDTO

__all__ = ["UserResponseIdDTO", "UserDTO", "UserCreateDTO"]


class UserResponseIdDTO(ImmutableDTO):
    telegram_id: int


class UserDTO(UserResponseIdDTO):
    username: str | None
    first_name: str | None
    last_name: str | None
    token_balance: int
    tokens_spent: int


class UserCreateDTO(UserResponseIdDTO):
    username: str | None
    first_name: str | None
    last_name: str | None
