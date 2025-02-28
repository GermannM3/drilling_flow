import json
import os
import logging
import asyncio
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.markdown import hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import parse_qs
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Настройка логирования
logger.remove()  # Удаляем все предыдущие обработчики
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if os.getenv("DEBUG") else "INFO",
    colorize=True
)

# Отладочная информация
logger.debug(f"Python version: {sys.version}")
logger.debug(f"Environment variables:")
logger.debug(f"TELEGRAM_TOKEN: {'Set' if os.getenv('TELEGRAM_TOKEN') else 'Not set'}")
logger.debug(f"VERCEL_URL: {os.getenv('VERCEL_URL')}")
logger.debug(f"USE_POLLING: {os.getenv('USE_POLLING')}")
logger.debug(f"BOT_WEBHOOK_DOMAIN: {os.getenv('BOT_WEBHOOK_DOMAIN')}")
logger.debug(f"DEBUG: {os.getenv('DEBUG')}")

# Настройки
class Settings:
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    if not BOT_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set in environment variables")
        raise ValueError("TELEGRAM_TOKEN is not set in environment variables")
    
    # Используем BOT_WEBHOOK_DOMAIN если он установлен, иначе VERCEL_URL
    SITE_URL = os.getenv("BOT_WEBHOOK_DOMAIN") or os.getenv("VERCEL_URL", "localhost:8000")
    
    # Убираем протокол из URL, если он есть
    if SITE_URL.startswith("https://"):
        SITE_URL = SITE_URL[8:]
    elif SITE_URL.startswith("http://"):
        SITE_URL = SITE_URL[7:]
    
    WEBHOOK_PATH = "/webhook"  # Упрощенный путь без токена
    WEBHOOK_URL = f"https://{SITE_URL}{WEBHOOK_PATH}"

try:
    settings = Settings()
    logger.debug(f"Bot settings:")
    logger.debug(f"BOT_TOKEN: {'*' * 5}...{'*' * 5}")
    logger.debug(f"SITE_URL: {settings.SITE_URL}")
    logger.debug(f"WEBHOOK_PATH: {settings.WEBHOOK_PATH}")
    logger.debug(f"WEBHOOK_URL: {settings.WEBHOOK_URL}")
except Exception as e:
    logger.error(f"Error initializing settings: {e}")
    logger.exception(e)
    raise

# Создаем экземпляры бота и диспетчера
try:
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    logger.debug("Bot and dispatcher initialized successfully")
except Exception as e:
    logger.error(f"Error initializing bot: {e}")
    logger.exception(e)
    raise

# Создаем FastAPI приложение
app = FastAPI()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инлайн-клавиатура
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="📦 Заказы", callback_data="orders")
        ],
        [
            InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
        ]
    ])
    return keyboard

# Обработчики команд
@dp.message(CommandStart())
async def start_command(message: Message):
    """Обработчик команды /start"""
    try:
        logger.info(f"Received start command from user {message.from_user.id}")
        await message.answer(
            f"Привет, {hbold(message.from_user.full_name)}!\n"
            f"Добро пожаловать в DrillFlow - платформу для управления буровыми работами.\n\n"
            f"🔹 Заказчики могут размещать заказы\n"
            f"🔹 Подрядчики могут принимать заказы\n"
            f"🔹 Автоматическое распределение заказов\n\n"
            f"Выберите действие в меню ниже:",
            reply_markup=get_main_keyboard()
        )
        logger.info("Welcome message sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")
        logger.exception(e)
        return False

# Обработчики колбэков
@dp.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.message.answer("Ваш профиль...")
    await callback.answer()

@dp.callback_query(F.data == "orders")
async def orders_callback(callback: CallbackQuery):
    await callback.message.answer("Ваши заказы...")
    await callback.answer()

@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    await callback.message.answer("Раздел помощи...")
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    await callback.message.answer("Ваша статистика...")
    await callback.answer()

# Обработчик вебхука
@app.post("/webhook")
async def webhook_handler(request: Request):
    """Обработчик вебхука от Telegram"""
    try:
        logger.info("Received webhook request")
        
        # Получаем данные запроса
        try:
            update_data = await request.json()
            logger.debug(f"Update data: {json.dumps(update_data)[:200]}...")
        except Exception as e:
            logger.error(f"Error parsing request JSON: {e}")
            logger.exception(e)
            return Response(content="Bad Request: Invalid JSON", status_code=400)
        
        # Создаем объект Update из полученных данных
        try:
            telegram_update = Update.model_validate(update_data)
            logger.debug(f"Update validated successfully")
        except Exception as e:
            logger.error(f"Error validating update: {e}")
            logger.exception(e)
            return Response(content=f"Bad Request: Invalid update format - {str(e)}", status_code=400)
        
        # Обрабатываем обновление
        try:
            await dp.feed_update(bot=bot, update=telegram_update)
            logger.debug(f"Update processed successfully")
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            logger.exception(e)
            return Response(content=f"Internal Server Error: {str(e)}", status_code=500)
        
        # Возвращаем успешный ответ
        return Response(content="OK", media_type="text/plain")
    except Exception as e:
        logger.error(f"Unhandled error in webhook handler: {e}")
        logger.exception(e)
        return Response(content=f"Internal Server Error: {str(e)}", status_code=500)

