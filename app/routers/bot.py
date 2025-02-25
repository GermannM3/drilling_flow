"""
Роутер для Telegram бота
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from ..core.bot import bot, dp
from aiogram.types import Update
from aiogram import Bot, Dispatcher
from ..core.config import get_settings
import json
import asyncio

router = APIRouter(tags=["bot"])
logger = logging.getLogger(__name__)
settings = get_settings()

@router.post("/webhook")
async def webhook(request: Request):
    """
    Обработчик вебхука от Telegram
    """
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {data}")
        
        # Создаем объект Update из данных
        update = Update.model_validate(data)
        
        # Обрабатываем обновление
        await dp.feed_update(bot=bot, update=update)
        
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@router.get("/bot/info")
async def bot_info():
    """
    Получение информации о боте
    """
    try:
        bot_info = await bot.get_me()
        webhook_info = await bot.get_webhook_info()
        
        return {
            "bot": {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name
            },
            "webhook": {
                "url": webhook_info.url,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "pending_update_count": webhook_info.pending_update_count,
                "last_error_date": webhook_info.last_error_date,
                "last_error_message": webhook_info.last_error_message
            }
        }
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start_polling")
async def start_polling():
    """
    Запуск поллинга бота (альтернатива вебхуку)
    """
    try:
        # Сбрасываем вебхук, если он был установлен
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запускаем поллинг в фоновом режиме
        logger.info("Starting bot polling")
        
        # Используем create_task для запуска асинхронной задачи без await
        asyncio.create_task(dp.start_polling(bot))
        
        return {"status": "success", "message": "Bot polling started"}
    except Exception as e:
        logger.error(f"Error starting bot polling: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 