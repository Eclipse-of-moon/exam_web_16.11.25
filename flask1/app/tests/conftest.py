from datetime import datetime
import pytest
from flask import template_rendered
from contextlib import contextmanager
from app import app as application

@pytest.fixture
def app():
    return application

@pytest.fixture
def client(app):
    return app.test_client()

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

@pytest.fixture
def posts_list():
    return [
        {
            'id': 1,
            'title': 'Заголовок поста',
            'text': 'Текст поста',
            'author': 'Иванов Иван Иванович',
            'date': datetime(2025, 3, 10),
            'image_id': '123.jpg',
            'comments': []
        }
    ]

@pytest.fixture
def test_post():
    return {
        'id': 99,
        'title': 'Test Post Title',
        'text': 'Test post content.',
        'author': 'Test Author',
        'date': datetime(2024, 1, 1),
        'image_id': 'test.jpg',
        'comments': []
    }

@pytest.fixture
def posts_list_with_comments():
    return [
        {
            'id': 1,
            'title': 'Post with Comments',
            'text': 'This post has comments.',
            'author': 'Comment Author',
            'date': datetime(2024, 2, 1),
            'image_id': 'comment.jpg',
            'comments': [
                {'author': 'Commenter 1', 'text': 'First comment', 'date': datetime(2024, 2, 2)},
                {'author': 'Commenter 2', 'text': 'Second comment', 'date': datetime(2024, 2, 3)}
            ]
        }
    ]