# Обработчик для проверки вебхука
@app.get("/webhook")
async def webhook_get_handler():
    """Обработчик GET-запросов к вебхуку для проверки"""
    try:
        webhook_info = await bot.get_webhook_info()
        return {
            "status": "webhook endpoint is working",
            "webhook_url": settings.WEBHOOK_URL,
            "current_webhook": webhook_info.url,
            "pending_updates": webhook_info.pending_update_count
        }
    except Exception as e:
        logger.error(f"Error in webhook GET handler: {e}")
        logger.exception(e)
        return {"status": "error", "message": str(e)}

# Обработчик проверки работоспособности
@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    try:
        bot_info = await bot.get_me()
        return {
            "status": "ok",
            "bot_info": {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name
            },
            "webhook_url": settings.WEBHOOK_URL
        }
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        logger.exception(e)
        return {"status": "error", "message": str(e)}

# Обработчик корневого пути
@app.get("/")
async def root_handler():
    """Обработчик корневого пути"""
    try:
        return {
            "app": "DrillFlow Bot",
            "version": "1.0.0",
            "status": "running",
            "webhook_url": settings.WEBHOOK_URL,
            "telegram_bot": "@Drill_Flow_bot"
        }
    except Exception as e:
        logger.error(f"Error in root handler: {e}")
        logger.exception(e)
        return {"status": "error", "message": str(e)}

# Обработчик для отладки
@app.get("/debug")
async def debug_handler():
    """Обработчик для отладочной информации"""
    try:
        webhook_info = await bot.get_webhook_info()
        return {
            "python_version": sys.version,
            "environment": {
                "VERCEL_URL": os.getenv("VERCEL_URL"),
                "BOT_WEBHOOK_DOMAIN": os.getenv("BOT_WEBHOOK_DOMAIN"),
                "USE_POLLING": os.getenv("USE_POLLING"),
                "DEBUG": os.getenv("DEBUG")
            },
            "bot_settings": {
                "site_url": settings.SITE_URL,
                "webhook_path": settings.WEBHOOK_PATH,
                "webhook_url": settings.WEBHOOK_URL
            },
            "webhook_info": {
                "url": webhook_info.url,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "pending_update_count": webhook_info.pending_update_count,
                "ip_address": webhook_info.ip_address,
                "last_error_message": webhook_info.last_error_message,
                "last_error_date": webhook_info.last_error_date.isoformat() if webhook_info.last_error_date else None,
                "last_synchronization_error_date": webhook_info.last_synchronization_error_date.isoformat() if webhook_info.last_synchronization_error_date else None
            }
        }
    except Exception as e:
        logger.error(f"Error in debug handler: {e}")
        logger.exception(e)
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

# События приложения
@app.on_event("startup")
async def on_startup():
    """Действия при запуске приложения"""
    logger.info("Starting up the application...")
    
    # Проверяем режим работы
    if os.getenv("USE_POLLING", "False").lower() == "true":
        logger.info("Using polling mode")
        return
    
    # Настраиваем вебхук
    try:
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Current webhook: {webhook_info.url}")
        
        if webhook_info.url != settings.WEBHOOK_URL:
            # Удаляем старый вебхук
            await bot.delete_webhook()
            logger.info("Old webhook deleted")
            
            # Устанавливаем новый вебхук
            await bot.set_webhook(
                url=settings.WEBHOOK_URL,
                allowed_updates=["message", "callback_query"]
            )
            logger.info(f"Webhook set to {settings.WEBHOOK_URL}")
            
            # Проверяем, что вебхук установлен
            webhook_info = await bot.get_webhook_info()
            logger.info(f"Webhook verification: {webhook_info.url}")
        else:
            logger.info("Webhook is already set correctly")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        logger.exception(e)

@app.on_event("shutdown")
async def on_shutdown():
    """Действия при остановке приложения"""
    logger.info("Shutting down the application...")
    try:
        await bot.delete_webhook()
        logger.info("Webhook removed")
    except Exception as e:
        logger.error(f"Failed to remove webhook: {e}")
        logger.exception(e)

# Обработчик для Vercel Serverless Functions
def handler(request, context):
    """Обработчик для Vercel Serverless Functions"""
    return app 