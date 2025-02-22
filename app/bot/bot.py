from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
import json
import base64
from app.core.logger import logger
from app.core.config import settings

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_TOKEN)
        self.dp = Dispatcher()
        self.webapp_url = "https://t.me/Drill_Flow_bot/D_F"
        
        # Регистрируем хендлеры
        self.register_handlers()

    def register_handlers(self):
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.handle_webapp_data, lambda m: m.web_app_data)

    async def start_command(self, message: types.Message):
        """Отправляет приветственное сообщение с кнопкой для открытия веб-приложения"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Создать заказ",
                web_app=WebAppInfo(url=self.webapp_url)
            )
        ]])
        
        await message.answer(
            "Добро пожаловать! Нажмите кнопку ниже, чтобы создать заказ:",
            reply_markup=keyboard
        )

    async def handle_webapp_data(self, message: types.Message):
        """Обрабатывает данные, отправленные из веб-приложения"""
        try:
            data = json.loads(message.web_app_data.data)
            
            if data['action'] == 'create_order':
                order_data = data['data']
                
                # Создаем заказ
                order = await self.create_order(
                    client_id=message.from_user.id,
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
                await message.answer(
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
            await message.answer("❌ Произошла ошибка при создании заказа")

    async def start(self):
        """Запускает бота"""
        try:
            logger.info("Starting bot...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise 