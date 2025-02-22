from django.shortcuts import render
from apps.orders.models import Order
from apps.auth.models import ContractorProfile
import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.contractors.models import Contractor
from apps.clients.models import Client
from django.conf import settings

def dashboard_view(request):
    orders_count = Order.objects.count()
    top_contractors = ContractorProfile.objects.order_by('-rating')[:10]
    context = {
        'orders_count': orders_count,
        'top_contractors': top_contractors,
    }
    return render(request, 'dashboard.html', context)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика
        context['orders_count'] = Order.objects.count()
        context['contractors_count'] = Contractor.objects.count()
        context['clients_count'] = Client.objects.count()
        
        # Последние заказы
        recent_orders = Order.objects.select_related('client').order_by('-created_at')[:10]
        context['recent_orders'] = recent_orders
        
        # Данные для карты
        orders_for_map = Order.objects.filter(latitude__isnull=False, longitude__isnull=False)
        orders_json = [{
            'id': order.id,
            'latitude': float(order.latitude),
            'longitude': float(order.longitude),
            'status': order.get_status_display()
        } for order in orders_for_map]
        context['orders_json'] = json.dumps(orders_json)
        
        # API ключ для Google Maps
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        
        return context 