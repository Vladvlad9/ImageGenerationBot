from enum import StrEnum

__all__ = ["ImageAspectRatio"]


class ImageAspectRatio(StrEnum):
    AUTO = "auto"
    ONE_TO_ONE = "1:1"
    TWO_TO_THREE = "2:3"
    THREE_TO_TWO = "3:2"
    THREE_TO_FOUR = "3:4"
    FOUR_TO_THREE = "4:3"
    TWO_TO_ONE = "2:1"
    NINE_TO_SIXTEEN = "9:16"
    SIXTEEN_TO_NINE = "16:9"
