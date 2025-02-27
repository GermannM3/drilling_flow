import json
import os
import logging
import asyncio
import sys
from http.server import BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import parse_qs

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
logger.info(f"Bot token: {TELEGRAM_TOKEN[:4]}...{TELEGRAM_TOKEN[-4:] if TELEGRAM_TOKEN else 'Not set'}")

try:
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    logger.info("Bot and dispatcher initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    raise

# Клавиатура для главного меню
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

# Обработчик команды /start
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
        logger.error(f"Traceback: {sys.exc_info()}")
        return False

# Обработчик команды /начать
@dp.message(Command("начать"))
async def start_command_ru(message: Message):
    """Обработчик команды /начать"""
    return await start_command(message)

# Обработчик команды /profile
@dp.message(Command("profile"))
async def profile_command(message: Message):
    """Обработчик команды /profile"""
    try:
        logger.info(f"Received profile command from user {message.from_user.id}")
        await message.answer(
            f"🔑 Профиль пользователя {hbold(message.from_user.full_name)}\n\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"👤 Username: @{message.from_user.username or 'не указан'}\n\n"
            f"Для редактирования профиля используйте кнопки ниже:",
            reply_markup=get_main_keyboard()
        )
        logger.info("Profile info sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send profile info: {e}")
        return False

# Обработчик команды /профиль
@dp.message(Command("профиль"))
async def profile_command_ru(message: Message):
    """Обработчик команды /профиль"""
    return await profile_command(message)

# Обработчик команды /orders
@dp.message(Command("orders"))
async def orders_command(message: Message):
    """Обработчик команды /orders"""
    try:
        logger.info(f"Received orders command from user {message.from_user.id}")
        await message.answer(
            "📦 Управление заказами\n\n"
            "Здесь вы можете:\n"
            "• Создать новый заказ\n"
            "• Просмотреть активные заказы\n"
            "• Управлять существующими заказами",
            reply_markup=get_main_keyboard()
        )
        logger.info("Orders info sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send orders info: {e}")
        return False

# Обработчик команды /заказы
@dp.message(Command("заказы"))
async def orders_command_ru(message: Message):
    """Обработчик команды /заказы"""
    return await orders_command(message)

# Обработчик команды /help
@dp.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    try:
        logger.info(f"Received help command from user {message.from_user.id}")
        await message.answer(
            "ℹ️ Справка по командам:\n\n"
            "/start, /начать - Начать работу с ботом\n"
            "/profile, /профиль - Просмотр профиля\n"
            "/orders, /заказы - Управление заказами\n"
            "/help, /помощь - Показать эту справку",
            reply_markup=get_main_keyboard()
        )
        logger.info("Help info sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send help info: {e}")
        return False

# Обработчик команды /помощь
@dp.message(Command("помощь"))
async def help_command_ru(message: Message):
    """Обработчик команды /помощь"""
    return await help_command(message)

# Обработчик текстовых сообщений с эмодзи
@dp.message(F.text.startswith("📋"))
async def profile_text(message: Message):
    """Обработчик текстовых сообщений с эмодзи 'Профиль'"""
    try:
        logger.info(f"Received profile text from user {message.from_user.id}")
        await profile_command(message)
        return True
    except Exception as e:
        logger.error(f"Failed to process profile text: {e}")
        return False

@dp.message(F.text.startswith("📦"))
async def orders_text(message: Message):
    """Обработчик текстовых сообщений с эмодзи 'Заказы'"""
    try:
        logger.info(f"Received orders text from user {message.from_user.id}")
        await orders_command(message)
        return True
    except Exception as e:
        logger.error(f"Failed to process orders text: {e}")
        return False

@dp.message(F.text.startswith("❓"))
async def help_text(message: Message):
    """Обработчик текстовых сообщений с эмодзи 'Помощь'"""
    try:
        logger.info(f"Received help text from user {message.from_user.id}")
        await help_command(message)
        return True
    except Exception as e:
        logger.error(f"Failed to process help text: {e}")
        return False

@dp.message(F.text.startswith("📊"))
async def stats_text(message: Message):
    """Обработчик текстовых сообщений с эмодзи 'Статистика'"""
    try:
        logger.info(f"Received stats text from user {message.from_user.id}")
        await message.answer(
            "📊 Статистика\n\n"
            "В разработке...",
            reply_markup=get_main_keyboard()
        )
        logger.info("Stats info sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to process stats text: {e}")
        return False

@dp.message(F.text.startswith("📝"))
async def reports_text(message: Message):
    """Обработчик текстовых сообщений с эмодзи 'Отчеты'"""
    try:
        logger.info(f"Received reports text from user {message.from_user.id}")
        await message.answer(
            "📝 Отчеты\n\n"
            "Здесь будут ваши отчеты...",
            reply_markup=get_main_keyboard()
        )
        logger.info("Reports info sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to process reports text: {e}")
        return False

@dp.message(F.text.startswith("⚙️"))
async def settings_text(message: Message):
    """Обработчик текстовых сообщений с эмодзи 'Настройки'"""
    try:
        logger.info(f"Received settings text from user {message.from_user.id}")
        await message.answer(
            "⚙️ Настройки\n\n"
            "Здесь будут настройки...",
            reply_markup=get_main_keyboard()
        )
        logger.info("Settings info sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to process settings text: {e}")
        return False

# Обработчик всех остальных текстовых сообщений
@dp.message(F.text)
async def handle_message(message: Message):
    """Обработчик всех остальных текстовых сообщений"""
    try:
        logger.info(f"Received text message from user {message.from_user.id}: {message.text}")
        await message.answer(
            f"Вы отправили: {message.text}\n\n"
            f"Используйте команду /help или /помощь для просмотра доступных команд.",
            reply_markup=get_main_keyboard()
        )
        logger.info("Response to text message sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to process text message: {e}")
        return False

# Обработчик callback-кнопок
@dp.callback_query()
async def process_callback(callback: CallbackQuery):
    """Обработчик всех callback-кнопок"""
    try:
        logger.info(f"Received callback {callback.data} from user {callback.from_user.id}")
        
        if callback.data == "profile":
            await callback.message.edit_text(
                f"🔑 Профиль пользователя {hbold(callback.from_user.full_name)}\n\n"
                f"🆔 ID: {callback.from_user.id}\n"
                f"👤 Username: @{callback.from_user.username or 'не указан'}",
                reply_markup=get_main_keyboard()
            )
        elif callback.data == "orders":
            await callback.message.edit_text(
                "📦 Управление заказами\n\n"
                "Здесь вы можете:\n"
                "• Создать новый заказ\n"
                "• Просмотреть активные заказы\n"
                "• Управлять существующими заказами",
                reply_markup=get_main_keyboard()
            )
        elif callback.data == "help":
            await callback.message.edit_text(
                "ℹ️ Справка по командам:\n\n"
                "/start, /начать - Начать работу с ботом\n"
                "/profile, /профиль - Просмотр профиля\n"
                "/orders, /заказы - Управление заказами\n"
                "/help, /помощь - Показать эту справку",
                reply_markup=get_main_keyboard()
            )
        elif callback.data == "stats":
            await callback.message.edit_text(
                "📊 Статистика\n\n"
                "В разработке...",
                reply_markup=get_main_keyboard()
            )
            
        await callback.answer()
        logger.info(f"Callback {callback.data} processed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to process callback {callback.data}: {e}")
        return False

# Моковые данные для API
mock_data = {
    "users": [
        {"id": 1, "name": "Иван Иванов", "role": "admin", "email": "ivan@example.com"},
        {"id": 2, "name": "Петр Петров", "role": "contractor", "email": "petr@example.com"},
        {"id": 3, "name": "Сидор Сидоров", "role": "client", "email": "sidor@example.com"}
    ],
    "orders": [
        {"id": 1, "title": "Бурение скважины 1", "status": "active", "client_id": 3, "contractor_id": 2},
        {"id": 2, "title": "Бурение скважины 2", "status": "pending", "client_id": 3, "contractor_id": None},
        {"id": 3, "title": "Ремонт оборудования", "status": "completed", "client_id": 3, "contractor_id": 2}
    ],
    "stats": {
        "active_contractors": 247,
        "active_clients": 156,
        "projects_completed": 573,
        "total_revenue": 12500000
    }
}

async def process_update(update_data: dict) -> bool:
    """Обработка обновления от Telegram"""
    try:
        logger.debug(f"Processing update: {update_data}")
        
        # Создаем объект Update
        update = types.Update(**update_data)
        update_type = "unknown"
        if update.message:
            update_type = f"message from {update.message.from_user.id}"
            if update.message.text:
                update_type += f" with text: {update.message.text}"
        elif update.callback_query:
            update_type = f"callback_query from {update.callback_query.from_user.id} with data: {update.callback_query.data}"
            
        logger.info(f"Created Update object: {update_type}")
        
        try:
            # Передаем обновление в диспетчер
            result = await dp.feed_update(bot=bot, update=update)
            if result:
                logger.info("Update processed successfully")
            else:
                logger.warning("Update not processed by any handler")
            return True
        except Exception as e:
            logger.error(f"Error processing update through dispatcher: {e}")
            logger.error(f"Traceback: {sys.exc_info()}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        logger.error(f"Update data: {update_data}")
        logger.error(f"Traceback: {sys.exc_info()}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Обработка POST-запросов"""
        try:
            # Получаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Проверяем путь запроса
            logger.info(f"Received POST request to {self.path}")
            logger.debug(f"Headers: {dict(self.headers)}")
            
            # Если это webhook-запрос от Telegram
            if self.path == '/webhook':
                update_data = json.loads(post_data.decode('utf-8'))
                logger.debug(f"Webhook body: {update_data}")
                
                try:
                    # Создаем event loop для асинхронной обработки
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Обрабатываем обновление
                    success = loop.run_until_complete(process_update(update_data))
                    
                    # Закрываем loop
                    loop.close()
                    
                    # Отправляем ответ
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        "status": "success" if success else "error",
                        "message": "Update processed" if success else "Failed to process update"
                    }
                    
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                except Exception as e:
                    logger.error(f"Error processing webhook: {e}")
                    logger.error(f"Traceback: {sys.exc_info()}")
                    raise
            
            # Если это API запрос для веб-интерфейса
            elif self.path.startswith('/api/'):
                update_data = json.loads(post_data.decode('utf-8'))
                logger.debug(f"API request body: {update_data}")
                
                # Обработка API запросов
                api_path = self.path[5:]  # Удаляем '/api/' из пути
                
                # Обработка создания заказа
                if api_path == 'orders/create':
                    # Добавляем заказ в моковые данные
                    new_order = update_data
                    new_order["id"] = len(mock_data["orders"]) + 1
                    mock_data["orders"].append(new_order)
                    
                    # Отправляем ответ
                    self.send_response(201)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        "status": "success",
                        "message": "Order created successfully",
                        "order": new_order
                    }
                    
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                # Другие API запросы
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        "status": "error",
                        "message": "API endpoint not found"
                    }
                    
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
            # Для других POST-запросов
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "success",
                "received": json.loads(post_data.decode('utf-8'))
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error in do_POST: {e}")
            logger.error(f"Traceback: {sys.exc_info()}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": str(e),
                "type": type(e).__name__
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Обработка OPTIONS-запросов для CORS"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "CORS preflight request successful"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_GET(self):
        """Обработка GET-запросов"""
        try:
            # Проверяем путь запроса
            logger.info(f"Received GET request to {self.path}")
            
            # Если это корневой запрос API
            if self.path == '/api':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "ok",
                    "message": "DrillFlow API is running",
                    "version": "1.0.0",
                    "bot_initialized": bool(TELEGRAM_TOKEN),
                    "environment": os.getenv("ENVIRONMENT", "unknown"),
                    "endpoints": [
                        "/api/users",
                        "/api/orders",
                        "/api/stats"
                    ]
                }
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # Если это API запрос для пользователей
            elif self.path == '/api/users':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "ok",
                    "users": mock_data["users"]
                }
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # Если это API запрос для заказов
            elif self.path == '/api/orders':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "ok",
                    "orders": mock_data["orders"]
                }
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # Если это API запрос для статистики
            elif self.path == '/api/stats':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "ok",
                    "stats": mock_data["stats"]
                }
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # Для других GET-запросов
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "ok",
                    "message": "DrillFlow API is running",
                    "version": "1.0.0",
                    "bot_initialized": bool(TELEGRAM_TOKEN),
                    "environment": os.getenv("ENVIRONMENT", "unknown")
                }
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
        except Exception as e:
            logger.error(f"Error in do_GET: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": str(e)
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8')) 