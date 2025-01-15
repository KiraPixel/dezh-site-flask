import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, session

from modules import kuber_controller
from active_directory_module.ad_controller import check_on_admin, search_users
from app.flask_custom_wraps import validate_sessions

bp = Blueprint('main', __name__)

#Страница логина
@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if check_on_admin(username, password):
            session['user'] = username
            session['password'] = password
            return redirect(url_for('search'))
        else:
            return 'Access Denied: You are not in the Users_dadmins OU.', 403
    return render_template('login.html')

# поиск пользаков
@validate_sessions()
@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_filter = request.form.get('search_filter')
        results = search_users(session['user'], session['password'], f'(displayName=*{search_filter}*)')
        return render_template('search.html', results=results)

    return render_template('search.html')

# работа по логину
@validate_sessions()
@bp.route('/instruments', methods=['GET', 'POST'])
def instruments():
    return render_template('instruments.html')

# страница с терминалми
@validate_sessions()
@bp.route('/terminals/<username>')
def terminals_page(username):
    return render_template('terminals.html', username=username)

# страница кубера
@validate_sessions()
@bp.route('/kuber')
def kuber():
    username = session['user'].split('\\')[1]
    password = session['password']
    kuber_controller.update_file(username, password)
    return render_template('console.html')

# смена пароля
@validate_sessions()
@bp.route('/change_pass/<username>')
def change_pass(username):
    return render_template('change_password.html', username=username)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Функция для получения всех отпусков из базы данных
def get_vacations():
    conn = sqlite3.connect('vacations.db')
    c = conn.cursor()
    c.execute('SELECT id, employee_name, cover_name, vacation_date, author FROM vacations')
    vacations = c.fetchall()
    conn.close()
    return vacations


# Маршрут для добавления, отображения и удаления отпусков
@validate_sessions()
@bp.route('/vacations', methods=['GET', 'POST'])
def vacations():
    if request.method == 'POST':
        if 'employee_name' in request.form and 'cover_name' in request.form and 'vacation_date' in request.form:
            # Добавление отпуска
            employee_name = request.form.get('employee_name')
            cover_name = request.form.get('cover_name')
            vacation_date = request.form.get('vacation_date')

            conn = sqlite3.connect('vacations.db')
            c = conn.cursor()
            c.execute('INSERT INTO vacations (employee_name, cover_name, vacation_date, author) VALUES (?, ?, ?, ?)',
                      (employee_name, cover_name, vacation_date, session['user']))
            conn.commit()
            conn.close()

        elif 'id' in request.form:
            # Удаление отпуска
            vacation_id = request.form.get('id')

            conn = sqlite3.connect('vacations.db')
            c = conn.cursor()
            c.execute('DELETE FROM vacations WHERE id = ?', (vacation_id,))
            conn.commit()
            conn.close()

    vacations = get_vacations()
    return render_template('vacation.html', vacations=vacations)