import os
import sys
import json
import logging
import traceback
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Импортируем функции из основного файла бота
from bot import (
    register_handlers, 
    init_db, 
    logger
)

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Получаем токен из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
UPDATE_FILE = os.getenv('UPDATE_FILE')

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    sys.exit(1)

if not UPDATE_FILE:
    logger.error("UPDATE_FILE не найден в переменных окружения!")
    sys.exit(1)

try:
    # Инициализация базы данных
    db_conn = init_db()

    # Инициализация бота и диспетчера
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())

    # Регистрируем все обработчики
    register_handlers(dp)

    # Читаем данные обновления из файла
    try:
        with open(UPDATE_FILE, 'r', encoding='utf-8') as f:
            update_data = json.load(f)
            logger.info(f"Получены данные обновления: {json.dumps(update_data)[:100]}...")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла обновления: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

    # Создаем объект Update из данных
    update = types.Update(**update_data)
    
    # Обрабатываем обновление
    async def process():
        try:
            logger.info(f"Обработка обновления ID: {update.update_id}")
            await dp.process_update(update)
            logger.info(f"Обновление ID: {update.update_id} успешно обработано")
        except Exception as e:
            logger.error(f"Ошибка при обработке обновления: {e}")
            logger.error(traceback.format_exc())

    # Запускаем обработку
    import asyncio
    asyncio.run(process())

    # Удаляем файл обновления после обработки
    try:
        os.remove(UPDATE_FILE)
        logger.info(f"Файл обновления {UPDATE_FILE} удален")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла обновления: {e}")

except Exception as e:
    logger.critical(f"Критическая ошибка при обработке обновления: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1) 