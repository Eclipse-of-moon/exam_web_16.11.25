from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, BooleanField, SelectMultipleField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import SelectMultipleField, widgets

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class BookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Краткое описание', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired(), NumberRange(min=1000, max=2025)])
    publisher = StringField('Издательство', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    pages = IntegerField('Объем (в страницах)', validators=[DataRequired(), NumberRange(min=1)])
    cover = FileField('Обложка', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Только картинки!')])
    submit = SubmitField('Добавить книгу')

class ReviewForm(FlaskForm):
    rating = SelectField(
        'Оценка',
        coerce=int,
        choices=[
            (5, 'отлично'),
            (4, 'хорошо'),
            (3, 'удовлетворительно'),
            (2, 'неудовлетворительно'),
            (1, 'плохо'),
            (0, 'ужасно'),
        ],
        default=5,
        validators=[DataRequired()]
    )
    text = TextAreaField('Текст отзыва', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class EditBookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Краткое описание', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired(), NumberRange(min=1000, max=2025)])
    publisher = StringField('Издание', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    pages = IntegerField('Объем (в страницах)', validators=[DataRequired(), NumberRange(min=1)])
    cover = FileField('Обложка', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Только картинки!')])
    genres = SelectMultipleField(
        'Жанры',
        coerce=int,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    submit = SubmitField('Изменить')