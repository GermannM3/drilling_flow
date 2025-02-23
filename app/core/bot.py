from aiogram import Bot, Dispatcher
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
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

@dp.message_handler(lambda message: message.text == "📊 Статистика")
async def statistics(message):
    stats_text = """
📊 *Статистика DrillFlow*
• Активных подрядчиков: 247
• Выполненных заказов: 1,893
• Ожидающих заказов: 42
• Средний рейтинг: 4.8⭐️
    """
    await message.answer(stats_text, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "📝 Новый заказ")
async def new_order(message):
    order_keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Создать заказ", web_app=WebAppInfo(url="https://drilling-flow.vercel.app/new-order"))
    )
    await message.answer("Создайте новый заказ через веб-интерфейс:", reply_markup=order_keyboard)

@dp.message_handler(lambda message: message.text == "👥 Подрядчики")
async def contractors(message):
    await message.answer("Список доступных подрядчиков:\n\n" + 
                        "1. ООО 'БурСтрой' - ⭐️4.9\n" +
                        "2. ИП Иванов - ⭐️4.8\n" +
                        "3. АО 'ГеоДрилл' - ⭐️4.7")

@dp.message_handler(lambda message: message.text == "⭐️ Рейтинг")
async def rating(message):
    await message.answer("Ваш текущий рейтинг: ⭐️4.8\n\n" +
                        "Выполнено заказов: 12\n" +
                        "Положительных отзывов: 11\n" +
                        "Статус: Надёжный партнёр 🏆")

@dp.message_handler()
async def handle_message(message):
    if message.web_app_data:
        await message.answer(f"Получены данные: {message.web_app_data.data}")
    else:
        await message.answer("Пожалуйста, используйте кнопки меню для навигации.") 