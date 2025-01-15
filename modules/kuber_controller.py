import requests
import os
import subprocess

# URL для авторизации и скачивания конфигурации
login_url = 'https://prd-k8s-kubectl.msk.csat.ru/login'
final_url = 'https://prd-k8s-kubectl.msk.csat.ru/commandline'
config_url = 'https://prd-k8s-kubectl.msk.csat.ru/kubeconf'


def update_file(username, password):
    session = requests.Session()
    response = session.get(login_url)
    auth_url = response.url
    payload = {
        'login': username,
        'password': password
    }

    response = session.post(auth_url, data=payload)
    final_url_actual = response.url
    if final_url_actual != final_url:
        print(f'KubeConfUPD | {username} Не удалось войти или произошла ошибка редиректа.')
    else:
        config_dir = f'./kubeconf/{username}'
        os.makedirs(config_dir, exist_ok=True)

        config_file_path = os.path.join(config_dir, 'kubeconfig.txt')

        if os.path.exists(config_file_path):
            os.remove(config_file_path)

        config_response = session.get(config_url)

        if config_response.status_code == 200:
            with open(config_file_path, 'wb') as f:
                f.write(config_response.content)
            print(f'KubeConfUPD | Конфигурационный файл {username} успешно скачан: {config_file_path}')
        else:
            print(f'KubeConfUPD | Ошибка при скачивании конфигурационного файла: {username} - {config_response.status_code}')


def run_kubectl_command(username, command):
    try:
        kubeconfig_path = os.path.abspath(f"./kubeconf/{username}/kubeconfig.txt")
        full_command = f"kubectl --kubeconfig={kubeconfig_path} {command}"

        cmd_list = full_command.split()

        result = subprocess.run(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"KubeConfUPD | Произошла ошибка: {result.stderr}")
            return None
    except Exception as e:
        print(f"KubeConfUPD | Произошла ошибка: {e}")
        return None
