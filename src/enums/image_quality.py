from enum import StrEnum

__all__ = ["ImageQuality"]


class ImageQuality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
