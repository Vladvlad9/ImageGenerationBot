from settings._base import BaseSettingsConfig

__all__ = ["BotSettings"]


class BotSettings(BaseSettingsConfig, env_prefix="BOT_"):
    TOKEN: str