import base64
import os
from io import BytesIO
from typing import Any, Literal

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

_TOKEN_PRICES_PER_1M = {
    "gpt-image-2": {
        "text_input": 5.00,
        "image_input": 8.00,
        "text_output": 0.00,
        "image_output": 30.00,
    },
    "gpt-image-1.5": {
        "text_input": 5.00,
        "image_input": 8.00,
        "text_output": 10.00,
        "image_output": 32.00,
    },
    "chatgpt-image-latest": {
        "text_input": 5.00,
        "image_input": 8.00,
        "text_output": 10.00,
        "image_output": 32.00,
    },
    "gpt-image-1": {
        "text_input": 5.00,
        "image_input": 10.00,
        "text_output": 0.00,
        "image_output": 40.00,
    },
    "gpt-image-1-mini": {
        "text_input": 2.00,
        "image_input": 2.50,
        "text_output": 0.00,
        "image_output": 8.00,
    },
}

_PER_IMAGE_PRICES = {
    "gpt-image-1.5": {
        "low": {"1024x1024": 0.009, "1024x1536": 0.013, "1536x1024": 0.013},
        "medium": {"1024x1024": 0.034, "1024x1536": 0.05, "1536x1024": 0.05},
        "high": {"1024x1024": 0.133, "1024x1536": 0.20, "1536x1024": 0.20},
    },
    "chatgpt-image-latest": {
        "low": {"1024x1024": 0.009, "1024x1536": 0.013, "1536x1024": 0.013},
        "medium": {"1024x1024": 0.034, "1024x1536": 0.05, "1536x1024": 0.05},
        "high": {"1024x1024": 0.133, "1024x1536": 0.20, "1536x1024": 0.20},
    },
    "gpt-image-1-mini": {
        "low": {"1024x1024": 0.005, "1024x1536": 0.006, "1536x1024": 0.006},
        "medium": {"1024x1024": 0.011, "1024x1536": 0.015, "1536x1024": 0.015},
        "high": {"1024x1024": 0.036, "1024x1536": 0.052, "1536x1024": 0.052},
    },
}


def _normalize_model(model: str) -> str:
    if model.startswith("gpt-image-2"):
        return "gpt-image-2"
    if model.startswith("gpt-image-1.5"):
        return "gpt-image-1.5"
    if model.startswith("gpt-image-1-mini"):
        return "gpt-image-1-mini"
    if model.startswith("gpt-image-1"):
        return "gpt-image-1"
    return model


def _estimate_cost_from_usage(model: str, usage: Any | None) -> float | None:
    if usage is None:
        return None

    prices = _TOKEN_PRICES_PER_1M.get(_normalize_model(model))
    if not prices:
        return None

    input_details = usage.input_tokens_details
    output_details = usage.output_tokens_details
    text_input_tokens = input_details.text_tokens
    image_input_tokens = input_details.image_tokens
    text_output_tokens = output_details.text_tokens if output_details else 0
    image_output_tokens = output_details.image_tokens if output_details else usage.output_tokens

    return (
        text_input_tokens * prices["text_input"]
        + image_input_tokens * prices["image_input"]
        + text_output_tokens * prices["text_output"]
        + image_output_tokens * prices["image_output"]
    ) / 1_000_000


def _estimate_cost_per_image(model: str, size: str, quality: str) -> float | None:
    model_prices = _PER_IMAGE_PRICES.get(_normalize_model(model))
    if not model_prices:
        return None

    return model_prices.get(quality, {}).get(size)


def format_image_generation_cost(cost_usd: float | None) -> str:
    if cost_usd is None:
        return ""

    return f"\nПримерная стоимость: ${cost_usd:.4f}"


