import logging
import os
from dataclasses import dataclass
from environs import Env


logger = logging.getLogger(__name__)


@dataclass
class TgBot:
    token: str # Токен для доступа к телеграм-боту
    admin_ids: list[int] # Список пользователей с ролью админ
    timezone: str # Часовой пояс


@dataclass
class LoggSettings:
    level: str
    format: str


@dataclass
class DatabaseSettings:
    name: str
    host: str
    port: int
    user: str
    password: str


@dataclass
class RedisSettings:
    host: str
    port: int
    db: int
    password: str
    username: str


@dataclass
class WebhookSettings:
    host: str
    port: int
    base_url: str
    path: str


@dataclass
class Config:
    bot: TgBot
    db: DatabaseSettings
    redis: RedisSettings
    log: LoggSettings
    webhook: WebhookSettings


def load_config(path: str | None = None) -> Config:
    env = Env()

    if path:
        if not os.path.exists(path):
            logger.warning(f".env file not found at {path}, skipping...")
        else:
            logger.info(f"Loading .env from {path}")

    env.read_env(path)

    token = env("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN must not be empty")

    raw_ids = env.list('ADMIN_IDS', default=[])

    try:
        admin_ids = [int(x) for x in raw_ids]
    except ValueError as e:
        raise ValueError(f"ADMIN_IDS must be integers, for {raw_ids}") from e

    db = DatabaseSettings(
        name=env("POSTGRES_DB"),
        host=env("POSTGRES_HOST"),
        port=env.int("POSTGRES_PORT", 5432),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
    )

    redis = RedisSettings(
        host=env("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        db=env.int("REDIS_DATABASE"),
        password=env("REDIS_PASSWORD", default=""),
        username=env("REDIS_USERNAME", default=""),
    )

    webhook = WebhookSettings(
        host=env.str("WEBHOOK_HOST", "0.0.0.0"),
        port=env.int("PORT", 8000),
        base_url=env("WEBHOOK_BASE_URL"),
        path=env.str("WEBHOOK_PATH", "/webhook"),
    )

    logg_settings = LoggSettings(
        level=env("LOG_LEVEL"),
        format=env("LOG_FORMAT"),
    )

    logger.info("Configuration loaded successfully")

    return Config(
        bot=TgBot(token=token, admin_ids=admin_ids, timezone="Asia/Novosibirsk"),
        db=db,
        redis=redis,
        log=logg_settings,
        webhook=webhook
    )