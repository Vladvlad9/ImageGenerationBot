from settings._base import BaseSettingsConfig

__all__ = ["StorageSettings"]


class StorageSettings(BaseSettingsConfig, env_prefix="STORAGE_"):
    ENDPOINT: str
    PROJECT: str
    KEY: str
    BUCKET_ID: str
