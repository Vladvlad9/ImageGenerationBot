# Fake generation load test

This test checks how the bot's style image generation flow behaves under concurrent load
without calling OpenAI, Telegram, Appwrite, Postgres, or Redis.

Run a small smoke test:

```bash
uv run python scripts/fake_generation_load_test.py --users 10 --concurrency 2
```

Run a larger load test:

```bash
uv run python scripts/fake_generation_load_test.py --users 100 --concurrency 20
```

Useful options:

```bash
--users 100                 # total fake requests
--concurrency 20            # max requests in flight
--generation-delay 3        # fake AI generation delay in seconds
--generation-jitter 1       # extra random delay in seconds
--fail-rate 0.05            # fake failure rate, for example 5%
--initial-balance 5000      # fake token balance per user
```

The important line is:

```text
OpenAI calls: 0
```

If this line is printed, the test used fake image generation and did not spend API money.
