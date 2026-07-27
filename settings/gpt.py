from settings._base import BaseSettingsConfig

__all__ = ["GPTSettings"]


class GPTSettings(BaseSettingsConfig, env_prefix="GPT_"):
    API_KEY: str
    MODEL: str
    SIZE: str
    MIN_STYLE_IMAGE_GENERATION_TOKENS: int
