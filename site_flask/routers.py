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


# """--- Категории ---"""
# def categories():
#     categories_list = Category.query.all()
#     return render_template('admin/categories.html', categories=categories_list)
#
#
# def new_category():
#     form = CategoryForm()
#     if form.validate_on_submit():
#         # Проверка уникальности slug
#         if Category.query.filter_by(slug=form.slug.data).first():
#             flash('Slug уже существует!', 'danger')
#             return render_template(
#                 'admin/category_form.html',
#                 form=form,
#                 title="Новая категория"
#             )
#
#         category = Category(
#             name=form.name.data,
#             slug=form.slug.data,
#             is_active=form.is_active.data
#         )
#         db.session.add(category)
#         db.session.commit()
#         flash('Категория создана!', 'success')
#         return redirect(url_for('categories'))
#
#     return render_template(
#         'admin/category_form.html',
#         form=form,
#         title="Новая категория"
#     )
#
#
# def edit_category(id):
#     category = Category.query.get_or_404(id)
#     form = CategoryForm(obj=category)
#     if form.validate_on_submit():
#         # Проверка уникальности slug (кроме текущей)
#         existing = Category.query.filter(
#             Category.slug == form.slug.data,
#             Category.id != id
#         ).first()
#         if existing:
#             flash('Slug уже используется другой категорией!', 'danger')
#             return render_template(
#                 'admin/category_form.html',
#                 form=form,
#                 title="Редактировать категорию"
#             )
#
#         category.name = form.name.data
#         category.slug = form.slug.data
#         category.is_active = form.is_active.data
#         db.session.commit()
#         flash('Категория обновлена!', 'success')
#         return redirect(url_for('categories'))
#
#     return render_template(
#         'admin/category_form.html',
#         form=form,
#         title="Редактировать категорию"
#     )
#
#
# def delete_category(id):
#     category = Category.query.get_or_404(id)
#     # Проверяем, есть ли товары в этой категории
#     if category.products:
#         flash('Нельзя удалить категорию - в ней есть товары!', 'danger')
#         return redirect(url_for('categories'))
#
#     db.session.delete(category)
#     db.session.commit()
#     flash('Категория удалена!', 'success')
#     return redirect(url_for('categories'))
#
#
# """--- Товары ---"""
# def products():
#     """Добавляем сортировку товаров по категориям"""
#     # Получаем ID категории из GET-параметра
#     category_id = request.args.get('category_id', type=int)
#
#     # Запрос товаров: фильтруем по категории, если category_id передан
#     query = Product.query
#     if category_id:
#         query = query.filter(Product.category_id == category_id)
#
#     products_list = query.all()
#
#     # Получаем все активные категории дл фильтра
#     categories_list = Category.query.filter_by(is_active=True).all()
#
#     return render_template(
#         'admin/products.html',
#         products=products_list,
#         categories=categories_list,
#         selected_category_id=category_id
#     )
#
#
# def new_product():
#     form = ProductForm()
#     if form.validate_on_submit():
#         photo_url = form.photo_url.data
#
#         category_id = form.category_id.data if form.category_id.data != 0 else None
#
#         product = Product(
#             name=form.name.data,
#             price=form.price.data,
#             photo_url=photo_url,
#             category_id=category_id,
#             is_available=form.is_available.data
#         )
#         db.session.add(product)
#         db.session.commit()
#         flash('Товар добавлен!', 'success')
#         return redirect(url_for('products'))
#
#     return render_template('admin/product_form.html', form=form, title="Новый товар")
#
#
# def edit_product(id):
#     product = Product.query.get_or_404(id)
#     form = ProductForm(obj=product)
#     if form.validate_on_submit():
#         photo_url = form.photo_url.data
#
#         category_id = form.category_id.data if form.category_id.data != 0 else None
#
#         product.name = form.name.data
#         product.price = form.price.data
#         product.photo_url = photo_url
#         product.category_id = category_id
#         product.is_available = form.is_available.data
#
#         db.session.commit()
#         flash('Товар обновлён!', 'success')
#         return redirect(url_for('products'))
#
#     # Предзаполним текущие значения
#     form.category_id.data = product.category_id or 0
#     return render_template('admin/product_form.html', form=form, title="Редактировать товар")
#
#
# def delete_product(id):
#     product = Product.query.get_or_404(id)
#     db.session.delete(product)
#     db.session.commit()
#     flash('Товар удалён!', 'success')
#     return redirect(url_for('products'))