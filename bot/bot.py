import os
import sys
import logging
import traceback
from datetime import datetime
import asyncio
import sqlite3
import json
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
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_WEBHOOK_DOMAIN = os.getenv('BOT_WEBHOOK_DOMAIN')
USE_POLLING = os.getenv('USE_POLLING', 'False').lower() in ('true', '1', 't')
DISABLE_BOT = os.getenv('DISABLE_BOT', 'False').lower() in ('true', '1', 't')
DATABASE_URL = os.getenv('DATABASE_URL')

# Проверка наличия токена
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    sys.exit(1)

logger.info(f"Инициализация бота с параметрами: USE_POLLING={USE_POLLING}, DISABLE_BOT={DISABLE_BOT}")
logger.info(f"Токен: {TELEGRAM_TOKEN[:5]}...{TELEGRAM_TOKEN[-5:]}")

# Инициализация соединения с базой данных
def init_db():
    try:
        # В зависимости от окружения используем разные БД
        if 'VERCEL' in os.environ:
            # На Vercel используем SQLite в памяти или подключаемся к внешней БД
            if DATABASE_URL and DATABASE_URL.startswith('postgres'):
                # Здесь должна быть логика подключения к PostgreSQL
                logger.info("Используется PostgreSQL на Vercel")
                return None  # заглушка для примера
            else:
                # Используем SQLite в памяти
                conn = sqlite3.connect(':memory:')
                logger.info("Используется SQLite в памяти на Vercel")
        else:
            # Локально используем файл SQLite
            conn = sqlite3.connect('drillflow.db')
            logger.info("Используется локальная SQLite база данных")
        
        # Создаем таблицы, если их нет
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS drilling_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            operation_type TEXT NOT NULL,
            depth REAL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_type TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        return conn
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        logger.error(traceback.format_exc())
        return None

# Функции для работы с базой данных
def register_user(conn, user_id, username, first_name, last_name):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, last_name)
        )
        conn.commit()
        logger.info(f"Пользователь {username} (ID: {user_id}) зарегистрирован")
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        conn.rollback()

def create_drilling_operation(conn, user_id, operation_type, depth=None):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO drilling_operations (user_id, operation_type, depth, status) VALUES (?, ?, ?, ?)",
            (user_id, operation_type, depth, "начато")
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Ошибка при создании операции бурения: {e}")
        conn.rollback()
        return None

def update_drilling_operation(conn, operation_id, status, depth=None):
    try:
        cursor = conn.cursor()
        if depth is not None:
            cursor.execute(
                "UPDATE drilling_operations SET status = ?, depth = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, depth, operation_id)
            )
        else:
            cursor.execute(
                "UPDATE drilling_operations SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, operation_id)
            )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении операции бурения: {e}")
        conn.rollback()
        return False

def get_user_operations(conn, user_id, limit=5):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, operation_type, depth, status, created_at FROM drilling_operations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении операций пользователя: {e}")
        return []

