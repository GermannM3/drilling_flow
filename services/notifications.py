import logging

logger = logging.getLogger(__name__)

def send_notification(user_contact, message, method='telegram'):
    """
    Отправка уведомления:
    - user_contact: контакт пользователя (telegram_id, телефон и т.д.)
    - message: текст уведомления
    - method: способ доставки ('telegram', 'sms')
    """
    logger.info(f"Уведомление через {method} для {user_contact}: {message}")
    # Реализуйте интеграцию с SMS API или Telegram API для отправки уведомлений
    return True 