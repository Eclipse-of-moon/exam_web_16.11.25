from app.models import User, Role
from app import db, create_app
import pytest
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash


def test_login_page(client: FlaskClient):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Логин' in response.text
    assert 'Пароль' in response.text
    assert 'Войти' in response.text

def test_successful_login(client: FlaskClient):
    response = client.post('/login', data={
        'login': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно вошли!'.encode('utf-8') in response.data

def test_logout(auth_client: FlaskClient):
    response = auth_client.get('/logout', follow_redirects=True)
    assert 'Вы вышли из системы'.encode('utf-8') in response.data

def test_failed_login_wrong_password(client: FlaskClient):
    response = client.post('/login', data={
        'login': 'admin',
        'password': 'wrong'
    })
    assert 'Неверный логин или пароль'.encode('utf-8') in response.data

def test_view_nonexistent_user(client: FlaskClient):
    response = client.get('/user/999999')
    assert response.status_code == 404

def test_unauthorized_access(client: FlaskClient):
    # Тест доступа к защищенным страницам без авторизации
    protected_routes = [
        '/users/create',
        '/users/1/edit',
        '/change_password'
    ]

    for route in protected_routes:
        response = client.get(route, follow_redirects=True)
        assert 'Для доступа необходимо авторизоваться.'.encode('utf-8') in response.data
        assert '/login' in response.request.path

def test_create_user_page_access_authorized(auth_client: FlaskClient):
    """Проверяет доступ к странице создания пользователя для авторизованного пользователя."""
    response = auth_client.get('/users/create')
    assert response.status_code == 200
    assert 'Создать пользователя' in response.text


def test_edit_user_page_access_authorized(auth_client: FlaskClient, app):
    """Проверяет доступ к странице редактирования пользователя для авторизованного пользователя."""
    # Предполагаем, что у нас есть хотя бы один пользователь, который можно редактировать.
    # Получим первого пользователя (или создадим, если нет)
    with app.app_context(): # app context
        user = User.query.first()
        if not user:
            hashed_pw = generate_password_hash('password').decode('utf-8')
            role = Role.query.first()
            user = User(login='testuser', password_hash=hashed_pw, first_name='Test', role_id=role.id)
            db.session.add(user)
            db.session.commit()

    response = auth_client.get(f'/users/{user.id}/edit')
    assert response.status_code == 200
    assert 'Редактировать пользователя' in response.text  # Проверяем наличие заголовка формы

def test_edit_user_success(auth_client: FlaskClient, app):
    """Проверяет успешное редактирование пользователя."""
    # Получаем первого пользователя
    with app.app_context(): # app context
        user = User.query.first()
        if not user:
            hashed_pw = generate_password_hash('password').decode('utf-8')
            role = Role.query.first()
            user = User(login='testuser', password_hash=hashed_pw, first_name='Test', role_id=role.id)
            db.session.add(user)
            db.session.commit()

    response = auth_client.post(f'/users/{user.id}/edit', data={
        'first_name': 'Updated',
        'last_name': 'Name',
        'role': 1
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Данные пользователя успешно обновлены!' in response.text
    # Проверим, что данные обновились
    with app.app_context(): # app context
        user = User.query.get(user.id)
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'


def test_change_password_success(auth_client: FlaskClient, client: FlaskClient): # Указываем client
     """Проверяет успешную смену пароля."""
     response = auth_client.post('/change_password', data={
         'old_password': 'password',
         'new_password': 'NewPassword123',
         'confirm_password': 'NewPassword123'
     }, follow_redirects=True)
     assert response.status_code == 200
     assert 'Пароль успешно изменен!' in response.text
     #Проверим что пароль реально изменился (логинимся с новым паролем)
     login_response = client.post('/login', data={
         'login': 'admin',
         'password': 'NewPassword123'
     }, follow_redirects=True)
     assert login_response.status_code == 200
     assert 'Вы успешно вошли!'.encode('utf-8') in login_response.data