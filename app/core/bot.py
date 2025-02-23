from aiogram import Bot, Dispatcher
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from ..core.config import get_settings

settings = get_settings()
bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Создаем клавиатуру с веб-приложением
webapp_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text="🌐 Открыть DrillFlow",
            web_app=WebAppInfo(url="https://drilling-flow.vercel.app")
        )],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📝 Новый заказ")],
        [KeyboardButton(text="👥 Подрядчики"), KeyboardButton(text="⭐️ Рейтинг")]
    ],
    resize_keyboard=True
)

@dp.message_handler(commands=['start'])
async def start_command(message):
    await message.answer(
        "Добро пожаловать в DrillFlow! Выберите действие или откройте веб-приложение:",
        reply_markup=webapp_keyboard
    )

@dp.message_handler()
async def handle_message(message):
    if message.web_app_data:
        # Обработка данных из веб-приложения
        await message.answer(f"Получены данные: {message.web_app_data.data}")
    else:
        await message.answer(f"Получена команда: {message.text}") 