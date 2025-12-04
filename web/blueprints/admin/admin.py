"""Маршруты для управления категориями и товарами"""
from flask import redirect, url_for, render_template, flash, request, Blueprint
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import select
from datetime import datetime
from functools import wraps

from web.extensions import db
from web.services import build_appointments_sort_column
from web.url_creator import ADMIN_USERNAME, ADMIN_PASSWORD
from bot.models import User, Point, Finance, Appoint, Doctor, DoctorSlot


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
    sort_column, sort_by, order = build_appointments_sort_column('full_name')

    users = db.session.execute(
        select(User, Point.total_points)
        .outerjoin(Point, Point.telegram_id == User.telegram_id)
        .order_by(sort_column)).all()

    return render_template(
                    'admin/points.html',
                    users=users,
                    sort_by=sort_by,
                    order=order
    )

@admin.route('/points/<int:telegram_id>', methods=['GET', 'POST'])
def change_points(telegram_id):
    """Меняет количество баллов клиенту"""
    point_record = Point.query.filter_by(telegram_id=telegram_id).first()
    if request.method == 'POST':
        try:
            amount = int(request.form.get('amount', 0))
            operation = request.form.get('operation') # 'add' или 'subtract'

            if amount <= 0:
                flash("Количество баллов должно быть положительным числом.", "danger")
                return redirect(url_for('admin.change_points', telegram_id=telegram_id))

            if operation == 'add':
                change = Finance(
                    telegram_id=telegram_id,
                    income_points=amount,
                )
            elif operation == 'subtract':
                if point_record.total_points < amount:
                    flash("Недостаточно баллов для списания.", "warning")
                    return redirect(url_for('admin.change_points', telegram_id=telegram_id))

                change = Finance(
                    telegram_id=telegram_id,
                    expense_points=amount,
                )

            db.session.add(change)
            db.session.commit()
            flash(f"Баллы успешно {'начислены' if operation == 'add' else 'списаны'}.", "success")
            return redirect(url_for('admin.points'))

        except ValueError:
            flash("Некорректное значение баллов", "danger")
            return redirect(url_for('admin.change_points', telegram_id=telegram_id))

    # GET: отображает форму
    user = User.query.filter_by(telegram_id=telegram_id).first()

    return render_template('admin/change_points.html',point=point_record, user=user)


@admin.route('/points/history/<int:telegram_id>', methods=['GET'])
def points_history(telegram_id):
    """Показывает историю изменения баллов клиента"""
    user = ((db.session.query(User)
               .where(User.telegram_id == telegram_id))
               .first())

    finances = user.finance

    return render_template('admin/points_history.html', finances=finances, user_name=user.full_name)

@admin.route('/points/delete/<int:id>', methods=['POST'])
def delete_points_history(id):
    """Удаляет запись к врачу"""
    history = Finance.query.get_or_404(id)
    db.session.delete(history)
    db.session.commit()
    flash("Запись удалена!", "success")

    referer = request.headers.get('Referer')  # Перенаправляем на страницу, откуда была нажата кнопка удалить
    return redirect(referer)

"""--- Управление записями ---"""
@admin.route('/appointment', methods=['GET'])
def appointment():
    sort_column, sort_by, order = build_appointments_sort_column('time')
    # Получаем дату из параметров
    date_filter = request.args.get('date')

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
            stmt = stmt.where(db.func.date(DoctorSlot.time) == filter_date
            )
        except ValueError:
            # Игнорируем некорректную дату
            pass

    appointments = db.session.execute(stmt).all()

    return render_template(
                    'admin/appointment.html',
                    appointments=appointments,
                    sort_by=sort_by,
                    order=order,
    )

@admin.route('/records/<doctor>', methods=['GET'])
def records(doctor=None):
    """Показывает все расписание выбранного врача"""
    sort_column, sort_by, order = build_appointments_sort_column('time')
    # Получаем дату из параметров
    date_filter = request.args.get('date')

    query = (db.session.query(User, Appoint, DoctorSlot, Doctor.speciality)
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
            query = query.filter(
                db.func.date(DoctorSlot.time) == filter_date
            )
        except ValueError:
            # Игнорируем некорректную дату
            pass

    schedule = query.order_by(sort_column).all()

    return render_template(
                'admin/records.html',
                schedule=schedule,
                speciality=doctor,
                sort_by=sort_by,
                order=order
    )

@admin.route('/toggle-accepted', methods=['POST'])
def toggle_accepted():
    """Меняет значение столбца Appoint.accepted"""
    appoint_id = request.form.get('appoint_id')
    accepted_str = request.form.get('accepted')

    # Преобразуем строку в булево значение
    accepted = accepted_str.lower() in ('да', 'true', '1', 'yes', 'on')

    appoint = Appoint.query.get(appoint_id)
    if appoint:
        appoint.accepted = accepted
        db.session.commit()
        flash("Статус записи обновлен", "success")
    else:
        flash("Запись не найдена", "error")

    return redirect(url_for('admin.appointment'))

@admin.route('/appointment/delete/<int:id>', methods=['POST'])
def delete_record(id):
    """Удаляет запись к врачу"""
    record = Appoint.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash("Запись удалена!", "success")

    referer = request.headers.get('Referer') # Перенаправляем на страницу, откуда была нажата кнопка удалить
    return redirect(referer)