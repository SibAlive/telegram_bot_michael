import os
from flask import Flask

from .extensions import db
from .blueprints import admin
from .url_creator import DATABASE_URL


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 МБ максимальный размер файла

    # Создаем папку для загрузок, если ее нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Подключаем blueprints
    app.register_blueprint(admin, url_prefix='/admin')

    # Инициализируем расширения
    db.init_app(app)

    return app