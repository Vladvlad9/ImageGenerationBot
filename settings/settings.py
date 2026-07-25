from pathlib import Path
from typing import Annotated

from pydantic import Field

from settings._base import BaseSettingsConfig
from settings.storage import StorageSettings
from settings.database import DataBaseSettings
from settings.gpt import GPTSettings
from settings.bot import BotSettings
from settings.redis import RedisSettings

__all__ = ['settings']


class Settings(BaseSettingsConfig):
    BASE_DIR: Path = Path(__file__).parent.parent

    BOT: Annotated[BotSettings, Field(default_factory=BotSettings)]
    GPT: Annotated[GPTSettings, Field(default_factory=GPTSettings)]
    DATABASE: Annotated[DataBaseSettings, Field(default_factory=DataBaseSettings)]
    REDIS: Annotated[RedisSettings, Field(default_factory=RedisSettings)]
    STORAGE: Annotated[StorageSettings, Field(default_factory=StorageSettings)]


settings = Settings()
