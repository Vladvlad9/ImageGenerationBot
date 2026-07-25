import base64
import os
from typing import Literal

from openai import AsyncOpenAI

from settings import settings

ImageQualityLiteral = Literal[
    "low",
    "medium",
    "high",
    "auto",
]

_IMAGE_SIZE_BY_ASPECT_RATIO = {
    "auto": "auto",
    "1:1": "1024x1024",
    "2:3": "1024x1536",
    "3:2": "1536x1024",
    "3:4": "1024x1536",
    "4:3": "1536x1024",
    "2:1": "1536x1024",
    "9:16": "1024x1536",
    "16:9": "1536x1024",
}


class ImageGenerationService:
    def __init__(
            self,
            api_key: str,
            model: str,
            size: str,
            quality: ImageQualityLiteral = "low",
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is not configured.")

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._size = size
        self._quality = quality

    async def generate(self, prompt: str) -> bytes:
        if not prompt.strip():
            raise ValueError("Промпт не должен быть пустым.")

        response = await self._client.images.generate(
            model=self._model,
            prompt=prompt,
            size=self._size,
            quality=self._quality,
            output_format="png",
            n=1,
        )

        if not response.data or not response.data[0].b64_json:
            raise RuntimeError("OpenAI API не вернул данные изображения.")

        return base64.b64decode(
            response.data[0].b64_json,
            validate=True,
        )


def build_image_generation_service(
        aspect_ratio: str = "1:1",
        quality: str = "low",
) -> ImageGenerationService:
    return ImageGenerationService(
        api_key=settings.GPT.API_KEY or os.getenv("OPENAI_API_KEY", ""),
        model=settings.GPT.MODEL,
        size=_IMAGE_SIZE_BY_ASPECT_RATIO.get(aspect_ratio, settings.GPT.SIZE),
        quality=quality if quality in {"low", "medium", "high", "auto"} else "low",
    )
