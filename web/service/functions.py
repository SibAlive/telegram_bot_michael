from flask import request, flash

from bot.models import User, Point, Appoint, Doctor, DoctorSlot
from .db_func import PointService


def build_appointments_sort_column(s_by):
    """Функция для построения базового запроса записей"""
    # по умолчанию сортируем по времени
    sort_by = request.args.get('sort_by', s_by)
    if sort_by == 'time':
        order = request.args.get('order', 'desc')
    else:
        order = request.args.get('order', 'asc')

    sort_columns = {
        'full_name': User.full_name,
        'doctor': Doctor.speciality,
        'time': DoctorSlot.time,
        'accepted': Appoint.accepted,
        'total_points': Point.total_points
    }
    sort_column = sort_columns.get(sort_by)

    sort_column = sort_column.desc().nulls_last() if order == 'desc' else sort_column.asc().nulls_first()
    return sort_column, sort_by, order


def change_user_points(*, db, telegram_id):
    """Добавляет или списывает баллы с проверкой"""
    point_service = PointService(db)
    try:
        amount = int(request.form.get('amount', 0))
        operation = request.form.get('operation')  # 'add' или 'subtract'

        if amount <= 0:
            flash("Количество баллов должно быть положительным числом.", "danger")
            return False

        if operation == 'add':
            point_service.change_points(
                telegram_id=telegram_id,
                amount=amount
            )
        elif operation == 'subtract':
            user_points = point_service.get_user_points(telegram_id=telegram_id).total_points
            if user_points < amount:
                flash("Недостаточно баллов для списания.", "warning")
                return False

            point_service.change_points(
                telegram_id=telegram_id,
                amount=amount,
                is_income=False
            )
        flash(f"Баллы успешно {'начислены' if operation == 'add' else 'списаны'}.", "success")
        return True

    except ValueError:
        flash("Некорректное значение баллов", "danger")
        return False