"""Данный модуль необходим для запуска админ панели на локальном сервере (отладка)"""
# Для запуска необходимо ввести в терминал: python -m admin_panel.run.
# При этом необходимо находиться в корне проекта

from .app import create_app


app = create_app()

if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)