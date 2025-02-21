import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logging.error("TELEGRAM_TOKEN не установлен")
    exit(1)

# Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.reply("Добро пожаловать в DrillFlow!")

# Обработчик команды /help
@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.reply("Доступные команды: /start, /help, /order, /support и т.д.")

# Пример эхо-обработчика для незнакомых команд или сообщений
@dp.message()
async def echo_handler(message: Message):
    await message.reply("Я не понимаю данную команду. Используйте /help для получения списка команд.")

async def main():
    logging.info("Запуск бота...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main()) 