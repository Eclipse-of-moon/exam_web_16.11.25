from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import hashlib
import os
import bleach
from sqlalchemy.exc import SQLAlchemyError
from app import db, check_role
from models import User, Role, Book, Genre, Review, Cover, ReviewStatus
from forms import LoginForm, BookForm, ReviewForm, EditBookForm
from config import Config
from sqlalchemy.orm.exc import NoResultFound

routes_bp = Blueprint('routes', __name__)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

@routes_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.year.desc()).paginate(page=page, per_page=10)
    approved_status = ReviewStatus.query.filter_by(name='одобрена').first()

    # Средний рейтинг и количество отзывов для каждой книги
    book_data = []
    for book in books.items:
        avg_rating = db.session.query(db.func.avg(Review.rating)).filter(Review.book_id == book.id, Review.status_id == approved_status.id).scalar() or 0
        review_count = Review.query.filter_by(book_id=book.id, status_id=approved_status.id).count()
        book_data.append({
            'book': book,
            'avg_rating': avg_rating,
            'review_count': review_count
        })

    return render_template('index.html', books=books, book_data=book_data)

@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('routes.index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    return render_template('login.html', form=form)

@routes_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@routes_bp.route('/add_book', methods=['GET', 'POST'])
@login_required
@check_role('administrator')
def add_book():
    form = BookForm()
    genres = Genre.query.all()

    if form.validate_on_submit():
        try:
            cover_image = form.cover.data
            filename = secure_filename(cover_image.filename)
            mime_type = cover_image.content_type

            md5_hash = hashlib.md5(cover_image.read()).hexdigest()
            cover_image.seek(0)

            existing_cover = Cover.query.filter_by(md5_hash=md5_hash).first()
            if existing_cover:
                cover_id = existing_cover.id
                flash('Обложка с таким содержанием уже существует. Используется существующая обложка.', 'info')
            else:
                new_filename = f"{hashlib.md5(filename.encode('utf-8')).hexdigest()}.jpg"
                file_path = os.path.join(Config.UPLOAD_FOLDER, new_filename)

                cover_image.save(file_path)

                new_cover = Cover(filename=new_filename, mime_type=mime_type, md5_hash=md5_hash)
                db.session.add(new_cover)
                db.session.flush()
                cover_id = new_cover.id

            selected_genre_ids = request.form.getlist('genres')
            selected_genres = [Genre.query.get(int(genre_id)) for genre_id in selected_genre_ids]

            cleaned_description = bleach.clean(form.description.data)

            new_book = Book(
                title=form.title.data,
                description=cleaned_description,
                year=form.year.data,
                publisher=form.publisher.data,
                author=form.author.data,
                pages=form.pages.data,
                cover_id=cover_id,
                genres=selected_genres
            )

            db.session.add(new_book)
            db.session.commit()
            flash('Книга успешно добавлена!', 'success')
            return redirect(url_for('routes.index'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Произошла ошибка базы данных: {e}', 'danger')
            return render_template('add_book.html', form=form, genres=genres)

        except Exception as e:
            db.session.rollback()
            flash(f'Произошла непредвиденная ошибка: {e}', 'danger')
            return render_template('add_book.html', form=form, genres=genres)

    return render_template('add_book.html', form=form, genres=genres)

@routes_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    review_form = ReviewForm()
    approved_status = ReviewStatus.query.filter_by(name='одобрена').first()

    # Получаем только одобренные отзывы
    reviews = Review.query.filter_by(book_id=book_id, status_id=approved_status.id).order_by(Review.date_added.desc()).all()

    # Проверяем, писал ли текущий пользователь отзыв на эту книгу
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()

    # Считаем средний рейтинг только для одобренных отзывов
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter(Review.book_id == book.id, Review.status_id == approved_status.id).scalar() or 0

    return render_template('book_detail.html', book=book, review_form=review_form, avg_rating=avg_rating, reviews=reviews, user_review=user_review)

@routes_bp.route('/book/<int:book_id>/add_review', methods=['GET', 'POST'])
@login_required
@check_role('user')
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()

    # Проверяем, писал ли уже пользователь отзыв к этой книге
    existing_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()

    if existing_review:
        # Если отзыв существует, проверяем его статус
        if existing_review.status.name == 'одобрена':
            flash('Вы уже оставили одобренный отзыв на эту книгу.', 'warning')
            return redirect(url_for('routes.book_detail', book_id=book_id))
        elif existing_review.status.name == 'на рассмотрении':
            flash('Ваш отзыв уже находится на рассмотрении.', 'warning')
            return redirect(url_for('routes.book_detail', book_id=book_id))
        else:  # Если статус "отклонена", удаляем старый отзыв
            db.session.delete(existing_review)
            db.session.commit()


    if form.validate_on_submit():
        try:
            # Санитайзинг текста отзыва
            cleaned_text = bleach.clean(form.text.data)

            new_review = Review(
                book_id=book.id,
                user_id=current_user.id,
                rating=form.rating.data,
                text=cleaned_text
            )
            db.session.add(new_review)
            db.session.commit()
            flash('Отзыв успешно добавлен и ожидает модерации!', 'success')
            return redirect(url_for('routes.book_detail', book_id=book_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Произошла ошибка при сохранении отзыва: {e}', 'danger')
            return render_template('add_review.html', form=form, book=book) #Отображаем форму с ошибкой

    return render_template('add_review.html', form=form, book=book)

@routes_bp.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
@check_role(['moderator', 'administrator'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = EditBookForm(obj=book)
    genres = Genre.query.all()
    form.genres.choices = [(genre.id, genre.name) for genre in genres]

    if form.validate_on_submit():
        try:
            # Санитайзинг описания
            cleaned_description = bleach.clean(form.description.data)

            book.title = form.title.data
            book.description = cleaned_description
            book.year = form.year.data
            book.publisher = form.publisher.data
            book.author = form.author.data
            book.pages = form.pages.data

            selected_genre_ids = request.form.getlist('genres')
            selected_genres = [Genre.query.get(int(genre_id)) for genre_id in selected_genre_ids]
            book.genres = selected_genres

            db.session.commit()
            flash('Данные книги успешно обновлены!', 'success')
            return redirect(url_for('routes.book_detail', book_id=book.id))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash('При сохранении данных произошла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('edit_book.html', form=form, book=book, genres=genres)

    return render_template('edit_book.html', form=form, book=book, genres=genres)

@routes_bp.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
@check_role('administrator')
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    cover_path = os.path.join(Config.UPLOAD_FOLDER, book.cover.filename)
    if os.path.exists(cover_path):
        os.remove(cover_path)

    db.session.delete(book)
    db.session.commit()
    flash('Книга успешно удалена!', 'success')
    return redirect(url_for('routes.index'))

@routes_bp.route('/my_reviews')
@login_required
@check_role('user')
def my_reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    return render_template('my_reviews.html', reviews=reviews)

@routes_bp.route('/moderate_reviews', methods=['GET'])
@login_required
@check_role('moderator')
def moderate_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Количество рецензий на странице
    status_filter = request.args.get('status', 'на рассмотрении')  # Статус по умолчанию

    # Получаем объект ReviewStatus для выбранного статуса
    status = ReviewStatus.query.filter_by(name=status_filter).first()
    if status:
        reviews = Review.query.filter_by(status_id=status.id).order_by(Review.date_added.desc()).paginate(page=page, per_page=per_page)
    else:
        # Если статус не найден, показываем "на рассмотрении"
        pending_status = ReviewStatus.query.filter_by(name='на рассмотрении').first()
        reviews = Review.query.filter_by(status_id=pending_status.id).order_by(Review.date_added.desc()).paginate(page=page, per_page=per_page)
        status_filter = 'на рассмотрении'

    return render_template('moderate_reviews.html', reviews=reviews, current_status=status_filter)

@routes_bp.route('/moderate_review/<int:review_id>')
@login_required
@check_role('moderator')
def moderate_review(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template('moderate_review.html', review=review)

@routes_bp.route('/approve_review/<int:review_id>')
@login_required
@check_role('moderator')
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    approved_status = ReviewStatus.query.filter_by(name='одобрена').first()
    review.status_id = approved_status.id
    db.session.commit()
    flash('Рецензия одобрена.', 'success')
    return redirect(url_for('routes.moderate_reviews'))

@routes_bp.route('/reject_review/<int:review_id>')
@login_required
@check_role('moderator')
def reject_review(review_id):
    review = Review.query.get_or_404(review_id)
    rejected_status = ReviewStatus.query.filter_by(name='отклонена').first()
    review.status_id = rejected_status.id
    db.session.commit()
    flash('Рецензия отклонена.', 'success')
    return redirect(url_for('routes.moderate_reviews'))

@routes_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)