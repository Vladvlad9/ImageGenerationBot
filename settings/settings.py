from pathlib import Path
from typing import Annotated

from pydantic import Field

from settings._base import BaseSettingsConfig
from settings.bot import BotSettings

__all__ = ['settings']


class Settings(BaseSettingsConfig):
    BASE_DIR: Path = Path(__file__).parent.parent

    BOT: Annotated[BotSettings, Field(default_factory=BotSettings)]


settings = Settings()
