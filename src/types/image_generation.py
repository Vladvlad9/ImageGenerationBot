from typing import Protocol


class ImageGenerationProtocol(Protocol):
    async def generate(self, prompt: str) -> bytes:
        ...

    async def edit_with_style(
            self,
            image_bytes: bytes,
            style_image_bytes: bytes,
            style_prompt: str | None = None,
    ) -> bytes:
        ...
