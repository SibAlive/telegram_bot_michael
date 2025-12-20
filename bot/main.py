"""Запуск бота через Polling, используется для отладки"""
import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config.config import Config, load_config
from bot.services import AsyncSessionLocal, engine
from bot.handlers import router
from bot.middlewares import DataBaseMiddleware
from bot.scheduler import setup_scheduler


# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуск бота
async def main() -> None:
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
            password=config.redis.password or None,
            username=config.redis.username or None,
        )
    storage = RedisStorage(redis)

    try:
        # Отправляем команду PING
        pong = await redis.ping()
        logger.info(f"Connection successful! PONG: {pong}")
    except Exception as e:
        logger.error(f"Connection to Redis failed: {e}")

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)
    # dp = Dispatcher()

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


    # Запускаем polling
    try:
        await dp.start_polling(
                        bot,
                        session=AsyncSessionLocal,
                        admin_ids=config.bot.admin_ids,
        )
    except Exception as e:
        logger.exception(e)
    finally:
        scheduler.shutdown(wait=False) # Останавливаем планировщик
        await engine.dispose() # Закрываем движок
        logger.info("Connection to PostgresSQL closed")


# Политика цикла событий для Windows
if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    asyncio.run(main())


"""Запуск бота через WebHoock на локальном сервере, с помощью Localtonnel"""
# import asyncio
# import re
# import logging
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.fsm.storage.redis import RedisStorage
# from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
# from aiohttp import web
# from redis.asyncio import Redis
#
# from config.config import Config, load_config
# from services.connections import AsyncSessionLocal, engine
# from handlers.settings import settings_router
# from handlers.admin import admin_router
# from handlers.user import user_router
# from handlers.other import other_router
# from middlewares.database_middleware import DataBaseMiddleware
# from middlewares.shadow_ban import ShadowBanMiddleware
# from middlewares.check_reg import UserRegistrationMiddleware
# from middlewares.delete_msg import DeleteLastMessageMiddleware
# from middlewares.i18n_middleware import TranslatorMiddleware
# from middlewares.lang_settings import LangSettingsMiddleware
# from middlewares.throttling_middleware import ThrottlingMiddleware
# from lexicon.i18n import get_translations
#
#
# # Инициализируем логгер
# logger = logging.getLogger(__name__)
#
# # Конфигурация вебхука
# WEBHOOK_PATH = "/webhook"
# WEBHOOK_SECRET = "my_secret"
# WEB_SERVER_HOST = "127.0.0.1"
# WEB_SERVER_PORT = 8080
#
# # Укажите ПОЛНЫЙ путь к lt.cmd (подставьте свой!)
# LT_EXECUTABLE = r"C:\Users\Anton\AppData\Roaming\npm\lt.cmd"
#
#
# async def start_localtunnel(port: int, timeout: int = 30) -> str:
#     """Запускает localtunnel и возвращает публичный URL с таймаутом."""
#     logger.info(f"Starting localtunnel on port {port}...")
#
#     try:
#         # Запускаем localtunnel
#         process = await asyncio.create_subprocess_exec(
#             LT_EXECUTABLE, "--port", str(port),
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE
#         )
#
#         url_pattern = re.compile(r"https://[a-zA-Z0-9\-]+\.loca\.lt")
#
#         async def read_stream(stream, name):
#             """Читает поток и ищет URL."""
#             while True:
#                 line = await stream.readline()
#                 if not line:
#                     break
#                 line = line.decode('utf-8', errors='ignore').strip()
#                 if line:
#                     logger.debug(f"lt {name}: {line}")
#                     match = url_pattern.search(line)
#                     if match:
#                         return match.group(0)
#             return None
#
#         # ЯВНО создаем задачи — это ключевое исправление!
#         task_stdout = asyncio.create_task(read_stream(process.stdout, "out"))
#         task_stderr = asyncio.create_task(read_stream(process.stderr, "err"))
#
#         # Ждем первую завершившуюся задачу (которая нашла URL)
#         done, pending = await asyncio.wait(
#             [task_stdout, task_stderr],
#             timeout=timeout,
#             return_when=asyncio.FIRST_COMPLETED
#         )
#
#         # Отменяем незавершённые задачи
#         for task in pending:
#             task.cancel()
#             try:
#                 await task  # Дожидаемся отмены
#             except asyncio.CancelledError:
#                 pass
#
#         # Получаем результат
#         for task in done:
#             result = await task  # ← ВАЖНО: await результата задачи
#             if result:
#                 logger.info(f"LocalTunnel URL: {result}")
#                 return result
#
#         raise asyncio.TimeoutError(f"LocalTunnel did not provide URL within {timeout} seconds")
#
#     except Exception as e:
#         logger.error(f"Failed to start localtunnel: {e}")
#         raise RuntimeError("Could not obtain LocalTunnel URL") from e
#
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
#             password=config.redis.password,
#             username=config.redis.username,
#         )
#     storage = RedisStorage(redis)
#
#     # Инициализируем бот и диспетчер
#     bot = Bot(
#         token=config.bot.token,
#         default=DefaultBotProperties(parse_mode=ParseMode.HTML),
#     )
#     dp = Dispatcher(storage=storage)
#
#     # Получаем словарь с переводами
#     translations = get_translations()
#
#     # Регистрируем роутеры в диспетчере
#     logger.info("Including routers...")
#     dp.include_routers(settings_router, admin_router, user_router, other_router)
#
#     # Регистрируем миддлвари
#     logger.info("Including middlewares...")
#     dp.update.middleware(DataBaseMiddleware())
#     dp.update.middleware(ShadowBanMiddleware())
#     dp.update.middleware(LangSettingsMiddleware())
#     dp.update.middleware(TranslatorMiddleware())
#     dp.message.middleware(UserRegistrationMiddleware())
#     dp.message.middleware(DeleteLastMessageMiddleware())
#     dp.message.middleware(ThrottlingMiddleware(redis, limit=1, tm=1))
#
#     # Создаем объект aiohttp приложения
#     app = web.Application()
#
#     # Создаем обработчик запросов от Telegram
#     webhook_handler = SimpleRequestHandler(
#         dispatcher=dp,
#         bot=bot,
#         secret_token=WEBHOOK_SECRET,
#         translations=translations,
#         session=AsyncSessionLocal,
#         admin_ids=config.bot.admin_ids,
#     )
#     webhook_handler.register(app, path=WEBHOOK_PATH)
#
#     # Подключаем диспетчер к приложению (для graceful shutdown и т.п.)
#     setup_application(app, dp, bot=bot)
#
#     # Запускаем localtunnel для получения публичного URL
#     try:
#         public_url = await start_localtunnel(WEB_SERVER_PORT)
#         webhook_url = f"{public_url}{WEBHOOK_PATH}"
#         logger.info(f"LocalTunnel established at: {public_url}")
#     except Exception as e:
#         logger.error("Failed to start localtunnel")
#         raise e
#
#     # Устанавливаем webhook в Telegram
#     try:
#         await bot.set_webhook(
#             url=webhook_url,
#             secret_token=WEBHOOK_SECRET,
#             drop_pending_updates=True,  # Очищаем старые обновления при запуске
#         )
#         logger.info(f"Webhook set to: {webhook_url}")
#     except Exception as e:
#         logger.exception("Failed to set webhook")
#         raise e
#
#     # Запускаем веб-сервер
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
#     logger.info(f"Starting webhook server on http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
#     await site.start()
#
#     # Ждем завершения (бот работает, пока не прервут Ctrl+C)
#     try:
#         await asyncio.Event().wait()    # Бесконечное ожидание
#     except (KeyboardInterrupt, SystemExit):
#         logger.info("Shutting down...")
#
#     finally:
#         # Удаляем webhook при завершении
#         await bot.delete_webhook(drop_pending_updates=True)
#         logger.info("Webhook deleted")
#
#         # Закрываем соединения
#         await runner.cleanup()
#         await bot.session.close()
#         await redis.close()
#         await engine.dispose()
#         logger.info("Connection to Redis and PostgreSQL closed")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


