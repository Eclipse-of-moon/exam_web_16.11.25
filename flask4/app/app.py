import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Role, User
from routes import routes_bp
from flask_login import LoginManager


app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '3266a513ac62f8c4be0670900e7fd71342a62f0fc685d900c38985938f49ca39')

# Инициализация SQLAlchemy
db.init_app(app)

# Инициализация Flask-Migrate для миграций базы данных
migrate = Migrate(app, db)

# Конфигурация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)  # Связываем login_manager с app
login_manager.login_view = 'routes.login'
login_manager.login_message = "У вас нет прав доступа к этой странице."

# Регистрация blueprint с маршрутами
app.register_blueprint(routes_bp)

# Функция для загрузки пользователя (необходима для Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание таблиц базы данных и ролей/пользователей
def create_app():
    with app.app_context():
        db.create_all()
        print("Создание таблиц выполнено")

        # Проверяем, существуют ли роли
        admin_role = Role.query.filter_by(name='Администратор').first()
        user_role = Role.query.filter_by(name='Пользователь').first()

        if not admin_role:
            print("Роль Администратор не найдена, создание...")
            admin_role = Role(name='Администратор', description='Имеет все права')
            admin_role.set_permissions({
                'create_user': True,
                'edit_user': True,
                'delete_user': True,
                'view_user': True,
                'view_logs': True,
                'view_self': True,
                'edit_self': True
            })
            db.session.add(admin_role)
            print("Роль Администратор создана")
        else:
            print("Роль Администратор уже существует")

        if not user_role:
            print("Роль Пользователь не найдена, создание...")
            user_role = Role(name='Пользователь', description='Ограниченные права')
            user_role.set_permissions({
                'view_self': True,
                'edit_self': True,
                'view_logs': True
            })
            db.session.add(user_role)
            print("Роль Пользователь создана")
        else:
            print("Роль Пользователь уже существует")

        # Проверяем, есть ли администратор
        admin_user = User.query.filter_by(login='admin').first()
        if not admin_user:
            admin_user = User(login='admin', first_name='Admin', last_name='Admin', middle_name='Adminovich', role=admin_role)
            admin_user.set_password('admin')
            db.session.add(admin_user)
            print("Пользователь Admin создан")
        else:
            print("Пользователь Admin уже существует")

        # Проверяем, есть ли простой пользователь
        simple_user = User.query.filter_by(login='user').first()
        if not simple_user:
            simple_user = User(login='user', first_name='User', last_name='User', middle_name='Userovich', role=user_role)
            simple_user.set_password('user')
            db.session.add(simple_user)
            print("Пользователь User создан")
        else:
            print("Пользователь User уже существует")

        db.session.commit()
        print("Данные записаны в базу данных")
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print(app.url_map)
    app.run(debug=True)