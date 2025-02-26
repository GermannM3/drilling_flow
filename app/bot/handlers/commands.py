"""
Bot command handlers
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.bot.keyboards import (
    get_main_keyboard,
    get_service_keyboard,
    get_location_keyboard,
    get_order_actions_keyboard
)
from app.services.users import UserService
from app.services.orders import OrderService
from app.core.bot import bot
from app.schemas.base import ServiceTypeEnum, OrderStatus

router = Router(name="commands")

class OrderStates(StatesGroup):
    """Order creation states"""
    choosing_service = State()
    entering_address = State()
    entering_description = State()
    confirming = State()

@router.message(Command("start"))
async def cmd_start(message: Message, user_service: UserService):
    """Handle /start command"""
    user = await user_service.get_or_create_user(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username or "",
        first_name=message.from_user.first_name
    )
    
    if user.is_new:
        await message.answer(
            f"👋 Добро пожаловать в DrillFlow, {user.first_name}!\n"
            "Я помогу вам заказать услуги по бурению скважин и монтажу канализации.",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            f"С возвращением, {user.first_name}!",
            reply_markup=get_main_keyboard()
        )

@router.message(F.text == "🔨 Создать заказ")
async def create_order(message: Message, state: FSMContext):
    """Start order creation"""
    await state.set_state(OrderStates.choosing_service)
    await message.answer(
        "Выберите тип услуги:",
        reply_markup=get_service_keyboard()
    )

@router.callback_query(lambda c: c.data.startswith("service_"))
async def process_service_choice(callback: CallbackQuery, state: FSMContext):
    """Process service type selection"""
    service_type = ServiceTypeEnum(callback.data.split("_")[1])
    await state.update_data(service_type=service_type)
    await state.set_state(OrderStates.entering_address)
    
    await callback.message.answer(
        "Отправьте адрес выполнения работ или поделитесь геолокацией.",
        reply_markup=get_location_keyboard()
    )
    await callback.answer()

@router.message(OrderStates.entering_address)
async def process_address(message: Message, state: FSMContext):
    """Process address input"""
    if message.location:
        address = f"lat: {message.location.latitude}, lon: {message.location.longitude}"
        await state.update_data(
            address=address,
            location_lat=message.location.latitude,
            location_lon=message.location.longitude
        )
    else:
        await state.update_data(address=message.text)
    
    await state.set_state(OrderStates.entering_description)
    await message.answer(
        "Опишите ваш заказ подробнее (глубина скважины, тип работ и т.д.):",
        reply_markup=None
    )

@router.message(OrderStates.entering_description)
async def process_description(
    message: Message,
    state: FSMContext,
    order_service: OrderService
):
    """Process order description and create order"""
    data = await state.get_data()
    order = await order_service.create_order(
        client_id=str(message.from_user.id),
        service_type=data["service_type"],
        address=data["address"],
        description=message.text,
        location_lat=data.get("location_lat"),
        location_lon=data.get("location_lon")
    )
    
    contractors = await order_service.find_contractors(order)
    for contractor in contractors:
        try:
            await bot.send_message(
                contractor.telegram_id,
                f"🔔 Новый заказ!\n"
                f"Тип: {order.service_type.value}\n"
                f"Адрес: {order.address}\n"
                f"Описание: {order.description}\n\n"
                f"У вас есть 5 минут на принятие заказа.",
                reply_markup=get_order_actions_keyboard(order.id)
            )
        except Exception as e:
            logger.error(f"Error sending notification to contractor {contractor.id}: {e}")
    
    await message.answer(
        "✅ Заказ успешно создан! Ожидайте подтверждения от подрядчика.",
        reply_markup=get_main_keyboard()
    )
    await state.clear()

@router.callback_query(lambda c: c.data.startswith(("accept_", "decline_")))
async def process_contractor_response(
    callback: CallbackQuery,
    order_service: OrderService
):
    """Process contractor's response to order"""
    action, order_id = callback.data.split("_")
    order_id = int(order_id)
    
    if action == "accept":
        success = await order_service.assign_contractor(
            order_id=order_id,
            contractor_id=str(callback.from_user.id)
        )
        if success:
            order = await order_service.get_order(order_id)
            await bot.send_message(
                order.client_id,
                f"✅ Ваш заказ #{order.id} принят подрядчиком!"
            )
            await callback.answer("Вы приняли заказ!")
        else:
            await callback.answer("Заказ уже принят другим подрядчиком")
    else:
        await callback.answer("Вы отказались от заказа") 