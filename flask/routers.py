"""Маршруты для управления категориями и товарами"""
from flask import redirect, url_for, render_template, flash, request

from .extensions import db
from .forms import CategoryForm, ProductForm
from models import Category, Product


# Главная страница
def index():
    return redirect(url_for('categories'))


"""--- Категории ---"""
def categories():
    categories_list = Category.query.all()
    return render_template('admin/categories.html', categories=categories_list)


def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        # Проверка уникальности slug
        if Category.query.filter_by(slug=form.slug.data).first():
            flash('Slug уже существует!', 'danger')
            return render_template(
                'admin/category_form.html',
                form=form,
                title="Новая категория"
            )

        category = Category(
            name=form.name.data,
            slug=form.slug.data,
            is_active=form.is_active.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Категория создана!', 'success')
        return redirect(url_for('categories'))

    return render_template(
        'admin/category_form.html',
        form=form,
        title="Новая категория"
    )


def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        # Проверка уникальности slug (кроме текущей)
        existing = Category.query.filter(
            Category.slug == form.slug.data,
            Category.id != id
        ).first()
        if existing:
            flash('Slug уже используется другой категорией!', 'danger')
            return render_template(
                'admin/category_form.html',
                form=form,
                title="Редактировать категорию"
            )

        category.name = form.name.data
        category.slug = form.slug.data
        category.is_active = form.is_active.data
        db.session.commit()
        flash('Категория обновлена!', 'success')
        return redirect(url_for('categories'))

    return render_template(
        'admin/category_form.html',
        form=form,
        title="Редактировать категорию"
    )


def delete_category(id):
    category = Category.query.get_or_404(id)
    # Проверяем, есть ли товары в этой категории
    if category.products:
        flash('Нельзя удалить категорию - в ней есть товары!', 'danger')
        return redirect(url_for('categories'))

    db.session.delete(category)
    db.session.commit()
    flash('Категория удалена!', 'success')
    return redirect(url_for('categories'))


"""--- Товары ---"""
def products():
    """Добавляем сортировку товаров по категориям"""
    # Получаем ID категории из GET-параметра
    category_id = request.args.get('category_id', type=int)

    # Запрос товаров: фильтруем по категории, если category_id передан
    query = Product.query
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products_list = query.all()

    # Получаем все активные категории дл фильтра
    categories_list = Category.query.filter_by(is_active=True).all()

    return render_template(
        'admin/products.html',
        products=products_list,
        categories=categories_list,
        selected_category_id=category_id
    )


def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        photo_url = form.photo_url.data

        category_id = form.category_id.data if form.category_id.data != 0 else None

        product = Product(
            name=form.name.data,
            price=form.price.data,
            photo_url=photo_url,
            category_id=category_id,
            is_available=form.is_available.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Товар добавлен!', 'success')
        return redirect(url_for('products'))

    return render_template('admin/product_form.html', form=form, title="Новый товар")


def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        photo_url = form.photo_url.data

        category_id = form.category_id.data if form.category_id.data != 0 else None

        product.name = form.name.data
        product.price = form.price.data
        product.photo_url = photo_url
        product.category_id = category_id
        product.is_available = form.is_available.data

        db.session.commit()
        flash('Товар обновлён!', 'success')
        return redirect(url_for('products'))

    # Предзаполним текущие значения
    form.category_id.data = product.category_id or 0
    return render_template('admin/product_form.html', form=form, title="Редактировать товар")


def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Товар удалён!', 'success')
    return redirect(url_for('products'))