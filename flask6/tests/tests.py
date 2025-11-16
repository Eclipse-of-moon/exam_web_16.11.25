import pytest
from flask import url_for
from app.models import User, Course, Review, Category  # Import Category
from flask_login import login_user
from app.models import db


def login(client, username, password, app):
    with app.test_request_context():
        return client.post(url_for('auth.login'), data=dict(
            login=username,
            password=password
        ), follow_redirects=True)


def logout(client, app):
    with app.test_request_context():
        return client.get(url_for('auth.logout'), follow_redirects=True)

def test_show_reviews(client, db_session, app):

    with app.test_request_context():
        login(client, 'testuser', 'password', app)

        course = db_session.execute(db.select(Course)).scalar()

        review = Review(course_id=course.id, user_id=1, rating=4, text='Another test review.')
        db_session.add(review)
        db_session.commit()

        response = client.get(url_for('courses.show', course_id=course.id))

        assert response.status_code == 200
        assert b'Another test review.' in response.data

        logout(client, app)


def test_show_all_reviews(client, db_session, app):
    with app.test_request_context():
        login(client, 'testuser', 'password', app)
        course = db_session.execute(db.select(Course)).scalar()

        review = Review(course_id=course.id, user_id=1, rating=3, text='Test review on review page.')
        db_session.add(review)
        db_session.commit()

        response = client.get(url_for('courses.reviews', course_id=course.id))

        assert response.status_code == 200
        assert b'Test review on review page.' in response.data

        logout(client, app)