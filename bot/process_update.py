import os
import sys
import json
import logging
import traceback
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv
import asyncio

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_webhook.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
UPDATE_FILE = os.getenv('UPDATE_FILE')

# Проверка наличия токена и файла обновления
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    sys.exit(1)

if not UPDATE_FILE or not os.path.exists(UPDATE_FILE):
    logger.error("Файл с данными обновления не найден!")
    sys.exit(1)

try:
    # Чтение данных обновления из файла
    with open(UPDATE_FILE, 'r', encoding='utf-8') as file:
        update_data = json.load(file)
    logger.info(f"Получены данные обновления из {UPDATE_FILE}")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())

    # Импортируем обработчики из основного файла бота
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from bot.bot import register_handlers

    # Регистрируем все обработчики
    register_handlers(dp)

    # Функция для обработки обновления
    async def process_update():
        try:
            # Создаем объект обновления из данных
            update = types.Update(**update_data)
            logger.info(f"Обрабатываем обновление: {update.update_id}")
            
            # Обрабатываем обновление через диспетчер
            results = await dp.process_update(update)
            logger.info(f"Обновление {update.update_id} обработано: {results}")
            
            # Удаляем временный файл обновления
            if os.path.exists(UPDATE_FILE):
                os.remove(UPDATE_FILE)
                logger.info(f"Временный файл {UPDATE_FILE} удален")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке обновления: {e}")
            logger.error(traceback.format_exc())

    # Запускаем обработку обновления
    if __name__ == '__main__':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(process_update())
        except Exception as e:
            logger.error(f"Критическая ошибка в цикле событий: {e}")
            logger.error(traceback.format_exc())
        finally:
            loop.close()
            logger.info("Обработчик обновления завершил работу")

except Exception as e:
    logger.critical(f"Критическая ошибка при обработке вебхука: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1) 