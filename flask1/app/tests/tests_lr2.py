import pytest
from flask import url_for
from forms import PhoneForm

def test_url_params_displays_all_params(client):
    # Проверяет, что на странице "Параметры URL" отображаются все переданные параметры.
    response = client.get('/url_params?param1=value1&param2=value2')
    assert response.status_code == 200
    assert b'param1' in response.data
    assert b'value1' in response.data
    assert b'param2' in response.data
    assert b'value2' in response.data

def test_headers_displays_all_headers(client):
    # Проверяет, что на странице "Заголовки запроса" отображаются все заголовки запроса.
    response = client.get('/headers', headers={'X-Custom-Header': 'custom_value'})
    assert response.status_code == 200
    assert b'X-Custom-Header' in response.data
    assert b'custom_value' in response.data

def test_cookies_sets_and_deletes_cookie(client):
    # Первый запрос устанавливает куку.
    response = client.get('/cookies')
    assert response.status_code == 200
    assert 'name' in response.headers.get('Set-Cookie', '')

    # Второй запрос удаляет куку.
    response = client.get('/cookies')
    assert response.status_code == 200
    assert 'Expires=Thu, 01 Jan 1970 00:00:00 GMT' in response.headers.get('Set-Cookie', '')

def test_form_params_displays_submitted_values(client):
    # Проверяет, что на странице "Параметры формы" отображаются введённые пользователем значения после отправки формы.
    response = client.post('/form_params', data={'theme': 'test_theme', 'text': 'test_text'})
    assert response.status_code == 200
    assert b'theme' in response.data
    assert b'test_theme' in response.data
    assert b'text' in response.data
    assert b'test_text' in response.data

def test_phone_form_valid_number_formatting(client):
    # Проверяет форматирование корректного номера телефона (11 цифр).
    form = PhoneForm(data={'phone_number': '79161234567'})
    assert form.validate()
    formatted_number = form.validate_phone_number(form.phone_number)
    assert formatted_number == '8-916-123-45-67'

def test_phone_form_valid_number_formatting_short(client):
    # Проверяет форматирование корректного номера телефона (10 цифр).
    form = PhoneForm(data={'phone_number': '9161234567'})
    assert form.validate()
    formatted_number = form.validate_phone_number(form.phone_number)
    assert formatted_number == '8-916-123-45-67'

def test_phone_form_valid_number_formatting_with_plus(client):
    # Проверяет форматирование корректного номера телефона (с +7 вначале).
    form = PhoneForm(data={'phone_number': '+79161234567'})
    assert form.validate()
    formatted_number = form.validate_phone_number(form.phone_number)
    assert formatted_number == '8-916-123-45-67'

def test_phone_form_invalid_number_length_short(client):
    # Проверяет обработку некорректного номера телефона (слишком короткий).
    form = PhoneForm(data={'phone_number': '123'})
    assert not form.validate()
    assert "Недопустимый ввод. Неверное количество цифр." in form.phone_number.errors

def test_phone_form_invalid_number_length_long(client):
    # Проверяет обработку некорректного номера телефона (слишком длинный).
    form = PhoneForm(data={'phone_number': '123456789012'})
    assert not form.validate()
    assert "Недопустимый ввод. Неверное количество цифр." in  form.phone_number.errors

def test_phone_form_invalid_characters(client):
    # Проверяет обработку некорректного номера телефона (содержит недопустимые символы).
    form = PhoneForm(data={'phone_number': 'abc'})
    assert not form.validate()
    assert "Недопустимый ввод. В номере телефона встречаются недопустимые символы." in form.phone_number.errors

def test_phone_form_invalid_characters_mixed(client):
    # Проверяет обработку некорректного номера телефона (содержит недопустимые символы в середине).
    form = PhoneForm(data={'phone_number': '7916abc1234'})
    assert not form.validate()
    assert "Недопустимый ввод. В номере телефона встречаются недопустимые символы." in form.phone_number.errors

def test_phone_form_displays_error_message(client):
    # Проверяет, что при вводе некорректного номера на странице /form отображается сообщение об ошибке и класс is-invalid Bootstrap.
    response = client.post('/form', data={'phone_number': 'abc'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.' in response.data.decode('utf-8')
    assert b'is-invalid' in response.data

def test_phone_form_displays_formatted_number(client):
    # Проверяет, что при вводе корректного номера на странице /form отображается отформатированный номер.
    response = client.post('/form', data={'phone_number': '79161234567'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'8-916-123-45-67' in response.data

def test_phone_form_displays_error_message_length(client):
    # Проверяет, что при вводе номера неверной длины на странице /form отображается сообщение об ошибке и класс is-invalid Bootstrap.
    response = client.post('/form', data={'phone_number': '123'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.data.decode('utf-8')
    assert b'is-invalid' in response.data

def test_phone_form_invalid_plus_number(client):
    # Проверяет обработку номера, начинающегося с "+", но имеющего неправильную длину.
    response = client.post('/form', data={'phone_number': '+7906338076'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.data.decode('utf-8')
    assert b'is-invalid' in response.data