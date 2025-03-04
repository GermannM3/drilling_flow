"""
Сервис управления рейтингами
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Order, OrderStatus, OrderRating
from .rating import OrderRating

async def calculate_contractor_rating(user: User) -> float:
    """
    Рассчитывает рейтинг подрядчика
    
    Args:
        user: Пользователь-подрядчик
    
    Returns:
        float: Обновленный рейтинг
    """
    completed_orders = [
        order for order in user.contractor_orders 
        if order.status == OrderStatus.COMPLETED and order.ratings
    ]
    
    if not completed_orders:
        return 0.0
        
    total_rating = sum(order.ratings[0].rating for order in completed_orders)
    return total_rating / len(completed_orders)

async def update_rating_after_order(order: Order, rating_value: float) -> None:
    """
    Обновляет рейтинг после выполнения заказа
    
    Args:
        order: Заказ
        rating_value: Оценка от 1 до 5
    """
    # Создаем новый рейтинг
    rating = OrderRating(
        order=order,
        contractor=order.contractor,
        rating=rating_value
    )
    
    # Обновляем рейтинг подрядчика
    if order.contractor:
        order.contractor.rating = await calculate_contractor_rating(order.contractor)

async def get_contractor_rating(
    db: AsyncSession,
    limit: int = 10
) -> list[User]:
    """Получение рейтинга подрядчиков"""
    query = (
        select(User)
        .filter(User.is_contractor == True)
        .order_by(User.rating.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    return result.scalars().all() 