"""Запуск бота через WebHoock на удаленном сервере, финальная версия"""
# import sys
# import os
# import asyncio
# import logging
# from functools import partial
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.fsm.storage.redis import RedisStorage
# from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
# from aiohttp import web
# from redis.asyncio import Redis
# from sqlalchemy import text
#
# from config.config import Config, load_config
# from services.connections import AsyncSessionLocal, engine
# from handlers.settings import settings_router
# from handlers.admin import admin_router
# from handlers.user import user_router
# from handlers.other import other_router
# from middlewares.database_middleware import DataBaseMiddleware
# from middlewares.shadow_ban import ShadowBanMiddleware
# from middlewares.check_reg import UserRegistrationMiddleware
# from middlewares.delete_msg import DeleteLastMessageMiddleware
# from middlewares.i18n_middleware import TranslatorMiddleware
# from middlewares.lang_settings import LangSettingsMiddleware
# from middlewares.throttling_middleware import ThrottlingMiddleware
# from lexicon.i18n import get_translations
#
#
# # Инициализируем логгер
# logger = logging.getLogger(__name__)
#
#
# async def on_startup(bot: Bot, config: Config, redis: Redis) -> None:
#     """Устанавливаем webhook при запуске"""
#     webhook_url = config.webhook.base_url + config.webhook.path
#     logger.info(f"Attempting to set webhook to: {webhook_url}")
#
#     # Проверка подключения к Redis
#     try:
#         await redis.ping()
#         logger.info("Successfully connected to Redis")
#     except Exception as e:
#         logger.error(f"Failed to connect to Redis: {e}")
#         raise e
#
#     # Проверка PostgreSQL
#     try:
#         async with engine.begin() as conn:
#             await conn.execute(text("SELECT 1"))
#         logger.info("Successfully connected to PostgreSQL")
#     except Exception as e:
#         logger.error(f"Failed to connect to PostgreSQL: {e}")
#         raise e
#
#     # Устанавливаем webhook в Telegram
#     try:
#         await bot.set_webhook(
#             url=webhook_url,
#             drop_pending_updates=False,  # Очищаем старые обновления при запуске
#         )
#         logger.info(f"Webhook set to: {webhook_url}")
#     except Exception as e:
#         logger.exception("Failed to set webhook")
#         raise e
#
#
# async def on_shutdown(bot: Bot) -> None:
#     """Удаляем вебхук только если не на Render"""
#     if not os.getenv("RENDER"):
#         await bot.delete_webhook(drop_pending_updates=True)
#         logger.info("Webhook deleted")
#     else:
#         logger.info("Skipping webhook deletion on Render")
#
#     # Закрываем соединения
#     await bot.session.close()
#     if hasattr(bot, "_redis"):
#         await bot._redis.close()
#         logger.info("Redis closed")
#     await engine.dispose()
#     logger.info("Connection to Redis and PostgreSQL closed")
#
#
# # Функция конфигурирования и запуск бота
# def create_app() -> web.Application:
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
#         host=config.redis.host,
#         port=config.redis.port,
#         db=config.redis.db,
#         password=config.redis.password,
#         username=config.redis.username,
#     )
#     storage = RedisStorage(redis)
#
#     # Инициализируем бот и диспетчер
#     bot = Bot(
#         token=config.bot.token,
#         default=DefaultBotProperties(parse_mode=ParseMode.HTML),
#     )
#     dp = Dispatcher(storage=storage)
#
#     # Получаем словарь с переводами
#     translations = get_translations()
#
#     # Регистрируем роутеры в диспетчере
#     logger.info("Including routers...")
#     dp.include_routers(settings_router, admin_router, user_router, other_router)
#
#     # Регистрируем миддлвари
#     logger.info("Including middlewares...")
#     dp.update.middleware(DataBaseMiddleware())
#     dp.update.middleware(ShadowBanMiddleware())
#     dp.update.middleware(LangSettingsMiddleware())
#     dp.update.middleware(TranslatorMiddleware())
#     dp.message.middleware(UserRegistrationMiddleware())
#     dp.message.middleware(DeleteLastMessageMiddleware())
#     dp.message.middleware(ThrottlingMiddleware(redis, limit=1, tm=1))
#
#     # Регистрируем события жизненного цикла
#     dp.startup.register(partial(on_startup, bot, config, redis))
#     dp.shutdown.register(on_shutdown)
#
#     # Создаем объект aiohttp приложения
#     app = web.Application()
#
#     # Создаем обработчик запросов от Telegram
#     try:
#         webhook_handler = SimpleRequestHandler(
#             dispatcher=dp,
#             bot=bot,
#             translations=translations,
#             session=AsyncSessionLocal,
#             admin_ids=config.bot.admin_ids,
#         )
#     except Exception as e:
#         logger.exception(f"Failed to dispatch webhook: {e}")
#         raise e
#     webhook_handler.register(app, path=config.webhook.path)
#
#     # Подключаем диспетчер к приложению (для graceful shutdown и т.п.)
#     setup_application(app, dp, bot=bot)
#
#     # Health check endpoint для Render
#     async def health_check(request):
#         return web.Response(text="OK", status=200)
#     app.router.add_get("/", health_check)
#     app.router.add_get("/health", health_check)
#
#     logger.info("Application created successfully")
#     return app
#
#
# # Политика цикла событий для Windows
# if sys.platform.startswith("win") or os.name == "nt":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
# app = create_app()
#
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     web.run_app(app, host="0.0.0.0", port=port)