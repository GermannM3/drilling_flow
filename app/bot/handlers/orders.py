"""
Обработчики команд для управления заказами
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.services.orders import OrderService
from app.services.users import UserService
from app.schemas.base import OrderStatus, UserRoleEnum
from app.bot.keyboards import get_main_keyboard
from app.utils.geo import format_location

router = Router(name="orders")

@router.message(F.text == "📋 Мои заказы")
async def show_orders(message: Message, order_service: OrderService, user_service: UserService):
    """Показать список заказов пользователя"""
    user = await user_service.get_user(str(message.from_user.id))
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        return

    # Получаем заказы в зависимости от роли пользователя
    if user.role == UserRoleEnum.CONTRACTOR:
        orders = await order_service.get_contractor_orders(str(message.from_user.id))
        title = "📋 Ваши заказы (подрядчик):"
    else:
        orders = await order_service.get_client_orders(str(message.from_user.id))
        title = "📋 Ваши заказы:"

    if not orders:
        await message.answer(
            "У вас пока нет заказов",
            reply_markup=get_main_keyboard()
        )
        return

    # Форматируем список заказов
    orders_text = [title]
    for order in orders:
        order_text = f"\n🔹 Заказ #{order.id}\n"
        order_text += f"Тип: {order.service_type.value}\n"
        order_text += f"Статус: {order.status.value}\n"
        order_text += f"Адрес: {order.address}\n"
        
        if order.location_lat and order.location_lon:
            order_text += f"Координаты: {format_location(order.location_lat, order.location_lon)}\n"
            
        order_text += f"Описание: {order.description}\n"
        
        if order.price:
            order_text += f"Цена: {order.price} ₽\n"
            
        if order.status == OrderStatus.COMPLETED and hasattr(order, 'rating'):
            order_text += f"Оценка: {'⭐' * round(order.rating.rating)}\n"
            if order.rating.comment:
                order_text += f"Комментарий: {order.rating.comment}\n"
                
        orders_text.append(order_text)

    # Разбиваем на сообщения, если текст слишком длинный
    message_text = ""
    for text in orders_text:
        if len(message_text) + len(text) > 4000:
            await message.answer(message_text)
            message_text = text
        else:
            message_text += text
            
    if message_text:
        await message.answer(
            message_text,
            reply_markup=get_main_keyboard()
        )

@router.callback_query(lambda c: c.data.startswith("complete_order_"))
async def complete_order(callback: CallbackQuery, order_service: OrderService):
    """Завершить заказ"""
    order_id = int(callback.data.split("_")[2])
    order = await order_service.get_order(order_id)
    
    if not order:
        await callback.answer("Заказ не найден")
        return
        
    if order.status != OrderStatus.ASSIGNED:
        await callback.answer("Заказ нельзя завершить в текущем статусе")
        return
        
    try:
        await order_service.complete_order(order_id)
        await callback.message.answer(
            f"✅ Заказ #{order_id} успешно завершен!\n"
            "Пожалуйста, оцените работу подрядчика.",
            reply_markup=get_rating_keyboard(order_id)
        )
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при завершении заказа: {str(e)}")
    
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("rate_"))
async def process_rating(callback: CallbackQuery, order_service: OrderService):
    """Обработка оценки заказа"""
    _, order_id, rating = callback.data.split("_")
    order_id = int(order_id)
    rating = float(rating)
    
    try:
        await order_service.complete_order(order_id, rating=rating)
        await callback.message.answer(
            f"Спасибо за вашу оценку! ({'⭐' * round(rating)})"
        )
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при сохранении оценки: {str(e)}")
    
    await callback.answer()

def get_rating_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру для оценки заказа"""
    builder = InlineKeyboardBuilder()
    for rating in range(1, 6):
        builder.button(
            text="⭐" * rating,
            callback_data=f"rate_{order_id}_{rating}"
        )
    builder.adjust(5)
    return builder.as_markup() 