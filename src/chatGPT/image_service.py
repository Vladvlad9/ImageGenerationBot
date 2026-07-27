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
        prompt = ("Use the first image with the white background as the base for the composition and visual style. Preserve the white background, black-and-white manga aesthetic, fine ink linework, cross-hatching, contrast, placement of all elements, floating leaves, and the character on the right exactly as they are."
                  "Replace only the character on the left with the character from the second image with the blue background. Accurately preserve the character’s recognizable design: the elongated white bone-like helmet with horns and sharp projections, light layered armor, long purple ribbons, and the large blade held in their hands. Redraw this character in the highly detailed black-and-white manga style of the first image, using fine ink lines, cross-hatching, and deep black shadows instead of color and glowing effects."
                  "Place the new character on the left in approximately the same position and at the same scale as the original left character. Show the character in side profile, turned to the right and facing the character on the right. Preserve natural anatomy and the important details of the armor, helmet, ribbons, and weapon. Remove the blue background, colored lighting, smoke, and game-like visual effects from the second image. Do not change anything else in the first image. Wide horizontal composition, high resolution, crisp professional manga illustration."
                  "Negative prompt: colored image, blue background, purple background, 3D render, video-game graphics, neon glow, blur, altered right character, changed composition, additional characters, extra limbs, deformed hands, incorrect weapon, cropped head, text, logo, watermark.")
        if style_prompt:
            prompt = f"{prompt}\nAdditional style instruction: {style_prompt}"

        user_image = BytesIO(image_bytes)
        user_image.name = "user-image.png"
        style_image = BytesIO(style_image_bytes)
        style_image.name = "style-reference.png"

        response = await self._client.images.edit(
            model=self._model,
            image=[user_image, style_image],
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
        aspect_ratio: str = "1:1",
        quality: str = "low",
) -> ImageGenerationService:
    return ImageGenerationService(
        api_key=settings.GPT.API_KEY or os.getenv("OPENAI_API_KEY", ""),
        model=settings.GPT.MODEL,
        size=_IMAGE_SIZE_BY_ASPECT_RATIO.get(aspect_ratio, settings.GPT.SIZE),
        quality=quality if quality in {"low", "medium", "high", "auto"} else "low",
    )
