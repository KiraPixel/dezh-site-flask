from flask import Blueprint, request, jsonify, session

from modules import kuber_controller
from active_directory_module.ad_controller import check_on_admin, change_user_password, unlock_user_account, search_users, get_user_info
from app.flask_custom_wraps import validate_sessions
from modules.mail_sender import send_email
from modules.term_controller import check_user_session_on_terminal, logoff_user_from_terminal

api_bp = Blueprint('api', __name__)


# проверка на админку в ад
@api_bp.route('/check_on_admin', methods=['POST'])
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

# проверяем сессии на терминалах
@validate_sessions()
@api_bp.route('/check_user_session', methods=['POST'])
def api_check_user_session():
    data = request.json
    username = data.get('username')
    terminal = data.get('terminal')

    session_id = check_user_session_on_terminal(username, terminal)
    if session_id:
        return jsonify({'status': 'ok', 'session_id': session_id})
    else:
        return jsonify({'status': 'not_found'}), 404

# выкидываем с терминалов
@validate_sessions()
@api_bp.route('/logout_session', methods=['POST'])
def api_logout_session():
    data = request.json
    terminal = data.get('terminal')
    session_id = data.get('session_id')

    status = logoff_user_from_terminal(terminal, session_id)
    if status:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error'}), 404

# меняем пароль пользаку
@validate_sessions()
@api_bp.route('/change_password', methods=['POST'])
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

# функция для активации учеток
@validate_sessions()
@api_bp.route('/unlock_account', methods=['POST'])
def api_unlock_account():

    data = request.json
    target_user = data.get('target_user')
    print(target_user)

    success = unlock_user_account(session['user'], session['password'], f'{target_user}')
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error'}), 500

# метод для поиска пользаков
@validate_sessions()
@api_bp.route('/search_users', methods=['POST'])
def api_search_users():
    data = request.json
    search_filter = data.get('search_filter')
    login = data.get('login')
    if login:
        results = search_users(session['user'], session['password'], f'(sAMAccountName={search_filter})', hard=True)
        if results:
            return jsonify({'status': 'ok'})
    else:
        results = search_users(session['user'], session['password'], f'(displayName=*{search_filter}*)')
        if results:
            formatted_results = []
            for entry in results:
                user_info = get_user_info(entry, session['user'], session['password'])
                formatted_results.append(user_info)
            return jsonify({'status': 'ok', 'results': formatted_results})
    return jsonify({'status': 'not_found'}), 404

# отправка сообщений на почту
@validate_sessions()
@api_bp.route('/send_mail', methods=['POST'])
def api_send_mail():

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

# общаемся с кубером
@validate_sessions()
@api_bp.route('/kuber', methods=['POST'])
def api_kuber():
    if 'user' not in session or 'password' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    username = session['user'].split('\\')[1]
    data = request.get_json()
    if 'command' not in data:
        return jsonify({'error': 'No command provided'}), 400
    command = data['command']
    try:
        result = kuber_controller.run_kubectl_command(username=username, command=command)
        print(result)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
