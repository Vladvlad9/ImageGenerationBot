from enum import StrEnum

__all__ = ['ButtonCallback']


class ButtonCallback(StrEnum):
    GENERATE = "generate"
    HELP = "help"
    PROFILE = "profile"
    BACK = "back"
    QUALITY = "quality"
    FORMAT = "format"
