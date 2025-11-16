from flask import Blueprint, render_template, request

from routes import check_rights
from models import VisitLog, db
from flask_login import login_required
from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user
import csv
import io
from models import VisitLog, db, User


reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
@check_rights('visit_log')
def visit_log():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    visits = VisitLog.query.order_by(VisitLog.created_at.desc()).paginate(page=page, per_page=per_page)

    # Создаем пронумерованный список записей
    enumerated_visits = enumerate(visits.items, start=(page - 1) * per_page + 1)

    # Передаем оба объекта в шаблон
    return render_template('reports/visit_log.html', visits=enumerated_visits, pagination=visits)

def export_page_visits_to_csv(data):
    si = io.StringIO()  # Создаем строковый буфер для записи CSV данных
    cw = csv.writer(si, delimiter=';', quoting=csv.QUOTE_MINIMAL)  # Создаем CSV writer
    cw.writerow(['Path', 'Count'])  # Записываем заголовок CSV
    for row in data:
        cw.writerow([row.path, row.count])  # Записываем данные в CSV
    response = make_response(si.getvalue())  # Создаем Response из CSV данных
    response.headers['Content-Disposition'] = 'attachment; filename=page_visits.csv'  # Устанавливаем заголовок для скачивания файла
    response.headers['Content-Type'] = 'text/csv'  # Устанавливаем MIME-тип
    return response

@reports_bp.route('/page_visits')
@login_required
@check_rights('page_visits')
def page_visits():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    page_visits_data = db.session.query(VisitLog.path, db.func.count(VisitLog.id).label('count')) \
        .group_by(VisitLog.path) \
        .order_by(db.func.count(VisitLog.id).desc()) \
        .paginate(page=page, per_page=per_page)

    # Создаем пронумерованный список
    enumerated_page_visits = enumerate(page_visits_data.items, start=(page - 1) * per_page + 1)

    if request.args.get('export_csv'):
        return export_page_visits_to_csv(page_visits_data.items)

    return render_template('reports/page_visits.html', page_visits=enumerated_page_visits, pagination=page_visits_data)  # Передаем и пронумерованный список, и объект пагинации

def export_user_visits_to_csv(data):
    si = io.StringIO()
    cw = csv.writer(si, delimiter=';', quoting=csv.QUOTE_MINIMAL)  # Изменено: quoting=csv.QUOTE_MINIMAL
    cw.writerow(['User', 'Count'])
    for row in data:
        user_name = f"{row.first_name} {row.last_name} {row.middle_name}" if row.first_name else "Неаутентифицированный пользователь"
        cw.writerow([user_name, row.count])
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=user_visits.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@reports_bp.route('/user_visits')
@login_required
@check_rights('user_visits')
def user_visits():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_visits_data = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        User.middle_name,
        db.func.count(VisitLog.id).label('count')
    ).join(VisitLog, User.id == VisitLog.user_id, isouter=True).group_by(User.id, User.first_name, User.last_name, User.middle_name).order_by(db.func.count(VisitLog.id).desc()).paginate(page=page, per_page=per_page)

    enumerated_user_visits = enumerate(user_visits_data.items, start=(page - 1) * per_page + 1)

    if request.args.get('export_csv'):
        return export_user_visits_to_csv(user_visits_data.items)

    return render_template('reports/user_visits.html', user_visits=enumerated_user_visits, pagination = user_visits_data)

@reports_bp.route('/user_visit_log')
@login_required
def user_visit_log():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    visits = VisitLog.query.filter_by(user_id=current_user.id).order_by(VisitLog.created_at.desc()).paginate(page=page, per_page=per_page)
    enumerated_visits = enumerate(visits.items, start=(page - 1) * per_page + 1)
    return render_template('reports/user_visit_log.html', visits=enumerated_visits, pagination=visits)