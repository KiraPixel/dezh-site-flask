from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from ad_controller import check_on_admin, search_users, change_user_password, unlock_user_account
from term_controller import check_user_session_on_terminal, logoff_user_from_terminal
from mail_sender import send_email
import json
import sqlite3

app = Flask(__name__)
app.secret_key = 'asdasds123z'


@app.route('/', methods=['GET', 'POST'])
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


@app.route('/api/check_on_admin', methods=['POST'])
def api_check_on_admin():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if check_on_admin(username, password):
        session['user'] = username
        session['password'] = password

        return jsonify({'status': 'ok'})
    else:
        return jsonify({'error': 'Unauthorized'}), 401


@app.route('/api/check_user_session', methods=['POST'])
def api_check_user_session():
    if 'user' not in session or 'password' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    username = data.get('username')
    terminal = data.get('terminal')

    session_id = check_user_session_on_terminal(username, terminal)
    if session_id:
        return jsonify({'status': 'ok', 'session_id': session_id})
    else:
        return jsonify({'status': 'not_found'}), 404


@app.route('/api/logout_session', methods=['POST'])
def api_logout_session():
    if 'user' not in session or 'password' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    terminal = data.get('terminal')
    session_id = data.get('session_id')

    status = logoff_user_from_terminal(terminal, session_id)
    if status:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error'}), 404


@app.route('/api/change_password', methods=['POST'])
def api_change_password():
    if 'user' not in session or 'password' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    target_user = data.get('target_user')
    new_password = data.get('new_password')

    success = change_user_password(session['user'], session['password'], target_user, new_password)
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error'}), 500


@app.route('/api/unlock_account', methods=['POST'])
def api_unlock_account():
    if 'user' not in session or 'password' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    target_user = data.get('target_user')
    print(target_user)

    success = unlock_user_account(session['user'], session['password'], f'{target_user}')
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error'}), 500


@app.route('/api/search_users', methods=['POST'])
def api_search_users():
    if 'user' not in session or 'password' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    search_filter = data.get('search_filter')
    login = data.get('login')
    print(login)
    if login is not None:
        print('lasdasd')
        results = search_users(session['user'], session['password'], f'(sAMAccountName=*{search_filter}*)', hard=True)
        if results:
            print('asdasd')
            return ({'status': 'ok'})
        else:
            return jsonify({'status': 'not_found'}), 404
    else:
        results = search_users(session['user'], session['password'], f'(displayName=*{search_filter}*)')

    if results:
        formatted_results = []
        for entry in results:
            if hasattr(entry, 'entry_to_json'):
                entry_json = entry.entry_to_json()
                entry_dict = json.loads(entry_json)

                # Преобразование значений атрибутов в список строк
                if 'attributes' in entry_dict:
                    for key in entry_dict['attributes']:
                        entry_dict['attributes'][key] = [str(s) for s in entry_dict['attributes'][key]]

                formatted_results.append(entry_dict)
            else:
                print(f'Unexpected result type: {type(entry)}')

        return jsonify({'status': 'ok', 'results': formatted_results})
    else:
        return jsonify({'status': 'not_found'}), 404


@app.route('/api/send_mail', methods=['POST'])
def api_send_mail():
    if 'user' not in session or 'password' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    target_user = data.get('target_user')
    password = data.get('password')
    target_email = data.get('target_email')

    sender_email = f"{session['user'].split('\\')[1]}@csat.ru"

    sender_login = session['user']
    sender_password = session['password']
    subject = f'Изменение учетной записи {target_user}'
    body = f'''
    <p><strong>{password}</strong></p>
    <p></p>
    <p>Письмо сгенерировано автоматически</p>
    '''

    success, message = send_email(sender_email, sender_login, sender_password, target_email, subject, body)

    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': message}), 500


@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session or 'password' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        search_filter = request.form.get('search_filter')
        results = search_users(session['user'], session['password'], f'(displayName=*{search_filter}*)')
        return render_template('search.html', results=results)

    return render_template('search.html')


@app.route('/instruments', methods=['GET', 'POST'])
def instruments():
    if 'user' not in session or 'password' not in session:
        return redirect(url_for('index'))

    return render_template('instruments.html')


@app.route('/terminals/<username>')
def terminals_page(username):
    if 'user' not in session or 'password' not in session:
        return redirect('/login')

    return render_template('terminals.html', username=username)


@app.route('/change_pass/<username>')
def change_pass(username):
    if 'user' not in session or 'password' not in session:
        return redirect('/login')

    return render_template('change_password.html', username=username)


@app.route('/logout')
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
@app.route('/vacations', methods=['GET', 'POST'])
def vacations():
    if 'user' not in session or 'password' not in session:
        return redirect(url_for('index'))

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
