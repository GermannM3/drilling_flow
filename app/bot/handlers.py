"""
Обработчики команд бота
"""
from aiogram import types
from .bot import TelegramBot
from app.db.models import Order

async def create_order(message: types.Message) -> dict:
    """
    Создает новый заказ
    """
    try:
        # Здесь будет логика создания заказа
        return {"id": 1, "status": "created"}
    except Exception as e:
        return {"error": str(e)} 