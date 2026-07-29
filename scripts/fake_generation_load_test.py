import argparse
import asyncio
import base64
import os
import random
import statistics
import sys
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Defaults let this load test run without a real .env and without touching
# Telegram, Appwrite, Postgres, Redis, or OpenAI.
os.environ.setdefault("BOT_TOKEN", "fake-token")
os.environ.setdefault("GPT_API_KEY", "fake-key")
os.environ.setdefault("GPT_MODEL", "fake-model")
os.environ.setdefault("GPT_SIZE", "1024x1024")
os.environ.setdefault("GPT_MIN_STYLE_IMAGE_GENERATION_TOKENS", "5000")
os.environ.setdefault("DATABASE_POSTGRES_DSN", "postgresql+asyncpg://user:pass@localhost:5432/db")
os.environ.setdefault("REDIS_DSN", "redis://localhost:6379/0")
os.environ.setdefault("STORAGE_ENDPOINT", "https://example.com")
os.environ.setdefault("STORAGE_PROJECT", "fake-project")
os.environ.setdefault("STORAGE_KEY", "fake-key")
os.environ.setdefault("STORAGE_BUCKET_ID", "fake-bucket")

from src.services.style_image_generation import (  # noqa: E402
    ImageGenerationFailedError,
    NotEnoughTokensError,
    StyleImageGenerationService,
)


FAKE_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


@dataclass(frozen=True)
class LoadTestConfig:
    users: int
    concurrency: int
    generation_delay: float
    generation_jitter: float
    telegram_delay: float
    storage_delay: float
    fail_rate: float
    initial_balance: int


class FakeBot:
    def __init__(self, delay: float) -> None:
        self._delay = delay

    async def download(self, file_id: str) -> BytesIO:
        await asyncio.sleep(self._delay)
        return BytesIO(FAKE_PNG_BYTES)


class FakeStorage:
    def __init__(self, delay: float) -> None:
        self._delay = delay

    async def get_file_view(self, file_id: str) -> bytes:
        await asyncio.sleep(self._delay)
        return FAKE_PNG_BYTES


class FakeUserService:
    def __init__(self, initial_balance: int) -> None:
        self._initial_balance = initial_balance
        self._balances: dict[int, int] = {}
        self._lock = asyncio.Lock()

    async def get(self, telegram_id: int):
        async with self._lock:
            balance = self._balances.setdefault(telegram_id, self._initial_balance)

        return SimpleNamespace(
            token_balance=balance,
            settings=SimpleNamespace(
                image_aspect_ratio="1:1",
                image_quality="low",
            ),
        )

    async def spend_tokens(self, telegram_id: int, tokens: int) -> int | None:
        async with self._lock:
            balance = self._balances.setdefault(telegram_id, self._initial_balance)
            if balance < tokens:
                return None

            balance -= tokens
            self._balances[telegram_id] = balance
            return balance

    async def refund_tokens(self, telegram_id: int, tokens: int) -> int | None:
        async with self._lock:
            balance = self._balances.setdefault(telegram_id, self._initial_balance)
            balance += tokens
            self._balances[telegram_id] = balance
            return balance

    async def total_balance(self) -> int:
        async with self._lock:
            return sum(self._balances.values())


class FakeImageGenerator:
    _lock = asyncio.Lock()
    _active = 0
    max_active = 0

    def __init__(self, delay: float, jitter: float, fail_rate: float) -> None:
        self._delay = delay
        self._jitter = jitter
        self._fail_rate = fail_rate
        self.last_usage = None
        self.last_cost_usd = 0.0

    async def generate(self, prompt: str) -> bytes:
        return await self._sleep_and_return()

    async def edit_with_style(
            self,
            image_bytes: bytes,
            style_image_bytes: bytes,
            style_prompt: str | None = None,
    ) -> bytes:
        return await self._sleep_and_return()

    async def _sleep_and_return(self) -> bytes:
        async with self._lock:
            type(self)._active += 1
            type(self).max_active = max(type(self).max_active, type(self)._active)

        try:
            delay = self._delay + random.uniform(0, self._jitter)
            await asyncio.sleep(delay)
            if random.random() < self._fail_rate:
                raise RuntimeError("Fake generation failed")
            return FAKE_PNG_BYTES
        finally:
            async with self._lock:
                type(self)._active -= 1


