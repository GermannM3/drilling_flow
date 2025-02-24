"""
Сервис распределения заказов
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import Order, User, UserRole
from .geo import calculate_distance
from app.core.config import get_settings

async def distribute_order(db: Session, order_id: int) -> bool:
    """Распределение заказа между подрядчиками"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        
        # Находим доступных подрядчиков
        available_contractors = db.query(User).filter(
            User.role == UserRole.CONTRACTOR
        ).all()
        
        if not available_contractors:
            return False
        
        # Здесь логика распределения заказа
        # ...
        
        return True
    except Exception as e:
        print(f"Error distributing order: {e}")
        return False

async def distribute_order_old(order: Order, contractors: List[User]) -> Optional[User]:
    """
    Распределяет заказ между подрядчиками
    
    Args:
        order: Заказ для распределения
        contractors: Список доступных подрядчиков
    
    Returns:
        User: Выбранный подрядчик или None
    """
    suitable_contractors: List[Tuple[User, float]] = []
    
    for contractor in contractors:
        if contractor.role != UserRole.CONTRACTOR:
            continue
            
        # Проверяем загрузку подрядчика
        if len(contractor.contractor_orders) >= 5:  # Максимум 5 заказов в день
            continue
            
        # Проверяем радиус работы
        distance = calculate_distance(
            (order.latitude, order.longitude),
            (contractor.location_lat, contractor.location_lon)  # Нужно добавить эти поля в User
        )
        if distance > 50:  # Максимальный радиус 50 км
            continue
            
        # Добавляем подходящего подрядчика
        suitable_contractors.append((contractor, distance))
    
    if not suitable_contractors:
        return None
        
    # Сортируем по рейтингу и расстоянию
    sorted_contractors = sorted(
        suitable_contractors,
        key=lambda x: (x[0].rating, -x[1]),  # Высокий рейтинг и малое расстояние
        reverse=True
    )
    
    return sorted_contractors[0][0] 