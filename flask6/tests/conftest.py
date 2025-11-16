import pytest
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from app.models import db, User, Course, Review, Category
from app.config import SQLALCHEMY_DATABASE_URI
from flask_login import login_user


@pytest.fixture(scope='session')
def app():
    """Creates the Flask application for the tests."""
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use an in-memory database for tests
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'DEBUG': True
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()

        # Create a test user
        user = User(first_name='Test', last_name='User', login='testuser', password_hash='password')
        db.session.add(user)

        # Create a test category
        category = Category(name='Test Category')
        db.session.add(category)

        # Create a test course
        course = Course(name='Test Course', short_desc='Test Course', full_desc='Test Course', author_id=1,
                        category_id=1, background_image_id='test_image_id')
        db.session.add(course)

        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    """Returns a test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def db_session(app):
    """Yields a database session."""
    with app.app_context():
        yield db.session


def login(client, username, password, app):
    with app.test_request_context():
        return client.post(url_for('auth.login'), data=dict(
            login=username,
            password=password
        ), follow_redirects=True)


def logout(client, app):
    with app.test_request_context():
        return client.get(url_for('auth.logout'), follow_redirects=True)