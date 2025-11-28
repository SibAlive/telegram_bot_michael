from flask import request

from models import User, Point, Appoint, Doctor, DoctorSlot


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