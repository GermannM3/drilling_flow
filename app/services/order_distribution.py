"""
Сервис распределения заказов
"""
from typing import List, Optional, Tuple
from app.db.models import Order, Contractor
from .geo import calculate_distance

async def distribute_order(order: Order, contractors: List[Contractor]) -> Optional[Contractor]:
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