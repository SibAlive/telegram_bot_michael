import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime, date, time, timedelta

from models import User, Point, Statistic, Appoint, Doctor, DoctorSlot

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(
            self,
            *,
            telegram_id: int,
            full_name: str,
            phone_number: int,
            age: int
    ) -> None:
        """Добавляет пользователя в базу данных"""
        new_user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            phone_number=phone_number,
            age=age
        )
        self.session.add(new_user)
        await self.session.commit()

        logger.info(
            f"User added. Table='users', telegram_id={telegram_id}, "
            f"full_name={full_name}, phone_number={phone_number}, age={age}"
        )

    async def get_user(self, *, user_id: int) -> list[dict] | None:
        """Возвращает кортеж данных пользователя"""
        result = await self.session.execute(
            select(
                User.telegram_id,
                User.full_name,
                User.phone_number,
                User.age,
            ).where(User.telegram_id == user_id)
        )
        return [
            {"full_name": row[1], "phone_number": row[2], "age": row[3]}
            for row in result.all()
        ]

    async def check_user_by_full_name(self, *, telegram_id: int, full_name: str) -> bool:
        """Проверяет, есть ли в БД пользователь с введенным ФИО"""
        result = await self.session.execute(
            select(User.telegram_id).where(User.full_name == full_name, User.telegram_id == telegram_id)
        )
        row = result.fetchone()
        return True if row else False

    async def update_user_id_by_full_name(self, *, full_name: str, telegram_id: int) -> None:
        """Добавляет telegram_id пользователя, зарегистрированного вручную"""
        await self.session.execute(
            update(User).where(User.full_name == full_name).values(telegram_id=telegram_id)
        )
        await self.session.commit()
        logger.info(f"telegram_id для пользователя {full_name} обновлено: {telegram_id}")


class PointService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_points(self, *, telegram_id: int) -> int | None:
        """Возвращает количество баллов пользователя"""
        result = await self.session.execute(
            select(Point.total_points).where(Point.telegram_id==telegram_id)
        )
        return result.scalar()


class StatisticService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_call_back(self, *, telegram_id: int, message: str, phone_number: int) -> None:
        """Добавляет базу данных запрос обратного звонка"""
        call_back = Statistic(
            telegram_id=telegram_id,
            message=message,
            contact_phone=phone_number,
        )
        self.session.add(call_back)
        await self.session.commit()


class DoctorService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_daily_schedule(self):
        """Ежедневно добавляет расписание на следующий день"""
        hours = range(8, 18)
        next_day = date.today() + timedelta(days=1)
        # next_day = date.today()

        # Ищем доктора по специальности
        result = await self.session.execute(select(Doctor))
        doctors = result.scalars()

        for doctor in doctors:
            for hour in hours:
                tm = time(hour, 0, 0)
                date_time = datetime.combine(next_day, tm)
                slot = DoctorSlot(
                    doctor_id=doctor.id,
                    time=date_time
                )
                self.session.add(slot)

        await self.session.commit()

    async def get_schedule(self, *, doctor: str, dt):
        """Формирует свободное время доктора"""
        result = await self.session.execute(
            select(DoctorSlot.time)
            .join(DoctorSlot.doctor)
            .where(
                Doctor.speciality == doctor,
                func.date(DoctorSlot.time) == dt,
                DoctorSlot.time > datetime.now(),
                DoctorSlot.is_available.is_(True))
        )
        row = result.scalars()
        return row

    async def sign_up_to_doctor(
            self,
            *,
            telegram_id: int,
            speciality: str,
            service: str,
            date_time: datetime,
    ) -> None:
        """Записаться к врачу"""
        # Получаем id доктора по его специальности
        doctor = await self.session.execute(
            select(Doctor.id).where(Doctor.speciality == speciality))
        doctor_id = doctor.scalar_one_or_none()

        # Получаем объект таблицы DoctorSlot
        result = await self.session.execute(
            select(DoctorSlot)
            .where(
                DoctorSlot.doctor_id == doctor_id,
                DoctorSlot.time == date_time,
                   )
        )
        doctor_slot = result.scalar_one_or_none()

        appointment = Appoint(
            telegram_id=telegram_id,
            slot_id=doctor_slot.id,
            service=service,
        )

        doctor_slot.is_available = False

        self.session.add(appointment)
        await self.session.commit()