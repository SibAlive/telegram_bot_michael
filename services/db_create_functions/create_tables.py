import asyncio
import asyncpg
import logging
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine

from config import Config, load_config
from models import Base


# Загрузка конфига
config: Config = load_config()

# Настройка логирования
logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format,
)
logger = logging.getLogger(__name__)

# Политика цикла событий для Windows
if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# URL для подключения к служебной БД 'postgres'
db_database = "postgres"
db_host = "localhost"
db_port = 5432
db_user = "postgres"
db_password = "Iskitimec94"

POSTGRES_URL = (
    f"postgresql+asyncpg://"
    f"{db_user}:{db_password}@"
    f"{db_host}:{db_port}/{db_database}"
)

# URL для целевой БД
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{config.db.user}:{config.db.password}@"
    f"{config.db.host}:{config.db.port}/{config.db.name}"
)


async def create_database_if_not_exists():
    """Создает базу данных, если она не существует"""
    # Подключаемся к служебной БД 'postgres'
    sys_conn = await asyncpg.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_database
    )

    try:
        # Проверяем, существует ли БД
        db_exists = await sys_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", config.db.name
        )
        if not db_exists:
            # Создаем БД
            await sys_conn.execute(f"CREATE DATABASE {config.db.name}")
            logger.info(f"База данных {config.db.name} создана")
        else:
            logger.info(f"База данных {config.db.name} уже существует")
    finally:
        await sys_conn.close()


async def create_tables():
    """Создает таблицы, если их нет"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Закрываем движок
    await engine.dispose()
    logger.info("Таблицы успешно созданы")


async def main():
    try:
        # Создает БД
        await create_database_if_not_exists()
        # Создаем таблицы
        await create_tables()
    except Exception as e:
        logger.exception(f"Ошибка при создании таблиц: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())