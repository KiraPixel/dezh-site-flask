# ad_controller.py
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE

from .ad_locations_parsers import get_user_location

# Параметры подключения к AD
server_address = 'msk.csat.ru'
search_base = 'dc=msk,dc=csat,dc=ru'


def search_users(ad_user, ad_password, search_filter, hard=False):
    conn = None
    try:
        server = Server(server_address, get_info=ALL)
        conn = Connection(server, user=ad_user, password=ad_password, auto_bind=True)
        conn.search(
            search_base,
            search_filter,
            search_scope=SUBTREE,
            attributes=[
                'cn', 'displayName', 'mail', 'title', 'department', 'manager',
                'telephoneNumber', 'mobile', 'homePhone', 'distinguishedName', 'userAccountControl'
            ],
            size_limit=50
        )
        if not conn.entries:
            return []
        if hard:
            return conn.entries[0]
        return conn.entries
    except Exception as e:
        print(f'Error: {e}')
        return []
    finally:
        if conn:
            conn.unbind()


def is_member_of_group(user_dn, group_name, ad_user, ad_password):
    try:
        server = Server(server_address, get_info=ALL)
        conn = Connection(server, user=ad_user, password=ad_password, auto_bind=True)
        search_filter = f'(&(objectClass=group)(cn={group_name})(member={user_dn}))'
        conn.search(search_base, search_filter, search_scope=SUBTREE, attributes=['cn'])
        if conn.entries:
            return True
        else:
            return False
    except Exception as e:
        return False
    finally:
        if conn:
            conn.unbind()


def check_on_admin(ad_user, ad_password):
    ad_user_split = ad_user.split('\\')
    if len(ad_user_split) != 2:
        return False
    domain, username = ad_user_split
    result = search_users(ad_user, ad_password, f'(sAMAccountName={username})', hard=True)
    try:
        if result:
            user_dn = result.entry_dn
            if is_member_of_group(user_dn, 'HelpDeskIT_Groups', ad_user, ad_password):
                return True
            else:
                return False
        return False
    except Exception as e:
        return False


def change_user_password(admin_user, admin_password, target_user, new_password):
    conn = None
    try:
        # Используем LDAPS (порт 636) для безопасного подключения
        server = Server(server_address, use_ssl=True, get_info=ALL)
        conn = Connection(server, user=admin_user, password=admin_password, auto_bind=True)

        # Поиск целевого пользователя
        search_filter = f'(sAMAccountName={target_user})'
        conn.search(search_base, search_filter, search_scope=SUBTREE, attributes=['distinguishedName'])

        if not conn.entries:
            print(f'User {target_user} not found.')
            return False

        user_dn = conn.entries[0].entry_dn

        # Новый пароль должен быть в формате unicode и заключен в двойные кавычки
        new_password = f'"{new_password}"'.encode('utf-16-le')

        # Изменение пароля пользователя
        changes = {'unicodePwd': [(MODIFY_REPLACE, [new_password])]}
        success = conn.modify(user_dn, changes)

        if success:
            print(f'Password for {target_user} changed successfully.')
            return True
        else:
            # Если произошла ошибка, выведем сообщения об ошибках
            print(f'Failed to change password for {target_user}.')
            print(conn.result)  # Выведем детальную информацию о результате операции
            return False

    except Exception as e:
        print(f'Error: {e}')
        return False
    finally:
        if conn:
            conn.unbind()


def unlock_user_account(admin_user, admin_password, target_user):
    conn = None
    try:
        # Используем LDAPS (порт 636) для безопасного подключения
        server = Server(server_address, use_ssl=True, get_info=ALL)
        conn = Connection(server, user=admin_user, password=admin_password, auto_bind=True)
        # Поиск целевого пользователя
        search_filter = f'(sAMAccountName={target_user})'
        conn.search(search_base, search_filter, search_scope=SUBTREE, attributes=['distinguishedName', 'lockoutTime'])

        if not conn.entries:
            print(f'User {target_user} not found.')
            return False

        user_dn = conn.entries[0].entry_dn

        # Разблокировка учетной записи (сброс lockoutTime)
        changes = {'lockoutTime': [(MODIFY_REPLACE, ['0'])]}
        success = conn.modify(user_dn, changes)

        if success:
            print(f'Account for {target_user} has been unlocked successfully.')
            return True
        else:
            print(f'Failed to unlock account for {target_user}.')
            print(conn.result)
            return False

    except Exception as e:
        print(f'Error: {e}')
        return False
    finally:
        if conn:
            conn.unbind()

def get_user_info(user, ad_login, ad_password):
    # Получаем информацию о руководителе
    manager = ''
    try:
        if user.manager:
            manager_entry = search_users(ad_login, ad_password, f'(distinguishedName={user.manager})', hard=True)
            if manager_entry:
                manager = manager_entry.displayName.value if hasattr(manager_entry.displayName, 'value') else None
    except:
        pass

    # Определяем локацию пользователя
    if user.mail and hasattr(user.mail, 'value') and user.mail.value and user.mail.value.endswith('@icf.ru'):
        location = "Аутсорс 1C"
    else:
        location = get_user_location(user.distinguishedName.value)

    # Собираем информацию о телефонах
    phones = []
    if hasattr(user, 'telephoneNumber') and user.telephoneNumber:
        phones.append(f"Рабочий: {user.telephoneNumber.value}")
    if hasattr(user, 'mobile') and user.mobile:
        phones.append(f"Мобильный: {user.mobile.value}")
    if hasattr(user, 'homePhone') and user.homePhone:
        phones.append(f"Домашний: {user.homePhone.value}")
    phone_info = ", ".join(phones) if phones else None

    # Определяем статус учетной записи (активна/неактивна)
    if hasattr(user, 'userAccountControl'):
        user_account_control = int(user.userAccountControl.value) if hasattr(user.userAccountControl, 'value') else 0
        is_active = not (user_account_control & 2)  # Проверяем флаг ACCOUNTDISABLE (2)
    else:
        is_active = None  # Если атрибут отсутствует, статус неизвестен

    login = user.mail.value if hasattr(user.mail, 'value') else None
    login = login.split('@')[0] if login else None
    print(user)
    # Формируем информацию о пользователе
    return {
        "Логин": login,
        "ФИО": user.displayName.value if hasattr(user.displayName, 'value') else None,
        "Почта": user.mail.value if hasattr(user.mail, 'value') else None,
        "Должность": user.title.value if hasattr(user.title, 'value') else None,
        "Отдел": user.department.value if hasattr(user.department, 'value') else None,
        "Руководитель": manager,
        "Телефоны": phone_info,
        "Локация": location,
        "АктивнаУЗ": is_active
    }


