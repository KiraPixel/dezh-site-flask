import subprocess


def check_user_session_on_terminal(username, terminal):
    command = f'quser | findstr /I {username}'
    process = subprocess.Popen(['powershell', '-Command', f"Invoke-Command -ComputerName {terminal} -ScriptBlock {{{command}}} 2>&1"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stdout:
        try:
            session_info = stdout.decode('cp866').strip()
            session_id = session_info.split()[2]  # Предполагается, что идентификатор сессии находится на 3 позиции
            print(f"Найдена сессия пользователя {username} на терминале {terminal} с ID {session_id}")
            return session_id
        except Exception as e:
            print(f"Ошибка при обработке сессии: {e}")
            print(f"Полученный вывод: {session_info}")
            return False
    else:
        print(f"Пользователь {username} не найден на терминале {terminal}.")
        return False


def logoff_user_from_terminal(terminal, session_id):
    bat_content = f"""
@echo off
logoff {session_id} /server:{terminal}
"""
    # Создаем временный .bat файл
    bat_file = 'logoff_user.bat'
    with open(bat_file, 'w') as file:
        file.write(bat_content)

    # Запускаем .bat файл
    result = subprocess.call([bat_file])
    if result == 0:
        print(f"Пользователь был успешно разлогинен с терминала {terminal}.")
        # Удаляем временный .bat файл
        subprocess.call(['del', bat_file], shell=True)
        return True
    else:
        print(f"Ошибка при разлогине пользователя с терминала {terminal}.")
        # Удаляем временный .bat файл
        subprocess.call(['del', bat_file], shell=True)
        return False

