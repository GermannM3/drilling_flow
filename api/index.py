import json
import os
import logging
import asyncio
import sys
from http.server import BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.markdown import hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import parse_qs
from fastapi import FastAPI, Request, Response
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
logger.debug(f"Environment variables:")
logger.debug(f"TELEGRAM_TOKEN: {os.getenv('TELEGRAM_TOKEN')}")
logger.debug(f"VERCEL_URL: {os.getenv('VERCEL_URL')}")
logger.debug(f"USE_POLLING: {os.getenv('USE_POLLING')}")
logger.debug(f"BOT_WEBHOOK_DOMAIN: {os.getenv('BOT_WEBHOOK_DOMAIN')}")

# Настройки
class Settings:
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    if not BOT_TOKEN:
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

settings = Settings()
logger.debug(f"Bot settings:")
logger.debug(f"BOT_TOKEN: {settings.BOT_TOKEN[:5]}...{settings.BOT_TOKEN[-5:] if len(settings.BOT_TOKEN) > 10 else ''}")
logger.debug(f"SITE_URL: {settings.SITE_URL}")
logger.debug(f"WEBHOOK_PATH: {settings.WEBHOOK_PATH}")
logger.debug(f"WEBHOOK_URL: {settings.WEBHOOK_URL}")

# Создаем экземпляры бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Создаем FastAPI приложение
app = FastAPI()

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
        update_data = await request.json()
        logger.debug(f"Update data: {json.dumps(update_data)[:200]}...")
        
        # Создаем объект Update из полученных данных
        telegram_update = Update.model_validate(update_data)
        
        # Обрабатываем обновление
        await dp.feed_update(bot=bot, update=telegram_update)
        
        # Возвращаем успешный ответ
        return Response(content="OK", media_type="text/plain")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        logger.exception(e)
        return {"ok": False, "error": str(e)}

# Обработчик для проверки вебхука
@app.get("/webhook")
async def webhook_get_handler():
    """Обработчик GET-запросов к вебхуку для проверки"""
    return {"status": "webhook endpoint is working", "webhook_url": settings.WEBHOOK_URL}

# Обработчик проверки работоспособности
@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "bot_info": await bot.get_me()}

# Обработчик корневого пути
@app.get("/")
async def root_handler():
    """Обработчик корневого пути"""
    return {
        "app": "DrillFlow Bot",
        "version": "1.0.0",
        "status": "running",
        "webhook_url": settings.WEBHOOK_URL,
        "telegram_bot": "@Drill_Flow_bot"
    }

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