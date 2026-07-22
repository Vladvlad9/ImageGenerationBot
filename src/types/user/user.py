from src.types.base import ImmutableDTO

__all__ = ["UserResponseIdDTO", "UserDTO", "UserCreateDTO"]


class UserResponseIdDTO(ImmutableDTO):
    telegram_id: int


class UserDTO(UserResponseIdDTO):
    username: str
    first_name: str
    last_name: str
    token_balance: int
    tokens_spent: int


class UserCreateDTO(UserResponseIdDTO):
    username: str
    first_name: str
    last_name: str
