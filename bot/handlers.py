from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext
import logging

logger = logging.getLogger(__name__)

ORDER_STATES = {
    'SELECTING_SERVICE': 1,
    'ENTERING_LOCATION': 2,
    'CONFIRMING_ORDER': 3
}

def start_order(update, context):
    keyboard = [
        [InlineKeyboardButton("Бурение", callback_data='drilling')],
        [InlineKeyboardButton("Канализация", callback_data='sewer')],
        [InlineKeyboardButton("Ремонт скважин", callback_data='repair')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Выберите тип услуги:",
        reply_markup=reply_markup
    )
    return ORDER_STATES['SELECTING_SERVICE']

def handle_service_selection(update, context):
    query = update.callback_query
    service_type = query.data
    context.user_data['service_type'] = service_type
    
    query.edit_message_text("Пожалуйста, отправьте ваше местоположение:")
    return ORDER_STATES['ENTERING_LOCATION']

def handle_location(update, context):
    location = update.message.location
    context.user_data['location'] = Point(location.longitude, location.latitude)
    
    # Создаем предварительный заказ
    order = Order.objects.create(
        client=context.user,
        service_type=context.user_data['service_type'],
        location=context.user_data['location'],
        status='pending'
    )
    
    # Пытаемся назначить заказ
    assign_order(order)
    
    update.message.reply_text("Ваш заказ принят! Ожидайте подтверждения от подрядчика.")
    return ConversationHandler.END 

def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    welcome_text = "Добро пожаловать в DrillFlow бот!\nИспользуйте /help для получения информации."
    update.message.reply_text(welcome_text)

def help_command(update: Update, context: CallbackContext):
    """Обработчик команды /help"""
    help_text = (
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/profile - информация о вашем профиле\n"
        "/order - создать заказ\n"
        "/support - связь с поддержкой"
    )
    update.message.reply_text(help_text)

def profile(update: Update, context: CallbackContext):
    """Обработчик команды /profile"""
    # Здесь необходимо реализовать получение профиля из БД
    update.message.reply_text("Ваш профиль: [информация о пользователе]")

def support(update: Update, context: CallbackContext):
    """Обработчик команды /support"""
    update.message.reply_text("Свяжитесь с поддержкой по адресу support@drillflow.com")

def create_order(update: Update, context: CallbackContext):
    """Обработчик команды /order для создания нового заказа"""
    try:
        service_type = context.args[0]
        address = " ".join(context.args[1:])
        # Здесь следует добавить логику сохранения заказа в БД и его распределения
        response = f"Заказ для услуги '{service_type}' по адресу '{address}' создан."
        update.message.reply_text(response)
    except IndexError:
        update.message.reply_text("Использование: /order <услуга> <адрес>")

def echo(update: Update, context: CallbackContext):
    """Эхо-ответ при получении нераспознанных сообщений"""
    update.message.reply_text("Я вас не понимаю. Используйте /help для получения списка команд.") 