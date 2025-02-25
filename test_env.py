import os
import sys
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Получаем и выводим переменные окружения
print(f"TELEGRAM_TOKEN: {os.getenv('TELEGRAM_TOKEN')}")
print(f"USE_POLLING: {os.getenv('USE_POLLING')}")
print(f"DISABLE_BOT: {os.getenv('DISABLE_BOT')}") 