from pydantic import PostgresDsn

from settings._base import BaseSettingsConfig

__all__ = ["DataBaseSettings"]


class DataBaseSettings(BaseSettingsConfig, env_prefix="DATABASE_"):
    POSTGRES_DSN: PostgresDsn
