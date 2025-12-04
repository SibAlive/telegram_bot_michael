import logging
from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker


logger = logging.getLogger(__name__)


class DataBaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        logger.debug(
            f"Вошли в миддлварь {__class__.__name__}, тип события {event.__class__.__name__}",
        )
        sessionmaker: async_sessionmaker = data.get("session")

        # Создаем новую сессию для каждого запроса
        async with sessionmaker() as session:
            try:
                # передаем сессию в хэндлер
                data["session"] = session
                result = await handler(event, data)
                logger.debug(f"Выходим из миддлвари  {__class__.__name__}")
                return result
            except Exception as e:
                logger.exception(f"Ошибка в сессии БД: {e}")
                await session.rollback()    # Откатываем транзакцию при ошибке
                raise
            # Сессия автоматически закроется при выходе из контекста