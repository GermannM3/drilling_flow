from django.shortcuts import render
from apps.orders.models import Order
from apps.auth.models import ContractorProfile

def dashboard_view(request):
    orders_count = Order.objects.count()
    top_contractors = ContractorProfile.objects.order_by('-rating')[:10]
    context = {
        'orders_count': orders_count,
        'top_contractors': top_contractors,
    }
    return render(request, 'dashboard.html', context) 