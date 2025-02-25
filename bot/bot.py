import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Получаем токен бота
def get_token():
    token = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Если токен не найден в переменных окружения, используем захардкоженный токен
    if not token:
        token = "7554540052:AAEvde_xL9d85kbJBdxPu8B6Mo4UEMF-qBs"
        logger.warning("Using hardcoded token! This is not secure for production.")
    
    if not token:
        logger.error("No Telegram token found. Please set TELEGRAM_TOKEN environment variable.")
        return None
        
    logger.info(f"Using token: {token[:5]}...{token[-5:]}")
    return token

# Создаем экземпляр бота и диспетчера
try:
    token = get_token()
    if not token:
        raise ValueError("No valid token found")
    
    bot = Bot(token=token)
    dp = Dispatcher()
    logger.info("Bot and dispatcher initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}", exc_info=True)
    raise

# Создаем основную клавиатуру
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Создать заказ"), KeyboardButton(text="📋 Мои заказы")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="⭐ Рейтинг")],
            [KeyboardButton(text="📞 Поддержка"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

# Создаем инлайн-клавиатуру для заказа
def get_order_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Бурение скважины", callback_data="order_drilling")],
            [InlineKeyboardButton(text="Ремонт скважины", callback_data="order_repair")],
            [InlineKeyboardButton(text="Обслуживание", callback_data="order_maintenance")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
    )
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"Start command from user {message.from_user.id}")
    try:
        await message.answer(
            'Привет! Я бот DrillFlow. Выберите действие на клавиатуре:',
            reply_markup=get_main_keyboard()
        )
        logger.info("Successfully sent start message")
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /help - Показать справку
    /profile - Ваш профиль
    /order - Создать заказ
    /status - Статус заказов
    """
    await message.answer(help_text, reply_markup=get_main_keyboard())

# Обработчик команды /order
@dp.message(Command("order"))
async def cmd_order(message: Message):
    await message.answer(
        "Выберите тип услуги:",
        reply_markup=get_order_keyboard()
    )

# Обработчик нажатий на инлайн-кнопки
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    
    if callback_data == "order_drilling":
        await callback_query.message.answer("Вы выбрали бурение скважины. Укажите адрес:")
    elif callback_data == "order_repair":
        await callback_query.message.answer("Вы выбрали ремонт скважины. Укажите адрес:")
    elif callback_data == "order_maintenance":
        await callback_query.message.answer("Вы выбрали обслуживание скважины. Укажите адрес:")
    elif callback_data == "cancel":
        await callback_query.message.answer("Действие отменено", reply_markup=get_main_keyboard())
    
    # Обязательно отвечаем на callback_query
    await callback_query.answer()

# Обработчик текстовых сообщений (для кнопок основной клавиатуры)
@dp.message()
async def handle_text(message: types.Message):
    text = message.text
    
    if text == "🔍 Создать заказ":
        await message.answer("Выберите тип услуги:", reply_markup=get_order_keyboard())
    elif text == "📋 Мои заказы":
        await message.answer("Ваши заказы:\n\nУ вас пока нет активных заказов.")
    elif text == "👤 Профиль":
        user_info = f"""
        Профиль пользователя:
        ID: {message.from_user.id}
        Имя: {message.from_user.first_name} {message.from_user.last_name or ''}
        Username: @{message.from_user.username or 'отсутствует'}
        """
        await message.answer(user_info)
    elif text == "⭐ Рейтинг":
        await message.answer("Топ подрядчиков по рейтингу:\n\n1. ООО 'БурСервис' - 4.9⭐\n2. ИП Иванов - 4.8⭐\n3. ООО 'АкваДрилл' - 4.7⭐")
    elif text == "📞 Поддержка":
        await message.answer("Для связи с поддержкой напишите на email: support@drillflow.ru или позвоните по телефону: +7 (800) 123-45-67")
    elif text == "ℹ️ Помощь":
        await cmd_help(message)
    else:
        await message.answer(f"Получено сообщение: {text}", reply_markup=get_main_keyboard())

# Функция запуска бота
async def main():
    try:
        logger.info("Starting bot...")
        # Запускаем бота
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
    finally:
        logger.info("Bot stopped, closing session")
        await bot.session.close()

if __name__ == '__main__':
    try:
        logger.info("Bot script started")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True) 