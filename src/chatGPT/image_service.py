import asyncio
import base64
import os
from pathlib import Path
from typing import Literal
from uuid import uuid4

from openai import AsyncOpenAI

ImageQuality = Literal[
    "low",
    "medium",
    "high",
    "auto",
]


class ImageGenerationService:

    def __init__(self, api_key: str, model: str, size: str):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._size = size

    async def generate(self, prompt: str) -> bytes:
        response = await self._client.images.generate(
            model=self._model,
            prompt=prompt,
            size=self._size,
            n=1,
        )
        image_b64 = response.data[0].b64_json
        return base64.b64decode(image_b64)


class ImageGenerator:
    def __init__(
            self,
            api_key: str | None = None,
            model: str = "gpt-image-2",
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "Переменная OPENAI_API_KEY не установлена."
            )

    async def generate(
            self,
            prompt: str,
            output_directory: str = "generated",
            size: str = "1024x1536",
            quality: ImageQuality = "medium",
    ) -> dict[str, str]:
        if not prompt.strip():
            raise ValueError("Промпт не должен быть пустым.")

        directory = Path(output_directory)
        await asyncio.to_thread(
            directory.mkdir,
            parents=True,
            exist_ok=True,
        )

        filename = f"{uuid4().hex}.png"
        output_path = directory / filename

        async with AsyncOpenAI(
                api_key=self.api_key,
        ) as client:
            response = await client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality=quality,
                output_format="png",
                n=1,
            )

        if not response.data:
            raise RuntimeError(
                "OpenAI API вернул пустой результат."
            )

        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise RuntimeError(
                "OpenAI API не вернул данные изображения."
            )

        image_bytes = base64.b64decode(
            image_base64,
            validate=True,
        )

        await asyncio.to_thread(
            output_path.write_bytes,
            image_bytes,
        )

        return {
            "path": str(output_path.resolve()),
            "filename": filename,
            "model": self.model,
            "size": size,
            "quality": quality,
        }
