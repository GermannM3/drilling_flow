from django.db.models import F, Q
from django.contrib.gis.db.models.functions import Distance
from datetime import timedelta

def calculate_priority(contractor, order):
    # Весовые коэффициенты
    distance_weight = 0.4
    rating_weight = 0.3
    availability_weight = 0.3
    
    # Нормализация значений
    distance_score = 1 - (contractor.distance / (contractor.work_radius * 1000))
    rating_score = contractor.rating / 5.0
    availability_score = 1 - (contractor.current_orders / contractor.max_daily_orders)
    
    return (distance_weight * distance_score +
            rating_weight * rating_score +
            availability_weight * availability_score)

def assign_order(order: Order):
    contractors = Contractor.objects.annotate(
        distance=Distance('location', order.location)
    ).filter(
        Q(specialization=order.service_type) | Q(specialization='general'),
        distance__lte=order.work_radius * 1000,
        is_verified=True,
        current_orders__lt=F('max_daily_orders')
    ).order_by('-rating', 'current_orders')

    if not contractors.exists():
        notify_admin('Не найдено подрядчиков')
        return

    # Рассчитываем приоритет для каждого подрядчика
    contractors = [
        (contractor, calculate_priority(contractor, order))
        for contractor in contractors
    ]
    
    # Сортируем по приоритету
    contractors.sort(key=lambda x: x[1], reverse=True)
    
    # Пытаемся назначить заказ по порядку
    for contractor, _ in contractors[:5]:
        if send_notification(contractor):
            order.assigned_to = contractor
            order.deadline = timezone.now() + timedelta(hours=24)  # Срок выполнения 24 часа
            order.status = 'assigned'
            order.save()
            start_confirmation_timer(order.id)
            return 