def build_fake_image_generator_factory(config: LoadTestConfig):
    def factory(aspect_ratio: str = "1:1", quality: str = "low") -> FakeImageGenerator:
        return FakeImageGenerator(
            delay=config.generation_delay,
            jitter=config.generation_jitter,
            fail_rate=config.fail_rate,
        )

    return factory


async def run_one_generation(index: int, service: StyleImageGenerationService, semaphore: asyncio.Semaphore):
    telegram_id = 10_000 + index
    started_at = time.perf_counter()

    async with semaphore:
        try:
            await service.generate(
                telegram_id=telegram_id,
                telegram_photo_file_id=f"user-photo-{index}",
                style_file_id="style-photo",
                style_prompt="fake load test prompt",
            )
            status = "ok"
        except NotEnoughTokensError:
            status = "not_enough_tokens"
        except ImageGenerationFailedError:
            status = "generation_failed"
        except Exception as error:
            status = f"unexpected_error:{type(error).__name__}"

    return status, time.perf_counter() - started_at


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]

    return statistics.quantiles(values, n=100, method="inclusive")[percent - 1]


def parse_args() -> LoadTestConfig:
    parser = argparse.ArgumentParser(
        description="Run a fake load test for style image generation without spending API money.",
    )
    parser.add_argument("--users", type=int, default=100, help="Total fake users/requests.")
    parser.add_argument("--concurrency", type=int, default=20, help="Max requests in flight.")
    parser.add_argument("--generation-delay", type=float, default=3.0, help="Base fake generation delay in seconds.")
    parser.add_argument("--generation-jitter", type=float, default=1.0, help="Extra random generation delay in seconds.")
    parser.add_argument("--telegram-delay", type=float, default=0.05, help="Fake Telegram download delay in seconds.")
    parser.add_argument("--storage-delay", type=float, default=0.05, help="Fake style storage download delay in seconds.")
    parser.add_argument("--fail-rate", type=float, default=0.0, help="Fake generation failure probability from 0 to 1.")
    parser.add_argument("--initial-balance", type=int, default=5000, help="Fake token balance for each user.")
    args = parser.parse_args()

    if args.users <= 0:
        parser.error("--users must be greater than 0")
    if args.concurrency <= 0:
        parser.error("--concurrency must be greater than 0")
    if not 0 <= args.fail_rate <= 1:
        parser.error("--fail-rate must be between 0 and 1")

    return LoadTestConfig(
        users=args.users,
        concurrency=args.concurrency,
        generation_delay=args.generation_delay,
        generation_jitter=args.generation_jitter,
        telegram_delay=args.telegram_delay,
        storage_delay=args.storage_delay,
        fail_rate=args.fail_rate,
        initial_balance=args.initial_balance,
    )


async def main() -> None:
    config = parse_args()
    user_service = FakeUserService(initial_balance=config.initial_balance)
    service = StyleImageGenerationService(
        bot=FakeBot(delay=config.telegram_delay),
        user_service=user_service,
        storage=FakeStorage(delay=config.storage_delay),
        image_generator_factory=build_fake_image_generator_factory(config),
    )
    semaphore = asyncio.Semaphore(config.concurrency)

    started_at = time.perf_counter()
    results = await asyncio.gather(
        *(run_one_generation(index, service, semaphore) for index in range(config.users)),
    )
    total_time = time.perf_counter() - started_at

    statuses: dict[str, int] = {}
    durations = []
    for status, duration in results:
        statuses[status] = statuses.get(status, 0) + 1
        durations.append(duration)

    ok_count = statuses.get("ok", 0)
    print("Fake generation load test finished")
    print(f"Users/requests: {config.users}")
    print(f"Concurrency limit: {config.concurrency}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {config.users / total_time:.2f} req/s")
    print(f"Successful: {ok_count}")
    print(f"Failed: {config.users - ok_count}")
    print(f"Statuses: {statuses}")
    print(f"Latency avg: {statistics.mean(durations):.2f}s")
    print(f"Latency p50: {percentile(durations, 50):.2f}s")
    print(f"Latency p95: {percentile(durations, 95):.2f}s")
    print(f"Latency max: {max(durations):.2f}s")
    print(f"Max active fake generations: {FakeImageGenerator.max_active}")
    print(f"Total remaining fake balance: {await user_service.total_balance()}")
    print("OpenAI calls: 0")


if __name__ == "__main__":
    asyncio.run(main())
