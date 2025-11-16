def test_counter(client):
    # Первое посещение
    response = client.get('/counter')
    assert 'Вы посетили эту страницу 1 раз' in response.text

    # Второе посещение
    response = client.get('/counter')
    assert 'Вы посетили эту страницу 2 раз' in response.text


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Login' in response.text
    assert 'Password' in response.text
    assert 'Submit' in response.text


def test_failed_login(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': '1234'
    })
    assert response.status_code == 200
    assert 'Пользователь не найден, проверьте корректность введенных данных.' in response.text

# Тесты для секретной страницы
def test_secret_page_authenticated(client):
    # Логинимся
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    # Проверяем доступ
    response = client.get('/secret')
    assert response.status_code == 200
    assert 'Секрет' in response.text


def test_redirect_after_login(client):
    # Пытаемся получить доступ к секретной странице
    response = client.get('/secret')
    assert response.status_code == 302  # Редирект на логин

    # Логинимся
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'next': '/secret'
    }, follow_redirects=True)
    assert 'Секрет' in response.text


def test_navbar_links_anonymous(client):
    response = client.get('/')
    assert 'Войти' in response.text
    assert 'Секрет' not in response.text


def test_navbar_links_authenticated(client):
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    response = client.get('/')
    assert 'Выход' in response.text
    assert 'Секрет' in response.text


def test_session_expiry(client):
    # Логинимся без remember me
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })

    # Очищаем сессию
    with client.session_transaction() as sess:
        sess.clear()

    # Проверяем, что пользователь разлогинен
    response = client.get('/secret', follow_redirects=True)
    assert 'Войти' in response.text


def test_user_model():
    from app import User
    # Создаем пользователя
    user = User('1', 'user')
    # Проверяем, что атрибуты id и login установлены правильно
    assert user.id == '1'
    assert user.login == 'user'

def test_load_user():
    from app import load_user
    # Проверяем, что load_user возвращает пользователя для существующего ID
    user = load_user('1')
    assert user is not None
    assert user.id == '1'
    assert user.login == 'user'

    # Проверяем, что load_user возвращает None для несуществующего ID
    user = load_user('99')
    assert user is None


