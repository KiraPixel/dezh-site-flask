# ad_controller.py
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE

# Параметры подключения к AD
server_address = 'msk.csat.ru'
search_base = 'dc=msk,dc=csat,dc=ru'


def search_users(ad_user, ad_password, search_filter, hard=False):
    conn = None
    try:
        server = Server(server_address, get_info=ALL)
        conn = Connection(server, user=ad_user, password=ad_password, auto_bind=True)
        conn.search(search_base, search_filter, search_scope=SUBTREE, attributes=['cn', 'displayName', 'mail'])
        if not conn.search:
            return False
        if hard:
            return conn.entries[0]
        return conn.entries
    except Exception as e:
        print(f'Error: {e}')
        return []
    finally:
        if conn:
            conn.unbind()


def check_on_admin(ad_user, ad_password):
    ad_user_split = ad_user.split('\\')
    result = search_users(ad_user, ad_password, f'(sAMAccountName={ad_user_split[1]})', hard=True)
    try:
        print(result.entry_dn)
        if result and 'IT_Support' in result.entry_dn:
            return True
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