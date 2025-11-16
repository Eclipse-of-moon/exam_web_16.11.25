import os
from app import app, db
from models import User, Role, Book, Genre, ReviewStatus
from werkzeug.security import generate_password_hash

def populate_genres():
    with app.app_context():
        if Genre.query.count() == 0:
            genres = [
                Genre(name='Фантастика'),
                Genre(name='Фэнтези'),
                Genre(name='Детектив'),
                Genre(name='Роман'),
                Genre(name='Научная литература'),
                Genre(name='Приключения'),
                Genre(name='Биография'),
            ]
            db.session.add_all(genres)
            db.session.commit()
            print("Жанры добавлены в базу данных.")
        else:
            print("Жанры уже существуют в базе данных.")


def populate_roles():
    with app.app_context():
        if Role.query.count() == 0:
            admin_role = Role(name='administrator', description='Суперпользователь, имеет полный доступ к системе')
            moderator_role = Role(name='moderator', description='Может редактировать данные книг и производить модерацию рецензий')
            user_role = Role(name='user', description='Может оставлять рецензии')

            db.session.add_all([admin_role, moderator_role, user_role])
            db.session.commit()
            print("Роли добавлены в базу данных.")
        else:
            print("Роли уже существуют в базе данных.")

def populate_users():
    with app.app_context():
        if User.query.count() == 0:
            admin_role = Role.query.filter_by(name='administrator').first()
            moderator_role = Role.query.filter_by(name='moderator').first()
            user_role = Role.query.filter_by(name='user').first()

            if not admin_role or not moderator_role or not user_role:
                print("Роли не найдены. Запустите сначала функцию populate_roles.")
                return

            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin'),
                first_name='Админ',
                last_name='Админов',
                middle_name='Админович',
                role=admin_role
            )

            moderator_user = User(
                username='moderator',
                password_hash=generate_password_hash('moderator'),
                first_name='Модератор',
                last_name='Модераторов',
                middle_name='Модераторович',
                role=moderator_role
            )

            user1 = User(
                username='user1',
                password_hash=generate_password_hash('user1'),
                first_name='Полина',
                last_name='Филиппова',
                middle_name='Владимировна',
                role=user_role
            )
            user2 = User(
                username='user2',
                password_hash=generate_password_hash('user2'),
                first_name='Виктор',
                last_name='Мохначёв',
                middle_name='Сергеевич',
                role=user_role
            )
            user3 = User(
                username='user3',
                password_hash=generate_password_hash('user3'),
                first_name='Арифа',
                last_name='Ашрафи',
                middle_name='',
                role=user_role
            )

            db.session.add_all([admin_user, moderator_user, user1, user2, user3])
            db.session.commit()
            print("Пользователи добавлены в базу данных.")
        else:
            print("Пользователи уже существуют в базе данных.")

def populate_review_statuses():
    with app.app_context():
        if ReviewStatus.query.count() == 0:
            statuses = [
                ReviewStatus(name='на рассмотрении'),
                ReviewStatus(name='одобрена'),
                ReviewStatus(name='отклонена'),
            ]
            db.session.add_all(statuses)
            db.session.commit()
            print("Статусы рецензий добавлены в базу данных.")
        else:
            print("Статусы рецензий уже существуют в базе данных.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    populate_roles()
    populate_users()
    populate_genres()
    populate_review_statuses()