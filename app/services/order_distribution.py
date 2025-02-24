"""
Сервис распределения заказов
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import Order, Contractor, User
from .geo import calculate_distance
from app.core.config import get_settings

async def distribute_order(db: Session, order_id: int) -> bool:
    """Распределение заказа между подрядчиками"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        
        # Находим доступных подрядчиков
        available_contractors = db.query(Contractor).filter(
            Contractor.is_available == True
        ).all()
        
        if not available_contractors:
            return False
        
        # Здесь логика распределения заказа
        # ...
        
        return True
    except Exception as e:
        print(f"Error distributing order: {e}")
        return False

async def distribute_order_old(order: Order, contractors: List[Contractor]) -> Optional[Contractor]:
    """
    Распределяет заказ между подрядчиками
    
    Args:
        order: Заказ для распределения
        contractors: Список доступных подрядчиков
    
    Returns:
        Contractor: Выбранный подрядчик или None
    """
    suitable_contractors: List[Tuple[Contractor, float]] = []
    
    for contractor in contractors:
        if not contractor.user:
            continue
            
        # Проверяем загрузку подрядчика
        if contractor.user.current_orders >= contractor.user.max_orders_per_day:
            continue
            
        # Проверяем радиус работы
        distance = calculate_distance(
            (order.latitude, order.longitude),
            (contractor.latitude, contractor.longitude)
        )
        if distance > contractor.user.work_radius:
            continue
            
        # Добавляем подходящего подрядчика
        suitable_contractors.append((contractor, distance))
    
    if not suitable_contractors:
        return None
        
    # Сортируем по рейтингу и расстоянию
    sorted_contractors = sorted(
        suitable_contractors,
        key=lambda x: (x[0].user.rating, -x[1]),  # Высокий рейтинг и малое расстояние
        reverse=True
    )
    
    return sorted_contractors[0][0] 