from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import json
import base64
from app.core.logger import logger
from app.core.config import get_settings

settings = get_settings()

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_TOKEN)
        self.dp = Dispatcher()
        self.webapp_url = "https://t.me/Drill_Flow_bot/D_F"
        
        # Регистрируем хендлеры
        self.register_handlers()

    def register_handlers(self):
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.handle_webapp_data, lambda m: m.web_app_data)

    async def start_command(self, message):
        """Отправляет приветственное сообщение с кнопкой для открытия веб-приложения"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Создать заказ",
                web_app=WebAppInfo(url=self.webapp_url)
            )
        ]])
        
        await message.answer(
            "Добро пожаловать! Нажмите кнопку ниже, чтобы создать заказ:",
            reply_markup=keyboard
        )

    async def handle_webapp_data(self, message):
        """Обрабатывает данные, отправленные из веб-приложения"""
        try:
            data = message.web_app_data.data
            await message.answer(f"Получены данные: {data}")
        except Exception as e:
            logger.error(f"Error handling webapp data: {e}")
            await message.answer("Произошла ошибка при обработке данных")

    async def start(self):
        """Запускает бота"""
        try:
            logger.info("Starting bot...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise 