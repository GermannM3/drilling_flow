from aiogram import Bot, Dispatcher, Router
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from ..core.config import get_settings

settings = get_settings()
bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()

# Регистрируем бота в диспетчере
dp.bot = bot

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

@router.message(Command("start"))
async def start_command(message):
    await message.answer(
        "Добро пожаловать в DrillFlow!\n\n" +
        "Используйте кнопки меню для навигации:",
        reply_markup=webapp_keyboard
    )

@router.message(lambda m: m.text == "📊 Статистика")
async def statistics(message):
    await message.answer(
        "Статистика за последний месяц:\n\n" +
        "Новых заказов: 156\n" +
        "Выполнено заказов: 142\n" +
        "Активных подрядчиков: 48"
    )

@router.message(lambda m: m.text == "📝 Новый заказ")
async def new_order(message):
    await message.answer(
        "Создайте новый заказ через веб-интерфейс:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                "Открыть веб-приложение",
                web_app=WebAppInfo(url="https://drilling-flow.vercel.app")
            )
        )
    )

@router.message(lambda m: m.text == "👥 Подрядчики")
async def contractors(message):
    await message.answer(
        "Список доступных подрядчиков:\n\n" + 
        "1. ООО 'БурСтрой' - ⭐️4.9\n" +
        "2. ИП Иванов - ⭐️4.8\n" +
        "3. АО 'ГеоДрилл' - ⭐️4.7"
    )

@router.message(lambda m: m.text == "⭐️ Рейтинг")
async def rating(message):
    await message.answer(
        "Ваш текущий рейтинг: ⭐️4.8\n\n" +
        "Выполнено заказов: 12\n" +
        "Положительных отзывов: 11\n" +
        "Статус: Надёжный партнёр 🏆"
    )

@router.message()
async def handle_message(message):
    if message.web_app_data:
        await message.answer(f"Получены данные: {message.web_app_data.data}")
    else:
        await message.answer("Пожалуйста, используйте кнопки меню для навигации.")

# Регистрируем роутер в диспетчере
dp.include_router(router) 