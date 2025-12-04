"""Формируем строку для подключения к БД"""
from environs import Env
from dataclasses import dataclass


env = Env()
env.read_env()


@dataclass
class Database:
    database: str
    host: str
    port: int
    user: str
    password: str

# URL для подключения к служебной БД 'postgres' для создания новой базы данных
db_main = Database(
    database=env("POSTGRES_MAIN_DB"),
    host=env("POSTGRES_MAIN_HOST"),
    port=env.int("POSTGRES_MAIN_PORT", 5432),
    user=env("POSTGRES_MAIN_USER"),
    password=env("POSTGRES_MAIN_PASSWORD")
    )

db_new = Database(
    database=env("POSTGRES_DB"),
    host=env("POSTGRES_HOST"),
    port=env.int("POSTGRES_PORT", 5432),
    user=env("POSTGRES_USER"),
    password=env("POSTGRES_PASSWORD")
    )

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{db_new.user}:{db_new.password}@"
    f"{db_new.host}:{db_new.port}/{db_new.database}"
)

ADMIN_USERNAME = env("ADMIN_USERNAME")
ADMIN_PASSWORD = env("ADMIN_PASSWORD")
