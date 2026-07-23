from src.types.base import ImmutableDTO

__all__ = ["UserSettingsCreateDTO", "UserSettingsUpdateDTO", "UserSettingsBaseDTO"]


class UserSettingsBaseDTO(ImmutableDTO):
    image_aspect_ratio: str
    image_quality: str
    language: str
    notify_on_finish: bool


class UserSettingsCreateDTO(ImmutableDTO):
    image_aspect_ratio: str = "1:1"
    image_quality: str = "auto"
    language: str = "ru"
    notify_on_finish: bool = True


class UserSettingsUpdateDTO(ImmutableDTO):
    image_aspect_ratio: str | None = None
    image_quality: str | None = None
    language: str | None = None
    notify_on_finish: bool | None = None
