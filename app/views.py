from django.shortcuts import render
from .models import Order, ContractorProfile

def dashboard(request):
    """
    Публичный дашборд с открытой статистикой:
    - Общее число заказов
    - Топ-10 подрядчиков по рейтингу
    """
    orders_count = Order.objects.count()
    top_contractors = ContractorProfile.objects.order_by('-rating')[:10]
    context = {
        'orders_count': orders_count,
        'top_contractors': top_contractors,
    }
    return render(request, 'dashboard.html', context)

def order_detail(request, order_id):
    """
    Детальная информация по заказу (реализация по необходимости)
    """
    # Пример: получение заказа и передача его в шаблон
    # order = Order.objects.get(id=order_id)
    # return render(request, 'order_detail.html', {'order': order})
    pass 