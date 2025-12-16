import psycopg2
import logging
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine

from config.config import Config, load_config
from web.extensions import db as database
from web.url_creator import db_new, db_main, DATABASE_URL


# Загрузка конфига
config: Config = load_config()

# Настройка логирования
logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format,
)
logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """Создает базу данных, если она не существует"""
    # Подключаемся к служебной БД 'postgres'
    conn = psycopg2.connect(
        host=db_main.host,
        port=db_main.port,
        user=db_main.user,
        password=db_main.password,
        database=db_main.database
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # Необходимо для создания БД
    cur = conn.cursor()

    try:
        # Проверяем, существует ли БД
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_new.database,))
        db_exists = cur.fetchone()
        if not db_exists:
            # Создаем БД
            cur.execute(f"CREATE DATABASE {db_new.database}")
            logger.info(f"База данных {db_new.database} успешно создана")
        else:
            logger.warning(f"База данных {db_new.database} уже существует")
    finally:
        cur.close()
        conn.close()


def create_tables():
    """Создает таблицы, если их нет"""
    # Созданы будут лишь импортированные таблицы
    engine = create_engine(DATABASE_URL, echo=True)

    # Создаем все таблицы
    database.metadata.create_all(bind=engine)
    logger.info("Таблицы успешно созданы")


def main():
    try:
        # Создает БД
        create_database_if_not_exists()
        # Создаем таблицы
        create_tables()
    except Exception as e:
        logger.exception(f"Ошибка при создании таблиц: {e}")
        raise


if __name__ == "__main__":
    main()