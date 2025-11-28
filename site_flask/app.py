import os
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from functools import wraps

from .extensions import db
from .routers import (index, points, change_points, points_history,
                      appointment, records, toggle_accepted, delete_record,
                      delete_points_history)
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
    app.add_url_rule('/', 'index', admin_required(index), methods=['GET'])
    app.add_url_rule('/points', 'points', admin_required(points), methods=['GET'])
    app.add_url_rule('/points/<int:telegram_id>', 'change_points', change_points, methods=['GET', 'POST'])
    app.add_url_rule('/points/history/<int:telegram_id>', 'points_history', points_history, methods=['GET'])
    app.add_url_rule('/points/delete/<int:id>', 'delete_points_history', delete_points_history, methods=['POST'])

    app.add_url_rule('/appointment', 'appointment', admin_required(appointment), methods=['GET'])
    app.add_url_rule('/appointment/<doctor>', 'records', records, methods=['GET'])
    app.add_url_rule('/toggle-accepted', 'toggle_accepted', toggle_accepted, methods=['POST'])
    app.add_url_rule('/appointment/delete/<int:id>', 'delete_record', delete_record, methods=['POST'])

    return app