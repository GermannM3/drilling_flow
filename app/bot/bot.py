from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
import base64
from log import logger

class Bot:
    def __init__(self, token: str, webapp_url: str):
        self.application = Application.builder().token(token).build()
        self.webapp_url = webapp_url
        
        # Handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.handle_webapp_data))

    async def start_command(self, update, context):
        """Отправляет приветственное сообщение с кнопкой для открытия веб-приложения"""
        keyboard = [[InlineKeyboardButton(
            "Создать заказ",
            web_app=WebAppInfo(url=f"{self.webapp_url}/webapp")
        )]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Добро пожаловать! Нажмите кнопку ниже, чтобы создать заказ:",
            reply_markup=reply_markup
        )

    async def handle_webapp_data(self, update, context):
        """Обрабатывает данные, отправленные из веб-приложения"""
        try:
            data = json.loads(update.message.web_app_data.data)
            
            if data['action'] == 'create_order':
                order_data = data['data']
                
                # Создаем заказ
                order = await self.create_order(
                    client_id=update.effective_user.id,
                    service_type=order_data['service_type'],
                    address=order_data['address'],
                    latitude=float(order_data['latitude']),
                    longitude=float(order_data['longitude']),
                    description=order_data['description']
                )
                
                # Если есть фото
                if 'photo' in order_data:
                    photo_data = base64.b64decode(order_data['photo'].split(',')[1])
                    await self.save_order_photo(order.id, photo_data)
                
                # Находим подходящих подрядчиков
                contractors = await self.find_nearby_contractors(
                    latitude=float(order_data['latitude']),
                    longitude=float(order_data['longitude'])
                )
                
                # Отправляем подтверждение
                await update.message.reply_text(
                    f"✅ Заказ создан!\n\n"
                    f"📍 {order_data['address']}\n"
                    f"🔧 {order.get_service_type_display()}\n"
                    f"📝 {order_data['description']}\n\n"
                    f"Найдено {len(contractors)} подходящих подрядчиков"
                )
                
                # Уведомляем подрядчиков
                for contractor in contractors:
                    await self.notify_contractor(contractor, order)
                    
        except Exception as e:
            logger.error(f"Error processing webapp data: {e}")
            await update.message.reply_text("❌ Произошла ошибка при создании заказа")

    def run(self):
        """Запускает бота"""
        self.application.run_polling() 