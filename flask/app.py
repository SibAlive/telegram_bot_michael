import os
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from functools import wraps

from .extensions import db
from .routers import (index, categories, new_category,edit_category,
                     delete_category, products, new_product, edit_product,
                     delete_product)
from .url_creator import DATABASE_URL_FOR_FLASK, ADMIN_USERNAME, ADMIN_PASSWORD


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL_FOR_FLASK
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 МБ максимальный размер файла

    # Создаем папку для загрузок, если ее нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Инициализируем расширения
    db.init_app(app)

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


    # Регистрируем маршруты с защитой
    app.add_url_rule('/', 'index', admin_required(index))
    app.add_url_rule('/categories', 'categories', admin_required(categories), methods=['GET'])
    app.add_url_rule('/category/new', 'new_category', new_category, methods=['GET', 'POST'])
    app.add_url_rule('/category/edit/<int:id>', 'edit_category', edit_category, methods=['GET', 'POST'])
    app.add_url_rule('/category/delete/<int:id>', 'delete_category', delete_category, methods=['POST'])

    app.add_url_rule('/products', 'products', admin_required(products), methods=['GET'])
    app.add_url_rule('/product/new', 'new_product', new_product, methods=['GET', 'POST'])
    app.add_url_rule('/product/edit/<int:id>', 'edit_product', edit_product, methods=['GET', 'POST'])
    app.add_url_rule('/product/delete/<int:id>', 'delete_product', delete_product, methods=['POST'])

    return app