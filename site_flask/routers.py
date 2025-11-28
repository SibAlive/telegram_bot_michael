"""Маршруты для управления категориями и товарами"""
from flask import redirect, url_for, render_template, flash, request
from datetime import datetime
from sqlalchemy import func

from .extensions import db
from .services import build_appointments_sort_column
from models import User, Point, Finance, Appoint, Doctor, DoctorSlot


# Главная страница
def index():
    return render_template('base.html')


"""--- Управление баллами ---"""
def points():
    sort_column, sort_by, order = build_appointments_sort_column('full_name')

    users = (db.session.query(User, Point.total_points)
                        .outerjoin(Point, Point.telegram_id == User.telegram_id)
                        .order_by(sort_column)
                        .all())

    return render_template(
                    'admin/points.html',
                    users=users,
                    sort_by=sort_by,
                    order=order
    )


def change_points(telegram_id):
    """Меняет количество баллов клиенту"""
    point_record = Point.query.filter_by(telegram_id=telegram_id).first()
    if request.method == 'POST':
        try:
            amount = int(request.form.get('amount', 0))
            operation = request.form.get('operation') # 'add' или 'subtract'

            if amount <= 0:
                flash("Количество баллов должно быть положительным числом.", "danger")
                return redirect(url_for('change_points', telegram_id=telegram_id))

            if operation == 'add':
                change = Finance(
                    telegram_id=telegram_id,
                    income_points=amount,
                )
            elif operation == 'subtract':
                if point_record.total_points < amount:
                    flash("Недостаточно баллов для списания.", "warning")
                    return redirect(url_for('change_points', telegram_id=telegram_id))

                change = Finance(
                    telegram_id=telegram_id,
                    expense_points=amount,
                )

            db.session.add(change)
            db.session.commit()
            flash(f"Баллы успешно {'начислены' if operation == 'add' else 'списаны'}.", "success")
            return redirect(url_for('points'))

        except ValueError:
            flash("Некорректное значение баллов", "danger")
            return redirect(url_for('change_points', telegram_id=telegram_id))

    # GET: отображает форму
    user = User.query.filter_by(telegram_id=telegram_id).first()

    return render_template('admin/change_points.html',point=point_record, user=user)



def points_history(telegram_id):
    """Показывает историю изменения баллов клиента"""
    user = ((db.session.query(User)
               .where(User.telegram_id == telegram_id))
               .first())

    finances = user.finance

    return render_template('admin/points_history.html', finances=finances, user_name=user.full_name)


def delete_points_history(id):
    """Удаляет запись к врачу"""
    history = Finance.query.get_or_404(id)
    db.session.delete(history)
    db.session.commit()
    flash("Запись удалена!", "success")

    referer = request.headers.get('Referer')  # Перенаправляем на страницу, откуда была нажата кнопка удалить
    return redirect(referer)

"""--- Управление записями ---"""
def appointment():
    sort_column, sort_by, order = build_appointments_sort_column('time')
    # Получаем дату из параметров
    date_filter = request.args.get('date')

    query = (db.session.query(User, Appoint, DoctorSlot, Doctor.speciality)
                .outerjoin(Appoint, Appoint.telegram_id == User.telegram_id)
                .outerjoin(DoctorSlot, DoctorSlot.id == Appoint.slot_id)
                .outerjoin(Doctor, Doctor.id == DoctorSlot.doctor_id)
             )

    # Фильтрация по дате
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

    appointments = query.order_by(sort_column).all()

    return render_template(
                    'admin/appointment.html',
                    appointments=appointments,
                    sort_by=sort_by,
                    order=order,
    )


def records(doctor):
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

    return redirect(url_for('appointment'))


def delete_record(id):
    """Удаляет запись к врачу"""
    record = Appoint.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash("Запись удалена!", "success")

    referer = request.headers.get('Referer') # Перенаправляем на страницу, откуда была нажата кнопка удалить
    return redirect(referer)