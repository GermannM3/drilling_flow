"""
Сервис управления рейтингами
"""
from app.db.models import (
    User,
    Order,
    OrderStatus,
    OrderRating
)

async def calculate_contractor_rating(user: User) -> float:
    """
    Рассчитывает рейтинг подрядчика
    
    Args:
        user: Пользователь-подрядчик
    
    Returns:
        float: Обновленный рейтинг
    """
    completed_orders = [
        order for order in user.orders 
        if order.status == OrderStatus.COMPLETED and order.rating
    ]
    
    if not completed_orders:
        return 0.0
        
    total_rating = sum(order.rating for order in completed_orders)
    return total_rating / len(completed_orders)

async def update_rating_after_order(order: Order, rating_value: float, comment: str = None) -> None:
    """
    Обновляет рейтинг после выполнения заказа
    
    Args:
        order: Заказ
        rating_value: Оценка от 1 до 5
        comment: Комментарий к оценке
    """
    order.rating = rating_value
    
    # Обновляем рейтинг подрядчика
    if order.contractor:
        order.contractor.rating = await calculate_contractor_rating(order.contractor) 