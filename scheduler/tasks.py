import logging
from aiogram import Bot
from datetime import datetime, date, time, timedelta
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Appoint, Doctor, DoctorSlot


logger = logging.getLogger(__name__)


async def create_daily_schedule(sessionmaker):
    """Ежедневно добавляет расписание на следующий день"""
    hours = range(8, 18)
    next_day = date.today() + timedelta(days=1)

    # Ищем доктора по специальности
    async with sessionmaker() as session:
        result = await session.execute(select(Doctor))
        doctors = result.scalars()

        for doctor in doctors:
            for hour in hours:
                tm = time(hour, 0, 0)
                date_time = datetime.combine(next_day, tm)
                slot = DoctorSlot(
                    doctor_id=doctor.id,
                    time=date_time
                )
                session.add(slot)

    await session.commit()


async def send_daily_reminder_message(bot: Bot, sessionmaker):
    """Ежедневная задача: отправка сообщения клиенту
    в 10:00 о напоминании завтрашнего посещения"""
    now = datetime.now()
    target_date = now + timedelta(hours=21)

    # Запрос: найти все подтвержденные записи
    async with sessionmaker() as session:
        result = await session.execute(
            select(Appoint)
            .join(DoctorSlot)
            .where(
                Appoint.accepted.is_(False),
                DoctorSlot.is_available.is_(False),
                DoctorSlot.time > target_date,
            )
            # Сохраняем связанные данные после закрытия сессии
            .options(
                joinedload(Appoint.slot).joinedload(DoctorSlot.doctor)
            )
        )
    appointments = result.scalars().all()

    for appoint in appointments:
        try:
            user_id = appoint.telegram_id
            tm = appoint.slot.time.strftime("%H:%M")
            text = (f"🔔 Напоминание!\n"
                f"У вас запись к врачу *{appoint.slot.doctor.name}* "
                f"({appoint.slot.doctor.speciality})\n"
                f"📅 Завтра в {tm}\n"
                    )
            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="Markdown"
            )
            logger.info(f"Напоминание отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить напоминание пользователю {e}")


async def check_and_notify_accepted_appointments(bot: Bot, sessionmaker):
    async with sessionmaker() as session:
        # Находим записи: accepted=True, notifies=False
        result = await session.execute(select(Appoint)
                .where(
                    Appoint.accepted.is_(True),
                    Appoint.notified.is_(False),
            )
        )
        appointments = result.scalars().all()

        for appoint in appointments:
            try:
                chat_id = appoint.telegram_id
                text = "Спасибо что выбрали нас!"

                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                )
                logger.info(f"Подтверждение отправлено пользователю {chat_id}")

                # Помечаем, как обработанный
                appoint.notified = True
                session.add(appoint)
            except Exception as e:
                logger.error(f"Ошибка отправки подтверждения: {e}")

        if appointments:
            await session.commit()