import logging
from sqlalchemy import select
from datetime import datetime

from bot.models import User, Point, Finance, Appoint, Doctor, DoctorSlot


logger = logging.getLogger(__name__)


class PointService:
    def __init__(self, db):
        self.db = db

    def get_users_list(self, *, sort_column):
        """Возвращает список пользователей с их баллами
        и возможностью сортировки по полям"""
        users = self.db.session.execute(
            select(User, Point.total_points)
            .outerjoin(Point, Point.telegram_id == User.telegram_id)
            .order_by(sort_column)).all()
        return users

    def get_user_by_id(self, *, telegram_id):
        user = self.db.session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
        ).scalar()
        return user

    def get_user_points(self, *, telegram_id):
        points = self.db.session.execute(
            select(Point)
            .where(Point.telegram_id == telegram_id)
        ).scalar()
        return points

    def change_points(self, *, telegram_id, amount, is_income=True):
        """Добавляет или списывает баллы"""
        if is_income: # Начисляем баллы
            change = Finance(
                telegram_id=telegram_id,
                income_points=amount,
            )
        else: # Списываем баллы
            change = Finance(
                telegram_id=telegram_id,
                expense_points=amount,
            )

        self.db.session.add(change)
        self.db.session.commit()

    def get_points_history(self, *, telegram_id):
        """Показывает историю изменения баллов клиента"""
        user = self.db.session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
        ).scalar()
        points_history_and_name = user.finance, user.full_name
        return points_history_and_name

    def delete_points_change(self, *, id):
        """Удаляет запись об изменении количества баллов"""
        history = self.db.session.execute(
            select(Finance)
            .where(Finance.id == id)
        ).scalar()

        self.db.session.delete(history)
        self.db.session.commit()


class AppointmentService:
    def __init__(self, db):
        self.db = db

    def get_appointments(self, *, sort_column, date_filter):
        """Возвращает все записи к врачам"""
        stmt = ((((select(User, Appoint, DoctorSlot, Doctor.speciality)
                   .outerjoin(Appoint, Appoint.telegram_id == User.telegram_id))
                  .outerjoin(DoctorSlot, DoctorSlot.id == Appoint.slot_id))
                 .outerjoin(Doctor, Doctor.id == DoctorSlot.doctor_id))
                .order_by(sort_column))

        # Фильтрация по дате
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                # Фильтруем записи, где DoctorSlot.time попадает в эту дату
                stmt = stmt.where(self.db.func.date(DoctorSlot.time) == filter_date
                                  )
            except ValueError:
                # Игнорируем некорректную дату
                pass

        appointments = self.db.session.execute(stmt).all()
        return appointments

    def get_records(self, *, doctor, date_filter, sort_column):
        """Показывает все расписание выбранного врача"""

        stmt = (
                select(User, Appoint, DoctorSlot, Doctor.speciality)
                .select_from(DoctorSlot)
                .join(Doctor, Doctor.id == DoctorSlot.doctor_id)
                .outerjoin(Appoint, Appoint.slot_id == DoctorSlot.id)
                .outerjoin(User, User.telegram_id == Appoint.telegram_id)
                .where(Doctor.speciality == doctor)
                )

        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                # Фильтруем записи, где DoctorSlot.time попадает в эту дату
                stmt = stmt.where(
                    self.db.func.date(DoctorSlot.time) == filter_date
                )
            except ValueError:
                # Игнорируем некорректную дату
                pass
        result = self.db.session.execute(stmt.order_by(sort_column))
        schedule = result.all()
        return schedule

    def confirm_acceptance(self, *, appoint_id, accepted):
        """Меняет значение столбца Appoint.accepted (подтверждение приема пациента)"""
        appoint = self.db.session.execute(
            select(Appoint)
            .where(Appoint.id == appoint_id)
        ).scalar()

        if appoint:
            appoint.accepted = accepted
            self.db.session.commit()
        else:
            raise ValueError("Запись не найдена")

    def delete_records(self, *, id):
        """Удаляет запись к врачу"""
        record = self.db.session.execute(
            select(Appoint)
            .where(Appoint.id == id)
        ).scalar()

        self.db.session.delete(record)
        self.db.session.commit()