from pathlib import Path
from typing import Annotated

from pydantic import Field

from settings._base import BaseSettingsConfig
from settings.database import DataBaseSettings
from settings.gpt import GPTSettings
from settings.bot import BotSettings

__all__ = ['settings']

from settings.redis import RedisSettings


class Settings(BaseSettingsConfig):
    BASE_DIR: Path = Path(__file__).parent.parent

    BOT: Annotated[BotSettings, Field(default_factory=BotSettings)]
    GPT: Annotated[GPTSettings, Field(default_factory=GPTSettings)]
    DATABASE: Annotated[DataBaseSettings, Field(default_factory=DataBaseSettings)]
    REDIS: Annotated[RedisSettings, Field(default_factory=RedisSettings)]


settings = Settings()
