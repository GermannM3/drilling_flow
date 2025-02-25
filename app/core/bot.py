"""
Инициализация Telegram бота
"""
from aiogram import Bot, Dispatcher, Router
from aiogram.types import (
    WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, 
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message, BotCommand
)
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from ..core.config import get_settings
import asyncio
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()

# Создаем бота только если не в режиме тестирования
if not settings.TESTING:
    bot = Bot(
        token=settings.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
else:
    from unittest.mock import AsyncMock, MagicMock
    # В тестах используем моки
    bot = MagicMock()
    bot.send_message = AsyncMock()
    dp = MagicMock()

# Регистрируем бота в диспетчере
dp.bot = bot

async def setup_bot_commands():
    """Установка команд бота"""
    try:
        commands = [
            BotCommand(command="start", description="Начать работу"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="orders", description="Мои заказы"),
            BotCommand(command="profile", description="Мой профиль")
        ]
        await bot.set_my_commands(commands)
        logger.info("Bot commands set up successfully")
        
        # Настраиваем вебхук, если указан домен
        if settings.TELEGRAM_BOT_DOMAIN:
            webhook_url = f"https://{settings.TELEGRAM_BOT_DOMAIN}/api/webhook"
            try:
                await bot.set_webhook(webhook_url)
                logger.info(f"Webhook set to {webhook_url}")
            except Exception as e:
                logger.error(f"Error setting webhook: {e}")
    except Exception as e:
        logger.error(f"Error setting up bot commands: {e}")

# Создаем клавиатуру с веб-приложением
webapp_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text="🌐 Открыть DrillFlow",
            web_app=WebAppInfo(url=f"https://{settings.TELEGRAM_BOT_DOMAIN}")
        )],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📝 Новый заказ")],
        [KeyboardButton(text="👥 Подрядчики"), KeyboardButton(text="⭐️ Рейтинг")]
    ],
    resize_keyboard=True,
    is_persistent=True
)

@router.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start"""
    try:
        await message.answer(
            "Добро пожаловать в DrillFlow! 🚀\n\n"
            "Я помогу вам управлять буровыми работами.\n"
            "Используйте кнопки ниже для навигации:",
            reply_markup=webapp_keyboard
        )
        logger.info(f"Start command processed for user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error processing start command: {e}")

@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🔍 Доступные команды:\n\n"
        "/start - Запустить бота\n"
        "/register - Регистрация\n"
        "/profile - Мой профиль\n"
        "/orders - Мои заказы\n"
        "/new_order - Создать заказ\n"
        "/help - Это сообщение\n\n"
        "Также вы можете использовать кнопки меню для навигации."
    )
    await message.answer(help_text, reply_markup=webapp_keyboard)

@router.message(Command("register"))
async def register_command(message: Message):
    """Обработчик команды /register"""
    register_button = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Зарегистрироваться",
            web_app=WebAppInfo(url=f"https://{settings.TELEGRAM_BOT_DOMAIN}/register")
        )
    ]])
    await message.answer(
        "Для регистрации нажмите кнопку ниже:",
        reply_markup=register_button
    )

@router.message(lambda m: m.text == "📊 Статистика")
async def statistics(message):
    await message.answer(
        "Статистика за последний месяц:\n\n" +
        "Новых заказов: 156\n" +
        "Выполнено заказов: 142\n" +
        "Активных подрядчиков: 48",
        reply_markup=webapp_keyboard
    )

@router.message(lambda m: m.text == "📝 Новый заказ")
async def new_order(message):
    await message.answer(
        "Создайте новый заказ через веб-интерфейс:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Открыть веб-приложение",
                web_app=WebAppInfo(url=f"https://{settings.TELEGRAM_BOT_DOMAIN}")
            )
        ]])
    )

@router.message(lambda m: m.text == "👥 Подрядчики")
async def contractors(message):
    await message.answer(
        "Список доступных подрядчиков:\n\n" + 
        "1. ООО 'БурСтрой' - ⭐️4.9\n" +
        "2. ИП Иванов - ⭐️4.8\n" +
        "3. АО 'ГеоДрилл' - ⭐️4.7",
        reply_markup=webapp_keyboard
    )

@router.message(lambda m: m.text == "⭐️ Рейтинг")
async def rating(message):
    await message.answer(
        "Ваш текущий рейтинг: ⭐️4.8\n\n" +
        "Выполнено заказов: 12\n" +
        "Положительных отзывов: 11\n" +
        "Статус: Надёжный партнёр 🏆",
        reply_markup=webapp_keyboard
    )

@router.message()
async def handle_message(message):
    if message.web_app_data:
        await message.answer(f"Получены данные: {message.web_app_data.data}")
    else:
        await message.answer(
            "Пожалуйста, используйте кнопки меню для навигации.",
            reply_markup=webapp_keyboard
        )

# Регистрируем роутер в диспетчере
dp.include_router(router)

# Экспортируем для использования в других модулях
__all__ = ["bot", "dp", "router"]

# Команды бота будут установлены при запуске приложения

async def setup_webhook():
    """Настройка вебхука"""
    if settings.BOT_WEBHOOK_URL:
        await bot.set_webhook(settings.BOT_WEBHOOK_URL)
        print(f"Webhook set to {settings.BOT_WEBHOOK_URL}") 