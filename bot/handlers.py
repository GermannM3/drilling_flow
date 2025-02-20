from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

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