from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from apscheduler.triggers.interval import IntervalTrigger

from .tasks import (send_daily_reminder_message, check_and_notify_accepted_appointments,
                    create_daily_schedule, check_and_notify_change_points)


def setup_scheduler(bot: Bot, session, timezone: str) -> AsyncIOScheduler:
    """Настраивает и возвращает экземпляр планировщика
    с зарегистрированными задачами."""
    scheduler = AsyncIOScheduler(timezone=timezone)

    # Ежедневно отправляет напоминание о записи
    scheduler.add_job(
        send_daily_reminder_message,
        trigger=CronTrigger(hour=19, minute=28, second=0),
        args=[bot, session], # Передаем переменные в функцию
        id="daily_reminder_message",
        replace_existing=True,
        misfire_grace_time=300 # Даем 5 минут на опоздавшие запуски
    )

    # Ежедневно создает расписание врачей на следующий день
    scheduler.add_job(
        create_daily_schedule,
        trigger=CronTrigger(hour=19, minute=27, second=0),
        args=[session],
        id="daily_schedule",
        replace_existing=True,
        misfire_grace_time=60
    )

    # Проверка отправки клиенту сообщения с анкетой каждые 30 секунд
    scheduler.add_job(
        check_and_notify_accepted_appointments,
        trigger=IntervalTrigger(seconds=30),
        args=[bot, session],
        id="check_accepted_appointments",
        replace_existing=True,
        misfire_grace_time=10
    )

    # Проверка изменения количества балов клиенту
    scheduler.add_job(
        check_and_notify_change_points,
        trigger=IntervalTrigger(seconds=10),
        args=[bot, session],
        id="check_change_points",
        replace_existing=True,
        misfire_grace_time=5
    )

    return scheduler