from celery import shared_task
from django.utils import timezone
from .models import Order
from contractors.models import ContractorProfile

@shared_task
def distribute_order(order_id):
    try:
        order = Order.objects.get(id=order_id, status='pending')
    except Order.DoesNotExist:
        return "Order not found or not pending"
    
    # Фильтруем подрядчиков, прошедших верификацию и у которых количество заказов за день меньше 2
    eligible_contractors = ContractorProfile.objects.filter(
        verified=True,
        daily_orders_count__lt=2,
        # Можно добавить дополнительную фильтрацию по специализации и расстоянию
    ).order_by('-rating')
    
    if eligible_contractors.exists():
        contractor = eligible_contractors.first()
        order.assigned_contractor = contractor
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()
        contractor.daily_orders_count += 1
        contractor.save()
        return f"Заказ {order.id} назначен подрядчику {contractor.full_name}"
    else:
        return "Не найдено подходящего подрядчика" 