import requests
import os
import argparse

# Получаем токен из переменной окружения или используем захардкоженный токен как запасной вариант
TOKEN = os.environ.get("BOT_TOKEN", "7554540052:AAEvde_xL9d85kbJBdxPu8B6Mo4UEMF-qBs")
WEBHOOK_URL = "https://drilling-flow.vercel.app/api/telegram_bot_webhook"

def set_webhook(info_only=False):
    # Сначала удаляем текущий вебхук
    delete_url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    delete_response = requests.get(delete_url)
    print("Удаление текущего вебхука:", delete_response.json())
    
    if not info_only:
        # Устанавливаем новый вебхук
        url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        response = requests.get(url, params={"url": WEBHOOK_URL, "allowed_updates": ["message", "callback_query"]})
        print("Установка нового вебхука:", response.json())
    
    # Получаем информацию о вебхуке
    info_url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
    info_response = requests.get(info_url)
    print("Информация о вебхуке:", info_response.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Установка вебхука для Telegram бота')
    parser.add_argument('--info', action='store_true', help='Только получить информацию о вебхуке')
    args = parser.parse_args()
    
    set_webhook(info_only=args.info) 