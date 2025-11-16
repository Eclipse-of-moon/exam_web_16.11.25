from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Связь между таблицами книг и жанров (многие ко многим)
book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Cover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True) # Добавлено unique=True
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f'<Cover {self.filename}>'

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Genre {self.name}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.Integer, db.ForeignKey('cover.id', ondelete='CASCADE'), nullable=False)
    cover = db.relationship('Cover', backref=db.backref('books', lazy=True))
    genres = db.relationship('Genre', secondary=book_genre, backref=db.backref('books', lazy=True))
    reviews = db.relationship('Review', backref='book', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Book {self.title}>'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class ReviewStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<ReviewStatus {self.name}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    status_id = db.Column(db.Integer, db.ForeignKey('review_status.id'), nullable=False, default=1)  # Статус "на рассмотрении" по умолчанию
    status = db.relationship('ReviewStatus', backref='reviews')

    def __repr__(self):
        return f'<Review by {self.user_id} on {self.book_id}>'