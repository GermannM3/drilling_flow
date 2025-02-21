import requests
from django.conf import settings

def send_telegram_notification(chat_id, message):
    """
    Отправляет уведомление в Telegram.
    Для работы требуется правильно заданный TELEGRAM_TOKEN в settings или .env.
    """
    telegram_token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки Telegram-уведомления: {e}")
        return None

def send_sms(phone_number, message):
    """
    Заглушка для отправки SMS. Здесь можно интегрировать API реального SMS-провайдера.
    """
    # Пример: логирование уведомления в консоль
    print(f"Отправка SMS на {phone_number}: {message}")
    return True 