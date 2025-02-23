"""
Инициализация Telegram бота
"""
from aiogram import Bot, Dispatcher
from app.core.config import get_settings

settings = get_settings()

# Создаем бота только если не в режиме тестирования
if not settings.TESTING:
    bot = Bot(token=settings.TELEGRAM_TOKEN)
    dp = Dispatcher()
else:
    # В тестах используем моки
    bot = None
    dp = None 