import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных окружения из .env

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/images/covers') # Папка для обложек
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Максимальный размер загружаемого файла (16MB)