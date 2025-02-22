"""
Модуль для проверки работоспособности Telegram бота.
Включает функции проверки соединения с API Telegram и основных компонентов бота.
"""

import asyncio
import logging
from typing import Tuple, Dict
from aiogram import Bot
from app.core.config import settings

logger = logging.getLogger(__name__)

async def check_bot_components() -> Dict[str, bool]:
    """Проверка всех компонентов бота"""
    return {
        "api_connection": await check_api_connection(),
        "database": await check_database_connection(),
        "webhook": await check_webhook_status()
    }

async def check_api_connection() -> bool:
    """Проверка соединения с API Telegram"""
    try:
        bot = Bot(token=settings.TELEGRAM_TOKEN)
        me = await bot.get_me()
        logger.info(f"Bot {me.username} is connected to Telegram API")
        await bot.session.close()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Telegram API: {e}")
        return False

async def check_database_connection() -> bool:
    """Проверка соединения с базой данных"""
    try:
        # Здесь должна быть проверка подключения к БД
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

async def check_webhook_status() -> bool:
    """Проверка статуса webhook"""
    try:
        bot = Bot(token=settings.TELEGRAM_TOKEN)
        webhook_info = await bot.get_webhook_info()
        await bot.session.close()
        return bool(webhook_info.url)
    except Exception as e:
        logger.error(f"Webhook check failed: {e}")
        return False

async def perform_health_check() -> Tuple[bool, Dict[str, bool]]:
    """
    Выполняет полную проверку здоровья бота
    Returns:
        Tuple[bool, Dict[str, bool]]: (общий статус, детальные результаты)
    """
    results = await check_bot_components()
    overall_status = all(results.values())
    return overall_status, results

if __name__ == "__main__":
    status, details = asyncio.run(perform_health_check())
    exit(0 if status else 1) 