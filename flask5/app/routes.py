# routes.py
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file
from forms import LoginForm, RegistrationForm, EditUserForm, ChangePasswordForm
from models import db, User, Role, VisitLog
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import json
from datetime import datetime
from collections import Counter
import csv
import io

routes_bp = Blueprint('routes', __name__)

def check_rights(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                user = User.query.get(current_user.get_id())
                role = Role.query.get(user.role_id)
                if role:
                    permissions = role.get_permissions()
                    # Если пользователь - администратор, разрешаем доступ
                    if role.name == 'Администратор':
                        return f(*args, **kwargs)
                    # Если user_id текущего пользователя совпадает с user_id в запросе, разрешаем доступ
                    if 'user_id' in kwargs and str(user.id) == kwargs['user_id']:
                        return f(*args, **kwargs)
                    if permission in permissions and permissions[permission]:
                        return f(*args, **kwargs)
                    else:
                        flash('У вас нет прав для просмотра этой страницы.', 'danger')
                        return redirect(url_for('routes.index'))
                else:
                    flash('У вас нет прав для просмотра этой страницы.', 'danger')
                    return redirect(url_for('routes.index'))
            else:
                flash('Необходимо войти в систему.', 'danger')
                return redirect(url_for('routes.login'))

        return decorated_function

    return decorator


@routes_bp.route('/')
def index():
    if current_user.is_authenticated:
        role = Role.query.get(current_user.role_id)
        if role and role.name == 'Администратор':
            return render_template('index.html', users=User.query.all(), current_user_permissions=role.get_permissions(), current_user_id=current_user.id, current_user=current_user)
        elif role and role.name == 'Пользователь':
            return render_template('index.html', users=User.query.all(), current_user_permissions={}, current_user_id=current_user.id, current_user=current_user)
    return render_template('index.html', users=User.query.all(), current_user_permissions={}, current_user_id=None, current_user=current_user)


@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)

            # Записываем в сессию информацию о посещении страницы
            session['last_visited'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return redirect(url_for('routes.index'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', title='Sign In', form=form)


@routes_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('routes.index'))


@routes_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@check_rights('create_user')
def create_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        role = Role.query.get(form.role.data)
        user = User(login=form.login.data, password_hash=hashed_password, first_name=form.first_name.data,
                    last_name=form.last_name.data, middle_name=form.middle_name.data, role=role)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь успешно создан', 'success')
        return redirect(url_for('routes.index'))
    return render_template('create_user.html', title='Register', form=form)


@routes_bp.route('/users/<user_id>')
@login_required
@check_rights('view_user')
def user_details(user_id):
    user = User.query.get(user_id)
    return render_template('user_details.html', user=user)


@routes_bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
@check_rights('edit_user')
def edit_user(user_id):
    user = User.query.get(user_id)
    form = EditUserForm(obj=user)
    is_editing_self = str(current_user.id) == user_id  # Проверяем, редактирует ли пользователь свой профиль
    current_user_role = Role.query.get(current_user.role_id) # Получаем роль текущего пользователя

    if is_editing_self and current_user_role.name == 'Пользователь':
        # Пользователь редактирует свой профиль и он "Пользователь"
        del form.role  # Удаляем поле role из формы

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.middle_name = form.middle_name.data

        if not is_editing_self or current_user_role.name != 'Пользователь':
            #Если не редактирует сам или Админ, то меняем роль
            user.role_id = form.role.data
        db.session.commit()
        flash('Профиль пользователя успешно обновлен!', 'success')
        return redirect(url_for('routes.user_details', user_id=user.id))

    return render_template('edit_user.html', title='Edit User', form=form, user=user, is_editing_self=is_editing_self)


@routes_bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_user')
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь успешно удален', 'success')
    return redirect(url_for('routes.index'))


@routes_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.get_id())
        if user.check_password(form.old_password.data):
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('routes.index'))
        else:
            flash('Неверный старый пароль', 'danger')
    return render_template('change_password.html', title='Change Password', form=form)


