import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import Config, load_config


# Загрузка конфига
config: Config = load_config()

logger = logging.getLogger(__name__)

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{config.db.user}:{config.db.password}@"
    f"{config.db.host}:{config.db.port}/{config.db.name}"
)

DATABASE_URL_FOR_ALEMBIC = (
    f"postgresql://"
    f"{config.db.user}:{config.db.password}@"
    f"{config.db.host}:{config.db.port}/{config.db.name}"
)

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=False,        # True — для логирования SQL-запросов (отладка)
    future=True,       # Использовать новые фичи SQLAlchemy 2.0+
)

# Создаём фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не закрывать объекты после коммита
)
