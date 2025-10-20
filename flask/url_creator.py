"""Формируем строку для подключения к БД"""
from environs import Env


env = Env()
env.read_env()

db_name=env("POSTGRES_DB")
db_host=env("POSTGRES_HOST")
db_port=env.int("POSTGRES_PORT", 5432)
db_user=env("POSTGRES_USER")
db_password=env("POSTGRES_PASSWORD")

DATABASE_URL_FOR_FLASK = (
    f"postgresql+psycopg2://"
    f"{db_user}:{db_password}@"
    f"{db_host}:{db_port}/{db_name}"
)

ADMIN_USERNAME = env("ADMIN_USERNAME", 'admin')
ADMIN_PASSWORD = env("ADMIN_PASSWORD", 'password')