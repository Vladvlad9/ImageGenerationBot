from typing import Protocol


class ImageGenerationProtocol(Protocol):
    async def generate(self, prompt: str) -> bytes:
        ...
