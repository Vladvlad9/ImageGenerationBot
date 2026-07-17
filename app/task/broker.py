import os

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

result_backend = RedisAsyncResultBackend(
    redis_url=REDIS_URL,

    # Результаты будут удаляться через час.
    result_ex_time=3600,
)

broker = RedisStreamBroker(
    url=REDIS_URL,
).with_result_backend(result_backend)