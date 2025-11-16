import os
import sys
import pytest
from contextlib import contextmanager
from flask import template_rendered
from app import app as application  # Импортируем экземпляр Flask
from models import User, Role, db  # Импортируем модели

# Добавляем пути в sys.path, чтобы импортировать модули из проекта
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='session')
def app():
    """Фикстура для создания экземпляра Flask приложения для тестов."""
    application.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Используем базу данных в памяти
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # Отключаем CSRF защиту в тестах
        'SERVER_NAME': 'localhost'  # Добавляем SERVER_NAME
    })

    with application.app_context():
        db.create_all()

        # Создаем роли, если они не существуют
        admin_role = Role.query.filter_by(name='Администратор').first()
        if not admin_role:
            admin_role = Role(name='Администратор', description='Имеет все права')

        user_role = Role.query.filter_by(name='Пользователь').first()
        if not user_role:
            user_role = Role(name='Пользователь', description='Ограниченные права')

        if not Role.query.filter_by(name='Администратор').first():
            db.session.add(admin_role)
        if not Role.query.filter_by(name='Пользователь').first():
            db.session.add(user_role)

        db.session.commit()

        # Создаем пользователей
        admin_user = User.query.filter_by(login='admin').first()
        if not admin_user:
            admin_user = User(login='admin', first_name='Admin', last_name='Admin', middle_name='Adminovich', role=admin_role)
            admin_user.set_password('admin')
            db.session.add(admin_user)

        user = User.query.filter_by(login='user').first()
        if not user:
            user = User(login='user', first_name='User', last_name='User', middle_name='Userovich', role=user_role)
            user.set_password('user')
            db.session.add(user)

        db.session.commit()

        yield application
        db.drop_all()

@pytest.fixture
def client(app):
    """Фикстура для создания тестового клиента Flask."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Фикстура для запуска команд CLI."""
    return app.test_cli_runner()


@pytest.fixture
def captured_templates(app):
    """Фикстура для перехвата шаблонов, отрендеренных Flask."""
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

import pytest
import string
import random
@pytest.fixture
def utils():
    class Utils:
        def generate_string(self, length):
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            return result_str
    return Utils()