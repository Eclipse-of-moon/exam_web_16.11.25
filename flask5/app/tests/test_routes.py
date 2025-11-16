import pytest
from flask import url_for
from flask_login import login_user
from models import User, Role, db
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash


def test_view_user(client, app):
    """Тест просмотра информации о пользователе у неавторизованных пользователей."""
    with app.app_context():
        # Создаем тестового пользователя (если его нет)
        user = User.query.filter_by(login='testuser').first()
        if not user:
            role = Role.query.filter_by(name='Пользователь').first()
            user = User(login='testuser', first_name='Test', last_name='User', middle_name='Testovich', role=role)
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

        # Получаем ID тестового пользователя
        user = User.query.filter_by(login='testuser').first()
        user_id = user.id
        url = url_for('routes.user_details', user_id=user_id)

        # Отправляем запрос на страницу пользователя
        response = client.get(url)
        assert response.status_code == 302  # Должен быть редирект на страницу логина

def test_create_user_requires_login(client):
    """Проверяет, что для создания пользователя требуется вход в систему."""
    response = client.get(url_for('routes.create_user'))
    assert response.status_code == 302
    assert response.location.startswith(url_for('routes.login', _external=False))

from flask_login import login_user
from flask import url_for

def test_display_create_form(client, app):
    """Проверяет, что администратор видит форму создания пользователя."""
    with app.app_context():
        # Получаем админа
        admin = User.query.filter_by(login='admin').first()

        # Логинимся как админ
        with app.test_request_context():  # Создаем контекст запроса
            login_user(admin)

        response = client.get(url_for('routes.create_user'))
        assert response.status_code == 200
        assert '<form' in response.data.decode('utf-8') and 'name="login"' in response.data.decode('utf-8') and 'name="password"' in response.data.decode('utf-8')  # Проверяем наличие формы

def test_create_user_forbidden(client):
    """Проверяет, что неавторизованный пользователь не видит форму создания пользователя (403)."""
    response = client.get(url_for('routes.create_user'))
    assert response.status_code == 302

def test_delete_user(client, app):
    """Проверяет, что администратор может удалить пользователя."""
    with app.app_context():
        # Создаем тестового пользователя для удаления
        user_to_delete = User(login='testuser_delete', first_name='Test', last_name='User', middle_name='Testovich')
        user_to_delete.set_password('password')
        db.session.add(user_to_delete)
        db.session.commit()

        # Получаем ID созданного пользователя
        user_id = user_to_delete.id

        # Логинимся как админ
        admin = User.query.filter_by(login='admin').first()
        with app.test_request_context():
            login_user(admin)

        # Отправляем POST-запрос на удаление пользователя
        response = client.post(url_for('routes.delete_user', user_id=user_id), follow_redirects=True)
        assert response.status_code == 200

        # Проверяем, что пользователя больше нет в базе данных
        deleted_user = User.query.filter_by(id=user_id).first()
        assert deleted_user is None

def test_delete_user_forbidden(client, app):
    """Проверяет, что обычный пользователь не может удалить другого пользователя."""
    with app.app_context():
        # Создаем тестового пользователя
        user_to_delete = User(login='testuser_delete', first_name='Test', last_name='User', middle_name='Testovich')
        user_to_delete.set_password('password')
        db.session.add(user_to_delete)
        db.session.commit()

        # Создаем обычного пользователя
        regular_user = User(login='regular_user', first_name='Regular', last_name='User', middle_name='Testovich')
        regular_user.set_password('password')
        db.session.add(regular_user)
        db.session.commit()


        # Логинимся как обычный пользователь
        regular_user = User.query.filter_by(login='regular_user').first()
        with app.test_request_context():
            login_user(regular_user)

        # Отправляем POST-запрос на удаление пользователя
        response = client.post(url_for('routes.delete_user', user_id=user_to_delete.id), follow_redirects=True)
        assert response.status_code == 200

        # Проверяем, что пользователь все еще есть в базе данных
        existing_user = User.query.filter_by(id=user_to_delete.id).first()
        assert existing_user is not None

def test_login_page(client: FlaskClient):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Логин' in response.text
    assert 'Пароль' in response.text
    assert 'Войти' in response.text

def test_create_page(client: FlaskClient):
    response = client.get('/users/create')
    assert response.status_code == 302


def test_failed_login_wrong_password(client: FlaskClient):
    response = client.post('/login', data={
        'login': 'admin',
        'password': 'wrong'
    })
    assert 'Неверный логин или пароль'.encode('utf-8') in response.data

def test_view_nonexistent_user(client: FlaskClient):
    response = client.get('/user/999999')
    assert response.status_code == 404

def test_successful_login(client: FlaskClient):
    response = client.post('/login', data={
        'login': 'admin',
        'password': 'admin'
    }, follow_redirects=True)
    assert response.status_code == 200
