from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp
from models import Role
import re

def validate_login(form, field):
    """Логин должен состоять только из латинских букв и цифр и иметь длину не менее 5 символов."""
    if not re.match("^[a-zA-Z0-9]+$", field.data):
        raise ValidationError("Логин должен содержать только латинские буквы и цифры.")
    if len(field.data) < 5:
        raise ValidationError("Логин должен быть не менее 5 символов.")

def validate_password(form, field):
    """Валидация пароля."""
    password = field.data
    if not (8 <= len(password) <= 128):
        raise ValidationError("Пароль должен быть от 8 до 128 символов.")

    if not re.search(r"[a-z]", password):
        raise ValidationError("Пароль должен содержать хотя бы одну строчную букву.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")
    if not re.search(r"\d", password):
        raise ValidationError("Пароль должен содержать хотя бы одну цифру.")
    if re.search(r"\s", password):
        raise ValidationError("Пароль не должен содержать пробелов.")

    # Допустимые символы
    allowed_chars = r'~!@#$%^&*_\-+=()\[\]{}></\'",.;:'
    for char in password:
        if not (char.isalnum() or char in allowed_chars):
            raise ValidationError("Пароль содержит недопустимые символы.")

class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), validate_login])
    password = PasswordField('Пароль', validators=[DataRequired(), validate_password])
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    role = SelectField('Роль', coerce=int, validators=[DataRequired()]) # coerce=int преобразует значение из формы в целое число
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Заполняем choices для SelectField ролями из базы данных
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class EditUserForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    role = SelectField('Роль', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), validate_password])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Изменить пароль')