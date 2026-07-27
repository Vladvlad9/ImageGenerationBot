import os

from openai import AsyncOpenAI

from settings import settings

__all__ = ["ChatGPTConnectionService", "build_chat_gpt_connection_service"]


class ChatGPTConnectionService:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is not configured.")

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def test_connection(self) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "Ты отвечаешь коротко и только на русском языке.",
                },
                {
                    "role": "user",
                    "content": "Ответь одной фразой: подключение к ChatGPT работает.",
                },
            ],
            max_tokens=30,
            temperature=0,
        )

        message = response.choices[0].message.content if response.choices else None
        if not message:
            raise RuntimeError("OpenAI API не вернул текстовый ответ.")

        return message.strip()


def build_chat_gpt_connection_service() -> ChatGPTConnectionService:
    return ChatGPTConnectionService(
        api_key=settings.GPT.API_KEY or os.getenv("OPENAI_API_KEY", ""),
        model=settings.GPT.CHAT_MODEL,
    )
