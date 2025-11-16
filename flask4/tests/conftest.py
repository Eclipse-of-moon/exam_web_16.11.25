import pytest
from flask import template_rendered
from contextlib import contextmanager
from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash,check_password_hash


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        if not Role.query.first():
            role = Role(name='admin', description='Administrator')
            db.session.add(role)
            db.session.commit()

            hashed_pw = generate_password_hash('password').decode('utf-8')
            admin = User(
                login='admin',
                password_hash=hashed_pw,
                first_name='Admin',
                role_id=role.id
            )
            db.session.add(admin)
            db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    client.post('/login', data={
        'login': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    return client


@pytest.fixture
@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)