def create_report(conn, user_id, report_type, data_dict):
    try:
        cursor = conn.cursor()
        data_json = json.dumps(data_dict)
        cursor.execute(
            "INSERT INTO reports (user_id, report_type, data) VALUES (?, ?, ?)",
            (user_id, report_type, data_json)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Ошибка при создании отчета: {e}")
        conn.rollback()
        return None

def get_user_reports(conn, user_id, limit=5):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, report_type, data, created_at FROM reports WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        reports = []
        for row in cursor.fetchall():
            report_id, report_type, data_json, created_at = row
            try:
                data = json.loads(data_json)
            except:
                data = {}
            reports.append({
                'id': report_id,
                'type': report_type,
                'data': data,
                'created_at': created_at
            })
        return reports
    except Exception as e:
        logger.error(f"Ошибка при получении отчетов пользователя: {e}")
        return []

try:
    # Инициализация базы данных
    db_conn = init_db()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    
    # Создаем клавиатуру для основного меню
    main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    main_keyboard.add(KeyboardButton("📊 Статистика"))
    main_keyboard.add(KeyboardButton("📝 Отчеты"), KeyboardButton("🔍 Создать заказ"))
    main_keyboard.add(KeyboardButton("⚙️ Настройки"), KeyboardButton("❓ Помощь"))
    
    # Создаем инлайн клавиатуру для отчетов
    reports_keyboard = InlineKeyboardMarkup(row_width=2)
    reports_keyboard.add(
        InlineKeyboardButton("Ежедневный", callback_data="report_daily"),
        InlineKeyboardButton("Еженедельный", callback_data="report_weekly"),
        InlineKeyboardButton("Ежемесячный", callback_data="report_monthly"),
        InlineKeyboardButton("Годовой", callback_data="report_yearly")
    )
    
    # Создаем инлайн клавиатуру для создания заказа
    order_keyboard = InlineKeyboardMarkup(row_width=2)
    order_keyboard.add(
        InlineKeyboardButton("Бурение скважины", callback_data="order_drilling"),
        InlineKeyboardButton("Ремонт скважины", callback_data="order_repair"),
        InlineKeyboardButton("Канализация", callback_data="order_sewer"),
        InlineKeyboardButton("Консультация", callback_data="order_consult")
    )
    
    @dp.message_handler(commands=['start'])
    async def cmd_start(message: types.Message):
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            
            logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
            
            # Регистрируем пользователя в базе
            if db_conn:
                register_user(db_conn, user_id, username, first_name, last_name)
            
            await message.answer(
                f"👋 Привет, {first_name}!\n\n"
                f"Я бот для управления буровыми работами. Используйте меню для навигации.",
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
                "/order - Создать заказ\n"
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
            user_id = message.from_user.id
            logger.info(f"Пользователь {message.from_user.username} (ID: {user_id}) запросил статистику")
            
            # Получаем данные из базы
            operations = []
            if db_conn:
                operations = get_user_operations(db_conn, user_id)
            
            current_date = datetime.now().strftime("%d.%m.%Y")
            
            if operations:
                # Формируем статистику на основе реальных данных
                completed = sum(1 for op in operations if op[3] == "завершено")
                in_progress = sum(1 for op in operations if op[3] == "в процессе")
                total_depth = sum(op[2] for op in operations if op[2] is not None)
                
                stats_text = (
                    f"📊 *Статистика на {current_date}*\n\n"
                    f"🔄 Всего операций: {len(operations)}\n"
                    f"✅ Завершено: {completed}\n"
                    f"⏳ В процессе: {in_progress}\n"
                    f"📏 Общая глубина бурения: {total_depth}м\n\n"
                    f"_Последнее обновление: {datetime.now().strftime('%H:%M:%S')}_"
                )
            else:
                # Если данных нет, показываем заглушку
                stats_text = (
                    f"📊 *Статистика на {current_date}*\n\n"
                    f"У вас пока нет операций бурения.\n"
                    f"Используйте кнопку '🔍 Создать заказ' для начала работы.\n\n"
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
    
    @dp.message_handler(commands=['order'])
    async def cmd_order(message: types.Message):
        try:
            logger.info(f"Пользователь {message.from_user.username} (ID: {message.from_user.id}) запросил создание заказа")
            
            await message.answer(
                "🔍 Выберите тип заказа:",
                reply_markup=order_keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике /order: {e}")
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
            
            # Создаем отчет в базе данных
            report_id = None
            if db_conn:
                # Собираем данные для отчета
                operations = get_user_operations(db_conn, user_id, limit=10)
                report_data = {
                    'type': report_type,
                    'operations_count': len(operations),
                    'generated_at': datetime.now().isoformat()
                }
                report_id = create_report(db_conn, user_id, report_type, report_data)
            
            await bot.answer_callback_query(callback_query.id)
            
            if report_id:
                await bot.send_message(
                    callback_query.from_user.id,
                    f"📊 *{report_titles[report_type]} отчет*\n\n"
                    f"Отчет #{report_id} за период: {datetime.now().strftime('%d.%m.%Y')}\n"
                    f"Статус: Готов\n\n"
                    f"Количество операций: {len(operations)}\n"
                    f"Детали доступны в веб-интерфейсе.",
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(
                    callback_query.from_user.id,
                    f"📊 *{report_titles[report_type]} отчет*\n\n"
                    f"Отчет за период: {datetime.now().strftime('%d.%m.%Y')}\n"
                    f"Статус: Ошибка генерации\n\n"
                    f"Не удалось создать отчет. Пожалуйста, попробуйте позже.",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Ошибка в обработчике callback_query (report): {e}")
            logger.error(traceback.format_exc())
            await bot.send_message(
                callback_query.from_user.id,
                "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."
            )
    
    @dp.callback_query_handler(lambda c: c.data.startswith('order_'))
    async def process_order_callback(callback_query: types.CallbackQuery):
        try:
            order_type = callback_query.data.split('_')[1]
            user_id = callback_query.from_user.id
            username = callback_query.from_user.username
            
            logger.info(f"Пользователь {username} (ID: {user_id}) создает заказ типа: {order_type}")
            
            order_titles = {
                'drilling': 'Бурение скважины',
                'repair': 'Ремонт скважины',
                'sewer': 'Канализация',
                'consult': 'Консультация'
            }
            
            # Создаем операцию в базе данных
            operation_id = None
            if db_conn:
                depth = 10.0 if order_type == 'drilling' else None
                operation_id = create_drilling_operation(db_conn, user_id, order_titles[order_type], depth)
            
            await bot.answer_callback_query(callback_query.id)
            
            if operation_id:
                await bot.send_message(
                    callback_query.from_user.id,
                    f"✅ *Заказ создан*\n\n"
                    f"Тип: {order_titles[order_type]}\n"
                    f"ID заказа: #{operation_id}\n"
                    f"Статус: Принят в обработку\n\n"
                    f"Мы свяжемся с вами в ближайшее время для уточнения деталей.",
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(
                    callback_query.from_user.id,
                    f"❌ *Ошибка создания заказа*\n\n"
                    f"Тип: {order_titles[order_type]}\n"
                    f"Статус: Не удалось создать\n\n"
                    f"Пожалуйста, попробуйте позже или обратитесь в поддержку.",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Ошибка в обработчике callback_query (order): {e}")
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
    
    @dp.message_handler(lambda message: message.text == "🔍 Создать заказ")
    async def text_order(message: types.Message):
        try:
            await cmd_order(message)
        except Exception as e:
            logger.error(f"Ошибка в обработчике текстовой команды 'Создать заказ': {e}")
            logger.error(traceback.format_exc())
            await message.answer("Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")
    
    @dp.message_handler(lambda message: message.text == "⚙️ Настройки")
    async def text_settings(message: types.Message):
        try:
            logger.info(f"Пользователь {message.from_user.username} (ID: {message.from_user.id}) запросил настройки")
            
            # Получаем настройки пользователя из базы
            has_settings = False
            if db_conn:
                # В реальном боте здесь была бы выборка настроек
                has_settings = True
            
            if has_settings:
                await message.answer(
                    "⚙️ *Настройки уведомлений*\n\n"
                    "🔔 Критические предупреждения: Включены\n"
                    "🔕 Обычные уведомления: Выключены\n"
                    "⏰ Ежедневный отчет: Включен (08:00)\n"
                    "📅 Еженедельный отчет: Включен (Пн, 09:00)\n\n"
                    "_Для изменения настроек используйте веб-интерфейс._",
                    parse_mode="Markdown"
                )
            else:
                await message.answer(
                    "⚙️ *Настройки уведомлений*\n\n"
                    "У вас пока нет настроек уведомлений.\n"
                    "Для их создания используйте веб-интерфейс системы.",
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
    
    # Функция для настройки вебхука
    async def on_startup(dp):
        if not DISABLE_BOT and not USE_POLLING:
            webhook_url = f"{BOT_WEBHOOK_DOMAIN}/webhook/{TELEGRAM_TOKEN}"
            logger.info(f"Устанавливаем вебхук на URL: {webhook_url}")
            await bot.set_webhook(webhook_url)
    
    # Функция для отключения вебхука
    async def on_shutdown(dp):
        if not USE_POLLING:
            logger.info("Отключаем вебхук")
            await bot.delete_webhook()
    
    # Функция для регистрации всех обработчиков сообщений
    def register_handlers(dp):
        """
        Регистрирует все обработчики сообщений бота.
        Эта функция используется как при запуске бота в режиме polling,
        так и при обработке вебхуков.
        """
        # Команды
        dp.register_message_handler(cmd_start, commands=['start'])
        dp.register_message_handler(cmd_help, commands=['help'])
        dp.register_message_handler(cmd_stats, commands=['stats'])
        dp.register_message_handler(cmd_reports, commands=['reports'])
        dp.register_message_handler(cmd_order, commands=['order'])
        
        # Callback запросы
        dp.register_callback_query_handler(process_report_callback, lambda c: c.data.startswith('report_'))
        dp.register_callback_query_handler(process_order_callback, lambda c: c.data.startswith('order_'))
        
        # Текстовые команды
        dp.register_message_handler(text_stats, lambda message: message.text == "📊 Статистика")
        dp.register_message_handler(text_reports, lambda message: message.text == "📝 Отчеты")
        dp.register_message_handler(text_order, lambda message: message.text == "🔍 Создать заказ")
        dp.register_message_handler(text_settings, lambda message: message.text == "⚙️ Настройки")
        dp.register_message_handler(text_help, lambda message: message.text == "❓ Помощь")
        
        # Все остальные сообщения
        dp.register_message_handler(echo)
        
        return dp
    
    # Точка входа
    if __name__ == '__main__':
        logger.info("Бот запущен")
        if DISABLE_BOT:
            logger.warning("Бот отключен в настройках")
            sys.exit(0)
        
        # Регистрируем обработчики
        register_handlers(dp)
        
        if USE_POLLING:
            logger.info("Запуск бота в режиме polling")
            executor.start_polling(dp, skip_updates=True)
        else:
            logger.info("Запуск бота в режиме webhook")
            # В этом режиме бот будет ждать запросов от вебхука
            # Для работы на Vercel это должно быть обработано в API эндпоинте
            # В данном случае это происходит в api/python/index.js
            sys.exit(0)

except Exception as e:
    logger.critical(f"Критическая ошибка при инициализации бота: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1) 