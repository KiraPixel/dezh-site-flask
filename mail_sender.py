from exchangelib import Credentials, Account, Message, DELEGATE, HTMLBody


def send_email(sender_email, sender_login, sender_password, target_email, subject, body):
    try:
        # Создаем учетные данные
        credentials = Credentials(username=sender_login, password=sender_password)

        # Подключаемся к учетной записи
        account = Account(sender_email, credentials=credentials, autodiscover=True, access_type=DELEGATE)

        # Создаем сообщение
        msg = Message(
            account=account,
            folder=account.sent,
            subject=subject,
            body=HTMLBody(body),
            to_recipients=[target_email]
        )

        # Отправляем сообщение
        msg.send()
        return True, "Email отправлен успешно!"
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        return False, str(e)



