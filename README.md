# ImageGenerationBot

Telegram-бот для генерации изображений через OpenAI Images API. Пользователь выбирает пример стиля, отправляет свое изображение, а бот переносит выбранный стиль на изображение пользователя, списывает токены с баланса и возвращает готовый PNG прямо в чат.

## Возможности

- генерация и редактирование изображений через OpenAI;
- выбор стиля из каталога примеров;
- настройка формата изображения: `auto`, `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9`;
- настройка качества изображения;
- профиль пользователя с балансом и потраченными токенами;
- списание токенов перед генерацией и возврат при ошибке генерации;
- платежные сценарии: Telegram Stars, крипта, DonationAlerts, промокоды;
- хранение стилевых изображений в Appwrite Storage;
- PostgreSQL + SQLAlchemy + Alembic для данных;
- Redis для инфраструктурных задач и rate-limit.

## Стек

- Python 3.14
- aiogram 3
- OpenAI Python SDK
- PostgreSQL
- SQLAlchemy async + asyncpg
- Alembic
- Redis
- Appwrite Storage
- Docker / Docker Compose
- uv

## Структура проекта

```text
app/                 Telegram handlers, buttons, middlewares, FSM states
src/chatGPT/         сервис генерации изображений через OpenAI
src/services/        бизнес-логика пользователей, стилей, оплат и генерации
src/repos/           репозитории для работы с базой данных
src/database/        SQLAlchemy models, connection, mixins
src/storage/         клиент Appwrite Storage
settings/            настройки приложения из .env
alembic/             миграции базы данных
server/              точка запуска бота для Docker
docs/                дополнительная документация
scripts/             вспомогательные скрипты
```

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=123456:telegram-bot-token

GPT_API_KEY=sk-proj-...
GPT_MODEL=gpt-image-1.5
GPT_SIZE=1024x1024
GPT_MIN_STYLE_IMAGE_GENERATION_TOKENS=5000

DATABASE_POSTGRES_DSN=postgresql+asyncpg://admin:admin@localhost:6432/image_gpt_bot

REDIS_DSN=redis://localhost:6379/0

STORAGE_ENDPOINT=https://cloud.appwrite.io/v1
STORAGE_PROJECT=appwrite-project-id
STORAGE_KEY=appwrite-api-key
STORAGE_BUCKET_ID=appwrite-bucket-id
```

Для запуска через `docker-compose.yaml` база доступна внутри Docker-сети по хосту `db`, поэтому DSN обычно должен быть таким:

```env
DATABASE_POSTGRES_DSN=postgresql+asyncpg://admin:admin@db:5432/image_gpt_bot
REDIS_DSN=redis://redis:6379/0
```

## Запуск через Docker Compose

```bash
docker compose up --build
```

Контейнеры поднимут:

- `bot` - Telegram-бот;
- `db` - PostgreSQL 15.1;
- `redis` - Redis 7.

После первого запуска примените миграции:

```bash
docker compose exec bot alembic upgrade head
```

## Локальный запуск

Установите зависимости:

```bash
uv sync
```

Поднимите PostgreSQL и Redis. Можно использовать сервисы из Docker Compose:

```bash
docker compose up -d db redis
```

Примените миграции:

```bash
uv run alembic upgrade head
```

Запустите бота:

```bash
uv run python -m server
```

Альтернативная точка запуска:

```bash
uv run python main.py
```

## Миграции

Создать новую миграцию:

```bash
uv run alembic revision --autogenerate -m "migration name"
```

Применить миграции:

```bash
uv run alembic upgrade head
```

Откатить последнюю миграцию:

```bash
uv run alembic downgrade -1
```

## Основной пользовательский сценарий

1. Пользователь запускает бота командой `/start`.
2. Бот создает пользователя, если его еще нет.
3. Пользователь открывает `Стили работ`.
4. Бот показывает стили из базы данных и изображения из Appwrite Storage.
5. Пользователь выбирает стиль и отправляет свое изображение.
6. Бот списывает минимальное количество токенов.
7. Изображение пользователя и референс стиля отправляются в OpenAI Images API.
8. Бот возвращает готовое изображение, usage, примерную стоимость и остаток токенов.
9. Если генерация падает после списания, токены возвращаются на баланс.

## Полезные файлы

- `server/__main__.py` - запуск aiogram polling;
- `app/handlers/start.py` - стартовый сценарий;
- `app/handlers/example_works.py` - выбор стиля и генерация;
- `src/services/style_image_generation.py` - оркестрация генерации, списания и возврата токенов;
- `src/chatGPT/image_service.py` - работа с OpenAI Images API;
- `src/storage/storage.py` - Appwrite Storage;
- `settings/` - все настройки приложения;
- `alembic/versions/` - миграции базы данных.

## Нагрузочное тестирование

В проекте есть скрипт для имитации генерации:

```bash
uv run python scripts/fake_generation_load_test.py
```

Дополнительные детали находятся в `docs/load_testing.md`.

## Примечания

- `README.md` предполагает, что реальные секреты хранятся только в `.env` и не коммитятся.
- Для корректной работы каталога стилей в базе должны быть записи стилей с `file_id`, который указывает на файл в Appwrite Storage.
- Бот работает через long polling и при старте удаляет webhook с `drop_pending_updates=True`.

## Что еще нужно сделать

- [ ] Добавить пример `.env.example` без реальных секретов.
- [ ] Описать процесс добавления новых стилей в базу данных и Appwrite Storage.
- [ ] Добавить seed-скрипт для начального набора стилей.
- [ ] Покрыть тестами списание и возврат токенов при ошибках генерации.
- [ ] Покрыть тестами пользовательские настройки формата и качества изображения.
- [ ] Добавить обработку недоступности Appwrite Storage с понятным сообщением пользователю.
- [ ] Добавить обработку rate limit и ошибок OpenAI API по типам.
- [ ] Проверить и документировать все платежные сценарии.
- [ ] Добавить логирование успешных генераций и платежей.
- [ ] Настроить CI для проверки линтера, тестов и миграций.
- [ ] Добавить инструкцию по деплою на сервер.
