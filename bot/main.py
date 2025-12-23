"""Запуск бота через Polling, используется для отладки"""
# import asyncio
# import logging
# import os
# import sys
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.fsm.storage.redis import RedisStorage
# from redis.asyncio import Redis
#
# from config.config import Config, load_config
# from bot.services import AsyncSessionLocal, engine
# from bot.handlers import router
# from bot.middlewares import DataBaseMiddleware
# from bot.scheduler import setup_scheduler
#
#
# # Инициализируем логгер
# logger = logging.getLogger(__name__)
#
#
# # Функция конфигурирования и запуск бота
# async def main() -> None:
#     # Загружаем конфиг в переменную конфиг
#     config: Config = load_config()
#
#     # Задаем базовую конфигурацию логирования
#     logging.basicConfig(
#         level=logging.getLevelName(level=config.log.level),
#         format=config.log.format
#     )
#     # Выводи в консоль информацию о начале запуска бота
#     logger.info("Starting bot...")
#
#     # Инициализируем хранилище
#     redis = Redis(
#             host=config.redis.host,
#             port=config.redis.port,
#             db=config.redis.db,
#             password=config.redis.password or None,
#             username=config.redis.username or None,
#         )
#     storage = RedisStorage(redis)
#
#     try:
#         # Отправляем команду PING
#         pong = await redis.ping()
#         logger.info(f"Connection successful! PONG: {pong}")
#     except Exception as e:
#         logger.error(f"Connection to Redis failed: {e}")
#
#     # Инициализируем бот и диспетчер
#     bot = Bot(
#         token=config.bot.token,
#         default=DefaultBotProperties(parse_mode=ParseMode.HTML)
#     )
#     dp = Dispatcher(storage=storage)
#     # dp = Dispatcher()
#
#     # Регистрируем роутеры в диспетчере
#     logger.info("Including routers...")
#     dp.include_router(router)
#
#     # Регистрируем миддлвари
#     logger.info("Including middlewares...")
#     dp.update.middleware(DataBaseMiddleware())
#
#     # Настройка и запуск планировщика
#     scheduler = setup_scheduler(bot, AsyncSessionLocal, config.bot.timezone)
#     scheduler.start()
#     logging.info("Планировщик задач запущен")
#
#
#     # Запускаем polling
#     try:
#         await dp.start_polling(
#                         bot,
#                         session=AsyncSessionLocal,
#                         admin_ids=config.bot.admin_ids,
#         )
#     except Exception as e:
#         logger.exception(e)
#     finally:
#         scheduler.shutdown(wait=False) # Останавливаем планировщик
#         await engine.dispose() # Закрываем движок
#         logger.info("Connection to PostgresSQL closed")
#
#
# # Политика цикла событий для Windows
# if sys.platform.startswith("win") or os.name == "nt":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
# if __name__ == "__main__":
#     asyncio.run(main())



"""Запуск бота через WebHook на удаленном сервере, финальная версия"""
import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from aiohttp import web
from functools import partial
from sqlalchemy import text

from config.config import Config, load_config
from bot.services import AsyncSessionLocal, engine
from bot.handlers import router
from bot.middlewares import DataBaseMiddleware
from bot.scheduler import setup_scheduler


# Инициализируем логгер
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, config: Config, redis: Redis) -> None:
    """Устанавливаем webhook при запуске"""
    webhook_url = config.webhook.base_url + config.webhook.path
    logger.info(f"Attempting to set webhook to: {webhook_url}")

    # Проверка подключения к Redis
    try:
        await redis.ping()
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise e

    # Проверка PostgreSQL
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to PostgreSQL")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise e

    # Устанавливаем webhook в Telegram
    try:
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=False,  # Очищаем старые обновления при запуске
        )
        logger.info(f"Webhook set to: {webhook_url}")
    except Exception as e:
        logger.exception("Failed to set webhook")
        raise e


async def on_shutdown(bot: Bot, scheduler) -> None:
    # Останавливаем планировщик задач
    scheduler.shutdown(wait=False)
    # Закрываем соединения
    await bot.session.close()
    if hasattr(bot, "_redis"):
        await bot._redis.close()
        logger.info("Redis closed")
    await engine.dispose()
    logger.info("Connection to Redis and PostgreSQL closed")


# Функция конфигурирования и запуск бота
def create_app() -> web.Application:
    # Загружаем конфиг в переменную конфиг
    config: Config = load_config()

    # Задаем базовую конфигурацию логирования
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format
    )
    # Выводи в консоль информацию о начале запуска бота
    logger.info("Starting bot...")

    # Инициализируем хранилище
    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
        username=config.redis.username,
    )
    storage = RedisStorage(redis)

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры в диспетчере
    logger.info("Including routers...")
    dp.include_router(router)

    # Регистрируем миддлвари
    logger.info("Including middlewares...")
    dp.update.middleware(DataBaseMiddleware())

    # Настройка и запуск планировщика
    scheduler = setup_scheduler(bot, AsyncSessionLocal, config.bot.timezone)
    scheduler.start()
    logging.info("Планировщик задач запущен")

    # Регистрируем события жизненного цикла
    dp.startup.register(partial(on_startup, bot, config, redis))
    dp.shutdown.register(partial(on_shutdown, bot, scheduler))

    # Создаем объект aiohttp приложения
    app = web.Application()

    # Создаем обработчик запросов от Telegram
    try:
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            session=AsyncSessionLocal,
            admin_ids=config.bot.admin_ids,
        )
    except Exception as e:
        logger.exception(f"Failed to dispatch webhook: {e}")
        raise e
    webhook_handler.register(app, path=config.webhook.path)

    # Подключаем диспетчер к приложению (для graceful shutdown и т.п.)
    setup_application(app, dp, bot=bot)

    # Health check endpoint для Render
    async def health_check(request):
        return web.Response(text="OK", status=200)
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    logger.info("Application created successfully")
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 2222))
    web.run_app(app, host="0.0.0.0", port=port)