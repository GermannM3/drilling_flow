from celery import shared_task
from .models import Order
from apps.auth.models import ContractorProfile
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import F

@shared_task
def distribute_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    contractors = ContractorProfile.objects.filter(
        specialization=order.service_type,
        current_load__lt=F('max_load'),
        geolocation__distance_lte=(order.geolocation, D(km=F('work_radius')))
    ).annotate(
        distance=Distance('geolocation', order.geolocation)
    ).order_by('-rating', 'distance')

    for contractor in contractors:
        # Здесь разместите логику подтверждения заказа (например, через Telegram)
        confirmed = True  # Заглушка подтверждения
        if confirmed:
            order.contractor = contractor
            order.status = 'assigned'
            order.save()
            contractor.current_load += 1
            contractor.save()
            break 