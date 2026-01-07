"""Маршруты для управления категориями и товарами"""
from flask import redirect, url_for, render_template, flash, request, Blueprint
from flask_httpauth import HTTPBasicAuth
from functools import wraps

from web.extensions import db
from web.url_creator import ADMIN_USERNAME, ADMIN_PASSWORD
from web.service import (build_appointments_sort_column, change_user_points,
                         PointService, AppointmentService)


admin = Blueprint(
    'admin',
    __name__,
    template_folder='templates',
    static_url_path='static',
)

"""Устанавливаем вход в админ панель по логину и паролю"""
# Добавляем Basic Auth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return username
    return None

@auth.error_handler
def unauthorized():
    return "Доступ запрещен", 401

# Оборачиваем все маршруты админки в декоратор auth.login_required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return auth.login_required(f)(*args, **kwargs)
    return decorated_function

@admin.before_request
@auth.login_required
def require_admin_auth():
    pass

"""--- Главная страница ---"""
@admin.route('/index', methods=['GET'])
def index():
    return render_template('base.html')


"""--- Управление баллами ---"""
@admin.route('/points', methods=['GET'])
def points():
    point_service = PointService(db)
    sort_column, sort_by, order = build_appointments_sort_column('full_name')

    users = point_service.get_users_list(sort_column=sort_column)
    return render_template(
                    'admin/points.html',
                    users=users,
                    sort_by=sort_by,
                    order=order
                    )

@admin.route('/points/<int:telegram_id>', methods=['GET', 'POST'])
def change_points(telegram_id):
    """Меняет количество баллов клиенту"""
    if request.method == 'POST':
        is_changed = change_user_points(db=db, telegram_id=telegram_id)
        if not is_changed:
            return redirect(url_for('admin.change_points', telegram_id=telegram_id))
        return redirect(url_for('admin.points'))

    # GET: отображает форму
    point_service = PointService(db)
    user_points = point_service.get_user_points(telegram_id=telegram_id)
    user = point_service.get_user_by_id(telegram_id=telegram_id)

    return render_template(
        'admin/change_points.html',
        point=user_points,
        user=user
    )


@admin.route('/points/history/<int:telegram_id>', methods=['GET'])
def points_history(telegram_id):
    """Показывает историю изменения баллов клиента"""
    point_service = PointService(db)
    point_history, user_name = point_service.get_points_history(telegram_id=telegram_id)

    return render_template(
        'admin/points_history.html',
        finances=point_history,
        user_name=user_name
    )

@admin.route('/points/delete/<int:id>', methods=['POST'])
def delete_points_change(id):
    """Удаляет запись об изменении количества баллов"""
    point_service = PointService(db)
    point_service.delete_points_change(id=id)
    flash("Запись удалена!", "success")

    referer = request.headers.get('Referer')  # Перенаправляем на страницу, откуда была нажата кнопка удалить
    return redirect(referer)

"""--- Управление записями ---"""
@admin.route('/appointment', methods=['GET'])
def appointment():
    """Возвращает все записи к врачам"""
    appointment_service = AppointmentService(db)
    sort_column, sort_by, order = build_appointments_sort_column('time')
    # Получаем дату из параметров
    date_filter = request.args.get('date')

    appointments = appointment_service.get_appointments(
        sort_column=sort_column,
        date_filter=date_filter
    )
    return render_template(
                    'admin/appointment.html',
                    appointments=appointments,
                    sort_by=sort_by,
                    order=order,
    )

@admin.route('/records/<doctor>', methods=['GET'])
def records(doctor=None):
    """Показывает все расписание выбранного врача"""
    appointment_service = AppointmentService(db)
    sort_column, sort_by, order = build_appointments_sort_column('time')
    # Получаем дату из параметров
    date_filter = request.args.get('date')

    schedule = appointment_service.get_records(
        doctor=doctor,
        date_filter=date_filter,
        sort_column=sort_column
    )
    return render_template(
                'admin/records.html',
                schedule=schedule,
                speciality=doctor,
                sort_by=sort_by,
                order=order
    )

@admin.route('/toggle-accepted', methods=['POST'])
def toggle_accepted():
    """Меняет значение столбца Appoint.accepted (подтверждение приема пациента)"""
    appoint_id = request.form.get('appoint_id')
    accepted_str = request.form.get('accepted')

    # Преобразуем строку в булево значение
    accepted = accepted_str.lower() in ('да', 'true', '1', 'yes', 'on')

    appointment_service = AppointmentService(db)
    appointment_service.confirm_acceptance(appoint_id=appoint_id, accepted=accepted)
    flash("Статус записи обновлен", "success")

    return redirect(url_for('admin.appointment'))

@admin.route('/appointment/delete/<int:id>', methods=['POST'])
def delete_record(id):
    """Удаляет запись к врачу"""
    appointment_service = AppointmentService(db)
    appointment_service.delete_records(id=id)
    flash("Запись удалена!", "success")

    referer = request.headers.get('Referer') # Перенаправляем на страницу, откуда была нажата кнопка удалить
    return redirect(referer)