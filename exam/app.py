import os
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import hashlib
from flask_bootstrap import Bootstrap
from models import db, User, Role, Book, Genre, Review, Cover
from forms import LoginForm, BookForm, ReviewForm, EditBookForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes.login'
login_manager.login_message = "Для выполнения данного действия необходимо пройти процедуру аутентификации"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from functools import wraps

def check_role(role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Требуется аутентификация", "danger")
                return redirect(url_for('routes.login'))

            _role_names = role_names
            if isinstance(_role_names, str):
                _role_names = [_role_names]

            if current_user.role.name not in _role_names:
                flash("У вас недостаточно прав для выполнения данного действия", "danger")
                return redirect(url_for('routes.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

from routes import routes_bp
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    app.run(debug=True)