def format_image_generation_tokens(usage: Any | None) -> str:
    if usage is None:
        return ""

    input_details = usage.input_tokens_details
    output_details = usage.output_tokens_details
    text_input_tokens = input_details.text_tokens
    image_input_tokens = input_details.image_tokens
    text_output_tokens = output_details.text_tokens if output_details else 0
    image_output_tokens = output_details.image_tokens if output_details else usage.output_tokens

    return (
        f"\nТокены: {usage.total_tokens}"
        f"\n- текст вход: {text_input_tokens}"
        f"\n- картинки вход: {image_input_tokens}"
        f"\n- текст выход: {text_output_tokens}"
        f"\n- картинка выход: {image_output_tokens}"
    )


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
        self._last_usage: Any | None = None
        self._last_cost_usd: float | None = None

    @property
    def last_cost_usd(self) -> float | None:
        return self._last_cost_usd

    @property
    def last_usage(self) -> Any | None:
        return self._last_usage

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

        self._last_usage = response.usage
        self._last_cost_usd = (
            _estimate_cost_from_usage(model=self._model, usage=response.usage)
            or _estimate_cost_per_image(
                model=self._model,
                size=self._size,
                quality=self._quality,
            )
        )

        return base64.b64decode(
            response.data[0].b64_json,
            validate=True,
        )

    async def edit_with_style(
            self,
            image_bytes: bytes,
            style_image_bytes: bytes,
            style_prompt: str | None = None,
    ) -> bytes:
        prompt = (
            "Use the first image as the source photo and the second image as the style reference. "
            "Create a new image that keeps every important detail from the source photo: the same "
            "character identity, face or head shape, pose, clothing, accessories, armor, weapons, "
            "colors where they matter for recognition, proportions, silhouette, small design marks, "
            "and overall composition. Render all of those details in the visual style, line quality, "
            "lighting, texture, mood, and finish of the style reference. Do not simplify the character "
            "or replace details with generic ones. Do not add text, logos, watermarks, extra people, "
            "extra limbs, or unrelated objects."
        )
        if style_prompt:
            prompt = f"{prompt}\nAdditional style instruction: {style_prompt}"

        source_image = BytesIO(image_bytes)
        source_image.name = "source-photo.png"
        style_image = BytesIO(style_image_bytes)
        style_image.name = "style-reference.png"

        response = await self._client.images.edit(
            model=self._model,
            image=[source_image, style_image],
            prompt=prompt,
            size=self._size,
            quality=self._quality,
            output_format="png",
            n=1,
        )

        if not response.data or not response.data[0].b64_json:
            raise RuntimeError("OpenAI API не вернул данные изображения.")

        self._last_usage = response.usage
        self._last_cost_usd = (
            _estimate_cost_from_usage(model=self._model, usage=response.usage)
            or _estimate_cost_per_image(
                model=self._model,
                size=self._size,
                quality=self._quality,
            )
        )

        return base64.b64decode(
            response.data[0].b64_json,
            validate=True,
        )

    async def replace_character_with_style(
            self,
            base_image_bytes: bytes,
            character_image_bytes: bytes,
            style_prompt: str | None = None,
    ) -> bytes:
        prompt = (
            "Use the first image as the base scene, composition, and final visual style. Use the "
            "second image as the replacement character reference. Replace only the main replaceable "
            "character in the base scene with the character from the second image. Keep the base "
            "scene's camera angle, framing, background, lighting style, rendering technique, and all "
            "other characters or objects unchanged. Preserve the replacement character's recognizable "
            "details from the second image: identity, silhouette, pose intent, face or head shape, "
            "clothing, armor, accessories, weapons, color accents needed for recognition, and small "
            "design marks. Adapt the replacement character naturally into the base scene at the right "
            "scale, perspective, and style. Do not change anything else in the base image. Do not add "
            "text, logos, watermarks, extra characters, extra limbs, deformed hands, or unrelated objects."
        )
        if style_prompt:
            prompt = f"{prompt}\nAdditional style instruction: {style_prompt}"

        base_image = BytesIO(base_image_bytes)
        base_image.name = "base-scene.png"
        character_image = BytesIO(character_image_bytes)
        character_image.name = "replacement-character.png"

        response = await self._client.images.edit(
            model=self._model,
            image=[base_image, character_image],
            prompt=prompt,
            size=self._size,
            quality=self._quality,
            output_format="png",
            n=1,
        )

        if not response.data or not response.data[0].b64_json:
            raise RuntimeError("OpenAI API не вернул данные изображения.")

        self._last_usage = response.usage
        self._last_cost_usd = (
            _estimate_cost_from_usage(model=self._model, usage=response.usage)
            or _estimate_cost_per_image(
                model=self._model,
                size=self._size,
                quality=self._quality,
            )
        )

        return base64.b64decode(
            response.data[0].b64_json,
            validate=True,
        )


def build_image_generation_service(
        aspect_ratio: str = "auto",
        quality: str = "low",
) -> ImageGenerationService:
    return ImageGenerationService(
        api_key=settings.GPT.API_KEY or os.getenv("OPENAI_API_KEY", ""),
        model=settings.GPT.MODEL,
        size=_IMAGE_SIZE_BY_ASPECT_RATIO.get(aspect_ratio, settings.GPT.SIZE),
        quality=quality if quality in {"low", "medium", "high", "auto"} else "low",
    )
