"""
DrillFlow Telegram Bot
"""
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
import logging
import asyncio
from datetime import datetime
from app.core.config import get_settings
from app.db.models import User, Order, Contractor
from app.schemas.order import OrderCreate, OrderStatus
from app.schemas.user import UserCreate, UserRoleEnum
from app.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=settings.TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = RedisStorage.from_url(settings.REDIS_URL)
dp = Dispatcher(storage=storage)

# Состояния FSM
class OrderStates(StatesGroup):
    choosing_service = State()
    entering_address = State()
    entering_description = State()
    confirming = State()

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔨 Создать заказ"),
            KeyboardButton(text="📋 Мои заказы")
        ],
        [
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="ℹ️ Помощь")
        ]
    ],
    resize_keyboard=True
)

service_keyboard = InlineKeyboardBuilder()
service_keyboard.button(text="🚰 Бурение скважины", callback_data="service_drilling")
service_keyboard.button(text="🔧 Ремонт скважины", callback_data="service_repair")
service_keyboard.button(text="🚽 Канализация", callback_data="service_sewage")
service_keyboard.adjust(1)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    try:
        async with get_async_session() as session:
            # Проверяем существование пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == str(message.from_user.id))
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # Создаем нового пользователя
                new_user = UserCreate(
                    telegram_id=str(message.from_user.id),
                    username=message.from_user.username or "",
                    first_name=message.from_user.first_name,
                    role=UserRoleEnum.CLIENT
                )
                user = User(**new_user.dict())
                session.add(user)
                await session.commit()
                
                await message.answer(
                    f"👋 Добро пожаловать в DrillFlow, {message.from_user.first_name}!\n"
                    "Я помогу вам заказать услуги по бурению скважин и монтажу канализации.",
                    reply_markup=main_keyboard
                )
            else:
                await message.answer(
                    f"С возвращением, {user.first_name}!",
                    reply_markup=main_keyboard
                )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")

@dp.message(lambda message: message.text == "🔨 Создать заказ")
async def create_order(message: types.Message, state: FSMContext):
    """Начало создания заказа"""
    await state.set_state(OrderStates.choosing_service)
    await message.answer(
        "Выберите тип услуги:",
        reply_markup=service_keyboard.as_markup()
    )

@dp.callback_query(lambda c: c.data.startswith("service_"))
async def process_service_choice(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора услуги"""
    service_type = callback.data.split("_")[1]
    await state.update_data(service_type=service_type)
    await state.set_state(OrderStates.entering_address)
    
    await callback.message.answer(
        "Отправьте адрес выполнения работ или поделитесь геолокацией.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
            resize_keyboard=True
        )
    )
    await callback.answer()

@dp.message(OrderStates.entering_address)
async def process_address(message: types.Message, state: FSMContext):
    """Обработка ввода адреса"""
    if message.location:
        # TODO: Преобразование координат в адрес через API
        address = f"lat: {message.location.latitude}, lon: {message.location.longitude}"
    else:
        address = message.text
        
    await state.update_data(address=address)
    await state.set_state(OrderStates.entering_description)
    
    await message.answer(
        "Опишите ваш заказ подробнее (глубина скважины, тип работ и т.д.):",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(OrderStates.entering_description)
async def process_description(message: types.Message, state: FSMContext):
    """Обработка описания заказа"""
    data = await state.get_data()
    await state.update_data(description=message.text)
    
    # Создание заказа
    try:
        async with get_async_session() as session:
            order = Order(
                client_id=message.from_user.id,
                service_type=data['service_type'],
                address=data['address'],
                description=message.text,
                status=OrderStatus.NEW
            )
            session.add(order)
            await session.commit()
            
            # Поиск подходящих подрядчиков
            result = await session.execute(
                select(Contractor)
                .where(Contractor.specialization == data['service_type'])
                .order_by(Contractor.rating.desc())
                .limit(5)
            )
            contractors = result.scalars().all()
            
            # Отправка уведомлений подрядчикам
            for contractor in contractors:
                try:
                    await bot.send_message(
                        contractor.telegram_id,
                        f"🔔 Новый заказ!\n"
                        f"Тип: {data['service_type']}\n"
                        f"Адрес: {data['address']}\n"
                        f"Описание: {message.text}\n\n"
                        f"У вас есть 5 минут на принятие заказа.",
                        reply_markup=InlineKeyboardBuilder()
                        .button(text="✅ Принять", callback_data=f"accept_{order.id}")
                        .button(text="❌ Отказаться", callback_data=f"decline_{order.id}")
                        .as_markup()
                    )
                except Exception as e:
                    logger.error(f"Error sending notification to contractor {contractor.id}: {e}")
            
            await message.answer(
                "✅ Заказ успешно создан! Ожидайте подтверждения от подрядчика.",
                reply_markup=main_keyboard
            )
            
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        await message.answer(
            "❌ Произошла ошибка при создании заказа. Попробуйте позже.",
            reply_markup=main_keyboard
        )
    
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith(("accept_", "decline_")))
async def process_contractor_response(callback: types.CallbackQuery):
    """Обработка ответа подрядчика"""
    action, order_id = callback.data.split("_")
    
    try:
        async with get_async_session() as session:
            result = await session.execute(
                select(Order).where(Order.id == int(order_id))
            )
            order = result.scalar_one_or_none()
            
            if not order:
                await callback.answer("Заказ уже не доступен")
                return
                
            if action == "accept":
                if order.contractor_id:
                    await callback.answer("Заказ уже принят другим подрядчиком")
                    return
                    
                order.contractor_id = callback.from_user.id
                order.status = OrderStatus.ASSIGNED
                await session.commit()
                
                # Уведомляем клиента
                await bot.send_message(
                    order.client_id,
                    f"✅ Ваш заказ #{order.id} принят подрядчиком!"
                )
                
                await callback.answer("Вы приняли заказ!")
                
            else:  # decline
                await callback.answer("Вы отказались от заказа")
                
    except Exception as e:
        logger.error(f"Error processing contractor response: {e}")
        await callback.answer("Произошла ошибка. Попробуйте позже.")

async def start_polling():
    """Запуск бота"""
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(start_polling()) 