import os
import sys
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
# TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_TOKEN = "7554540052:AAEvde_xL9d85kbJBdxPu8B6Mo4UEMF-qBs"  # Временно используем токен напрямую
# USE_POLLING = os.getenv('USE_POLLING', 'False').lower() in ('true', '1', 't')
# DISABLE_BOT = os.getenv('DISABLE_BOT', 'False').lower() in ('true', '1', 't')
USE_POLLING = True  # Временно включаем режим поллинга
DISABLE_BOT = False  # Временно включаем бота

# Проверка наличия токена
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    sys.exit(1)

logger.info(f"Инициализация бота с параметрами: USE_POLLING={USE_POLLING}, DISABLE_BOT={DISABLE_BOT}")
logger.info(f"Токен: {TELEGRAM_TOKEN[:5]}...{TELEGRAM_TOKEN[-5:]}")

try:
    # Инициализация бота и диспетчера
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    
    # Создаем клавиатуру для основного меню
    main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    main_keyboard.add(KeyboardButton("📊 Статистика"))
    main_keyboard.add(KeyboardButton("📝 Отчеты"), KeyboardButton("⚙️ Настройки"))
    main_keyboard.add(KeyboardButton("❓ Помощь"))
    
    # Создаем инлайн клавиатуру для отчетов
    reports_keyboard = InlineKeyboardMarkup(row_width=2)
    reports_keyboard.add(
        InlineKeyboardButton("Ежедневный", callback_data="report_daily"),
        InlineKeyboardButton("Еженедельный", callback_data="report_weekly"),
        InlineKeyboardButton("Ежемесячный", callback_data="report_monthly"),
        InlineKeyboardButton("Годовой", callback_data="report_yearly")
    )
    
    @dp.message_handler(commands=['start'])
    async def cmd_start(message: types.Message):
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
            
            await message.answer(
                f"👋 Привет, {message.from_user.first_name}!\n\n"
                f"Я бот для мониторинга бурения. Используйте меню для навигации.",
                reply_markup=main_keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике /start: {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler(commands=['help'])
    async def cmd_help(message: types.Message):
        try:
            logger.info(f"Пользователь {message.from_user.username} (ID: {message.from_user.id}) запросил помощь")
            
            help_text = (
                "📚 *Справка по командам:*\n\n"
                "/start - Запустить бота\n"
                "/help - Показать эту справку\n"
                "/stats - Показать статистику\n"
                "/reports - Выбрать тип отчета\n"
                "/settings - Настройки уведомлений\n\n"
                "Вы также можете использовать кнопки меню для навигации."
            )
            
            await message.answer(help_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка в обработчике /help: {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler(commands=['stats'])
    async def cmd_stats(message: types.Message):
        try:
            logger.info(f"Пользователь {message.from_user.username} (ID: {message.from_user.id}) запросил статистику")
            
            # Здесь будет логика получения реальных данных
            current_date = datetime.now().strftime("%d.%m.%Y")
            
            stats_text = (
                f"📊 *Статистика на {current_date}*\n\n"
                f"🕑 Время работы: 12ч 30м\n"
                f"🔄 Циклов бурения: 24\n"
                f"📏 Глубина: 1250м\n"
                f"⚠️ Предупреждений: 2\n"
                f"❌ Ошибок: 0\n\n"
                f"_Последнее обновление: {datetime.now().strftime('%H:%M:%S')}_"
            )
            
            await message.answer(stats_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка в обработчике /stats: {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при получении статистики. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler(commands=['reports'])
    async def cmd_reports(message: types.Message):
        try:
            logger.info(f"Пользователь {message.from_user.username} (ID: {message.from_user.id}) запросил отчеты")
            
            await message.answer(
                "📝 Выберите тип отчета:",
                reply_markup=reports_keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике /reports: {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")
    
    @dp.callback_query_handler(lambda c: c.data.startswith('report_'))
    async def process_report_callback(callback_query: types.CallbackQuery):
        try:
            report_type = callback_query.data.split('_')[1]
            user_id = callback_query.from_user.id
            username = callback_query.from_user.username
            
            logger.info(f"Пользователь {username} (ID: {user_id}) запросил отчет типа: {report_type}")
            
            report_titles = {
                'daily': 'Ежедневный',
                'weekly': 'Еженедельный',
                'monthly': 'Ежемесячный',
                'yearly': 'Годовой'
            }
            
            await bot.answer_callback_query(callback_query.id)
            await bot.send_message(
                callback_query.from_user.id,
                f"📊 *{report_titles[report_type]} отчет*\n\n"
                f"Отчет за период: {datetime.now().strftime('%d.%m.%Y')}\n"
                f"Статус: Генерация...\n\n"
                f"Отчет будет готов в течение нескольких минут.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике callback_query: {e}")
            logger.error(traceback.format_exc())
            await bot.send_message(
                callback_query.from_user.id,
                "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."
            )
    
    @dp.message_handler(lambda message: message.text == "📊 Статистика")
    async def text_stats(message: types.Message):
        try:
            await cmd_stats(message)
        except Exception as e:
            logger.error(f"Ошибка в обработчике текстовой команды 'Статистика': {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при получении статистики. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler(lambda message: message.text == "📝 Отчеты")
    async def text_reports(message: types.Message):
        try:
            await cmd_reports(message)
        except Exception as e:
            logger.error(f"Ошибка в обработчике текстовой команды 'Отчеты': {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler(lambda message: message.text == "⚙️ Настройки")
    async def text_settings(message: types.Message):
        try:
            logger.info(f"Пользователь {message.from_user.username} (ID: {message.from_user.id}) запросил настройки")
            
            await message.answer(
                "⚙️ *Настройки уведомлений*\n\n"
                "🔔 Критические предупреждения: Включены\n"
                "🔕 Обычные уведомления: Выключены\n"
                "⏰ Ежедневный отчет: Включен (08:00)\n"
                "📅 Еженедельный отчет: Включен (Пн, 09:00)\n\n"
                "_Для изменения настроек обратитесь к администратору._",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике текстовой команды 'Настройки': {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при получении настроек. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler(lambda message: message.text == "❓ Помощь")
    async def text_help(message: types.Message):
        try:
            await cmd_help(message)
        except Exception as e:
            logger.error(f"Ошибка в обработчике текстовой команды 'Помощь': {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler()
    async def echo(message: types.Message):
        try:
            logger.info(f"Получено сообщение от {message.from_user.username} (ID: {message.from_user.id}): {message.text}")
            
            await message.answer(
                "Извините, я не понимаю эту команду. Используйте меню или введите /help для получения списка доступных команд.",
                reply_markup=main_keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике echo: {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте позже.")
    
    # Функция для запуска бота
    def start_polling():
        try:
            logger.info("Запуск бота в режиме polling")
            executor.start_polling(dp, skip_updates=True)
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)
    
    # Точка входа
    if __name__ == '__main__':
        logger.info("Бот запущен")
        if DISABLE_BOT:
            logger.warning("Бот отключен в настройках")
            sys.exit(0)
        
        if USE_POLLING:
            start_polling()
        else:
            logger.info("Режим polling не активирован, бот не будет запущен")
            sys.exit(0)

except Exception as e:
    logger.critical(f"Критическая ошибка при инициализации бота: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1) 