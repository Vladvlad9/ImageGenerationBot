from settings._base import BaseSettingsConfig

__all__ = ["DonationalertsSettings"]


class DonationalertsSettings(BaseSettingsConfig, env_prefix="DONATIONALERTS_"):
    LINK: str
